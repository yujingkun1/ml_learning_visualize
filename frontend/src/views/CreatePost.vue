<template>
  <div class="create-post-page">
    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <h1>Create New Post</h1>
          <p>Share your machine learning insights with the community</p>
        </div>
        <div class="header-actions">
          <router-link to="/posts" class="btn btn-outline">
            <i class="fas fa-arrow-left"></i>
            Back to Community
          </router-link>
        </div>
      </div>

      <!-- 创建表单 -->
      <div class="create-form-container">
        <form @submit.prevent="createPost" class="create-form">
          <!-- 标题输入 -->
          <div class="form-section">
            <div class="form-group">
              <label for="title" class="form-label">
                <i class="fas fa-heading"></i>
                Post Title *
              </label>
              <input
                id="title"
                type="text"
                v-model="newPost.title"
                required
                placeholder="Enter an engaging title for your post"
                class="form-input title-input"
                maxlength="200"
              />
              <div class="char-count">{{ newPost.title.length }}/200</div>
            </div>
          </div>

          <!-- 内容输入 -->
          <div class="form-section">
            <div class="form-group">
              <label for="content" class="form-label">
                <i class="fas fa-edit"></i>
                Content *
              </label>
              <textarea
                id="content"
                v-model="newPost.content"
                required
                placeholder="Share your thoughts, experiences, or questions about machine learning..."
                class="form-textarea content-textarea"
                rows="12"
              ></textarea>
              <div class="char-count">{{ newPost.content.length }}/10000</div>
            </div>
          </div>

          <!-- 标签管理 -->
          <div class="form-section">
            <div class="form-group">
              <label class="form-label">
                <i class="fas fa-tags"></i>
                Tags
                <span class="label-hint">({{ selectedTags.length }}/5 tags selected)</span>
              </label>

              <!-- 预设标签区域 -->
              <div class="preset-tags-section">
                <h4>Popular Tags</h4>
                <p class="section-description">Choose from commonly used tags in the community</p>
                <div class="preset-tags-grid">
                  <button
                    v-for="tag in presetTags"
                    :key="tag"
                    type="button"
                    class="tag-button"
                    :class="{ selected: selectedTags.includes(tag) }"
                    @click="toggleTag(tag)"
                  >
                    {{ tag }}
                    <i v-if="selectedTags.includes(tag)" class="fas fa-check"></i>
                  </button>
                </div>
              </div>

              <!-- 自定义标签区域 -->
              <div class="custom-tags-section">
                <h4>Add Custom Tags</h4>
                <p class="section-description">Create your own tags to better categorize your post</p>
                <div class="custom-tag-input-group">
                  <label class="sr-only" for="custom-tag-input">Add custom tag</label>
                  <input
                    id="custom-tag-input"
                    type="text"
                    aria-label="Add custom tag"
                    v-model="customTagInput"
                    @keyup="handleCustomTagKeyup"
                    placeholder="Enter custom tag (press Enter or comma to add)"
                    class="custom-tag-input"
                    maxlength="30"
                  />
                  <button
                    type="button"
                    @click="addCustomTag"
                    class="add-tag-btn"
                    :disabled="!customTagInput.trim()"
                  >
                    <i class="fas fa-plus"></i>
                    Add Tag
                  </button>
                </div>
              </div>

              <!-- 已选标签展示 -->
              <div v-if="selectedTags.length > 0" class="selected-tags-section">
                <h4>Selected Tags</h4>
                <div class="selected-tags-list">
                  <span
                    v-for="tag in selectedTags"
                    :key="tag"
                    class="selected-tag-chip"
                  >
                    {{ tag }}
                    <button
                      type="button"
                      @click="removeTag(tag)"
                      class="remove-tag-btn"
                      title="Remove tag"
                    >
                      <i class="fas fa-times"></i>
                    </button>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 发布操作 -->
          <div class="form-actions">
            <button type="submit" class="btn btn-primary publish-btn" :disabled="isSubmitting">
              <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-paper-plane"></i>
              {{ isSubmitting ? 'Publishing...' : 'Publish Post' }}
            </button>
            <router-link to="/posts" class="btn btn-outline cancel-btn">
              <i class="fas fa-times"></i>
              Cancel
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 表单数据
const newPost = ref({
  title: '',
  content: '',
  tags: []
})

