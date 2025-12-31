<template>
  <div class="algorithm-page">
    <div class="container">
      <!-- 头部信息 -->
      <div class="algorithm-header">
        <div class="header-navigation">
          <button class="back-button" @click="router.push('/algorithms')">
            <i class="fas fa-arrow-left"></i> Back to Algorithms
          </button>
        </div>
        <h1>{{ algorithm?.name || 'Loading...' }}</h1>
        <p class="algorithm-description">{{ algorithm?.description || 'Loading algorithm description...' }}</p>

        <!-- Learning Progress Display -->
        <div v-if="userStore.isLoggedIn && userKnowledge && userKnowledge.progress !== undefined" class="progress-section">
          <div class="progress-info">
            <span class="progress-label">Learning Progress:</span>
            <span class="progress-value">{{ userKnowledge.progress }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: userKnowledge.progress + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- 标签页 -->
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab"
          :class="{ active: activeTab === tab.id }"
          @click="switchTab(tab.id)"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- 标签页内容 -->
      <div class="tab-content">
        <!-- Theory -->
        <div v-if="activeTab === 'theory'" class="theory-content">
          <h3>Theory</h3>
          <div v-if="algorithm && finalNotebookSrc" class="notebook-content">
            <iframe
              :src="finalNotebookSrc"
              width="100%"
              height="800"
              frameborder="0"
              allowfullscreen>
            </iframe>
          </div>
          <div v-else>
            <p>Loading notebook...</p>
          </div>
        </div>

        <!-- Interactive Demo -->
        <div v-if="activeTab === 'interactive'" class="interactive-content">
          <h3>Interactive Demo</h3>
          <div v-if="algorithm && finalInteractiveSrc" class="interactive-demo">
            <iframe
              :src="finalInteractiveSrc"
              width="100%"
              height="800"
              frameborder="0"
              allowfullscreen>
            </iframe>
          </div>
          <div v-else>
            <p>No interactive demo available for this algorithm.</p>
          </div>
        </div>

        <!-- Resources -->
        <div v-if="activeTab === 'resources'" class="resources-content">
          <h3>Learning Resources</h3>
          <div v-if="algorithm">
            <!-- Academic Papers -->
            <div class="resource-section">
              <h4>📄 Academic Papers</h4>
              <div v-for="paper in algorithmResources.papers" :key="paper.title" class="resource-item paper-item">
                <div class="resource-header">
                  <h5>{{ paper.title }}</h5>
                  <span class="resource-year">{{ paper.year }}</span>
                </div>
                <p class="resource-authors">{{ paper.authors }}</p>
                <div class="resource-actions">
                  <a :href="paper.url" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline" @click="trackResourceClick('paper', paper.title)">
                    <i class="fas fa-external-link-alt"></i> Read Paper
                  </a>
                  <a v-if="paper.arxiv" :href="paper.arxiv" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline" @click="trackResourceClick('arxiv', paper.title)">
                    <i class="fab fa-arxiv"></i> arXiv
                  </a>
                </div>
              </div>
            </div>

            <!-- GitHub Repositories -->
            <div class="resource-section">
              <h4>💻 GitHub Repositories</h4>
              <div v-for="repo in algorithmResources.repositories" :key="repo.name" class="resource-item repo-item">
                <div class="resource-header">
                  <h5>{{ repo.name }}</h5>
                  <span class="resource-stars">⭐ {{ repo.stars }}</span>
                </div>
                <p class="resource-description">{{ repo.description }}</p>
                <div class="resource-actions">
                  <a :href="repo.url" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-primary" @click="trackResourceClick('github', repo.name)">
                    <i class="fab fa-github"></i> View Code
                  </a>
                  <span class="resource-language">{{ repo.language }}</span>
                </div>
              </div>
            </div>

            <!-- Online Courses & Tutorials -->
            <div class="resource-section">
              <h4>🎓 Online Courses & Tutorials</h4>
              <div v-for="course in algorithmResources.courses" :key="course.title" class="resource-item course-item">
                <div class="resource-header">
                  <h5>{{ course.title }}</h5>
                  <span class="resource-platform">{{ course.platform }}</span>
                </div>
                <p class="resource-description">{{ course.description }}</p>
                <div class="resource-actions">
                  <a :href="course.url" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-success" @click="trackResourceClick('course', course.title)">
                    <i class="fas fa-play"></i> Start Learning
                  </a>
                  <span class="resource-duration">{{ course.duration }}</span>
                </div>
              </div>
            </div>

            <!-- Related Posts from Our Community -->
            <div class="resource-section">
              <h4>🌐 Related Posts from Our Community</h4>
              <div v-if="relatedPosts.length > 0">
                <div v-for="post in relatedPosts" :key="post.id" class="resource-item post-item">
                  <div class="resource-header">
                    <h5>{{ post.title }}</h5>
                    <span class="resource-author">by {{ post.author }}</span>
                  </div>
                  <p class="resource-description">{{ post.content }}</p>
                  <div class="resource-meta">
                    <span class="meta-item"><i class="fas fa-heart"></i> {{ post.like_count }}</span>
                    <span class="meta-item"><i class="fas fa-comment"></i> {{ post.comment_count }}</span>
                    <span class="meta-item"><i class="fas fa-calendar"></i> {{ formatDate(post.created_at) }}</span>
                  </div>
                  <div class="resource-actions">
                    <router-link :to="`/posts/${post.id}`" class="btn btn-sm btn-outline" @click="trackResourceClick('post', post.title)">
                      <i class="fas fa-eye"></i> Read Post
                    </router-link>
                  </div>
                </div>

                <!-- Pagination -->
                <div v-if="postPagination.pages > 1" class="pagination">
                  <button
                    class="btn btn-sm btn-outline"
                    :disabled="postPagination.page <= 1"
                    @click="loadRelatedPosts(postPagination.page - 1)"
                  >
                    <i class="fas fa-chevron-left"></i> Previous
                  </button>
                  <span class="pagination-info">
                    Page {{ postPagination.page }} of {{ postPagination.pages }}
                  </span>
                  <button
                    class="btn btn-sm btn-outline"
                    :disabled="postPagination.page >= postPagination.pages"
                    @click="loadRelatedPosts(postPagination.page + 1)"
                  >
                    Next <i class="fas fa-chevron-right"></i>
                  </button>
                </div>
              </div>
              <div v-else class="no-resources">
                <p>Loading related posts...</p>
              </div>
            </div>
          </div>
          <div v-else>
            <p>Loading resources...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const algorithm = ref<any>(null)
const activeTab = ref('theory')
const userKnowledge = ref<any>(null)
const relatedPosts = ref<any[]>([])
const postPagination = ref({ page: 1, per_page: 5, total: 0, pages: 0 })

// 学习进度跟踪
const tabViewTime = ref<Record<string, number>>({})
const resourceClicks = ref<Record<string, number>>({})
let tabStartTime = 0

// 动态生成标签页
const tabs = computed(() => {
  const baseTabs = [
    { id: 'theory', name: 'Theory' },
    { id: 'resources', name: 'Resources' }
  ]

  // 只有有交互演示的算法才显示交互演示标签页
  if (algorithm.value && algorithm.value.has_interactive_demo) {
    baseTabs.splice(1, 0, { id: 'interactive', name: 'Interactive Demo' })
  }

  return baseTabs
})

// 算法资源配置
const algorithmResources = computed(() => {
  if (!algorithm.value) return { papers: [], repositories: [], courses: [] }

  const resources: Record<string, any> = {
    'Gradient Descent': {
      papers: [
        {
          title: 'An Overview of Gradient Descent Optimization Algorithms',
          authors: 'Sebastian Ruder',
          year: '2016',
          url: 'https://arxiv.org/abs/1609.04747',
          arxiv: 'https://arxiv.org/abs/1609.04747'
        },
        {
          title: 'Adaptive Methods for Nonconvex Optimization',
          authors: 'Zeyuan Allen-Zhu, Yang Yuan',
          year: '2018',
          url: 'https://arxiv.org/abs/1810.11509',
          arxiv: 'https://arxiv.org/abs/1810.11509'
        }
      ],
      repositories: [
        {
          name: 'gradient-descent-animations',
          description: 'Interactive animations of gradient descent algorithms',
          url: 'https://github.com/trevorstephens/gradient-descent-animations',
          stars: '1.2k',
          language: 'Python'
        },
        {
          name: 'optim',
          description: 'PyTorch optimizers with gradient descent variants',
          url: 'https://github.com/pytorch/optim',
          stars: '2.8k',
          language: 'Python'
        }
      ],
      courses: [
        {
          title: 'Gradient Descent and Optimization',
          platform: 'Coursera',
          description: 'Deep dive into gradient descent algorithms and optimization techniques',
          url: 'https://www.coursera.org/learn/machine-learning-projects',
          duration: '4 weeks'
        }
      ]
    },
    'K-Means Clustering': {
      papers: [
        {
          title: 'A comparison of document clustering techniques',
          authors: 'Andrew McCallum et al.',
          year: '2002',
          url: 'https://www.cs.cmu.edu/~./papaers/kmeans.pdf',
          arxiv: null
        }
      ],
      repositories: [
        {
          name: 'scikit-learn',
          description: 'K-Means implementation in scikit-learn',
          url: 'https://github.com/scikit-learn/scikit-learn',
          stars: '58k',
          language: 'Python'
        },
        {
          name: 'k-means-constrained',
          description: 'K-Means with constraints and visualization',
          url: 'https://github.com/joshlk/k-means-constrained',
          stars: '450',
          language: 'Python'
        }
      ],
      courses: [
        {
          title: 'Unsupervised Learning and Clustering',
          platform: 'edX',
          description: 'Comprehensive course on clustering algorithms including K-Means',
          url: 'https://www.edx.org/learn/machine-learning',
          duration: '6 weeks'
        }
      ]
    },
    'Logistic Regression': {
      papers: [
        {
          title: 'Logistic Regression',
          authors: 'David G. Kleinbaum, Mitchel Klein',
          year: '2002',
          url: 'https://link.springer.com/book/10.1007/978-0-387-95299-1',
          arxiv: null
        }
      ],
      repositories: [
        {
          name: 'logistic-regression',
          description: 'From scratch implementation of logistic regression',
          url: 'https://github.com/akshaybhatia10/logistic-regression',
          stars: '120',
          language: 'Python'
        }
      ],
      courses: [
        {
          title: 'Logistic Regression for Classification',
          platform: 'Udacity',
          description: 'Hands-on course covering logistic regression fundamentals',
          url: 'https://www.udacity.com/course/machine-learning--ud262',
          duration: '8 weeks'
        }
      ]
    },
    'Neural Network': {
      papers: [
        {
          title: 'Deep Learning',
          authors: 'Ian Goodfellow, Yoshua Bengio, Aaron Courville',
          year: '2016',
          url: 'https://www.deeplearningbook.org/',
          arxiv: null
        }
      ],
      repositories: [
        {
          name: 'tensorflow',
          description: 'TensorFlow neural network implementations',
          url: 'https://github.com/tensorflow/tensorflow',
          stars: '183k',
          language: 'C++'
        },
        {
          name: 'pytorch',
          description: 'PyTorch neural network framework',
          url: 'https://github.com/pytorch/pytorch',
          stars: '81k',
          language: 'Python'
        }
      ],
      courses: [
        {
          title: 'Deep Learning Specialization',
          platform: 'Coursera',
          description: 'Comprehensive deep learning course by Andrew Ng',
          url: 'https://www.coursera.org/specializations/deep-learning',
          duration: '16 weeks'
        }
      ]
    },
    'Principal Component Analysis': {
      papers: [
        {
          title: 'Principal Component Analysis',
          authors: 'I.T. Jolliffe',
          year: '2002',
          url: 'https://link.springer.com/book/10.1007/978-0-387-22440-4',
          arxiv: null
        }
      ],
      repositories: [
        {
          name: 'pca',
          description: 'PCA implementation with visualization',
          url: 'https://github.com/akshaybhatia10/pca',
          stars: '85',
          language: 'Python'
        }
      ],
      courses: [
        {
          title: 'Dimensionality Reduction and PCA',
          platform: 'DataCamp',
          description: 'Interactive course on PCA and dimensionality reduction',
          url: 'https://www.datacamp.com/courses/dimensionality-reduction-in-python',
          duration: '4 hours'
        }
      ]
    },
    'Perceptron': {
      papers: [
        {
          title: 'The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain',
          authors: 'Frank Rosenblatt',
          year: '1958',
          url: 'https://psycnet.apa.org/doiLanding?doi=10.1037%2Fh0042519',
          arxiv: null
        }
      ],
      repositories: [
        {
          name: 'perceptron',
          description: 'Simple perceptron implementation from scratch',
          url: 'https://github.com/akshaybhatia10/perceptron',
          stars: '95',
          language: 'Python'
        }
      ],
      courses: [
        {
          title: 'Neural Networks Fundamentals',
          platform: 'fast.ai',
          description: 'Introduction to neural networks starting with perceptrons',
          url: 'https://course.fast.ai/',
          duration: '12 weeks'
        }
      ]
    }
  }

  return resources[algorithm.value?.name] || { papers: [], repositories: [], courses: [] }
})

// 标签页切换时更新进度
const switchTab = async (tabId: string) => {
  // 记录上一个标签页的停留时间
  if (tabStartTime > 0) {
    const duration = Date.now() - tabStartTime
    tabViewTime.value[activeTab.value] = (tabViewTime.value[activeTab.value] || 0) + duration
  }

  activeTab.value = tabId
  tabStartTime = Date.now()

  // 加载相关帖子
  if (tabId === 'resources') {
    await loadRelatedPosts(1)
  }

  // 根据查看的标签页更新进度
  await updateProgress()
}

// 加载相关帖子
const loadRelatedPosts = async (page: number = 1) => {
  try {
    const response = await axios.get(`/api/algorithms/${route.params.id}/related-posts?page=${page}&per_page=5`)
    relatedPosts.value = response.data.posts
    postPagination.value = response.data.pagination
  } catch (error) {
    console.error('Failed to load related posts:', error)
    relatedPosts.value = []
  }
}

// 跟踪资源点击
const trackResourceClick = async (resourceType: string, resourceName: string) => {
  resourceClicks.value[resourceType] = (resourceClicks.value[resourceType] || 0) + 1
  await updateProgress()
}

// 智能进度计算
const updateProgress = async () => {
  if (!userStore.isLoggedIn || !algorithm.value) return

  const currentProgress = userKnowledge.value?.progress || 0
  let newProgress = currentProgress

  // 1. 基础浏览进度 (10%)
  newProgress = Math.max(newProgress, 10)

  // 2. 标签页浏览时间 (最多30%)
  const totalViewTime = Object.values(tabViewTime.value).reduce((sum: number, time: number) => sum + time, 0)
  const timeBonus = Math.min(totalViewTime / (5 * 60 * 1000) * 30, 30) // 5分钟 = 30%进度
  newProgress = Math.max(newProgress, timeBonus)

  // 3. 资源点击次数 (最多30%)
  const totalClicks = Object.values(resourceClicks.value).reduce((sum: number, clicks: number) => sum + clicks, 0)
  const clickBonus = Math.min(totalClicks * 5, 30) // 每个资源点击5%进度，最多30%
  newProgress = Math.max(newProgress, clickBonus)

  // 4. 综合学习深度 (最多30%)
  let depthBonus = 0
  if (tabViewTime.value.theory && tabViewTime.value.theory > 2 * 60 * 1000) depthBonus += 10 // theory停留2分钟
  if (tabViewTime.value.interactive && tabViewTime.value.interactive > 3 * 60 * 1000) depthBonus += 10 // interactive停留3分钟
  if (resourceClicks.value.paper && resourceClicks.value.paper > 0) depthBonus += 5 // 阅读论文
  if (resourceClicks.value.github && resourceClicks.value.github > 0) depthBonus += 5 // 查看代码
  newProgress = Math.max(newProgress, depthBonus)

  // 更新进度
  if (newProgress > currentProgress) {
    await userStore.updateKnowledge(Number(route.params.id), Math.round(newProgress), algorithm.value?.tags || [])
    userKnowledge.value = userStore.getKnowledgeByAlgorithm(Number(route.params.id))
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const fetchAlgorithm = async () => {
  try {
    const algorithmId = route.params.id
    const response = await axios.get(`/api/algorithms/${algorithmId}`)
    algorithm.value = response.data.algorithm

    // 获取用户当前的知识状态
    if (userStore.isLoggedIn) {
      userKnowledge.value = userStore.getKnowledgeByAlgorithm(Number(algorithmId))
    }

    // 记录用户点击算法的行为并更新进度
    try {
      await axios.post(`/api/user/algorithm/${algorithmId}/click`)

      // 根据浏览行为更新进度（基础浏览给5%进度）
      if (userStore.isLoggedIn) {
        const currentProgress = userKnowledge.value?.progress || 0
        const newProgress = Math.max(currentProgress, 5) // 至少5%进度
        await userStore.updateKnowledge(Number(algorithmId), newProgress, algorithm.value?.tags || [])
        userKnowledge.value = userStore.getKnowledgeByAlgorithm(Number(algorithmId))
      }
    } catch (clickError) {
      console.warn('Failed to record algorithm click:', clickError)
      // 不影响主要功能
    }

    console.log('Algorithm loaded:', algorithm.value)
  } catch (error) {
    console.error('Failed to fetch algorithm:', error)
  }
}

// 页面卸载时保存停留时间
import { onBeforeUnmount } from 'vue'

onMounted(() => {
  console.log('Algorithm component mounted with ID:', route.params.id)
  tabStartTime = Date.now()
  fetchAlgorithm()
})

onBeforeUnmount(() => {
  // 保存最后一次停留时间
  if (tabStartTime > 0) {
    const duration = Date.now() - tabStartTime
    tabViewTime.value[activeTab.value] = (tabViewTime.value[activeTab.value] || 0) + duration
    updateProgress()
  }
})

// Local marimo endpoints mapping and embedded fallbacks
const marimoInteractiveMap: Record<string, string> = {
  // Only use Marimo for algorithms that don't have local HTML demos yet
  // Point to backend proxy so backend can inject Marimo-Server-Token header
}

const embeddedNotebookFallback: Record<string, string> = {
  'Gradient Descent': '/gradient_descent_embedded.html'
}

const finalNotebookSrc = computed(() => {
  if (!algorithm.value) return null
  if (algorithm.value.notebook_html_url) {
    return '/' + algorithm.value.notebook_html_url
  }
  const fallback = embeddedNotebookFallback[algorithm.value?.name]
  return fallback || null
})

const finalInteractiveSrc = computed(() => {
  if (!algorithm.value) return null
  // Prefer a local Marimo mapping (if available) so interactive always points to the Marimo service.
  const mapped = marimoInteractiveMap[algorithm.value?.name]
  if (mapped) return mapped
  // Otherwise, fall back to DB-provided URL (could be local static HTML or other)
  if (algorithm.value.interactive_demo_url && typeof algorithm.value.interactive_demo_url === 'string') {
    // Handle local HTML files by adding leading slash
    if (!algorithm.value.interactive_demo_url.startsWith('http') && !algorithm.value.interactive_demo_url.startsWith('/')) {
      return '/' + algorithm.value.interactive_demo_url
    }
    return algorithm.value.interactive_demo_url
  }
  return null
})
</script>

<style scoped>
.algorithm-page {
  min-height: 100vh;
  background: var(--brand-bg);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.algorithm-header {
  margin-bottom: 30px;
  text-align: center;
  position: relative;
}

.header-navigation {
  position: absolute;
  top: 0;
  left: 0;
}

.algorithm-header h1 {
  font-size: 2.5rem;
  color: #1f2937;
  margin-bottom: 10px;
}

.algorithm-description {
  font-size: 1.2rem;
  color: var(--text-muted);
  max-width: 800px;
  margin: 0 auto;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
  justify-content: center;
}

.tab {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  margin: 0 10px;
}

.tab:hover {
  background: #f1f5f9;
}

.tab.active {
  border-bottom-color: #1e40af;
  color: #1e40af;
  font-weight: 600;
}

/* 进度条样式 */
.progress-section {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.progress-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.progress-value {
  font-size: 16px;
  color: #1f2937;
  font-weight: 600;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #06b6d4);
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* 资源页面样式 */
.resource-section {
  margin-bottom: 2rem;
}

.resource-section h4 {
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.resource-item {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: all 0.2s ease;
}

.resource-item:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border-color: #3b82f6;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.resource-header h5 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  flex: 1;
}

.resource-year,
.resource-stars,
.resource-platform,
.resource-author {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
  white-space: nowrap;
  margin-left: 1rem;
}

.resource-authors,
.resource-description {
  color: #4b5563;
  font-size: 0.9rem;
  margin: 0.5rem 0;
  line-height: 1.5;
}

.resource-meta {
  display: flex;
  gap: 1rem;
  margin: 0.5rem 0;
}

.meta-item {
  font-size: 0.8rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.resource-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.resource-language,
.resource-duration {
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 500;
}

/* 按钮样式 - 统一白底蓝字设计 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
  border: 2px solid #1e40af;
  outline: none;
  background: white;
  color: #1e40af;
}

.btn:hover {
  background: #1e40af;
  color: white;
  border-color: #1e40af;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}

/* 特殊按钮样式保持原有设计 */
.btn-primary {
  background: white;
  color: #1e40af;
  border: 2px solid #1e40af;
}

.btn-primary:hover {
  background: #1e40af;
  color: white;
}

.btn-success {
  background: white;
  color: #059669;
  border: 2px solid #059669;
}

.btn-success:hover {
  background: #059669;
  color: white;
}

/* 回退按钮样式 */
.back-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #274060; /* 网站主色调 */
  color: white;
  border: 2px solid #274060;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(39, 64, 96, 0.2);
}

.back-button:hover {
  background: #1e3349;
  border-color: #1e3349;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(39, 64, 96, 0.3);
}

.back-button i {
  font-size: 0.8rem;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1rem;
}

.pagination-info {
  font-size: 0.9rem;
  color: #6b7280;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tab-content {
  background: var(--brand-panel);
  border-radius: 8px;
  padding: 20px;
  box-shadow: var(--shadow-soft);
  color: var(--text-light);
}

.notebook-content iframe,
.interactive-demo iframe {
  border-radius: 4px;
}

.resource-item {
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #3b82f6;
}

.resource-item strong {
  color: #374151;
  margin-right: 8px;
}

.resource-item a {
  color: #3b82f6;
  text-decoration: none;
}

.resource-item a:hover {
  text-decoration: underline;
}

.no-resources {
  color: #6b7280;
  font-style: italic;
}
</style>
