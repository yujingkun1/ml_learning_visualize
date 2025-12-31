<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero hero-immersive" aria-label="Hero">
      <div class="hero-media" aria-hidden="true"></div>
      <div class="hero-overlay"></div>
        <div class="container hero-content">
        <h1>Innovative learning for modern machine learning</h1>
        <p style="max-width:900px;margin:0.25rem auto 1rem;color:var(--text-dark)">Interactive visualizations, curated learning paths and practical projects — designed to make complex algorithms approachable.</p>
        <div class="hero-actions">
          <button class="btn btn-primary hover-float reveal" @click="scrollToGraph">Start Learning</button>
          <button class="btn btn-light btn-outline-dark hover-float reveal" @click="$router.push('/posts')">Explore Community</button>
        </div>
      </div>
    </section>

    <!-- Learning Roadmap Section -->
    <section class="roadmap-section" ref="graphSection">
      <div class="container">
        <h2>Machine Learning Learning Roadmap</h2>
        <div class="roadmap-container">
          <div v-if="loading" class="loading">
            <div class="spinner"></div>
            <p>Loading learning roadmap...</p>
          </div>
          <div v-else-if="roadmapStages.length === 0" class="no-data">
            <i class="fas fa-database"></i>
            <p>No algorithms available</p>
          </div>
          <div v-else class="roadmap-quadrants">
            <div class="quadrant-grid">
              <div class="quadrant" id="quadrant-tl">
                <h4 class="quadrant-title">Supervised Learning</h4>
                <div class="quadrant-layers">
                  <div v-for="alg in quadrantMap['supervised']" :key="alg.id" class="node" :data-category="alg.category" @click.stop="openNode(alg)">
                    <div class="node-name">{{ alg.name }}</div>
                    <div class="node-meta">{{ getDifficultyText(alg.difficulty) }}</div>
                  </div>
                </div>
              </div>

              <div class="quadrant" id="quadrant-tr">
                <h4 class="quadrant-title">Unsupervised Learning</h4>
                <div class="quadrant-layers">
                  <div v-for="alg in quadrantMap['unsupervised']" :key="alg.id" class="node" :data-category="alg.category" @click.stop="openNode(alg)">
                    <div class="node-name">{{ alg.name }}</div>
                    <div class="node-meta">{{ getDifficultyText(alg.difficulty) }}</div>
                  </div>
                </div>
              </div>

              <div class="quadrant" id="quadrant-bl">
                <h4 class="quadrant-title">Deep Learning</h4>
                <div class="quadrant-layers">
                  <div v-for="alg in quadrantMap['deep']" :key="alg.id" class="node" :data-category="alg.category" @click.stop="openNode(alg)">
                    <div class="node-name">{{ alg.name }}</div>
                    <div class="node-meta">{{ getDifficultyText(alg.difficulty) }}</div>
                  </div>
                </div>
              </div>

              <div class="quadrant" id="quadrant-br">
                <h4 class="quadrant-title">Specialized Topics</h4>
                <div class="quadrant-layers">
                  <div v-for="alg in quadrantMap['specialized']" :key="alg.id" class="node" :data-category="alg.category" @click.stop="openNode(alg)">
                    <div class="node-name">{{ alg.name }}</div>
                    <div class="node-meta">{{ getDifficultyText(alg.difficulty) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Claude-like merged Showcase + Features -->
    <section class="claude-section">
      <div class="container">
        <div class="claude-top">
          <div class="claude-intro">
            <h2>Selected Works & Learning Highlights</h2>
            <p class="sub">A curated selection of demos, learning paths and tools — designed to help you explore and build faster.</p>
            <div class="claude-cta">
              <button class="btn btn-primary hover-float reveal" @click="scrollToGraph">Start learning</button>
              <button class="btn btn-light btn-outline-dark hover-float reveal" @click="$router.push('/posts')">Get community</button>
            </div>
          </div>

          <div class="claude-cards">
            <div class="claude-card hover-float reveal">
              <h4>Interactive demos</h4>
              <p>Play with live visualizations to understand model behavior in seconds.</p>
            </div>
            <div class="claude-card hover-float reveal">
              <h4>Curated paths</h4>
              <p>Structured sequences from basics to projects to keep you progressing.</p>
            </div>
            <div class="claude-card hover-float reveal">
              <h4>Community</h4>
              <p>Share experiments, ask for feedback, and learn from others.</p>
            </div>
          </div>
        </div>

        <div class="claude-choices section-separated">
          <div class="choice">
            <h3>Build on your own</h3>
            <p>Use our interactive playgrounds and visual tools to prototype models and visualizations quickly.</p>
            <div class="choice-actions">
              <button class="btn btn-light btn-outline-dark hover-float reveal" @click="$router.push('/algorithms')">Explore demos</button>
            </div>
          </div>
          <div class="choice">
            <h3>Get course support</h3>
            <p>Follow curated learning paths and projects with step-by-step guidance and checkpoints.</p>
            <div class="choice-actions">
              <button class="btn btn-light btn-outline-dark hover-float reveal" @click="$router.push('/posts')">View paths</button>
            </div>
          </div>
        </div>
        
      </div>
    </section>
    <!-- Use cases section 模仿 Claude -->
    <section class="usecases" aria-label="Use cases">
      <div class="usecases-inner container">
        <div class="icon-hero">◧ ◭ ◯</div>
        <h2>Use cases for ML Learner</h2>
        <div class="usecases-grid">
          <div class="usecase">
            <span class="uc-icon">▹</span>
            <h4>Coding</h4>
            <p>High-quality code examples, reasoning and tool assistance to speed up engineering tasks.</p>
            <a class="learn-more" href="/algorithms">Learn more</a>
          </div>
          <div class="usecase">
            <span class="uc-icon">⚙</span>
            <h4>Agents</h4>
            <p>Compose agents and workflows that combine multiple tools and model calls for complex tasks.</p>
            <a class="learn-more" href="/posts">Learn more</a>
          </div>
          <div class="usecase">
            <span class="uc-icon">⚡</span>
            <h4>Productivity</h4>
            <p>Extract insights from documents, generate summaries, and speed up research workflows.</p>
            <a class="learn-more" href="/posts">Learn more</a>
          </div>
          <div class="usecase">
            <span class="uc-icon">💬</span>
            <h4>Customer support</h4>
            <p>Build automated flows that handle triage and complex inquiries with contextual awareness.</p>
            <a class="learn-more" href="/posts">Learn more</a>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// 数据
const categories = ref([])
const algorithms = ref([])
const loading = ref(true)

// DOM 引用
const graphSection = ref()

// 计算属性：构建路线图阶段数据
const roadmapStages = computed(() => {
  if (!algorithms.value.length) return []

  // 按照学习路径组织算法，按照roadmap.sh风格分组
  const stages = [
    {
      id: 'fundamentals',
      title: 'Machine Learning Fundamentals',
      description: 'Essential concepts and basic algorithms to start your ML journey',
      icon: 'fas fa-seedling',
      color: '#10b981',
      algorithms: [] as any[]
    },
    {
      id: 'supervised-learning',
      title: 'Supervised Learning',
      description: 'Learn with labeled data - regression and classification algorithms',
      icon: 'fas fa-chart-line',
      color: '#3b82f6',
      algorithms: [] as any[]
    },
    {
      id: 'unsupervised-learning',
      title: 'Unsupervised Learning',
      description: 'Discover patterns in unlabeled data',
      icon: 'fas fa-search',
      color: '#f59e0b',
      algorithms: [] as any[]
    },
    {
      id: 'deep-learning',
      title: 'Deep Learning',
      description: 'Neural networks and advanced architectures',
      icon: 'fas fa-brain',
      color: '#8b5cf6',
      algorithms: [] as any[]
    },
    {
      id: 'specialized',
      title: 'Specialized Topics',
      description: 'Advanced techniques and specialized algorithms',
      icon: 'fas fa-rocket',
      color: '#ef4444',
      algorithms: [] as any[]
    }
  ]

  // 按照类别分配算法
  algorithms.value.forEach((algorithm: any) => {
    const categoryName = algorithm.category?.name

    switch (categoryName) {
      case '监督学习':
      case 'Supervised Learning':
      case '线性模型':
      case 'Linear Models':
      case '决策树':
      case 'Decision Tree':
      case '支持向量机':
      case 'Support Vector Machine':
      case '贝叶斯方法':
      case 'Naive Bayes':
        stages[1].algorithms.push(algorithm) // Supervised Learning
        break
      case '无监督学习':
      case 'Unsupervised Learning':
      case '聚类算法':
      case 'Clustering':
      case '降维算法':
      case 'Dimensionality Reduction':
      case '关联规则':
      case 'Association Rules':
        stages[2].algorithms.push(algorithm) // Unsupervised Learning
        break
      case '深度学习':
      case 'Deep Learning':
      case '卷积神经网络':
      case 'Convolutional Neural Network':
      case '循环神经网络':
      case 'Recurrent Neural Network':
      case '生成对抗网络':
      case 'Generative Adversarial Network':
      case '图神经网络':
      case 'Graph Neural Network':
        stages[3].algorithms.push(algorithm) // Deep Learning
        break
      case '强化学习':
      case 'Reinforcement Learning':
      case '集成学习':
      case 'Ensemble Learning':
        stages[4].algorithms.push(algorithm) // Specialized Topics
        break
      default:
        stages[0].algorithms.push(algorithm) // Fundamentals (fallback)
    }
  })

  // 对每个阶段内的算法按难度排序
  stages.forEach(stage => {
    stage.algorithms.sort((a: any, b: any) => {
      const difficultyOrder = { 'beginner': 0, 'intermediate': 1, 'advanced': 2 }
      const diffA = difficultyOrder[a.difficulty as keyof typeof difficultyOrder] ?? 3
      const diffB = difficultyOrder[b.difficulty as keyof typeof difficultyOrder] ?? 3
      return diffA - diffB
    })
  })

  // 移除空的阶段
  return stages.filter(stage => stage.algorithms.length > 0)
})

// 四象限映射（按照算法名称重新分类到四类）
const quadrantMap = computed(() => {
  const map: { [key: string]: any[] } = {
    supervised: [],
    unsupervised: [],
    deep: [],
    specialized: []
  }

  algorithms.value.forEach((algorithm: any) => {
    const algName = algorithm.name.toLowerCase()

    // 监督学习：Logistic Regression, Perceptron (移除了Gradient Descent)
    if (algName.includes('logistic') || algName.includes('perceptron')) {
      map.supervised.push(algorithm)
    }
    // 无监督学习：K-Means, PCA
    else if (algName.includes('k-means') || algName.includes('principal') || algName.includes('pca')) {
      map.unsupervised.push(algorithm)
    }
    // 深度学习：Neural Network
    else if (algName.includes('neural')) {
      map.deep.push(algorithm)
    }
    // 特别主题：Gradient Descent等
    else if (algName.includes('gradient')) {
      map.specialized.push(algorithm)
    }
    // 其他算法放在specialized
    else {
      map.specialized.push(algorithm)
    }
  })

  // 按难度分组并返回
  const sortByDifficulty = (arr: any[]) => arr.sort((a,b) => {
    const order = { beginner: 0, intermediate: 1, advanced: 2 }
    return (order[a.difficulty]||3) - (order[b.difficulty]||3)
  })

  map.supervised = sortByDifficulty(map.supervised)
  map.unsupervised = sortByDifficulty(map.unsupervised)
  map.deep = sortByDifficulty(map.deep)
  map.specialized = sortByDifficulty(map.specialized)

  return map
})

const scrollToGraph = () => {
  graphSection.value?.scrollIntoView({ behavior: 'smooth' })
}

// 视差/显现：使用 IntersectionObserver 为带 .reveal 的元素添加 in-view 类并做 stagger
const registerReveal = (selector = '.reveal', stagger = 80) => {
  const els = Array.from(document.querySelectorAll(selector))
  if (!els.length) return
  const io = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const group = entry.target
        // if target is a container with multiple reveal children, stagger them
        const children = group.querySelectorAll?.('.reveal') || [group]
        if (children.length) {
          Array.from(children).forEach((ch: any, i) => {
            setTimeout(() => ch.classList.add('in-view'), i * stagger)
          })
        } else {
          group.classList.add('in-view')
        }
        observer.unobserve(group)
      }
    })
  }, { threshold: 0.12 })

  els.forEach(el => io.observe(el))
}
const fetchData = async () => {
  try {
    loading.value = true
    const [categoriesRes, algorithmsRes] = await Promise.all([
      axios.get('/api/categories'),
      axios.get('/api/algorithms?per_page=100')
    ])

    categories.value = categoriesRes.data.categories
    algorithms.value = algorithmsRes.data.algorithms
  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

const navigateToAlgorithm = (algorithmId: number) => {
  router.push(`/algorithms/${algorithmId}`)
}

// 算法节点点击处理
const openNode = (algorithm: any) => {
  // 直接跳转到算法详情页面
  router.push(`/algorithms/${algorithm.id}`)
}

const getNodePositionClass = (index: number) => {
  // 交替左右分布，创建类似roadmap.sh的布局
  const positions = ['left', 'right', 'center', 'left', 'right']
  return positions[index % positions.length]
}

const getAlgorithmIcon = (algorithmName: string) => {
  const iconMap: { [key: string]: string } = {
    'Linear Regression': 'fas fa-chart-line',
    'Logistic Regression': 'fas fa-sigmoid',
    'Decision Tree': 'fas fa-tree',
    'Random Forest': 'fas fa-trees',
    'Support Vector Machine': 'fas fa-vector-square',
    'K-Means Clustering': 'fas fa-circle-nodes',
    'Naive Bayes': 'fas fa-calculator',
    'K-Nearest Neighbors': 'fas fa-users',
    'Principal Component Analysis': 'fas fa-compress',
    'Convolutional Neural Network': 'fas fa-brain',
    'Recurrent Neural Network': 'fas fa-wave-square',
    'Long Short-Term Memory': 'fas fa-memory',
    'Generative Adversarial Network': 'fas fa-robot',
    'Graph Neural Network': 'fas fa-project-diagram',
    'Reinforcement Learning': 'fas fa-gamepad',
    'Autoencoder': 'fas fa-compress-arrows-alt',
    'Transformer': 'fas fa-exchange-alt',
    'Gradient Boosting': 'fas fa-arrow-up',
    'Hierarchical Clustering': 'fas fa-sitemap',
    'DBSCAN': 'fas fa-dot-circle',
    'Apriori Algorithm': 'fas fa-link',
    'FP-Growth': 'fas fa-seedling'
  }
  return iconMap[algorithmName] || 'fas fa-brain'
}

const getDifficultyText = (difficulty: string) => {
  const textMap = {
    'beginner': 'Beginner',
    'intermediate': 'Intermediate',
    'advanced': 'Advanced'
  }
  return textMap[difficulty as keyof typeof textMap] || difficulty
}

const getStageTitle = (level: string) => {
  const titles = {
    beginner: 'Beginner Level',
    intermediate: 'Intermediate Level',
    advanced: 'Advanced Level'
  }
  return titles[level as keyof typeof titles] || level
}

const getStageDescription = (level: string) => {
  const descriptions = {
    beginner: 'Start your ML journey with fundamental algorithms',
    intermediate: 'Build upon basics with more sophisticated techniques',
    advanced: 'Master cutting-edge algorithms and complex architectures'
  }
  return descriptions[level as keyof typeof descriptions] || ''
}

const getStageIcon = (level: string) => {
  const icons = {
    beginner: 'fas fa-seedling',
    intermediate: 'fas fa-cogs',
    advanced: 'fas fa-rocket'
  }
  return icons[level as keyof typeof icons] || 'fas fa-brain'
}

const getCategoryClass = (categoryName: string) => {
  const categoryClasses: { [key: string]: string } = {
    '线性模型': 'category-linear',
    '决策树': 'category-tree',
    '支持向量机': 'category-svm',
    '贝叶斯方法': 'category-bayes',
    '聚类算法': 'category-clustering',
    '降维算法': 'category-dimensionality',
    '关联规则': 'category-association',
    '卷积神经网络': 'category-cnn',
    '循环神经网络': 'category-rnn',
    '生成对抗网络': 'category-gan',
    '图神经网络': 'category-gnn',
    '强化学习': 'category-rl',
    '集成学习': 'category-ensemble'
  }
  return categoryClasses[categoryName] || 'category-default'
}

onMounted(() => {
  fetchData()
  // 注册页面显现动画
  // wait a tick to ensure DOM nodes are present
  setTimeout(() => {
    registerReveal('.claude-intro h2, .claude-intro .sub, .claude-card, .choice, .usecase, .btn.reveal', 90)
  }, 120)
})
</script>

<style scoped>
.hero-immersive {
  position: relative;
  min-height: 420px;
  display: flex;
  align-items: center;
  color: var(--text-dark);
  overflow: hidden;
  background: transparent;
  margin-top: calc(-1 * var(--nav-height)); /* pull hero up so there's no blank space under the nav */
}
.hero-media {
  position: absolute;
  inset: 0;
  background-image: url('/assets/hero.jpg');
  background-size: cover;
  background-position: center center;
  transform: scale(1.02);
  filter: saturate(0.98) contrast(1) brightness(1.05);
  transition: transform 8s ease;
  will-change: transform;
}
.hero-media:hover { transform: scale(1.04); }
.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.25), rgba(255,255,255,0.35)); /* brighten hero */
}
.hero-content {
  position: relative;
  z-index: 5;
  padding: 1.5rem 0;
  padding-top: calc(var(--nav-height) + 8px); /* ensure title is visible under sticky nav */
  text-align: center;
}
.hero-content h1 {
  font-family: var(--heading-font);
  font-size: 2.8rem;
  font-weight: 700;
  letter-spacing: 0.2px;
  margin-bottom: 0.6rem;
  color: var(--text-dark); /* black title */
  max-width: 820px;
  margin-left: auto;
  margin-right: auto;
}
.hero-content p {
  font-family: var(--body-font);
  font-size: 1.05rem;
  color: var(--text-muted);
  max-width: 720px;
  margin: 0.4rem auto 1.2rem;
}
.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
}
.btn.btn-primary {
  background: #ffffff;
  color: #0f172a;
  padding: 0.9rem 1.4rem;
  border-radius: 999px;
  font-weight: 700;
  box-shadow: 0 8px 30px rgba(15,23,42,0.08);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  border: 1px solid rgba(15,23,42,0.06);
}
.btn.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 50px rgba(15,23,42,0.12);
}
.btn.btn-secondary {
  background: transparent;
  border: 1px solid rgba(15,23,42,0.08);
  color: #0f172a;
  padding: 0.75rem 1.25rem;
  border-radius: 999px;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-primary {
  background: #ffffff;
  border: none;
  color: #0f172a;
  padding: 0.75rem 1.25rem;
  border-radius: 0.5rem;
  font-weight: 600;
}

.btn-secondary {
  background: transparent;
  border: 1px solid rgba(15,23,42,0.08);
  color: #0f172a;
  padding: 0.75rem 1.25rem;
  border-radius: 0.5rem;
}


.roadmap-section {
  padding: 4rem 0;
  background: transparent;
}

.roadmap-section h2 {
  text-align: center;
  margin-bottom: 0.5rem;
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-dark);
}