// 标签管理
const presetTags = ref([
  // 核心算法
  'neural-networks', 'deep-learning', 'machine-learning', 'supervised-learning',
  'unsupervised-learning', 'reinforcement-learning',

  // 计算机视觉
  'computer-vision', 'cnn', 'image-classification', 'object-detection',
  'image-processing', 'opencv',

  // 自然语言处理
  'nlp', 'transformers', 'large-language-models', 'text-mining',
  'sentiment-analysis', 'bert',

  // 传统算法
  'regression', 'classification', 'clustering', 'dimensionality-reduction',
  'decision-trees', 'random-forest', 'gradient-descent',

  // 深度学习专项
  'convolutional-networks', 'recurrent-networks', 'attention-mechanism',
  'generative-adversarial-networks', 'autoencoders',

  // 数据科学
  'data-science', 'statistics', 'probability', 'feature-engineering',
  'data-visualization', 'pandas', 'numpy',

  // 工具和技术
  'python', 'tensorflow', 'pytorch', 'scikit-learn', 'jupyter',
  'data-analysis', 'model-deployment',

  // 学习相关
  'tutorials', 'beginner', 'intermediate', 'advanced', 'best-practices',
  'tips-and-tricks', 'career-advice'
])

const selectedTags = ref([])
const customTagInput = ref('')
const isSubmitting = ref(false)

// 标签操作函数
const toggleTag = (tag) => {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    if (selectedTags.value.length < 5) {
      selectedTags.value.push(tag)
    } else {
      alert('You can select up to 5 tags only')
    }
  }
  updatePostTags()
}

const addCustomTag = () => {
  const tag = customTagInput.value.trim().toLowerCase()
  if (!tag) return

  // 检查是否已存在
  if (selectedTags.value.includes(tag)) {
    alert('This tag is already selected')
    return
  }

  // 检查标签长度
  if (tag.length < 2) {
    alert('Tag must be at least 2 characters long')
    return
  }

  if (tag.length > 30) {
    alert('Tag must be no more than 30 characters long')
    return
  }

  // 检查是否达到最大标签数量
  if (selectedTags.value.length >= 5) {
    alert('You can select up to 5 tags only')
    return
  }

  selectedTags.value.push(tag)
  customTagInput.value = ''
  updatePostTags()
}

const handleCustomTagKeyup = (event) => {
  if (event.key === 'Enter' || event.key === ',') {
    event.preventDefault()
    addCustomTag()
  }
}

const removeTag = (tag) => {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
    updatePostTags()
  }
}

const updatePostTags = () => {
  newPost.value.tags = [...selectedTags.value]
}

// 发布帖子
const createPost = async () => {
  // 暂时移除认证检查用于测试
  // if (!userStore.isLoggedIn) {
  //   alert('Please login to create a post')
  //   router.push('/login')
  //   return
  // }

  if (!newPost.value.title.trim()) {
    alert('Please enter a title')
    return
  }

  if (!newPost.value.content.trim()) {
    alert('Please enter content')
    return
  }

  if (newPost.value.title.length > 200) {
    alert('Title must be no more than 200 characters')
    return
  }

  if (newPost.value.content.length > 10000) {
    alert('Content must be no more than 10,000 characters')
    return
  }

  isSubmitting.value = true

  try {
    const response = await axios.post('/api/posts', newPost.value)
    console.log('Post created successfully:', response.data)
    console.log('Post ID:', response.data.post.id)

    // 重定向到新创建的帖子
    const postId = response.data.post.id
    console.log('Redirecting to:', `/posts/${postId}`)
    try {
      await router.push(`/posts/${postId}`)
      console.log('Router push completed successfully')
      // 使用nextTick确保DOM更新
      await nextTick()
    } catch (error) {
      console.error('Router push failed:', error)
      // 如果路由跳转失败，使用window.location强制跳转
      window.location.href = `/posts/${postId}`
    }
  } catch (error) {
    console.error('Failed to create post:', error)
    if (error.response?.data?.message) {
      alert(`Failed to create post: ${error.response.data.message}`)
    } else {
      alert('Failed to create post. Please try again.')
    }
  } finally {
    isSubmitting.value = false
  }
}

