<template>
  <div class="profile-page">
    <div class="container">
      <!-- 用户信息头部 -->
      <div class="profile-header">
        <div class="user-info">
          <div class="avatar" style="width:96px;height:96px;border-radius:14px;overflow:hidden;">
            <img :src="userStore.user?.avatar || '/assets/profile.jpg'" alt="profile avatar" style="width:100%;height:100%;object-fit:cover;" />
          </div>
          <div class="user-details">
            <h1>{{ userStore.user?.username }}</h1>
            <p class="user-role">{{ getRoleText(userStore.user?.role) }}</p>
            <div class="user-stats">
              <div class="stat">
                <span class="stat-number">{{ userKnowledge.length }}</span>
                <span class="stat-label">Learned Algorithms</span>
              </div>
              <div class="stat">
                <span class="stat-number">{{ totalProgress }}%</span>
                <span class="stat-label">Average Progress</span>
              </div>
              <div class="stat">
                <span class="stat-number">{{ favoritePosts.length }}</span>
                <span class="stat-label">Favorite Posts</span>
              </div>
            </div>
          </div>
        </div>
                        <div class="profile-actions">
          <label class="btn btn-secondary" for="avatarUpload">
            <i class="fas fa-upload"></i> Upload Avatar
          </label>
          <input id="avatarUpload" ref="avatarInput" type="file" accept="image/*" style="display:none" @change="onAvatarSelected" />
          <button class="btn btn-secondary" @click="$router.push('/posts')">
            <i class="fas fa-plus"></i> Create Post
          </button>
          <button v-if="userStore.isAdmin" class="btn btn-primary" @click="$router.push('/admin')">
            <i class="fas fa-cog"></i> Admin Panel
          </button>
        </div>
      </div>

      <!-- Knowledge Mastery Radar Chart -->
      <div class="radar-section">
        <div class="radar-header">
          <h2>Knowledge Mastery Radar</h2>
          <div class="radar-stats" v-if="radarStats">
            <div class="stat-item">
              <span class="stat-label">Learned Algorithms:</span>
              <span class="stat-value">{{ radarStats.totalKnowledge }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Average Progress:</span>
              <span class="stat-value">{{ radarStats.avgProgress }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Community Activities:</span>
              <span class="stat-value">{{ radarStats.totalActivities }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Recent Activity:</span>
              <span class="stat-value">{{ radarStats.recentActivity }}</span>
            </div>
          </div>
        </div>
        <!-- 新结构：radar-body 为两列布局，左侧为图 + 图例，最右侧为独立建议列 -->
        <div class="radar-body">
          <div class="radar-container">
            <div id="knowledge-radar" class="radar-chart"></div>
            <div class="radar-side">
              <div class="radar-legend">
                <div class="legend-item">
                  <div class="legend-color" style="background: #a78bfa;"></div>
                  <span style="color:var(--text-dark)">已掌握 (≥80%)</span>
                </div>
                <div class="legend-item">
                  <div class="legend-color" style="background: #fbbf24;"></div>
                  <span style="color:var(--text-dark)">学习中 (20%-79%)</span>
                </div>
                <div class="legend-item">
                  <div class="legend-color" style="background: #b91c1c;"></div>
                  <span style="color:var(--text-dark)">薄弱 (<20%)</span>
                </div>
              </div>
            </div>
          </div>

          <div class="radar-suggestions" v-if="learningSuggestions.length > 0">
            <div class="learning-suggestions no-top-border">
              <h3>💡 学习建议</h3>
              <ul class="suggestions-list">
                <li v-for="suggestion in learningSuggestions" :key="suggestion" class="suggestion-item">
                  {{ suggestion }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        
      </div>

      <!-- Learning Records -->
      <div class="learning-records">
        <h2>Learning Records</h2>
        <div class="records-filters">
          <!-- Date Range Filter -->
          <div class="filter-group">
            <label>Date Range:</label>
            <select v-model="dateFilter" @change="applyFilters">
              <option value="all">All Time</option>
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
              <option value="quarter">Last 3 Months</option>
              <option value="year">Last Year</option>
            </select>
          </div>

          <!-- Type Filter -->
          <div class="filter-group">
            <label>Type:</label>
            <select v-model="typeFilter" @change="applyFilters">
              <option value="all">All Activities</option>
              <option value="algorithm">Algorithm Learning</option>
              <option value="post">Post Interactions</option>
            </select>
          </div>

          <!-- Sort Options -->
          <div class="filter-group">
            <label>Sort by:</label>
            <select v-model="sortBy" @change="sortRecords">
              <option value="last_accessed">Most Recent</option>
              <option value="progress">Progress</option>
              <option value="name">Name</option>
            </select>
          </div>
        </div>
        <div class="records-list">
          <div
            v-for="record in paginatedLearningRecords"
            :key="`${record.type}-${record.id || record.algorithm_id}`"
            class="record-card"
            :class="record.type === 'algorithm' ? 'algorithm-record' : 'post-record'"
            @click="record.type === 'algorithm' ? $router.push(`/algorithms/${record.algorithm_id}`) : $router.push(`/posts/${record.id}`)"
          >
            <div class="record-icon">
              <i :class="record.icon" :style="{ color: record.color }"></i>
            </div>
            <div class="record-info">
              <h3>{{ record.type === 'algorithm' ? getAlgorithmName(record.algorithm_id) : record.title }}</h3>
              <div class="record-meta">
                <span class="category">
                  {{ record.type === 'algorithm' ? getAlgorithmCategory(record.algorithm_id) : 'Post' }}
                </span>
                <span v-if="record.last_accessed || record.created_at" class="last-accessed">{{ formatDate(record.last_accessed || record.created_at) }}</span>
                <span class="record-type">
                  {{ record.type === 'algorithm' ? 'Algorithm Learning' :
                     record.type === 'post' ? 'Post Interaction' :
                     record.type === 'like' ? 'Liked' :
                     record.type === 'favorite' ? 'Saved' : 'Commented' }}
                </span>
              </div>
            </div>
            <div v-if="record.type === 'algorithm'" class="record-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: `${record.progress}%` }"></div>
              </div>
              <span class="progress-text">{{ record.progress }}%</span>
            </div>
            <div v-else class="record-stats">
              <span class="stat"><i class="fas fa-eye"></i> {{ record.view_count }}</span>
              <span class="stat"><i class="fas fa-thumbs-up"></i> {{ record.like_count }}</span>
            </div>
            <div v-if="record.type === 'algorithm' && record.interests" class="record-interests">
              <div v-for="interest in record.interests.slice(0, 2)" :key="interest" class="interest-tag">
                {{ interest }}
              </div>
            </div>
          </div>
        </div>

        <!-- 学习记录分页 -->
        <div v-if="totalLearningRecordPages > 1" class="pagination">
          <button
            class="page-btn"
            :disabled="learningRecordsPage === 1"
            @click="learningRecordsPage--"
            aria-label="上一页"
          >
            <i class="fas fa-chevron-left" aria-hidden="true"></i>
          </button>

          <button
            v-for="page in visiblePages(totalLearningRecordPages, learningRecordsPage)"
            :key="page"
            type="button"
            class="page-number"
            :class="{ active: page === learningRecordsPage }"
            @click="learningRecordsPage = page"
            :aria-current="page === learningRecordsPage ? 'page' : null"
          >
            {{ page }}
          </button>

          <button
            class="page-btn"
            :disabled="learningRecordsPage === totalLearningRecordPages"
            @click="learningRecordsPage++"
            aria-label="下一页"
          >
            <i class="fas fa-chevron-right" aria-hidden="true"></i>
          </button>
        </div>
      </div>

      <!-- My Activity -->
      <div class="user-activity">
        <h2>My Activity</h2>
        <div class="activity-tabs">
          <button class="btn btn-outline" :class="{ active: activeSection === 'favorites' }" @click="loadFavorites">Favorites<span v-if="favorites.length"> ({{ favorites.length }})</span></button>
          <button class="btn btn-outline" :class="{ active: activeSection === 'likes' }" @click="loadLikes">Likes<span v-if="likes.length"> ({{ likes.length }})</span></button>
          <button class="btn btn-outline" :class="{ active: activeSection === 'replies' }" @click="loadReplies">Replies<span v-if="replies.length"> ({{ replies.length }})</span></button>
          <button class="btn btn-outline" :class="{ active: activeSection === 'posts' }" @click="loadUserPosts">My Posts<span v-if="userPosts.length"> ({{ userPosts.length }})</span></button>
        </div>

        <div class="activity-content">
          <div v-if="activeSection === 'favorites'">
            <div v-if="currentActivityItems.length === 0" class="no-posts">
              <p>还没有收藏的帖子</p>
            </div>
            <div v-else class="activity-list">
              <div v-for="post in currentActivityItems" :key="post.id" class="activity-card" @click="$router.push(`/posts/${post.id}`)">
                <h4>{{ post.title }}</h4>
                <p>{{ post.content.substring(0, 100) }}...</p>
                <div class="activity-meta">
                  <span>{{ post.like_count }} 赞</span>
                  <span>{{ post.comment_count }} 评论</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeSection === 'likes'">
            <div v-if="currentActivityItems.length === 0" class="no-posts">
              <p>还没有点赞的帖子</p>
            </div>
            <div v-else class="activity-list">
              <div v-for="post in currentActivityItems" :key="post.id" class="activity-card" @click="$router.push(`/posts/${post.id}`)">
                <h4>{{ post.title }}</h4>
                <p>{{ post.content.substring(0, 100) }}...</p>
                <div class="activity-meta">
                  <span>{{ post.like_count }} 赞</span>
                  <span>{{ post.comment_count }} 评论</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeSection === 'replies'">
            <div v-if="currentActivityItems.length === 0" class="no-posts">
              <p>还没有新的回复</p>
            </div>
            <div v-else class="activity-list">
              <div v-for="reply in currentActivityItems" :key="reply.id" class="activity-card">
                <p><strong>回复你的评论:</strong></p>
                <p>{{ reply.content }}</p>
                <div class="activity-meta">
                  <span>{{ reply.author?.username }}</span>
                  <span>{{ formatDate(reply.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeSection === 'posts'">
            <div v-if="currentActivityItems.length === 0" class="no-posts">
              <p>还没有发布帖子</p>
            </div>
            <div v-else class="activity-list">
              <div v-for="post in currentActivityItems" :key="post.id" class="activity-card" @click="$router.push(`/posts/${post.id}`)">
                <div class="post-actions-top">
                  <button class="btn btn-sm btn-outline delete-btn" @click.stop="confirmDeletePost(post)">
                    <i class="fas fa-trash"></i> Delete
                  </button>
                </div>
                <h4>{{ post.title }}</h4>
                <p>{{ post.content.substring(0, 100) }}...</p>
                <div class="activity-meta">
                  <span>{{ post.like_count }} likes</span>
                  <span>{{ post.comment_count }} comments</span>
                  <span>{{ formatDate(post.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 活动分页 -->
          <div v-if="totalActivityPages > 1" class="pagination activity-pagination">
            <button
              class="page-btn"
              :disabled="activityPage === 1"
              @click="activityPage--"
              aria-label="上一页"
            >
              <i class="fas fa-chevron-left" aria-hidden="true"></i>
            </button>

            <button
              v-for="page in visiblePages(totalActivityPages, activityPage)"
              :key="page"
              type="button"
              class="page-number"
              :class="{ active: page === activityPage }"
              @click="activityPage = page"
              :aria-current="page === activityPage ? 'page' : null"
            >
              {{ page }}
            </button>

            <button
              class="page-btn"
              :disabled="activityPage === totalActivityPages"
              @click="activityPage++"
              aria-label="下一页"
            >
              <i class="fas fa-chevron-right" aria-hidden="true"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 推荐内容 -->
      <div class="recommendations">
        <h2>Recommended for you</h2>
        <div class="recommendations-tabs">
          <button
            v-for="tab in recommendationTabs"
            :key="tab.id"
            class="tab"
            :class="{ active: activeRecommendationTab === tab.id }"
            @click="activeRecommendationTab = tab.id"
          >
            {{ tab.name }}
          </button>
        </div>
        <div class="recommendations-content">
          <!-- Recommended algorithms -->
          <div v-if="activeRecommendationTab === 'algorithms'" class="recommended-algorithms">
            <div
              v-for="algorithm in recommendedAlgorithms"
              :key="algorithm.id"
              class="algorithm-card recommended-card"
              @click="$router.push(`/algorithms/${algorithm.id}`)"
            >
              <div class="card-header">
                <h4>{{ algorithm.chinese_name || algorithm.name }}</h4>
                <div class="recommendation-score">
                  <span class="score-badge">{{ algorithm.recommendation_score }}</span>
                </div>
              </div>
              <p>{{ algorithm.description.substring(0, 80) }}...</p>
              <div class="algorithm-meta">
                <span class="difficulty" :class="algorithm.difficulty">{{ getDifficultyText(algorithm.difficulty) }}</span>
                <span class="category">{{ algorithm.category?.name }}</span>
              </div>
              <div class="recommendation-reasons" v-if="algorithm.recommendation_reasons && algorithm.recommendation_reasons.length > 0">
                <div class="reasons-list">
                  <span v-for="reason in algorithm.recommendation_reasons" :key="reason" class="reason-tag">
                    {{ reason }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Recommended posts -->
          <div v-if="activeRecommendationTab === 'posts'" class="recommended-posts">
            <div
              v-for="post in recommendedPosts"
              :key="post.id"
              class="post-card recommended-card"
              @click="$router.push(`/posts/${post.id}`)"
            >
              <div class="card-header">
                <h4>{{ post.title }}</h4>
                <div class="recommendation-score">
                  <span class="score-badge">{{ post.recommendation_score }}</span>
                </div>
              </div>
              <p>{{ post.content.substring(0, 100) }}...</p>
              <div class="post-meta">
                <span>{{ post.author?.username }}</span>
                <span>{{ post.like_count }} 赞</span>
              </div>
              <div class="recommendation-reasons" v-if="post.recommendation_reasons && post.recommendation_reasons.length > 0">
                <div class="reasons-list">
                  <span v-for="reason in post.recommendation_reasons" :key="reason" class="reason-tag">
                    {{ reason }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Learning Analysis -->
      <div class="ai-analysis">
        <h2>AI Learning Analysis</h2>
        <p>Get personalized insights about your learning progress and recommendations</p>

        <div class="analysis-controls">
          <button
            class="btn btn-primary generate-report-btn"
            @click="generateLearningReport"
            :disabled="generatingReport"
          >
            <i class="fas fa-chart-line"></i>
            {{ generatingReport ? 'Analyzing...' : 'Generate Learning Report' }}
          </button>
        </div>

        <div v-if="aiReport" class="report-content">
          <div class="report-header">
            <h3>📊 Personalized Learning Analysis Report</h3>
            <small>Generated: {{ formatReportTime(aiReport.generated_at) }}</small>
          </div>

          <div class="report-body">
            <div class="report-text" v-html="formatReportContent(aiReport.report)"></div>
          </div>
        </div>

        <div v-else-if="!generatingReport" class="no-report">
          <div class="no-report-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <h4>还没有生成学习报告</h4>
          <p>点击上方按钮，让AI为您分析学习情况并提供个性化建议</p>
        </div>

        <div v-if="generatingReport" class="loading-report">
          <div class="loading-spinner">
            <div class="spinner"></div>
          </div>
          <h4>AI正在分析您的学习数据...</h4>
          <p>这可能需要几秒钟时间，请耐心等待</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const userKnowledge = ref([])
const favoritePosts = ref([])
const likedPosts = ref([])
const commentedPosts = ref([])
const userPosts = ref([])
const recommendedAlgorithms = ref([])
const recommendedPosts = ref([])
const algorithms = ref([])
const sortBy = ref('last_accessed')
const filterBy = ref('all')
const dateFilter = ref('all')
const typeFilter = ref('all')
const activeRecommendationTab = ref('algorithms')
  const activeSection = ref('favorites') // favorites | likes | replies
  const favorites = ref<any[]>([])
  const likes = ref<any[]>([])
  const replies = ref<any[]>([])
  const avatarInput = ref<HTMLInputElement | null>(null)
  const radarStats = ref<any>(null)
  const learningSuggestions = ref<string[]>([])

  // AI分析相关
  const aiReport = ref<any>(null)
  const generatingReport = ref(false)

  // 分页相关
  const learningRecordsPage = ref(1)
  const learningRecordsPerPage = ref(6) // 减少每页显示数量
  const activityPage = ref(1)
  const activityPerPage = ref(8)

const recommendationTabs = [
  { id: 'algorithms', name: 'Recommended Algorithms' },
  { id: 'posts', name: 'Recommended Posts' }
]

let radarChart: any = null

const totalProgress = computed(() => {
  if (userKnowledge.value.length === 0) return 0
  const total = userKnowledge.value.reduce((sum, record) => sum + record.progress, 0)
  return Math.round(total / userKnowledge.value.length)
})

// 分页计算属性
const paginatedLearningRecords = computed(() => {
  const filtered = filteredRecords.value

  const start = (learningRecordsPage.value - 1) * learningRecordsPerPage.value
  const end = start + learningRecordsPerPage.value
  return filtered.slice(start, end)
})

const totalLearningRecordPages = computed(() => {
  return Math.ceil(filteredRecords.value.length / learningRecordsPerPage.value)
})

const currentActivityItems = computed(() => {
  let items = []
  switch (activeSection.value) {
    case 'favorites':
      items = favorites.value
      break
    case 'likes':
      items = likes.value
      break
    case 'replies':
      items = replies.value
      break
    case 'posts':
      items = userPosts.value
      break
    default:
      items = []
  }

  const start = (activityPage.value - 1) * activityPerPage.value
  const end = start + activityPerPage.value
  return items.slice(start, end)
})

const totalActivityPages = computed(() => {
  let totalItems = 0
  switch (activeSection.value) {
    case 'favorites':
      totalItems = favorites.value.length
      break
    case 'likes':
      totalItems = likes.value.length
      break
    case 'replies':
      totalItems = replies.value.length
      break
    case 'posts':
      totalItems = userPosts.value.length
      break
  }
  return Math.ceil(totalItems / activityPerPage.value)
})

// 应用筛选
const applyFilters = () => {
  // 筛选逻辑会在filteredRecords中处理
  // 重置页码到第一页
  learningRecordsPage.value = 1
}

const filteredRecords = computed(() => {
  let records = [
    ...userKnowledge.value.map(record => ({ ...record, type: 'algorithm', icon: 'fas fa-brain', color: '#6b46c1' })),
    ...likedPosts.value.map(post => ({ ...post, type: 'post', icon: 'fas fa-heart', color: '#b91c1c' })),
    ...favoritePosts.value.map(post => ({ ...post, type: 'post', icon: 'fas fa-bookmark', color: '#f59e0b' })),
    ...commentedPosts.value.map(post => ({ ...post, type: 'post', icon: 'fas fa-comment', color: '#10b981' }))
  ]

  // 类型筛选
  if (typeFilter.value !== 'all') {
    records = records.filter(record => record.type === typeFilter.value)
  }

  // 日期筛选
  if (dateFilter.value !== 'all') {
    const now = new Date()
    let days = 0
    switch (dateFilter.value) {
      case 'week': days = 7; break
      case 'month': days = 30; break
      case 'quarter': days = 90; break
      case 'year': days = 365; break
    }
    const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
    records = records.filter(record => {
      const recordDate = new Date(record.last_accessed || record.created_at)
      return recordDate >= cutoffDate
    })
  }

  // 排序
  records.sort((a, b) => {
    switch (sortBy.value) {
      case 'last_accessed':
        const dateA = new Date(a.last_accessed || a.created_at)
        const dateB = new Date(b.last_accessed || b.created_at)
        return dateB - dateA
      case 'progress':
        return (b.progress || 0) - (a.progress || 0)
      case 'name':
        const nameA = a.type === 'algorithm' ? getAlgorithmName(a.algorithm_id) : a.title
        const nameB = b.type === 'algorithm' ? getAlgorithmName(b.algorithm_id) : b.title
        return (nameA || '').localeCompare(nameB || '')
      default:
        return 0
    }
  })

  return records
})

const getRoleText = (role: string) => {
  const roles = {
    user: 'User',
    admin: 'Admin'
  }
  return roles[role] || role
}

// 删除帖子
const confirmDeletePost = async (post: any) => {
  if (!userStore.isLoggedIn || userStore.user?.id !== post.author?.id) {
    alert('You do not have permission to delete this post')
    return
  }

  const confirmed = confirm(`Are you sure you want to delete "${post.title}"? This action cannot be undone.`)
  if (!confirmed) return

  try {
    await axios.delete(`/api/posts/${post.id}`)
    // 从列表中移除帖子
    const index = userPosts.value.findIndex(p => p.id === post.id)
    if (index > -1) {
      userPosts.value.splice(index, 1)
    }
    alert('Post deleted successfully')
  } catch (error: any) {
    console.error('Failed to delete post:', error)
    alert(error.response?.data?.message || 'Failed to delete post')
  }
}

const getDifficultyText = (difficulty: string) => {
  const texts = {
    beginner: 'Beginner',
    intermediate: 'Intermediate',
    advanced: 'Advanced'
  }
  return texts[difficulty] || difficulty
}

const getAlgorithmName = (algorithmId: number) => {
  const algorithm = algorithms.value.find((alg: any) => alg.id === algorithmId)
  return algorithm ? (algorithm.chinese_name || algorithm.name) : 'Unknown Algorithm'
}

const getAlgorithmCategory = (algorithmId: number) => {
  const algorithm = algorithms.value.find((alg: any) => alg.id === algorithmId)
  return algorithm?.category?.name || 'Unknown Category'
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US')
}

const visiblePages = (totalPages: number, currentPage: number) => {
  const pages = []
  const start = Math.max(1, currentPage - 1)
  const end = Math.min(totalPages, start + 2)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
}

const sortRecords = () => {
  // 触发computed重新计算
}

const filterRecords = () => {
  // 触发computed重新计算
}

const fetchUserData = async () => {
  try {
    // 获取算法数据（用于显示名称和分类）
    const algorithmsRes = await axios.get('/api/algorithms?per_page=200')
    algorithms.value = algorithmsRes.data.algorithms

    // 获取用户的所有交互记录
    try {
      const summaryRes = await axios.get('/api/user/summary')
      console.log('Raw API response:', JSON.stringify(summaryRes.data))
      favorites.value = summaryRes.data.favorites || []
      favoritePosts.value = summaryRes.data.favorites || []
      likes.value = summaryRes.data.likes || []
      likedPosts.value = summaryRes.data.likes || []
      replies.value = summaryRes.data.replies || []
      commentedPosts.value = summaryRes.data.comments || []
      console.log('User summary loaded:', favorites.value.length, 'favorites,', likes.value.length, 'likes,', commentedPosts.value.length, 'comments')
      console.log('Favorites data length:', favorites.value?.length || 0)
      console.log('API response favorites:', summaryRes.data.favorites?.length || 0)
      console.log('First favorite item:', summaryRes.data.favorites?.[0])
    } catch (error) {
      console.error('Failed to load user summary:', error)
      // 出错时设置为空数组
      favoritePosts.value = []
      likedPosts.value = []
      commentedPosts.value = []
    }

    // 额外加载用户知识记录，确保雷达图有数据来源
    try {
      const knowledgeRes = await axios.get('/api/user/knowledge')
      // 接口返回 { knowledge: [...] }
      if (knowledgeRes && knowledgeRes.data && Array.isArray(knowledgeRes.data.knowledge)) {
        userKnowledge.value = knowledgeRes.data.knowledge
        // 同步到 store（如果需要）
        if (userStore && typeof userStore.knowledge !== 'undefined') {
          userStore.knowledge = knowledgeRes.data.knowledge
        }
        console.log('User knowledge loaded:', userKnowledge.value.length, 'records')
      }
    } catch (err) {
      console.warn('Failed to load user knowledge for radar:', err)
      // 不阻塞，保留现有 userKnowledge 值（可能来自 store 的 watch）
    }

    // 获取用户发布的帖子
    if (userStore.isLoggedIn && userStore.user?.id) {
      try {
        const userPostsRes = await axios.get(`/api/posts?author_id=${userStore.user.id}&per_page=100`)
        userPosts.value = userPostsRes.data.posts || []
        console.log('User posts loaded:', userPosts.value.length, 'posts')
      } catch (error) {
        console.error('Failed to load user posts:', error)
        userPosts.value = []
      }
    }

    // 获取推荐内容
    try {
      const recommendationsRes = await axios.get('/api/recommendations')
      recommendedAlgorithms.value = recommendationsRes.data.algorithms || []
      recommendedPosts.value = recommendationsRes.data.posts || []
      console.log('Recommendations loaded:', recommendedAlgorithms.value.length, 'algorithms,', recommendedPosts.value.length, 'posts')
    } catch (error) {
      console.error('Failed to load recommendations:', error)
      // 出错时显示默认推荐
      recommendedAlgorithms.value = algorithms.value.slice(0, 5) || []
      recommendedPosts.value = []
    }

  } catch (error) {
    console.error('Failed to fetch user data:', error)
  }
}

const loadFavorites = () => {
  activeSection.value = 'favorites'
  activityPage.value = 1 // 重置分页
  // 数据已经在 fetchUserData 中设置到 favorites 变量中
}

const loadLikes = () => {
  activeSection.value = 'likes'
  activityPage.value = 1 // 重置分页
  // 数据已经在 fetchUserData 中获取
}

const loadReplies = () => {
  activeSection.value = 'replies'
  activityPage.value = 1 // 重置分页
  // 数据已经在 fetchUserData 中获取
}

const loadUserPosts = () => {
  activeSection.value = 'posts'
  activityPage.value = 1 // 重置分页
  // 数据已经在 fetchUserData 中获取
}


const onAvatarSelected = async (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return
  const file = input.files[0]
  const fd = new FormData()
  fd.append('avatar', file)
  try {
    if (!userStore.isLoggedIn) {
      alert('Please sign in to upload avatar')
      return
    }
    // Try POST (some browsers/devtools handle FormData + POST more reliably than PUT)
    let res
    try {
      res = await axios.post('/api/auth/avatar', fd)
    } catch (e) {
      console.log('POST failed, trying PUT...')
      // fallback to PUT if POST fails
      res = await axios.put('/api/auth/avatar', fd)
    }
    // update store user avatar
    if (res.data.user) {
      userStore.user = res.data.user
    }
    alert('Avatar uploaded successfully!')
  } catch (err: any) {
    console.error('Upload avatar failed', err, err?.response?.data)
    const errorMessage = err?.response?.data?.message || err?.response?.data?.detail || err.message || 'Unknown error'
    alert('Failed to upload avatar: ' + errorMessage)
  } finally {
    // clear input
    if (avatarInput.value) avatarInput.value.value = ''
  }
}

const initRadarChart = async () => {
  const radarElement = document.getElementById('knowledge-radar')
  if (!radarElement) {
    console.warn('Radar chart element not found')
    return
  }

  try {
    // 如果用户没有登录或没有学习记录，显示默认图表
    if (!userStore.isLoggedIn || !userKnowledge.value || userKnowledge.value.length === 0) {
      // 销毁之前的图表实例
      if (radarChart) {
        radarChart.dispose()
      }

      radarChart = echarts.init(radarElement)
      const option = {
        radar: {
          indicator: [
            { name: '算法学习', max: 100 },
            { name: '实践应用', max: 100 },
            { name: '理论理解', max: 100 },
            { name: '社区参与', max: 100 },
            { name: '学习进度', max: 100 }
          ],
          shape: 'circle',
          splitNumber: 4,
          axisName: {
            color: '#9ca3af',
            fontSize: 12
          }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [0, 0, 0, 0, 0],
            name: '知识掌握',
            areaStyle: {
              color: 'rgba(156, 163, 175, 0.1)'
            },
            lineStyle: {
              color: '#9ca3af',
              width: 1
            },
            itemStyle: {
              color: '#9ca3af'
            }
          }]
        }]
      }
      radarChart.setOption(option)

      // 设置默认统计和建议
      radarStats.value = {
        totalKnowledge: 0,
        totalActivities: 0,
        avgProgress: 0,
        recentActivity: 0
      }
      learningSuggestions.value = ['开始你的机器学习学习之旅吧！', '浏览算法知识图谱了解学习路径', '参与社区讨论，加深理解']

      return
    }

    // 获取用户的完整活动数据来计算知识掌握情况
    let userData = {
      knowledge: userKnowledge.value,
      favorites: [],
      likes: [],
      comments: []
    }

    try {
      const summaryRes = await axios.get('/api/user/summary')
      userData = {
        knowledge: userKnowledge.value,
        favorites: summaryRes.data.favorites || [],
        likes: summaryRes.data.likes || [],
        comments: summaryRes.data.comments || []
      }
    } catch (summaryError) {
      console.warn('Failed to fetch user summary for radar:', summaryError)
      // 继续使用默认数据
    }

    // 销毁之前的图表实例
    if (radarChart) {
      radarChart.dispose()
    }

    radarChart = echarts.init(radarElement)

    // 计算各个维度的知识掌握情况
    const result = calculateKnowledgeDimensions(userData)
    const knowledgeDimensions = result.scores

    // 更新响应式数据
    radarStats.value = result.stats
    learningSuggestions.value = result.suggestions

    // If the computed scores are all very small but >0, scale them up slightly
    let plottedValues = knowledgeDimensions.slice()
    const maxScore = Math.max(...plottedValues)
    if (maxScore > 0 && maxScore < 25) {
      const factor = 25 / maxScore
      plottedValues = plottedValues.map(v => Math.min(Math.round(v * factor), 100))
      console.log('Radar values scaled for visibility, factor=', factor, 'original=', knowledgeDimensions, 'scaled=', plottedValues)
    }

    const option = {
      radar: {
        indicator: [
          { name: '算法学习', max: 100 },
          { name: '实践应用', max: 100 },
          { name: '理论理解', max: 100 },
          { name: '社区参与', max: 100 },
          { name: '学习进度', max: 100 }
        ],
        shape: 'circle',
        splitNumber: 4,
        axisName: {
          color: '#374151',
          fontSize: 12
        },
        splitLine: {
          lineStyle: {
            color: '#e5e7eb'
          }
        },
        splitArea: {
          areaStyle: {
            color: ['rgba(107, 70, 193, 0.1)', 'rgba(251, 191, 36, 0.1)', 'rgba(239, 68, 68, 0.1)', 'transparent']
          }
        }
      },
      tooltip: {
        show: true,
        formatter: (params: any) => {
          if (params && params.data) {
            return `${params.name}: ${params.data.value.join(', ')}`
          }
          return ''
        }
      },
      series: [{
        type: 'radar',
        data: [{
          value: plottedValues,
          name: '知识掌握',
          areaStyle: {
            color: 'rgba(107, 70, 193, 0.35)'
          },
          lineStyle: {
            color: '#6b46c1',
            width: 2
          },
          itemStyle: {
            color: '#6b46c1'
          },
          symbol: 'circle',
          symbolSize: 6
        }]
      }]
    }

    radarChart.setOption(option, true) // 第二个参数表示不合并，完全替换配置
    console.log('Radar chart initialized successfully with data:', knowledgeDimensions)

  } catch (error) {
    console.error('Failed to initialize radar chart:', error)
    // 即使出错也要显示一个基本的图表
    try {
      if (!radarChart) {
        radarChart = echarts.init(radarElement)
      }
      const fallbackOption = {
        radar: {
          indicator: [
            { name: '算法学习', max: 100 },
            { name: '实践应用', max: 100 },
            { name: '理论理解', max: 100 },
            { name: '社区参与', max: 100 },
            { name: '学习进度', max: 100 }
          ],
          shape: 'circle'
        },
        series: [{
          type: 'radar',
          data: [{
            value: [10, 10, 10, 10, 10],
            name: '基础水平'
          }]
        }]
      }
      radarChart.setOption(fallbackOption)
    } catch (fallbackError) {
      console.error('Fallback radar chart also failed:', fallbackError)
    }
  }
}

const calculateKnowledgeDimensions = (userData) => {
  const { knowledge, favorites, likes, comments } = userData
  // 1. 算法学习维度：基础进度（40%）+ 最高掌握度（30%）+ 最近活跃度（20%）+ 学习数量（10%）
  let algorithmLearning = 0
  let learningSuggestions = []
  let recentActivities = []

  if (Array.isArray(knowledge) && knowledge.length > 0) {
    // 使用副本避免原数组被排序/变更
    const knowledgeCopy = knowledge.slice()

    // 基础进度（40%权重）
    const avgProgress = knowledgeCopy.reduce((sum, k) => sum + (k.progress || 0), 0) / knowledgeCopy.length
    const progressScore = avgProgress * 0.4

    // 最高掌握度（30%权重）
    const maxProgress = Math.max(...knowledgeCopy.map(k => (k.progress || 0)))
    const masteryScore = (maxProgress / 100) * 30

    // 最近活跃度（20%权重）
    recentActivities = knowledgeCopy.filter(k => {
      if (!k.last_accessed) return false
      const daysSinceAccess = (new Date() - new Date(k.last_accessed)) / (1000 * 60 * 60 * 24)
      return daysSinceAccess <= 30
    })
    const recencyScore = (recentActivities.length / knowledgeCopy.length) * 20

    // 学习数量（10%权重）
    const quantityScore = Math.min(knowledgeCopy.length / 8, 1) * 10

    algorithmLearning = progressScore + masteryScore + recencyScore + quantityScore

    // 生成学习建议
    if (avgProgress < 40) learningSuggestions.push("建议加强基础算法学习")
    if (maxProgress < 80) learningSuggestions.push("尝试深入掌握一些高级算法")
    if (recentActivities.length < knowledgeCopy.length * 0.5) learningSuggestions.push("保持学习频率，避免中断")
  } else {
    learningSuggestions.push("开始你的机器学习学习之旅吧！")
  }

  // 2. 实践应用维度：基于点赞和收藏的帖子数量和质量
  let practicalApplication = 0
  let practiceSuggestions = []
  const interactedPosts = [...favorites, ...likes]

  if (interactedPosts.length > 0) {
    const totalLikes = interactedPosts.reduce((sum, p) => sum + (p.like_count || 0), 0)
    const avgQuality = totalLikes / interactedPosts.length
    // 更稳定的归一化：帖子数量和质量共同决定，确保输出范围 0-100
    const countScore = Math.min(interactedPosts.length / 5, 1) * 60
    const qualityScore = Math.min(avgQuality / 20, 1) * 40
    practicalApplication = Math.min(Math.round(countScore + qualityScore), 100)

    if (interactedPosts.length < 3) practiceSuggestions.push("多参与社区讨论，学习他人经验")
    if (avgQuality < 20) practiceSuggestions.push("关注高质量内容，提升学习效果")
  } else {
    practiceSuggestions.push("积极参与社区，与其他学习者交流")
  }

  // 3. 理论理解维度：基于评论数量和学习进度
  let theoreticalUnderstanding = 0
  let theorySuggestions = []

  if (comments.length > 0 || knowledge.length > 0) {
    const commentScore = Math.min((comments.length / 3) * 50, 50)
    const progressScore = Array.isArray(knowledge) && knowledge.length > 0 ?
      (knowledge.reduce((sum, k) => sum + (k.progress || 0), 0) / knowledge.length) * 0.5 : 0

    theoreticalUnderstanding = Math.min(Math.round(commentScore + progressScore), 100)

    if (comments.length < 2) theorySuggestions.push("多发表见解，加深理论理解")
    if (progressScore < 30) theorySuggestions.push("注重理论学习，打好基础")
  } else {
    theorySuggestions.push("理论与实践相结合，效果更佳")
  }

  // 4. 社区参与维度：基于所有社区活动的综合评分
  let communityEngagement = 0
  let communitySuggestions = []
  const totalActivities = favorites.length + likes.length + comments.length

  if (totalActivities > 0) {
    const activityScore = Math.min(totalActivities / 5 * 40, 40)
    const qualityScore = Math.min(
      (favorites.length * 1.5 + likes.length * 1.0 + comments.length * 1.2) / 10 * 60,
      60
    )
    communityEngagement = activityScore + qualityScore
    if (totalActivities < 5) communitySuggestions.push("积极参与社区互动")
    if (favorites.length < likes.length) communitySuggestions.push("收藏优质内容，便于复习")
  } else {
    communitySuggestions.push("加入学习社区，共同进步")
  }

  // 5. 学习进度维度：时间趋势指标 + 学习一致性指标
  let learningProgress = 0
  let progressSuggestions = []

  if (knowledge.length > 0) {
    // 时间趋势指标（学习是否在进步）
    const sortedKnowledgeForTrend = (knowledge || []).slice().sort((a, b) =>
      new Date(a.last_accessed) - new Date(b.last_accessed)
    )
    const recentSlice = sortedKnowledgeForTrend.slice(-3)
    const olderSlice = sortedKnowledgeForTrend.slice(0, 3)
    const recentProgress = recentSlice.length > 0 ? recentSlice.reduce((sum, k) => sum + (k.progress || 0), 0) / recentSlice.length : 0
    const olderProgress = olderSlice.length > 0 ? olderSlice.reduce((sum, k) => sum + (k.progress || 0), 0) / olderSlice.length : 0
    const trendScore = Math.max(0, Math.min(((recentProgress - olderProgress) / 20) * 40 + 40, 80))

    // 学习一致性指标
    const consistencyScore = Math.min(knowledge.length / 6 * 20, 20)

    learningProgress = trendScore + consistencyScore
    if (trendScore < 40) progressSuggestions.push("保持学习进度，避免停滞")
    if (consistencyScore < 10) progressSuggestions.push("制定学习计划，保持一致性")
  } else {
    progressSuggestions.push("制定学习计划，开始系统学习")
  }

  // 生成综合建议
  const allSuggestions = [
    ...learningSuggestions,
    ...practiceSuggestions,
    ...theorySuggestions,
    ...communitySuggestions,
    ...progressSuggestions
  ]

  return {
    scores: [
      Math.round(algorithmLearning),
      Math.round(practicalApplication),
      Math.round(theoreticalUnderstanding),
      Math.round(communityEngagement),
      Math.round(learningProgress)
    ],
    suggestions: allSuggestions.slice(0, 5), // 最多5条建议
    stats: {
      totalKnowledge: knowledge.length,
      totalActivities: totalActivities,
      avgProgress: knowledge.length > 0 ?
        Math.round(knowledge.reduce((sum, k) => sum + k.progress, 0) / knowledge.length) : 0,
      recentActivity: recentActivities ? recentActivities.length : 0
    }
  }
}

// AI分析相关函数
const generateLearningReport = async () => {
  if (!userStore.isLoggedIn) {
    alert('请先登录')
    return
  }

  generatingReport.value = true
  try {
    const response = await axios.post('/api/ai/generate-learning-report')
    if (response.data.success) {
      aiReport.value = response.data
      console.log('AI学习报告生成成功:', response.data)
    } else {
      alert('生成报告失败: ' + response.data.message)
    }
  } catch (error: any) {
    console.error('生成学习报告失败:', error)
    alert('生成报告失败，请稍后重试: ' + (error.response?.data?.message || error.message))
  } finally {
    generatingReport.value = false
  }
}

const formatReportTime = (timeStr: string) => {
  const date = new Date(timeStr + (timeStr.includes('T') ? '' : 'T00:00:00'))
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatReportContent = (content: string) => {
  // 将markdown风格的文本转换为HTML
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // **text** -> <strong>text</strong>
    .replace(/^### (.*$)/gim, '<h4>$1</h4>')           // ### title -> <h4>title</h4>
    .replace(/^## (.*$)/gim, '<h3>$1</h3>')            // ## title -> <h3>title</h3>
    .replace(/^# (.*$)/gim, '<h2>$1</h2>')             // # title -> <h2>title</h2>
    .replace(/^(\d+)\.\s+(.*$)/gim, '<div class="step-item"><span class="step-number">$1.</span> $2</div>')  // 1. text -> 带编号的步骤
    .replace(/\n\n/g, '</p><p>')                       // 双换行 -> 段落分隔
    .replace(/\n/g, '<br>')                            // 单换行 -> 换行
    .replace(/^/, '<p>')                               // 开头加<p>
    .replace(/$/, '</p>')                              // 结尾加</p>
}

watch(() => userStore.knowledge, (newKnowledge) => {
  userKnowledge.value = newKnowledge
  setTimeout(initRadarChart, 100) // 延迟确保DOM更新
}, { immediate: true })

onMounted(() => {
  fetchUserData()
})
</script>

<style scoped>
.profile-page {
  padding: 2rem 0;
  background: var(--brand-bg);
  min-height: 100vh;
}

.profile-header {
  background: var(--light-panel);
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-soft);
  color: var(--text-dark);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.avatar {
  font-size: 4rem;
  color: #6b46c1;
}

.user-details h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
  color: var(--text-dark);
}

.user-role {
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.user-stats {
  display: flex;
  gap: 2rem;
}

.stat {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #6b46c1;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.profile-actions {
  display: flex;
  gap: 1rem;
}

.radar-section {
  background: var(--light-panel);
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-soft);
}

.radar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.radar-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-dark);
  margin: 0;
}

.radar-stats {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.stat-label {
  color: var(--text-muted);
}

.stat-value {
  font-weight: 600;
  color: #6b46c1;
}

.learning-suggestions {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.learning-suggestions h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-dark);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-item {
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  border-left: 4px solid #6b46c1;
  color: var(--text-dark);
  font-size: 0.875rem;
  line-height: 1.5;
}

.suggestion-item:last-child {
  margin-bottom: 0;
}

.radar-container {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.radar-chart {
  width: 400px;
  height: 400px;
}

.radar-side {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 280px;
}

.radar-side .learning-suggestions {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

.radar-body {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
  justify-content: space-between;
}

.radar-suggestions {
  width: 320px;
}

.learning-suggestions.no-top-border {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

.radar-legend {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.learning-records {
  background: var(--brand-panel);
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-soft);
}

.learning-records h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #1f2937;
}

.records-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  background: var(--brand-panel);
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: var(--shadow-soft);
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 150px;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-dark);
}

.records-filters select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
  color: var(--text-dark);
}

.records-list {
  display: grid;
  gap: 1rem;
}

.record-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.record-card:hover {
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  border-color: #6b46c1;
}

.record-info {
  flex: 1;
}

.record-info h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.record-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.record-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 150px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6b46c1, #8b5cf6);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  min-width: 40px;
}

.record-interests {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  min-width: 200px;
}

.interest-tag {
  background: #e5e7eb;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
}

.user-activity {
  background: var(--brand-panel);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-soft);
}

.user-activity h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1f2937;
}

.activity-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.activity-content {
  min-height: 200px;
}

.activity-list {
  display: grid;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.activity-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  transition: all 0.2s;
  background: white;
  cursor: pointer;
  position: relative;
}

.post-actions-top {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  z-index: 10;
}

.activity-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border-color: #6b46c1;
}

.activity-card h4 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.activity-card p {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.activity-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #4b5563;
}

.no-posts {
  text-align: center;
  padding: 2rem;
  color: #9ca3af;
}

.no-posts p {
  margin: 0;
  font-size: 0.875rem;
}

.activity-pagination {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.record-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--brand-bg);
  margin-right: 1rem;
  flex-shrink: 0;
}

.record-icon i {
  font-size: 1.125rem;
  color: #6b46c1;
}

.record-type {
  background: #e5e7eb;
  color: #374151;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.record-stats {
  display: flex;
  gap: 1rem;
  align-items: center;
  min-width: 150px;
}

.record-stats .stat {
  font-size: 0.75rem;
  color: #6b7280;
}

.record-stats .stat i {
  color: #000000;
}

.recommendations {
  background: var(--brand-panel);
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: var(--shadow-soft);
}

.recommendations h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #1f2937;
}

.recommendations-tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
}

.tab {
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  font-weight: 500;
}

.tab.active {
  border-bottom-color: #6b46c1;
  color: #6b46c1;
}

.recommendations-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  max-width: 100%;
}

.algorithm-card,
.post-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.algorithm-card:hover,
.post-card:hover {
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  border-color: #6b46c1;
}

.algorithm-card h4,
.post-card h4 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.algorithm-card p,
.post-card p {
  color: #374151;
  margin-bottom: 1rem;
  line-height: 1.6;
}

.algorithm-meta,
.post-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #4b5563;
}

.difficulty {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.difficulty.beginner {
  background: #dbeafe;
  color: #1e40af;
}

.difficulty.intermediate {
  background: #fef3c7;
  color: #92400e;
}

.difficulty.advanced {
  background: #dc2626;
  color: #ffffff;
}

.recommended-card {
  position: relative;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.card-header h4 {
  flex: 1;
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.recommendation-score {
  margin-left: 1rem;
}

.score-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.recommendation-reasons {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e5e7eb;
}

.reasons-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.reason-tag {
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 500;
  border: 1px solid #bae6fd;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.page-btn {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  color: #374151;
}

.page-btn:hover:not(:disabled) {
  background: #6b46c1;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-number {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.2s;
  color: #374151;
}

.page-number:hover,
.page-number.active {
  background: #6b46c1;
  color: white;
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
    margin-top: calc(var(--nav-height) + 1rem); /* 避免导航栏遮挡 */
  }

  .user-stats {
    justify-content: center;
  }

  .radar-container {
    flex-direction: column;
    gap: 1rem;
  }

  .radar-chart {
    width: 100%;
    height: 300px;
  }

  .record-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .record-interests {
    min-width: auto;
  }

  .recommendations-content {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

/* AI分析区域样式 */
.ai-analysis {
  background: var(--brand-panel);
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-soft);
  color: var(--text-dark);
}

.ai-analysis h2 {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-dark);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ai-analysis > p {
  color: var(--text-muted);
  margin-bottom: 2rem;
  font-size: 1rem;
}

.analysis-controls {
  margin-bottom: 2rem;
}

.generate-report-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 0.875rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
}

.generate-report-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.generate-report-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.report-content {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.report-header {
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
  margin-bottom: 1.5rem;
}

.report-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.report-header small {
  color: #6b7280;
  font-size: 0.875rem;
}

.report-body {
  line-height: 1.7;
}

.report-text {
  color: #374151;
  font-size: 1rem;
}

.report-text h2,
.report-text h3,
.report-text h4 {
  color: #1f2937;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.report-text h2 {
  font-size: 1.25rem;
}

.report-text h3 {
  font-size: 1.125rem;
}

.report-text h4 {
  font-size: 1rem;
}

.report-text p {
  margin-bottom: 1rem;
  color: #4b5563;
}

.report-text .step-item {
  margin-bottom: 0.5rem;
  padding-left: 1rem;
  position: relative;
}

.report-text .step-number {
  font-weight: 600;
  color: #667eea;
  margin-right: 0.5rem;
}

.no-report {
  text-align: center;
  padding: 3rem 2rem;
  color: #6b7280;
}

.no-report-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
  color: #d1d5db;
}

.no-report h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #374151;
}

.loading-report {
  text-align: center;
  padding: 3rem 2rem;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-report h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #374151;
}

.loading-report p {
  color: #6b7280;
}

@media (max-width: 768px) {
  .ai-analysis {
    padding: 1.5rem;
  }

  .ai-analysis h2 {
    font-size: 1.5rem;
  }

  .generate-report-btn {
    padding: 0.75rem 1.25rem;
    font-size: 0.9rem;
  }

  .report-content {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .recommendations-content {
    grid-template-columns: 1fr;
  }
}
</style>