.roadmap-section > p {
  text-align: center;
  color: var(--text-muted);
  margin-bottom: 3rem;
  font-size: 1.1rem;
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
}

.roadmap-container {
  background: var(--brand-panel);
  border-radius: 12px;
  box-shadow: var(--shadow-soft);
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  border: 1px solid var(--border-color);
  color: var(--text-dark);
}

/* Roadmap Grid Layout */
.roadmap-quadrants {
  margin-top: 2rem;
}
.quadrant-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 1.5rem;
}
.quadrant {
  background: var(--light-panel);
  border-radius: 12px;
  padding: 1rem;
  min-height: 220px;
  box-shadow: var(--shadow-soft);
  border: 1px solid var(--border-color);
}
.quadrant-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-dark);
  margin-bottom: 0.75rem;
}
.quadrant-layers {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.node {
  padding: 0.6rem 0.8rem;
  border-radius: 0.5rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-dark);
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

/* 为不同分类设置不同的背景颜色 */
.node[data-category*="Supervised"],
.node[data-category*="Linear"],
.node[data-category*="Decision"] {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.node[data-category*="Unsupervised"],
.node[data-category*="Clustering"],
.node[data-category*="Dimensionality"] {
  background: linear-gradient(135deg, #10b981, #059669);
}

.node[data-category*="Deep"],
.node[data-category*="Convolutional"],
.node[data-category*="Recurrent"],
.node[data-category*="Neural"] {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.node[data-category*="Optimization"],
.node[data-category*="Ensemble"],
.node[data-category*="Bayesian"] {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.node[data-category*="Reinforcement"],
.node[data-category*="Generative"],
.node[data-category*="Graph"] {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}
.node:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(2,6,23,0.08); }
.node-name {
  font-weight: 600;
}
.node-meta {
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* Stage Styles */
.roadmap-stage {
  background: #f8fafc;
  border-radius: 12px;
  border: 2px solid var(--stage-color);
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.stage-header {
  background: var(--stage-color);
  color: white;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stage-icon-wrapper {
  flex-shrink: 0;
}

.stage-icon {
  font-size: 1.5rem;
  opacity: 0.9;
}

.stage-info {
  flex: 1;
}

.stage-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: white;
}

.stage-description {
  font-size: 0.9rem;
  margin: 0 0 0.75rem 0;
  opacity: 0.9;
  line-height: 1.4;
}

.stage-count {
  font-size: 0.8rem;
  font-weight: 600;
  opacity: 0.8;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  display: inline-block;
}

/* Algorithms Grid */
.algorithms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  padding: 1.5rem;
}

.algorithm-card {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.algorithm-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px -8px rgba(0, 0, 0, 0.2);
  border-color: var(--stage-color);
}

.algorithm-card.difficulty-beginner {
  border-left: 4px solid #10b981;
}

.algorithm-card.difficulty-intermediate {
  border-left: 4px solid #f59e0b;
}

.algorithm-card.difficulty-advanced {
  border-left: 4px solid #ef4444;
}

.algorithm-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.algorithm-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 6px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 1rem;
  flex-shrink: 0;
}

.algorithm-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.difficulty-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.difficulty-badge.beginner {
  background: #dcfce7;
  color: #166534;
}

.difficulty-badge.intermediate {
  background: #fef3c7;
  color: #92400e;
}

.difficulty-badge.advanced {
  background: #dc2626;
  color: #ffffff;
}

.algorithm-category {
  background: #f3f4f6;
  color: var(--text-muted);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 500;
}

.algorithm-content {
  margin-bottom: 1rem;
}

.algorithm-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.algorithm-description {
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.4;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.algorithm-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  margin-bottom: 0.75rem;
}

.algorithm-tags .tag {
  background: #f3f4f6;
  color: var(--text-muted);
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-size: 0.65rem;
  font-weight: 500;
}

.algorithm-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.learn-link {
  color: var(--stage-color);
  font-size: 0.8rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
}

.algorithm-card:hover .learn-link {
  text-decoration: underline;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--text-muted);
  font-size: 1.125rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--text-muted);
  font-size: 1.125rem;
}

.no-data i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.features {
  padding: 4rem 0;
  background: transparent;
}

.features h2 {
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2rem;
  font-weight: 600;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  background: var(--brand-panel);
  border-radius: 0.75rem;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: var(--shadow-soft);
  color: var(--text-dark);
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 60px rgba(2,6,23,0.55);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-dark);
}

.feature-card p {
  color: var(--text-muted);
  line-height: 1.6;
}

/* 知识图谱样式 */
.graph-tooltip {
  background: rgba(0, 0, 0, 0.8) !important;
  color: white !important;
  padding: 8px 12px !important;
  border-radius: 6px !important;
  font-size: 12px !important;
  pointer-events: none !important;
  z-index: 1000 !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2rem;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .graph-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}

.showcase {
  padding: 4rem 0;
  background: transparent;
}
.showcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
  align-items: start;
  margin-top: 1.5rem;
}
.showcase .glass-card {
  padding: 0;
  overflow: hidden;
  min-height: 360px;
  display: flex;
  flex-direction: column;
  background: var(--brand-panel);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-soft);
}
.showcase .card-img {
  width: 100%;
  height: 320px;
  object-fit: cover;
  display: block;
}
.showcase h3 { margin: 0.75rem 1rem 0 1rem; color: var(--text-dark); }
.showcase p { margin: 0.25rem 1rem 1rem 1rem; color: var(--text-muted); }

