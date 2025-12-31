<template>
  <div class="posts-page">
    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h1>Machine Learning Community</h1>
        <p>Share experiences with other learners and discover quality content</p>
        <div class="header-actions">
          <!-- 智能切换按钮 -->
          <div class="mode-toggle">
            <button
              class="mode-btn"
              :class="{ active: activeMode === 'traditional' }"
              @click="switchToTraditional"
            >
              <i class="fas fa-list"></i>
              Browse
            </button>
            <button
              class="mode-btn"
              :class="{ active: activeMode === 'ai' }"
              @click="switchToAI"
            >
              <i class="fas fa-brain"></i>
              AI Discover
            </button>
          </div>
          <router-link to="/create-post" class="btn btn-white" aria-label="Create new post - Press Ctrl+Plus">
            <i class="fas fa-plus"></i> Create Post
          </router-link>
        </div>
      </div>

      <!-- AI推荐模式 -->
      <div v-if="activeMode === 'ai'" class="ai-mode">
        <!-- AI学习分析 -->
        <AILearningAnalysis ref="aiAnalysisRef" />

        <!-- AI推荐内容 -->
        <AIRecommendations ref="aiRecommendationsRef" />
      </div>

      <!-- 传统浏览模式 -->
      <div v-else class="traditional-mode">
        <!-- 筛选和搜索 -->
          <div class="posts-controls">
            <div class="search-box">
              <input
                ref="searchInput"
                type="search"
                aria-label="Search posts - Press Ctrl+K to focus"
                v-model="searchQuery"
                @input="debouncedSearch"
                placeholder="Search posts..."
                class="search-input"
              >
              <i class="fas fa-search search-icon"></i>
            </div>
            <div class="filter-buttons">
              <div class="filter-group">
                <label>Sort by:</label>
                <select v-model="sortBy" @change="handleSortChange()">
                  <option v-for="option in sortOptions" :key="option.id" :value="option.id">{{ option.name }}</option>
                </select>
              </div>
              <div class="filter-group">
                <label>Order:</label>
                <div class="order-buttons">
                  <button
                    class="order-btn"
                    :class="{ active: sortOrder === 'desc' }"
                    @click="setSortOrder('desc')"
                  >
                    <i class="fas fa-sort-amount-down"></i>
                    Descending
                  </button>
                  <button
                    class="order-btn"
                    :class="{ active: sortOrder === 'asc' }"
                    @click="setSortOrder('asc')"
                  >
                    <i class="fas fa-sort-amount-up"></i>
                    Ascending
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 帖子列表 -->
          <div class="posts-container">
            <div v-if="loading" class="loading">Loading posts...</div>
            <div v-else-if="posts.length === 0" class="no-posts">
              <i class="fas fa-inbox fa-3x"></i>
              <h3>No posts yet</h3>
              <p>Be the first to share your learning experience!</p>
              <router-link v-if="userStore.isLoggedIn" to="/create-post" class="btn btn-primary">
                Create the first post
              </router-link>
            </div>
            <div v-else class="posts-list">
              <div
                v-for="(post, index) in posts"
                :key="post.id"
                class="post-card"
                @click="$router.push(`/posts/${post.id}`)"
              >
                <div class="post-header">
                  <div class="post-author">
                    <div class="author-avatar">
                      <img :src="post.author?.avatar || '/assets/profile.jpg'" alt="author avatar" />
                    </div>
                    <div class="author-info">
                      <span class="author-name">{{ post.author?.username }}</span>
                      <span class="post-time">{{ formatDate(post.created_at) }}</span>
                    </div>
                  </div>
                  <div v-if="post.is_featured" class="featured-badge">
                    <i class="fas fa-star"></i> Featured
                  </div>
                </div>

                <div class="post-content">
                  <h3 class="post-title">
                    {{ post.title }}
                    <span
                      v-if="accessibilityStore.accessibilityMode && index < 9"
                      class="accessibility-shortcut"
                      :aria-label="`Keyboard shortcut: Alt + ${index + 1}`"
                    >
                      Alt+{{ index + 1 }}
                    </span>
                  </h3>
                  <p class="post-excerpt">{{ post.content?.substring(0, 150) }}...</p>
                </div>

                <div class="post-footer">
                  <div class="post-stats">
                    <span class="stat-item"><i class="fas fa-heart"></i> {{ post.like_count || 0 }}</span>
                    <span class="stat-item"><i class="fas fa-comment"></i> {{ post.comment_count || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div v-if="totalPages > 1" class="pagination">
            <button
              class="btn btn-outline"
              :disabled="currentPage <= 1"
              @click="goToPage(currentPage - 1)"
            >
              <i class="fas fa-chevron-left"></i> Previous
            </button>
            <span class="pagination-info">
              Page {{ currentPage }} of {{ totalPages }}
            </span>
            <button
              class="btn btn-outline"
              :disabled="currentPage >= totalPages"
              @click="goToPage(currentPage + 1)"
            >
              Next <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { useAccessibilityStore } from '@/stores/accessibility'
import AILearningAnalysis from '@/components/AILearningAnalysis.vue'
import AIRecommendations from '@/components/AIRecommendations.vue'

const userStore = useUserStore()
const accessibilityStore = useAccessibilityStore()
const $router = useRouter()
const searchInput = ref<HTMLInputElement | null>(null)

// 页面键盘事件处理
const handlePageKeydown = (event: KeyboardEvent) => {
  // Ctrl+K 聚焦搜索框
  if (event.ctrlKey && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    searchInput.value?.focus()
  }
}

// 监听键盘快捷键事件
const handleOpenCreatePost = () => {
  $router.push('/create-post')
}

const handleJumpToPost = (event: Event) => {
  const detail = (event as CustomEvent).detail
  const index = detail.index - 1 // 转换为0-based索引

  if (index >= 0 && index < posts.value.length) {
    const postId = posts.value[index].id
    $router.push(`/posts/${postId}`)
  } else {
    alert(`帖子序号超出范围，请输入1-${posts.value.length}之间的数字`)
  }
}

const handleAccessibilityShortcut = (event: Event) => {
  const detail = (event as CustomEvent).detail
  if (detail.type === 'post' && detail.index >= 0 && detail.index < posts.value.length) {
    const postId = posts.value[detail.index].id
    $router.push(`/posts/${postId}`)
  }
}

// Listen for global event from keyboard manager
onMounted(() => {
  // 添加页面级键盘事件监听
  window.addEventListener('keydown', handlePageKeydown)
  window.addEventListener('open-create-post', handleOpenCreatePost)
  window.addEventListener('jump-to-post-by-index', handleJumpToPost)
  window.addEventListener('accessibility-shortcut', handleAccessibilityShortcut)

  // 初始化数据加载
  if (activeMode.value === 'traditional') {
    fetchPosts()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handlePageKeydown)
  window.removeEventListener('open-create-post', handleOpenCreatePost)
  window.removeEventListener('jump-to-post-by-index', handleJumpToPost)
  window.removeEventListener('accessibility-shortcut', handleAccessibilityShortcut)
})

// 模式切换相关
const activeMode = ref('traditional') // 'traditional' | 'ai'
const aiAnalysisRef = ref()
const aiRecommendationsRef = ref()

// 传统浏览模式相关
const posts = ref([])
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const sortBy = ref('created_at')
const sortOrder = ref('desc')

const sortOptions = [
  { id: 'created_at', name: 'Date' },
  { id: 'like_count', name: 'Likes' },
  { id: 'comment_count', name: 'Comments' },
  { id: 'view_count', name: 'Views' }
]


// 获取帖子列表
const fetchPosts = async () => {
  console.log('fetchPosts called, activeMode:', activeMode.value)
  if (activeMode.value === 'ai') {
    console.log('Skipping fetchPosts because activeMode is ai')
    return // AI模式不加载传统帖子
  }

  console.log('Starting to fetch posts...')
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      per_page: '12',
      search: searchQuery.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value
    })

    console.log('Fetching posts with params:', params.toString())
    const response = await axios.get(`/api/posts?${params}`)
    console.log('API response:', response.data)
    posts.value = response.data.posts || []
    totalPages.value = response.data.pages || response.data.total_pages || 1
    console.log('Posts set to:', posts.value.length, 'items')
  } catch (error) {
    console.error('Failed to fetch posts:', error)
    posts.value = []
  } finally {
    loading.value = false
    console.log('Loading set to false')
  }
}

