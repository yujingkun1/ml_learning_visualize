<template>
  <div class="algorithms-page">
    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h1>Machine Learning Algorithms</h1>
        <p>Explore and learn various machine learning algorithms with interactive visualizations</p>
      </div>

      <!-- 筛选和搜索 -->
  <div class="algorithms-controls">
        <div class="search-box">
          <input
            ref="searchInput"
            type="search"
            aria-label="Search algorithms - Press Ctrl+K to focus"
            v-model="searchQuery"
            @input="debouncedSearch"
            placeholder="Search algorithms..."
            class="search-input"
          >
          <i class="fas fa-search search-icon"></i>
        </div>
        <div class="filter-buttons">
          <select v-model="selectedCategory" @change="filterAlgorithms">
            <option value="">All Categories</option>
            <option v-for="category in derivedCategories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
          <select v-model="selectedDifficulty" @change="filterAlgorithms">
            <option value="">All Levels</option>
            <option v-for="level in derivedLevels" :key="level" :value="level">
              {{ getDifficultyText(level) }}
            </option>
          </select>
        </div>
      </div>

      <!-- 算法网格 -->
      <div class="algorithms-container">
        <div v-if="loading" class="loading">Loading algorithms...</div>
        <div v-else-if="filteredAlgorithms.length === 0" class="no-algorithms">
          <i class="fas fa-brain fa-3x"></i>
          <p>No algorithms found</p>
        </div>
        <div v-else class="algorithms-grid">
          <div
            v-for="algorithm in filteredAlgorithms"
            :key="algorithm.id"
            :id="`alg-${algorithm.id}`"
            class="algorithm-card"
            tabindex="0"
            role="button"
            :aria-label="`Learn about ${algorithm.name}`"
            @click="$router.push(`/algorithms/${algorithm.id}`)"
            @keydown="handleCardKeydown($event, algorithm.id)"
          >
            <div class="algorithm-header">
              <div class="algorithm-icon">
                <i :class="getAlgorithmIcon(algorithm.name)"></i>
              </div>
              <div class="algorithm-meta">
                <span class="difficulty" :class="algorithm.difficulty">{{ getDifficultyText(algorithm.difficulty) }}</span>
                <span class="category">{{ algorithm.category?.name }}</span>
              </div>
            </div>

            <div class="algorithm-content">
              <h3>{{ algorithm.name }}</h3>
              <p>{{ algorithm.description }}</p>
              <div class="algorithm-tags">
                <span v-for="tag in algorithm.tags" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </div>

            <div class="algorithm-actions">
              <button class="btn btn-primary" @click.stop="$router.push(`/algorithms/${algorithm.id}`)">Learn More</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const algorithms = ref([])
const categories = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedDifficulty = ref('')
const searchInput = ref<HTMLInputElement | null>(null)
const $router = useRouter()

// 防抖搜索
let searchTimeout: number | null = null
const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    filterAlgorithms()
  }, 500)
}

