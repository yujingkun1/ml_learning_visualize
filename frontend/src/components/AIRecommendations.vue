<template>
  <div class="ai-recommendations">
    <div class="recommendations-header">
      <h3>🎯 AI-Powered Recommendations</h3>
      <p>Discover content tailored to your learning journey</p>
    </div>

    <!-- 推荐内容标签页 -->
    <div class="recommendations-tabs">
      <button
        v-for="tab in recommendationTabs"
        :key="tab.id"
        class="tab"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <i :class="tab.icon"></i>
        {{ tab.name }}
        <span v-if="getTabCount(tab.id) > 0" class="tab-count">{{ getTabCount(tab.id) }}</span>
      </button>
    </div>

    <!-- 推荐内容 -->
    <div class="recommendations-content">
      <!-- 推荐算法 -->
      <div v-if="activeTab === 'algorithms' && recommendedAlgorithms.length > 0" class="algorithms-grid">
        <div
          v-for="algorithm in recommendedAlgorithms"
          :key="algorithm.id"
          class="algorithm-card recommended-card"
          @click="$router.push(`/algorithms/${algorithm.id}`)"
        >
          <div class="card-header">
            <h4>{{ algorithm.chinese_name || algorithm.name }}</h4>
          </div>
          <p>{{ algorithm.description?.substring(0, 80) }}...</p>
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

      <!-- 推荐帖子 -->
      <div v-if="activeTab === 'posts' && recommendedPosts.length > 0" class="posts-grid">
        <div
          v-for="post in recommendedPosts"
          :key="post.id"
          class="post-card recommended-card"
          @click="$router.push(`/posts/${post.id}`)"
        >
          <div class="card-header">
            <h4>{{ post.title }}</h4>
          </div>
          <p>{{ post.content?.substring(0, 100) }}...</p>
          <div class="post-meta">
            <span class="author">{{ post.author?.username || 'Anonymous' }}</span>
            <span class="stats">
              <i class="fas fa-heart"></i> {{ post.like_count || 0 }}
              <i class="fas fa-comment"></i> {{ post.comment_count || 0 }}
            </span>
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

      <!-- 空状态 -->
      <div v-if="(activeTab === 'algorithms' && recommendedAlgorithms.length === 0) || (activeTab === 'posts' && recommendedPosts.length === 0)" class="no-recommendations">
        <i class="fas fa-search fa-2x"></i>
        <h4>No recommendations yet</h4>
        <p>Complete more learning activities to get personalized recommendations</p>
      </div>

      <!-- 刷新按钮 -->
      <div class="refresh-section">
        <button class="btn btn-outline" @click="refreshRecommendations" :disabled="loading">
          <i class="fas fa-refresh"></i>
          {{ loading ? 'Refreshing...' : 'Refresh Recommendations' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 推荐数据
const recommendedAlgorithms = ref([])
const recommendedPosts = ref([])
const loading = ref(false)

// 标签页
const activeTab = ref('posts')
const recommendationTabs = [
  { id: 'posts', name: 'Recommended Posts', icon: 'fas fa-file-alt' },
  { id: 'algorithms', name: 'Recommended Algorithms', icon: 'fas fa-brain' }
]

// 获取标签页计数
const getTabCount = (tabId: string) => {
  if (tabId === 'posts') return recommendedPosts.value.length
  if (tabId === 'algorithms') return recommendedAlgorithms.value.length
  return 0
}

// 获取难度文本
const getDifficultyText = (difficulty: string) => {
  const texts: { [key: string]: string } = {
    'beginner': 'Beginner',
    'intermediate': 'Intermediate',
    'advanced': 'Advanced'
  }
  return texts[difficulty] || difficulty
}

// 加载推荐数据
const loadRecommendations = async () => {
  if (!userStore.isLoggedIn) return

  loading.value = true
  try {
    const response = await axios.get('/api/recommendations')
    recommendedAlgorithms.value = response.data.algorithms || []
    recommendedPosts.value = response.data.posts || []
  } catch (error) {
    console.error('Failed to load recommendations:', error)
    recommendedAlgorithms.value = []
    recommendedPosts.value = []
  } finally {
    loading.value = false
  }
}

// 刷新推荐
const refreshRecommendations = () => {
  loadRecommendations()
}

// 初始化
onMounted(() => {
  loadRecommendations()
})

// 暴露方法供父组件调用
defineExpose({
  loadRecommendations,
  refreshRecommendations
})
</script>

<style scoped>
.ai-recommendations {
  background: var(--brand-panel);
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: var(--shadow-soft);
}

.recommendations-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-dark);
}

.recommendations-header p {
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

.recommendations-tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
  gap: 0.5rem;
}

.tab {
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab:hover {
  color: var(--text-dark);
}

.tab.active {
  border-bottom-color: #1e40af;
  color: #1e40af;
  font-weight: 600;
}

.tab-count {
  background: #e5e7eb;
  color: #6b7280;
  padding: 0.125rem 0.375rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 1.25rem;
  text-align: center;
}

.tab.active .tab-count {
  background: #dbeafe;
  color: #1e40af;
}

.recommendations-content {
  min-height: 300px;
}

.algorithms-grid,
.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.algorithm-card,
.post-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-dark);
}

.algorithm-card:hover,
.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #1e40af;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-dark);
  margin: 0;
  flex: 1;
}

.algorithm-card p,
.post-card p {
  color: var(--text-muted);
  margin-bottom: 1rem;
  line-height: 1.5;
}

.algorithm-meta,
.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.875rem;
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

.category {
  color: #6b7280;
  font-weight: 500;
}

.post-meta .author {
  color: #6b7280;
}

.post-meta .stats {
  color: #9ca3af;
  display: flex;
  align-items: center;
  gap: 0.75rem;
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
  white-space: nowrap;
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
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.no-recommendations {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
}

.no-recommendations i {
  color: #9ca3af;
  margin-bottom: 1rem;
  display: block;
}

.no-recommendations h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-dark);
}

.refresh-section {
  text-align: center;
  margin-top: 2rem;
}

.refresh-section .btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-recommendations {
    padding: 1rem;
  }

  .recommendations-tabs {
    flex-wrap: wrap;
  }

  .tab {
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
  }

  .algorithms-grid,
  .posts-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .algorithm-card,
  .post-card {
    padding: 1rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .recommendation-score {
    margin-left: 0;
    align-self: flex-end;
  }
}
</style>