@media (max-width: 768px) {
  .showcase {
    padding: 2rem 0;
  }
  .showcase-grid {
    grid-template-columns: 1fr;
  }
}

/* Claude-like section styles */
.claude-section {
  padding: 4rem 0;
  background: transparent;
}
.claude-top {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 2rem;
  align-items: start;
  margin-bottom: 2.25rem;
}
.claude-intro h2 {
  font-family: var(--heading-font);
  font-size: 2.4rem;
  color: var(--text-dark);
  margin-bottom: 0.5rem;
}
.claude-intro .sub {
  color: var(--text-muted);
  max-width: 640px;
  margin-bottom: 1.25rem;
}
.claude-cta { display:flex; gap:0.75rem; margin-top:0.5rem; }
.claude-cards { display:flex; flex-direction:column; gap:1rem; }
.claude-card {
  background: var(--brand-panel);
  border: 1px solid var(--border-color);
  padding: 1rem;
  border-radius: 10px;
  box-shadow: var(--shadow-soft);
}

/* Paired buttons: 左侧深色（黑底白字），右侧米色（浅底深字）——仅作用于并排的按钮容器 */
.hero-actions > .btn:first-child,
.claude-cta > .btn:first-child,
.hero-actions > button:first-child,
.claude-cta > button:first-child {
  background: #0f172a; /* near black */
  color: #ffffff;
  border: none;
  padding: 0.9rem 1.4rem;
  border-radius: 999px;
  font-weight: 700;
  box-shadow: 0 10px 36px rgba(2,6,23,0.18);
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 160ms ease;
}
.hero-actions > .btn:first-child:hover,
.claude-cta > .btn:first-child:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 48px rgba(2,6,23,0.22);
}