// 页面加载时的初始化
onMounted(() => {
  // 暂时移除认证检查用于测试
  // if (!userStore.isLoggedIn) {
  //   router.push('/login')
  // }
})
</script>

<style scoped>
.create-post-page {
  padding: 2rem 0;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.header-content h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.header-content p {
  color: #64748b;
  font-size: 1.1rem;
}

.header-actions {
  flex-shrink: 0;
}

.create-form-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  padding: 3rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.form-section {
  margin-bottom: 2.5rem;
}

.form-section:last-child {
  margin-bottom: 0;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.label-hint {
  font-size: 0.9rem;
  font-weight: 400;
  color: #6b7280;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 1rem 1.25rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-family: inherit;
  background: #ffffff;
  transition: all 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.title-input {
  font-size: 1.25rem;
  font-weight: 600;
}

.content-textarea {
  resize: vertical;
  min-height: 300px;
  line-height: 1.6;
}

.char-count {
  text-align: right;
  font-size: 0.875rem;
  color: #9ca3af;
  margin-top: 0.5rem;
}

/* 标签管理样式 */
.preset-tags-section,
.custom-tags-section,
.selected-tags-section {
  margin-bottom: 2rem;
}

.preset-tags-section h4,
.custom-tags-section h4,
.selected-tags-section h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.section-description {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

/* Accessibility helper: visually hidden text for screen readers */
.sr-only {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0 0 0 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

.preset-tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem;
}

.tag-button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border: 2px solid #e5e7eb;
  background: #ffffff;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.tag-button:hover {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #1d4ed8;
}

.tag-button.selected {
  border-color: #3b82f6;
  background: #3b82f6;
  color: white;
}

.custom-tag-input-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.custom-tag-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  background: #ffffff;
}

.custom-tag-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.add-tag-btn {
  padding: 0.75rem 1.25rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.add-tag-btn:hover:not(:disabled) {
  background: #2563eb;
}

.add-tag-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.selected-tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.selected-tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid #bfdbfe;
}

.remove-tag-btn {
  background: none;
  border: none;
  color: #1d4ed8;
  cursor: pointer;
  padding: 0;
  font-size: 0.75rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1rem;
  height: 1rem;
}

.remove-tag-btn:hover {
  color: #1e40af;
}

/* 表单操作 */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.publish-btn,
.cancel-btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 0.75rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 160px;
  justify-content: center;
}

.publish-btn {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
}

.publish-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
}

.publish-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.cancel-btn {
  background: white;
  color: #6b7280;
  border: 2px solid #e5e7eb;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.cancel-btn:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .create-post-page {
    padding: 1rem 0;
  }

  .container {
    padding: 0 0.5rem;
  }

  .page-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
    padding-top: calc(var(--nav-height) + 1rem); /* 避免导航栏遮挡 */
    margin-bottom: 2rem;
  }

  .header-content h1 {
    font-size: 2rem;
  }

  .create-form-container {
    padding: 2rem 1.5rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .publish-btn,
  .cancel-btn {
    width: 100%;
  }

  .preset-tags-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }

  .custom-tag-input-group {
    flex-direction: column;
    align-items: stretch;
  }

  .add-tag-btn {
    align-self: flex-start;
  }
}
</style>