// 防抖搜索
let searchTimeout = null
const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchPosts()
  }, 500)
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`

  return date.toLocaleDateString()
}

// 分页函数
const goToPage = (page: number) => {
  currentPage.value = page
  fetchPosts()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 排序处理函数
const handleSortChange = () => {
  currentPage.value = 1
  fetchPosts()
}

const setSortOrder = (order: string) => {
  sortOrder.value = order
  currentPage.value = 1
  fetchPosts()
}

// 模式切换相关函数
const switchToTraditional = () => {
  activeMode.value = 'traditional'
  // 切换到传统模式时加载帖子
  fetchPosts()
}

const switchToAI = () => {
  activeMode.value = 'ai'
  // 当切换到AI模式时，确保AI组件加载数据
  if (aiRecommendationsRef.value) {
    aiRecommendationsRef.value.loadRecommendations()
  }
}

// 初始化已在上面的onMounted中处理
</script>

<style scoped>
.posts-page {
  padding: 2rem 0;
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-dark);
  margin-bottom: 0.5rem;
}

.page-header p {
  color: var(--text-muted);
  margin-bottom: 2rem;
}

/* 模式切换样式 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

.mode-toggle {
  display: flex;
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  background: rgba(255, 255, 255, 0.8);
}

.mode-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mode-btn:hover {
  background: rgba(30, 64, 175, 0.12);
  color: #1e40af;
}

.mode-btn.active {
  background: #1e40af;
  color: white;
  font-weight: 600;
}

/* AI模式和传统模式容器 */
.ai-mode,
.traditional-mode {
  margin-top: 2rem;
}

/* 筛选和搜索 */
.posts-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: center;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.9);
}

.search-input:focus {
  outline: none;
  border-color: #1e40af;
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.12);
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.filter-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* 帖子列表 */
.posts-container {
  margin-top: 2rem;
}

.loading {
  text-align: center;
  padding: 3rem;
  font-size: 1.1rem;
  color: var(--text-muted);
}

.no-posts {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
}

.no-posts i {
  display: block;
  margin-bottom: 1rem;
  font-size: 3rem;
}

.no-posts h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-dark);
}

.no-posts p {
  margin-bottom: 1.5rem;
}

.posts-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.post-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-dark);
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #1e40af;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.author-avatar img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: var(--text-dark);
  font-size: 0.9rem;
}

.post-time {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.featured-badge {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.post-content h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-dark);
  line-height: 1.4;
}

.post-excerpt {
  color: var(--text-muted);
  line-height: 1.5;
  margin-bottom: 1rem;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-stats {
  display: flex;
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* 筛选控件 */
.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-dark);
  white-space: nowrap;
  margin-bottom: 0;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  background: white;
  font-size: 0.875rem;
  min-width: 120px;
}

.filter-group select:focus {
  outline: none;
  border-color: #1e40af;
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.12);
}

/* 排序按钮 */
.order-buttons {
  display: flex;
  gap: 0.5rem;
}

.order-btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e7eb;
  background: white;
  color: var(--text-muted);
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.order-btn:hover {
  border-color: #1e40af;
  color: #1e40af;
}

.order-btn.active {
  background: #1e40af;
  color: white;
  border-color: #1e40af;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.pagination-info {
  color: var(--text-muted);
  font-size: 0.9rem;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .posts-controls {
    flex-wrap: wrap;
    gap: 1rem;
  }

  .filter-buttons {
    flex-wrap: wrap;
  }

  .posts-list {
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .page-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .page-header h1 {
    font-size: 2rem;
    margin-bottom: 0.75rem;
  }

  .page-header p {
    font-size: 1rem;
  }

  .header-actions {
    flex-direction: column;
    gap: 1rem !important;
    align-items: stretch !important;
  }

  .mode-toggle {
    justify-content: center;
    gap: 0.5rem;
  }

  .mode-btn {
    padding: 0.5rem 0.75rem !important;
    font-size: 0.85rem;
  }

  .posts-controls {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
    padding: 1rem;
  }

  .search-box {
    order: 1;
  }

  .search-input {
    padding: 0.625rem 1rem 0.625rem 2.5rem;
    font-size: 0.9rem;
  }

  .search-icon {
    left: 0.75rem;
  }

  .filter-buttons {
    order: 2;
    flex-direction: column;
    gap: 0.75rem;
  }

  .filter-group {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .filter-group label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-dark);
  }

  .filter-group select {
    width: 100%;
    padding: 0.625rem;
    font-size: 0.85rem;
  }

  .order-buttons {
    flex-direction: row;
    justify-content: center;
    gap: 0.5rem;
  }

  .order-btn {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }

  .posts-container {
    padding: 1.5rem 0;
  }

  .posts-list {
    gap: 0.75rem;
  }

  .post-card {
    padding: 1rem;
  }

  .post-header {
    margin-bottom: 0.75rem;
  }

  .author-info {
    flex: 1;
  }

  .author-name {
    font-size: 0.9rem;
  }

  .post-time {
    font-size: 0.8rem;
  }

  .post-content {
    margin-bottom: 0.75rem;
  }

  .post-title {
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
  }

  .post-excerpt {
    font-size: 0.9rem;
  }

  .post-footer {
    margin-top: 0.75rem;
  }

  .post-stats {
    gap: 1rem;
  }

  .stat-item {
    font-size: 0.8rem;
  }

  .pagination {
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
  }

  .btn {
    min-height: 44px;
    padding: 0.625rem 1rem;
  }

  .accessibility-shortcut {
    display: none !important;
  }
}

@media (max-width: 576px) {
  .posts-page {
    padding: 1.5rem 0;
  }

  .page-header h1 {
    font-size: 1.75rem;
  }

  .page-header p {
    font-size: 0.95rem;
  }

  .header-actions {
    gap: 0.75rem !important;
  }

  .mode-btn {
    padding: 0.5rem 0.625rem !important;
    font-size: 0.8rem;
  }

  .posts-controls {
    padding: 0.75rem;
  }

  .search-input {
    padding: 0.5rem 0.75rem 0.5rem 2.25rem;
    font-size: 0.85rem;
  }

  .filter-group label {
    font-size: 0.8rem;
  }

  .filter-group select {
    padding: 0.5rem;
    font-size: 0.8rem;
  }

  .order-btn {
    padding: 0.4rem 0.625rem;
    font-size: 0.75rem;
  }

  .posts-container {
    padding: 1rem 0;
  }

  .post-card {
    padding: 0.875rem;
  }

  .post-title {
    font-size: 1rem;
  }

  .post-excerpt {
    font-size: 0.85rem;
  }

  .author-name {
    font-size: 0.85rem;
  }

  .post-time {
    font-size: 0.75rem;
  }

  .stat-item {
    font-size: 0.75rem;
  }

  .pagination {
    padding: 0.75rem;
  }

  .btn {
    min-height: 40px;
    padding: 0.5rem 0.875rem;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .posts-page {
    padding: 1rem 0;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .page-header p {
    font-size: 0.9rem;
  }

  .header-actions {
    gap: 0.5rem !important;
  }

  .mode-btn {
    padding: 0.4rem 0.5rem !important;
    font-size: 0.75rem;
  }

  .posts-controls {
    padding: 0.5rem;
  }

  .search-input {
    padding: 0.45rem 0.625rem 0.45rem 2rem;
    font-size: 0.8rem;
  }

  .filter-group label {
    font-size: 0.75rem;
  }

  .filter-group select {
    padding: 0.45rem;
    font-size: 0.75rem;
  }

  .order-btn {
    padding: 0.35rem 0.5rem;
    font-size: 0.7rem;
  }

  .post-card {
    padding: 0.75rem;
  }

  .post-title {
    font-size: 0.95rem;
  }

  .post-excerpt {
    font-size: 0.8rem;
  }

  .author-name {
    font-size: 0.8rem;
  }

  .post-time {
    font-size: 0.7rem;
  }

  .stat-item {
    font-size: 0.7rem;
  }

  .btn {
    min-height: 36px;
    padding: 0.45rem 0.75rem;
    font-size: 0.8rem;
  }
}

/* Accessibility shortcut styles */
.accessibility-shortcut {
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.125rem 0.375rem;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.accessibility-shortcut::selection {
  background: transparent;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .accessibility-shortcut {
    background: #000;
    color: #fff;
    border: 2px solid #fff;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .accessibility-shortcut {
    transition: none;
  }
}

</style>