.hero-actions > .btn:nth-child(2),
.claude-cta > .btn:nth-child(2),
.hero-actions > button:nth-child(2),
.claude-cta > button:nth-child(2) {
  background: #efece2; /* warm beige */
  color: #0f172a; /* dark text */
  border: 1px solid rgba(15,23,42,0.06);
  padding: 0.9rem 1.4rem;
  border-radius: 999px;
  font-weight: 600;
  box-shadow: 0 6px 20px rgba(15,23,42,0.04);
  transition: transform 0.18s ease, background 160ms ease, box-shadow 160ms ease;
}
.hero-actions > .btn:nth-child(2):hover,
.claude-cta > .btn:nth-child(2):hover {
  transform: translateY(-2px);
  background: #e7e3d8;
  box-shadow: 0 12px 30px rgba(15,23,42,0.06);
}

/* 在移动端恢复原有的垂直排列样式（覆盖上面的选择器） */
@media (max-width: 768px) {
  .hero-actions > .btn:first-child,
  .hero-actions > .btn:nth-child(2),
  .claude-cta > .btn:first-child,
  .claude-cta > .btn:nth-child(2) {
    width: auto;
  }
}
.claude-card h4 { margin:0 0 0.5rem 0; color:var(--text-dark); font-weight:700; font-family: 'Georgia', 'Times New Roman', serif; font-size:1.05rem;}
.claude-card p { margin:0; color:var(--text-muted); font-size:1rem; }