const filteredAlgorithms = computed(() => {
  let filtered = [...algorithms.value]

  if (selectedCategory.value) {
    const catId = parseInt(selectedCategory.value)
    filtered = filtered.filter((alg: any) => {
      const algCatId = alg?.category?.id ?? alg?.category_id
      return algCatId === catId
    })
  }

  if (selectedDifficulty.value) {
    filtered = filtered.filter((alg: any) => alg.difficulty === selectedDifficulty.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter((alg: any) => {
      const name = (alg.name || "").toLowerCase()
      const desc = (alg.description || "").toLowerCase()
      const tags = (alg.tags || []).map((t: any) => (t || "").toString().toLowerCase())
      return name.includes(query) || desc.includes(query) || tags.some((t: string) => t.includes(query))
    })
  }

  return filtered
})

// derive categories and difficulty levels from the fetched algorithms so filters only show available values
const derivedCategories = computed(() => {
  const map = new Map<number, { id: number; name: string }>()
  algorithms.value.forEach((alg: any) => {
    const cat = alg.category
    if (cat && cat.id) {
      if (!map.has(cat.id)) {
        map.set(cat.id, { id: cat.id, name: cat.name || cat.title || 'Unnamed' })
      }
    }
  })
  return Array.from(map.values())
})

const derivedLevels = computed(() => {
  const set = new Set<string>()
  algorithms.value.forEach((alg: any) => {
    if (alg.difficulty) set.add(alg.difficulty)
  })
  // preserve a predictable ordering if possible
  const order = ['beginner', 'intermediate', 'advanced']
  const ordered = order.filter(o => set.has(o))
  const others = Array.from(set).filter(s => !order.includes(s))
  return ordered.concat(others)
})

const fetchData = async () => {
  try {
    loading.value = true
    const res = await axios.get('/api/algorithms?per_page=200')
    algorithms.value = res.data.algorithms || []
  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

const filterAlgorithms = () => {
  // 触发computed重新计算
}

const getDifficultyText = (difficulty: string) => {
  const texts = {
    'beginner': 'Beginner',
    'intermediate': 'Intermediate',
    'advanced': 'Advanced'
  }
  return texts[difficulty] || difficulty
}

const getAlgorithmIcon = (algorithmName: string) => {
  const icons: { [key: string]: string } = {
    'Linear Regression': 'fas fa-chart-line',
    'Logistic Regression': 'fas fa-wave-square',
    'Decision Tree': 'fas fa-sitemap',
    'Random Forest': 'fas fa-tree',
    'K-Means Clustering': 'fas fa-circle-nodes',
    'Principal Component Analysis': 'fas fa-compress',
    'Convolutional Neural Network': 'fas fa-image',
    'Recurrent Neural Network': 'fas fa-clock',
    'Graph Neural Network': 'fas fa-project-diagram',
    't-SNE': 'fas fa-magic'
  }
  return icons[algorithmName] || 'fas fa-brain'
}

// 页面键盘事件处理
const handlePageKeydown = (event: KeyboardEvent) => {
  // Ctrl+K 聚焦搜索框
  if (event.ctrlKey && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    searchInput.value?.focus()
  }
}

onMounted(() => {
  fetchData()
  // 添加页面级键盘事件监听
  window.addEventListener('keydown', handlePageKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handlePageKeydown)
})

// 支持通过 query.focus 高亮并滚动到指定算法卡片
const route = useRoute()

const scrollToFocus = async () => {
  const focus = route.query.focus
  if (focus) {
    await nextTick()
    const el = document.getElementById(`alg-${focus}`)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      el.classList.add('highlight-focus')
      setTimeout(() => el.classList.remove('highlight-focus'), 3000)
    }
  }
}

watch(() => route.query.focus, () => {
  scrollToFocus()
})

// 键盘导航处理
const handleCardKeydown = (event: KeyboardEvent, algorithmId: number) => {
  const currentCard = event.target as HTMLElement
  const grid = currentCard.closest('.algorithms-grid') as HTMLElement
  const cards = Array.from(grid.querySelectorAll('.algorithm-card')) as HTMLElement[]
  const currentIndex = cards.indexOf(currentCard)

  switch (event.key) {
    case 'Enter':
    case ' ':
      event.preventDefault()
      $router.push(`/algorithms/${algorithmId}`)
      break
    case 'ArrowRight':
      event.preventDefault()
      const nextIndex = (currentIndex + 1) % cards.length
      cards[nextIndex].focus()
      break
    case 'ArrowLeft':
      event.preventDefault()
      const prevIndex = currentIndex === 0 ? cards.length - 1 : currentIndex - 1
      cards[prevIndex].focus()
      break
    case 'ArrowDown':
      event.preventDefault()
      // 假设每行有3个卡片，根据网格布局计算
      const columns = Math.floor(grid.offsetWidth / 320) || 1
      const nextDownIndex = Math.min(currentIndex + columns, cards.length - 1)
      cards[nextDownIndex].focus()
      break
    case 'ArrowUp':
      event.preventDefault()
      const columnsUp = Math.floor(grid.offsetWidth / 320) || 1
      const nextUpIndex = Math.max(currentIndex - columnsUp, 0)
      cards[nextUpIndex].focus()
      break
  }
}
</script>

<style scoped>
.algorithms-page {
  padding: 2rem 0;
  background: var(--brand-bg);
  min-height: 100vh;
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
  font-size: 1.125rem;
}

.algorithms-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: var(--brand-panel);
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: var(--shadow-soft);
  flex-wrap: wrap;
  gap: 1rem;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.filter-buttons {
  display: flex;
  gap: 1rem;
}

.filter-buttons select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  background: var(--light-panel);
  color: var(--text-dark);
}

.algorithms-container {
  background: transparent;
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: none;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  font-size: 1.125rem;
}

.no-algorithms {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.no-algorithms i {
  margin-bottom: 1rem;
  color: #d1d5db;
}

.algorithms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.highlight-focus {
  box-shadow: 0 8px 20px rgba(251,191,36,0.25);
  border-color: #FBBF24 !important;
  transform: translateY(-4px);
  transition: all 0.25s ease;
}

.algorithm-card {
  border: 1px solid rgba(255,255,255,0.04);
  border-radius: 0.5rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  color: var(--text-light);
  box-shadow: var(--shadow-soft);
}

.algorithm-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 50px rgba(2,6,23,0.6);
  border-color: var(--accent-color);
}

.algorithm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.algorithm-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: url('/assets/alg1.jpg') center/cover no-repeat;
  display: inline-block;
  flex-shrink: 0;
}