.claude-choices {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}
.choice {
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.03));
  border: 1px solid var(--border-color);
  padding: 1.25rem;
  border-radius: 12px;
  box-shadow: var(--shadow-soft);
}
.choice h3 { margin:0 0 0.5rem 0; color:var(--text-dark); font-size:1.25rem; font-family: 'Georgia', 'Times New Roman', serif; }
.choice p { margin:0 0 1rem 0; color:var(--text-muted); font-size:1rem; }
.choice-actions { display:flex; gap:0.5rem; }

.claude-models .models-title { margin-top:0; color:var(--text-dark); font-weight:700; margin-bottom:1rem; text-align:left; }
.models-grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:1rem; }
.model { background:var(--brand-panel); border:1px solid var(--border-color); border-radius:10px; overflow:hidden; display:flex; gap:0.75rem; align-items:center; padding:0.5rem; }
.model img { width:96px; height:72px; object-fit:cover; border-radius:6px; }
.model-info strong { display:block; color:var(--text-dark); font-weight:700; }
.model-info span { color:var(--text-muted); font-size:0.9rem; }

@media (max-width: 980px) {
  .claude-top { grid-template-columns: 1fr; }
  .models-grid { grid-template-columns: 1fr; }
  .claude-choices { grid-template-columns: 1fr; }
}