.algorithm-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
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
  font-size: 0.75rem;
  color: #6b7280;
}

.algorithm-content h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-dark) !important;
  margin-bottom: 0.5rem;
}

.algorithm-content p {
  color: var(--text-muted);
  margin-bottom: 1rem;
  line-height: 1.6;
}

.algorithm-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.tag {
  background: rgba(255,255,255,0.03);
  color: var(--text-muted);
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
}

.algorithm-actions {
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .algorithms-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .page-header {
    text-align: center;
    margin-bottom: 2rem;
    padding-top: calc(var(--nav-height) + 1rem); /* 避免导航栏遮挡 */
  }

  .page-header h1 {
    font-size: 2rem;
    margin-bottom: 0.75rem;
  }

  .page-header p {
    font-size: 1rem;
  }

  .algorithms-controls {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
    padding: 1rem;
  }

  .search-box {
    max-width: none;
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
    justify-content: center;
    flex-wrap: wrap;
  }

  .filter-buttons select {
    padding: 0.625rem 0.75rem;
    font-size: 0.85rem;
    min-width: 120px;
  }

  .algorithms-container {
    padding: 1.5rem 0;
  }

  .algorithms-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .algorithm-card {
    padding: 1.25rem;
    margin-bottom: 0.5rem;
  }

  .algorithm-header {
    margin-bottom: 0.75rem;
  }

  .algorithm-icon {
    width: 32px;
    height: 32px;
  }

  .algorithm-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .algorithm-content h3 {
    font-size: 1rem;
  }

  .algorithm-content p {
    font-size: 0.85rem;
    margin-bottom: 0.75rem;
  }

  .algorithm-tags {
    gap: 0.375rem;
    margin-bottom: 0.75rem;
  }

  .tag {
    font-size: 0.7rem;
    padding: 0.2rem 0.4rem;
  }

  .algorithm-actions {
    text-align: center;
  }

  .btn.btn-primary {
    width: 100%;
    padding: 0.625rem 1rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 576px) {
  .algorithms-page {
    padding: 1.5rem 0;
  }

  .page-header {
    margin-bottom: 1.5rem;
  }

  .page-header h1 {
    font-size: 1.75rem;
  }

  .algorithms-controls {
    padding: 0.75rem;
  }

  .algorithms-container {
    padding: 1rem 0;
  }

  .algorithm-card {
    padding: 1rem;
  }

  .algorithm-content h3 {
    font-size: 0.95rem;
  }

  .algorithm-content p {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .algorithms-page {
    padding: 1rem 0;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .page-header p {
    font-size: 0.9rem;
  }

  .algorithms-controls {
    padding: 0.5rem;
  }

  .search-input {
    padding: 0.5rem 0.75rem 0.5rem 2.25rem;
    font-size: 0.85rem;
  }

  .filter-buttons select {
    padding: 0.5rem 0.625rem;
    font-size: 0.8rem;
    min-width: 100px;
  }

  .algorithm-card {
    padding: 0.875rem;
  }

  .algorithm-content h3 {
    font-size: 0.9rem;
  }

  .algorithm-content p {
    font-size: 0.75rem;
  }

  .tag {
    font-size: 0.65rem;
    padding: 0.15rem 0.35rem;
  }
}
</style>