/* 按钮黑色边框样式 & 提高对比 */
.btn-outline-dark {
  background: transparent;
  border: 1px solid #0f172a;
  color: #0f172a;
  box-shadow: 0 8px 30px rgba(15,23,42,0.06);
  padding: 0.6rem 1rem;
  border-radius: 999px;
}
.btn-outline-dark:hover {
  background: #0f172a;
  color: #fff;
  transform: translateY(-2px);
}

/* 减小中部 whitespace，增强文字对比 */
.claude-top { gap:1rem; margin-bottom:1.5rem; padding-bottom:0.5rem; }
.claude-intro h2 { font-size:2.4rem; font-family: 'Georgia', 'Times New Roman', serif; }
.claude-intro .sub { color:#4b5563; font-size:1rem; } /* 更深一点 */
.claude-card p { color:#374151; } /* 提升可读性 */
.choice p { color:#374151; } /* 更有对比度 */
.model-info span { color:#4b5563; }

/* 在各大区块间增加明确分隔与呼吸空间 */
.section-separated { padding: 1.25rem 0; border-top: 1px solid rgba(15,23,42,0.04); margin-top: 0.75rem; }
.claude-section { padding-bottom: 2.5rem; margin-bottom: 1rem; }
.usecases { padding-top: 2.5rem; margin-top: 1.5rem; border-top: 1px solid rgba(15,23,42,0.04); }

/* 浅色按钮（白底深字）*/
.btn-light {
  background: #ffffff;
  color: #0f172a;
  border-radius: 999px;
  padding: 0.6rem 1rem;
  font-weight: 700;
  border: 1px solid rgba(15,23,42,0.06);
  box-shadow: 0 6px 24px rgba(15,23,42,0.04);
}

/* 悬浮微交互：各卡片和按钮浮动效果 */
.hover-float {
  transition: transform 260ms cubic-bezier(.16,.84,.44,1), box-shadow 260ms cubic-bezier(.16,.84,.44,1);
  will-change: transform, box-shadow;
}
.hover-float:hover {
  transform: translateY(-6px);
  box-shadow: 0 24px 60px rgba(15,23,42,0.12);
}
.choice, .claude-card, .usecase, .claude-cta .btn { /* apply hover behavior */
  /* promote to layer */
  transform: translateZ(0);
}
 

/* reveal base */
.reveal {
  opacity: 0;
  transform: translateY(-14px);
  transition: opacity 420ms cubic-bezier(.16,.84,.44,1), transform 420ms cubic-bezier(.16,.84,.44,1);
  will-change: transform, opacity;
}
.reveal.in-view {
  opacity: 1;
  transform: translateY(0);
}

/* Use cases section （模仿 Claude 图二） */
.usecases {
  padding: 3.5rem 0 2rem;
  background: transparent;
}
.usecases .usecases-inner {
  text-align: center;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1rem;
}
.usecases .icon-hero {
  font-size: 40px;
  color: #0f172a;
  opacity: 0.9;
  margin-bottom: 12px;
}
.usecases h2 {
  font-family: var(--heading-font);
  font-size: 2.6rem;
  margin-bottom: 1.25rem;
  color: var(--text-dark);
}
.usecases-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
  margin-top: 2rem;
  align-items: start;
  border-top: 1px solid rgba(15, 23, 42, 0.04);
  padding-top: 1.75rem;
}
.usecase {
  text-align: left;
  padding: 1rem 1.25rem;
  border-right: 1px solid rgba(15, 23, 42, 0.04);
}
.usecase:last-child { border-right: none; }
.usecase .uc-icon { font-size: 20px; color:var(--text-muted); margin-bottom:0.6rem; display:block; }
.usecase h4 { margin:0 0 0.5rem 0; color:var(--text-dark); font-weight:700; }
.usecase p { margin:0; color:var(--text-muted); font-size:0.95rem; line-height:1.6; }
.usecase .learn-more {
  display:inline-block;
  margin-top:0.9rem;
  padding:0.35rem 0.6rem;
  border:1px solid rgba(15,23,42,0.08);
  border-radius:8px;
  color:#0f172a;
  background:transparent;
  font-size:0.9rem;
}

@media (max-width: 980px) {
  .usecases-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 600px) {
  .usecases-grid { grid-template-columns: 1fr; }
}
</style>
