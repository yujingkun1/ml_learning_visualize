<template>
  <div class="admin-page">
    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h1 style="color: #000;">Admin Panel</h1>
        <p>Manage content and users</p>
      </div>

      <!-- 导航标签页 -->
      <div class="admin-tabs">
        <button
          v-for="tab in adminTabs"
          :key="tab.id"
          class="tab"
          :class="{ active: activeTab === tab.id }"
          @click="changeTab(tab.id)"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- System Logs -->
      <div v-if="activeTab === 'logs'" class="admin-content">
        <div class="content-header">
          <h2>System Logs</h2>
        <label class="sr-only" for="log-action-filter">Filter action</label>
          <div class="filters">
            <select id="log-action-filter" v-model="logFilter.action" @change="fetchLogs">
              <option value="">All Actions</option>
              <option value="login">Login</option>
              <option value="register">Register</option>
              <option value="create_post">Create Post</option>
              <option value="like_post">Like Post</option>
              <option value="delete_post">Delete Post</option>
            </select>
            <label class="sr-only" for="log-date-filter">Filter date</label>
            <input
              id="log-date-filter"
              type="date"
              v-model="logFilter.date"
              @change="fetchLogs"
            >
          </div>
        </div>

        <div class="logs-table">
          <div class="table-header">
            <div>Time</div>
            <div>User</div>
            <div>Action</div>
            <div>Resource</div>
            <div>Details</div>
          </div>
          <div
            v-for="log in logs"
            :key="log.id"
            class="table-row"
          >
            <div>{{ formatDateTime(log.created_at) }}</div>
            <div>{{ log.user_id ? `User ${log.user_id}` : 'System' }}</div>
            <div>{{ getActionText(log.action) }}</div>
            <div>{{ getResourceText(log) }}</div>
            <div>{{ log.details || '-' }}</div>
          </div>
        </div>

        <div v-if="logs.length === 0" class="no-data">
          <p>No logs found</p>
        </div>

        <!-- 日志分页 -->
        <div v-if="totalLogsPages > 1" class="pagination">
          <button
            class="page-btn"
            :disabled="currentLogsPage === 1"
            @click="goToLogsPage(currentLogsPage - 1)"
            aria-label="Previous logs page"
          >
            <i class="fas fa-chevron-left"></i>
          </button>

          <span
            v-for="page in visibleLogsPages"
            :key="page"
            :class="[
              page === '...' ? 'page-ellipsis' : 'page-number',
              { active: page === currentLogsPage }
            ]"
            @click="page !== '...' && goToLogsPage(page)"
            v-bind="page === '...' ? { 'aria-hidden': 'true', tabindex: '-1' } : { role: 'button', tabindex: '0', 'aria-current': page === currentLogsPage ? 'page' : null }"
            @keyup.enter="page !== '...' && goToLogsPage(page)"
          >
            {{ page }}
          </span>

          <button
            class="page-btn"
            :disabled="currentLogsPage === totalLogsPages"
            @click="goToLogsPage(currentLogsPage + 1)"
            aria-label="Next logs page"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>

      <!-- Posts Management -->
      <div v-if="activeTab === 'posts'" class="admin-content">
        <div class="content-header">
          <h2>Posts Management</h2>
          <div class="search-box">
            <label class="sr-only" for="post-search">Search posts</label>
            <input
              id="post-search"
              type="text"
              v-model="postSearch"
              placeholder="Search posts..."
              @input="debouncedSearchPosts"
            >
          </div>
        </div>

        <div class="posts-list">
          <div
            v-for="post in adminPosts"
            :key="post.id"
            class="post-item"
          >
            <div class="post-info">
              <h3>{{ post.title }}</h3>
              <p>Author: {{ post.author?.username }} | Posted: {{ formatDate(post.created_at) }}</p>
              <div class="post-stats">
                <span>Views: {{ post.view_count }}</span>
                <span>Likes: {{ post.like_count }}</span>
                <span>Comments: {{ post.comment_count }}</span>
              </div>
            </div>
            <div class="post-actions">
              <button
                v-if="!post.is_featured"
                class="btn btn-secondary"
                @click="toggleFeatured(post)"
              >
                Feature
              </button>
              <button
                class="btn btn-danger"
                @click="deletePost(post.id)"
              >
                Delete
              </button>
            </div>
          </div>
        </div>

        <div v-if="adminPosts.length === 0" class="no-data">
          <p>No posts found</p>
        </div>

        <!-- 帖子分页 -->
        <div v-if="totalPostsPages > 1" class="pagination">
          <button
            class="page-btn"
            :disabled="currentPostsPage === 1"
            @click="goToPostsPage(currentPostsPage - 1)"
            aria-label="Previous posts page"
          >
            <i class="fas fa-chevron-left"></i>
          </button>

          <span
            v-for="page in visiblePostsPages"
            :key="page"
            :class="[
              page === '...' ? 'page-ellipsis' : 'page-number',
              { active: page === currentPostsPage }
            ]"
            @click="page !== '...' && goToPostsPage(page)"
            v-bind="page === '...' ? { 'aria-hidden': 'true', tabindex: '-1' } : { role: 'button', tabindex: '0', 'aria-current': page === currentPostsPage ? 'page' : null }"
            @keyup.enter="page !== '...' && goToPostsPage(page)"
          >
            {{ page }}
          </span>

          <button
            class="page-btn"
            :disabled="currentPostsPage === totalPostsPages"
            @click="goToPostsPage(currentPostsPage + 1)"
            aria-label="Next posts page"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>

      <!-- Users Management -->
      <div v-if="activeTab === 'users'" class="admin-content">
        <div class="content-header">
          <h2>Users Management</h2>
          <div class="search-box">
            <label class="sr-only" for="user-search">Search users</label>
            <input
              id="user-search"
              type="text"
              v-model="userSearch"
              placeholder="Search users..."
              @input="debouncedSearchUsers"
            >
          </div>
        </div>

        <div class="users-list">
          <div
            v-for="user in adminUsers"
            :key="user.id"
            class="user-item"
          >
            <div class="user-info">
              <h3>{{ user.username }}</h3>
              <p>{{ user.email }}</p>
              <span class="user-role" :class="user.role">{{ getRoleText(user.role) }}</span>
            </div>
            <div class="user-stats">
              <span>Joined: {{ formatDate(user.created_at) }}</span>
            </div>
            <div class="user-actions">
              <button
                v-if="user.role !== 'admin'"
                class="btn btn-secondary"
                @click="changeUserRole(user)"
              >
                Make Admin
              </button>
              <button
                class="btn btn-danger"
                @click="deleteUser(user.id)"
              >
                Delete User
              </button>
            </div>
          </div>
        </div>

        <div v-if="adminUsers.length === 0" class="no-data">
          <p>No users found</p>
        </div>

        <!-- 用户分页 -->
        <div v-if="totalUsersPages > 1" class="pagination">
          <button
            class="page-btn"
            :disabled="currentUsersPage === 1"
            @click="goToUsersPage(currentUsersPage - 1)"
            aria-label="Previous users page"
          >
            <i class="fas fa-chevron-left"></i>
          </button>

          <span
            v-for="page in visibleUsersPages"
            :key="page"
            :class="[
              page === '...' ? 'page-ellipsis' : 'page-number',
              { active: page === currentUsersPage }
            ]"
            @click="page !== '...' && goToUsersPage(page)"
            v-bind="page === '...' ? { 'aria-hidden': 'true', tabindex: '-1' } : { role: 'button', tabindex: '0', 'aria-current': page === currentUsersPage ? 'page' : null }"
            @keyup.enter="page !== '...' && goToUsersPage(page)"
          >
            {{ page }}
          </span>

          <button
            class="page-btn"
            :disabled="currentUsersPage === totalUsersPages"
            @click="goToUsersPage(currentUsersPage + 1)"
            aria-label="Next users page"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>

      <!-- Statistics -->
      <div v-if="activeTab === 'stats'" class="admin-content">
        <div class="content-header">
          <h2>Statistics Overview</h2>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-users"></i>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalUsers }}</h3>
              <p>Total Users</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-file-alt"></i>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalPosts }}</h3>
              <p>Total Posts</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-comments"></i>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalComments }}</h3>
              <p>Total Comments</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-brain"></i>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalAlgorithms }}</h3>
              <p>Total Algorithms</p>
            </div>
          </div>
        </div>

        <div class="recent-activity">
          <h3>Recent Activity</h3>
          <div class="activity-list">
            <div
              v-for="activity in recentActivities"
              :key="activity.id"
              class="activity-item"
            >
              <div class="activity-icon">
                <i :class="getActivityIcon(activity.action)"></i>
              </div>
              <div class="activity-info">
                <p>{{ getActivityText(activity) }}</p>
                <span>{{ formatDateTime(activity.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Algorithms Management -->
      <div v-if="activeTab === 'algorithms'" class="admin-content">
        <div class="content-header">
          <h2>Algorithms Management</h2>
          <button class="btn btn-primary" @click="showAddAlgorithmModal = true">
            <i class="fas fa-plus"></i>
            Add Algorithm
          </button>
        </div>

        <div class="algorithms-table">
          <div class="table-header">
            <div>ID</div>
            <div>Name</div>
            <div>Category</div>
            <div>Difficulty</div>
            <div>Created</div>
            <div>Actions</div>
          </div>

          <div
            v-for="algorithm in algorithms"
            :key="algorithm.id"
            class="table-row"
          >
            <div>{{ algorithm.id }}</div>
            <div>{{ algorithm.name }}</div>
            <div>{{ algorithm.category?.name || 'Uncategorized' }}</div>
            <div>
              <span :class="`difficulty-${algorithm.difficulty}`">
                {{ algorithm.difficulty }}
              </span>
            </div>
            <div>{{ formatDateTime(algorithm.created_at) }}</div>
            <div class="actions">
              <button class="btn btn-sm btn-secondary" @click="editAlgorithm(algorithm)">
                <i class="fas fa-edit"></i>
                Edit
              </button>
              <button class="btn btn-sm btn-danger" @click="deleteAlgorithm(algorithm.id)">
                <i class="fas fa-trash"></i>
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Data Analytics -->
      <div v-if="activeTab === 'analytics'" class="admin-content">
        <div class="content-header">
          <h2>Data Analytics</h2>
        </div>

        <!-- User Activity Rankings -->
        <div class="analytics-section">
          <h3>User Activity Rankings</h3>
          <div v-if="userActivityRankings.length === 0" class="no-data">
            <p>No user activity data available</p>
          </div>
          <div v-else class="rankings-table">
            <div class="table-header">
              <div>Rank</div>
              <div>Username</div>
              <div>Posts</div>
              <div>Comments</div>
              <div>Likes Received</div>
              <div>Activity Score</div>
            </div>
            <div
              v-for="(user, index) in userActivityRankings"
              :key="user.id"
              class="table-row"
            >
              <div>{{ index + 1 }}</div>
              <div>{{ user.username }}</div>
              <div>{{ user.posts_count }}</div>
              <div>{{ user.comments_count }}</div>
              <div>{{ user.likes_received }}</div>
              <div>{{ user.activity_score }}</div>
            </div>
          </div>
        </div>

        <!-- Post Popularity Rankings -->
        <div class="analytics-section">
          <h3>Post Popularity Rankings</h3>
          <div v-if="postPopularityRankings.length === 0" class="no-data">
            <p>No post popularity data available</p>
          </div>
          <div v-else class="rankings-table">
            <div class="table-header">
              <div>Rank</div>
              <div>Title</div>
              <div>Author</div>
              <div>Views</div>
              <div>Likes</div>
              <div>Comments</div>
              <div>Popularity Score</div>
            </div>
            <div
              v-for="(post, index) in postPopularityRankings"
              :key="post.id"
              class="table-row"
            >
              <div>{{ index + 1 }}</div>
              <div>{{ post.title }}</div>
              <div>{{ post.author?.username }}</div>
              <div>{{ post.view_count }}</div>
              <div>{{ post.like_count }}</div>
              <div>{{ post.comment_count }}</div>
              <div>{{ post.popularity_score }}</div>
            </div>
          </div>
        </div>

        <!-- System Usage Statistics -->
        <div class="analytics-section">
          <h3>System Usage Statistics</h3>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-clock"></i>
              </div>
              <div class="stat-info">
                <h3>{{ systemStats.avgSessionTime }}</h3>
                <p>Avg Session Time</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-mouse-pointer"></i>
              </div>
              <div class="stat-info">
                <h3>{{ systemStats.avgPageViews }}</h3>
                <p>Avg Page Views</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-chart-line"></i>
              </div>
              <div class="stat-info">
                <h3>{{ systemStats.growthRate }}%</h3>
                <p>User Growth Rate</p>
              </div>
            </div>
          </div>
          <div class="analytics-actions">
            <button class="btn btn-secondary" @click="fetchAnalyticsData">
              <i class="fas fa-refresh"></i>
              Refresh Data
            </button>
          </div>
        </div>
      </div>

      <!-- Database Management -->
      <div v-if="activeTab === 'database'" class="admin-content">
        <div class="content-header">
          <h2>Database Management</h2>
        </div>

        <div class="db-management-section">
          <h3>User Data Management</h3>
          <p class="section-description">Manage user accounts and data</p>
          <div class="management-actions">
            <div class="action-item">
              <button class="btn btn-warning" @click="cleanupInactiveUsers" :disabled="isProcessing">
                <i class="fas fa-broom"></i>
                Cleanup Inactive Users
              </button>
              <p class="action-description">Remove users who haven't been active for 90+ days and have no posts/comments</p>
            </div>
            <div class="action-item">
              <button class="btn btn-info" @click="exportUserData" :disabled="isProcessing">
                <i class="fas fa-download"></i>
                Export User Data
              </button>
              <p class="action-description">Download all user data as JSON file for backup or analysis</p>
            </div>
          </div>
        </div>

        <div class="db-management-section">
          <h3>Content Data Management</h3>
          <p class="section-description">Manage posts, comments and other content</p>
          <div class="management-actions">
            <div class="action-item">
              <button class="btn btn-warning" @click="cleanupOldPosts" :disabled="isProcessing">
                <i class="fas fa-trash-alt"></i>
                Cleanup Old Posts
              </button>
              <p class="action-description">Remove posts older than 1 year with low engagement (views < 5, likes < 2, no comments)</p>
            </div>
            <div class="action-item">
              <button class="btn btn-info" @click="exportContentData" :disabled="isProcessing">
                <i class="fas fa-download"></i>
                Export Content Data
              </button>
              <p class="action-description">Download all posts and comments data as JSON file</p>
            </div>
          </div>
        </div>

        <div class="db-management-section">
          <h3>System Maintenance</h3>
          <p class="section-description">Database maintenance and optimization</p>
          <div class="management-actions">
            <div class="action-item">
              <button class="btn btn-secondary" @click="backupDatabase" :disabled="isProcessing">
                <i class="fas fa-save"></i>
                Backup Database
              </button>
              <p class="action-description">Create a backup copy of the current database</p>
            </div>
            <div class="action-item">
              <button class="btn btn-danger" @click="optimizeDatabase" :disabled="isProcessing">
                <i class="fas fa-wrench"></i>
                Optimize Database
              </button>
              <p class="action-description">Run database optimization to improve performance</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 添加/编辑算法模态框 -->
  <div v-if="showAddAlgorithmModal || showEditAlgorithmModal" class="modal-overlay" @click="closeModals">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ showEditAlgorithmModal ? '编辑算法' : '添加算法' }}</h3>
        <button class="modal-close" @click="closeModals">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <form @submit.prevent="submitAlgorithm" class="algorithm-form">
        <div class="form-group">
          <label>算法名称 *</label>
          <input
            v-model="algorithmForm.name"
            type="text"
            required
            placeholder="输入算法名称"
          >
        </div>

        <div class="form-group">
          <label>中文名称</label>
          <input
            v-model="algorithmForm.chinese_name"
            type="text"
            placeholder="输入中文名称（可选）"
          >
        </div>

        <div class="form-group">
          <label>描述 *</label>
          <textarea
            v-model="algorithmForm.description"
            required
            placeholder="输入算法描述"
            rows="3"
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>分类 *</label>
            <select v-model="algorithmForm.category_id" required>
              <option value="">选择分类</option>
              <option
                v-for="category in categories"
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>难度 *</label>
            <select v-model="algorithmForm.difficulty" required>
              <option value="">选择难度</option>
              <option value="beginner">入门</option>
              <option value="intermediate">中级</option>
              <option value="advanced">高级</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>标签</label>
          <input
            v-model="algorithmForm.tags"
            type="text"
            placeholder="用逗号分隔的标签（可选）"
          >
        </div>

        <div class="form-group">
          <label>论文链接</label>
          <input
            v-model="algorithmForm.paper_url"
            type="url"
            placeholder="论文链接（可选）"
          >
        </div>

        <div class="form-group">
          <label>代码链接</label>
          <input
            v-model="algorithmForm.code_url"
            type="url"
            placeholder="代码链接（可选）"
          >
        </div>

        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="closeModals">取消</button>
          <button type="submit" class="btn btn-primary">
            {{ showEditAlgorithmModal ? '更新' : '添加' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const activeTab = ref('stats')
const logs = ref([])
const adminPosts = ref([])
const adminUsers = ref([])
const stats = ref({
  totalUsers: 0,
  totalPosts: 0,
  totalComments: 0,
  totalAlgorithms: 0
})
const recentActivities = ref([])

const logFilter = ref({
  action: '',
  date: ''
})

const postSearch = ref('')
const userSearch = ref('')

// 分页相关
const currentUsersPage = ref(1)
const totalUsersPages = ref(1)
const currentPostsPage = ref(1)
const totalPostsPages = ref(1)
const currentLogsPage = ref(1)
const totalLogsPages = ref(1)

// 算法管理相关
const algorithms = ref([])
const categories = ref([])
const showAddAlgorithmModal = ref(false)
const showEditAlgorithmModal = ref(false)
const editingAlgorithmId = ref<number | null>(null)

// 数据分析相关
const userActivityRankings = ref([])
const postPopularityRankings = ref([])
const systemStats = ref({
  avgSessionTime: '0分钟',
  avgPageViews: '0页',
  growthRate: '0'
})

// 数据库管理相关
const showCleanupModal = ref(false)
const isProcessing = ref(false)

const algorithmForm = ref({
  name: '',
  chinese_name: '',
  description: '',
  category_id: '',
  difficulty: '',
  tags: '',
  paper_url: '',
  code_url: ''
})

const adminTabs = [
  { id: 'stats', name: 'Overview' },
  { id: 'algorithms', name: 'Algorithms' },
  { id: 'posts', name: 'Posts' },
  { id: 'users', name: 'Users' },
  { id: 'logs', name: 'Logs' },
  { id: 'analytics', name: 'Analytics' },
  { id: 'database', name: 'Database' }
]

// 防抖搜索
let postSearchTimeout: number | null = null
let userSearchTimeout: number | null = null

// 分页计算函数
const visibleUsersPages = computed(() => {
  const pages = []
  const total = totalUsersPages.value

  if (total <= 7) {
    // 少于等于7页，显示所有页面
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // 多于7页，使用专业格式：1 2 3 ... 最后页

    // 始终显示前3页
    pages.push(1, 2, 3)

    // 如果当前页面在中间区域，显示当前页面及其前后页面
    if (currentUsersPage.value > 3 && currentUsersPage.value < total - 2) {
      if (currentUsersPage.value > 4) {
        pages.push('...')
      }
      const start = Math.max(4, currentUsersPage.value - 1)
      const end = Math.min(currentUsersPage.value + 1, total - 3)
      for (let i = start; i <= end; i++) {
        if (!pages.includes(i)) {
          pages.push(i)
        }
      }
      if (currentUsersPage.value < total - 3) {
        pages.push('...')
      }
    } else if (currentUsersPage.value >= total - 2) {
      // 当前页面在最后区域
      pages.push('...')
    }

    // 始终显示最后3页（如果还没显示）
    if (total > 3) {
      if (!pages.includes(total - 2)) pages.push('...')
      if (!pages.includes(total - 2)) pages.push(total - 2)
      if (!pages.includes(total - 1)) pages.push(total - 1)
      if (!pages.includes(total)) pages.push(total)
    }
  }

  return pages
})

const visiblePostsPages = computed(() => {
  const pages = []
  const total = totalPostsPages.value

  if (total <= 7) {
    // 少于等于7页，显示所有页面
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // 多于7页，使用专业格式：1 2 3 ... 最后页

    // 始终显示前3页
    pages.push(1, 2, 3)

    // 如果当前页面在中间区域，显示当前页面及其前后页面
    if (currentPostsPage.value > 3 && currentPostsPage.value < total - 2) {
      if (currentPostsPage.value > 4) {
        pages.push('...')
      }
      const start = Math.max(4, currentPostsPage.value - 1)
      const end = Math.min(currentPostsPage.value + 1, total - 3)
      for (let i = start; i <= end; i++) {
        if (!pages.includes(i)) {
          pages.push(i)
        }
      }
      if (currentPostsPage.value < total - 3) {
        pages.push('...')
      }
    } else if (currentPostsPage.value >= total - 2) {
      // 当前页面在最后区域
      pages.push('...')
    }

    // 始终显示最后3页（如果还没显示）
    if (total > 3) {
      if (!pages.includes(total - 2)) pages.push('...')
      if (!pages.includes(total - 2)) pages.push(total - 2)
      if (!pages.includes(total - 1)) pages.push(total - 1)
      if (!pages.includes(total)) pages.push(total)
    }
  }

  return pages
})

const visibleLogsPages = computed(() => {
  const pages = []
  const total = totalLogsPages.value

  if (total <= 7) {
    // 少于等于7页，显示所有页面
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // 多于7页，使用专业格式：1 2 3 ... 最后页

    // 始终显示前3页
    pages.push(1, 2, 3)

    // 如果当前页面在中间区域，显示当前页面及其前后页面
    if (currentLogsPage.value > 3 && currentLogsPage.value < total - 2) {
      if (currentLogsPage.value > 4) {
        pages.push('...')
      }
      const start = Math.max(4, currentLogsPage.value - 1)
      const end = Math.min(currentLogsPage.value + 1, total - 3)
      for (let i = start; i <= end; i++) {
        if (!pages.includes(i)) {
          pages.push(i)
        }
      }
      if (currentLogsPage.value < total - 3) {
        pages.push('...')
      }
    } else if (currentLogsPage.value >= total - 2) {
      // 当前页面在最后区域
      pages.push('...')
    }

    // 始终显示最后3页（如果还没显示）
    if (total > 3) {
      if (!pages.includes(total - 2)) pages.push('...')
      if (!pages.includes(total - 2)) pages.push(total - 2)
      if (!pages.includes(total - 1)) pages.push(total - 1)
      if (!pages.includes(total)) pages.push(total)
    }
  }

  return pages
})

// 分页跳转函数
const goToUsersPage = (page: number) => {
  currentUsersPage.value = page
  fetchAdminUsers()
}

const goToPostsPage = (page: number) => {
  currentPostsPage.value = page
  fetchAdminPosts()
}

const goToLogsPage = (page: number) => {
  currentLogsPage.value = page
  fetchLogs()
}

const debouncedSearchPosts = () => {
  if (postSearchTimeout) clearTimeout(postSearchTimeout)
  postSearchTimeout = setTimeout(() => {
    currentPostsPage.value = 1
    fetchAdminPosts()
  }, 500)
}

const debouncedSearchUsers = () => {
  if (userSearchTimeout) clearTimeout(userSearchTimeout)
  userSearchTimeout = setTimeout(() => {
    currentUsersPage.value = 1
    fetchAdminUsers()
  }, 500)
}

const fetchStats = async () => {
  try {
    const response = await axios.get('/api/admin/stats')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const fetchLogs = async () => {
  try {
    const params = {
      page: currentLogsPage.value,
      per_page: 20
    }
    if (logFilter.value.action) params.action = logFilter.value.action
    if (logFilter.value.date) params.date = logFilter.value.date

    const response = await axios.get('/api/admin/logs', { params })
    logs.value = response.data.logs
    totalLogsPages.value = response.data.pages
  } catch (error) {
    console.error('Failed to fetch logs:', error)
  }
}

const fetchAdminPosts = async () => {
  try {
    const params = {
      page: currentPostsPage.value,
      per_page: 10,
      search: postSearch.value || undefined
    }

    const response = await axios.get('/api/admin/posts', { params })
    adminPosts.value = response.data.posts
    totalPostsPages.value = response.data.pages
  } catch (error) {
    console.error('Failed to fetch admin posts:', error)
  }
}

const fetchAdminUsers = async () => {
  try {
    const params = {
      page: currentUsersPage.value,
      per_page: 10,
      search: userSearch.value || undefined
    }

    const response = await axios.get('/api/admin/users', { params })
    adminUsers.value = response.data.users
    totalUsersPages.value = response.data.pages
  } catch (error) {
    console.error('Failed to fetch admin users:', error)
  }
}

const fetchRecentActivities = async () => {
  try {
    const response = await axios.get('/api/admin/logs?per_page=10')
    recentActivities.value = response.data.logs
  } catch (error) {
    console.error('Failed to fetch recent activities:', error)
  }
}

const toggleFeatured = async (post: any) => {
  try {
    await axios.put(`/api/admin/posts/${post.id}/featured`, {
      featured: !post.is_featured
    })
    post.is_featured = !post.is_featured
  } catch (error) {
    console.error('Failed to toggle featured:', error)
  }
}

const deletePost = async (postId: number) => {
  if (!confirm('确定要删除这个帖子吗？')) return

  try {
    await axios.delete(`/api/admin/posts/${postId}`)
    adminPosts.value = adminPosts.value.filter(p => p.id !== postId)
  } catch (error) {
    console.error('Failed to delete post:', error)
  }
}

const changeUserRole = async (user: any) => {
  try {
    await axios.put(`/api/admin/users/${user.id}/role`, {
      role: user.role === 'user' ? 'admin' : 'user'
    })
    user.role = user.role === 'user' ? 'admin' : 'user'
  } catch (error) {
    console.error('Failed to change user role:', error)
  }
}

const deleteUser = async (userId: number) => {
  if (!confirm('确定要删除这个用户吗？')) return

  try {
    await axios.delete(`/api/admin/users/${userId}`)
    adminUsers.value = adminUsers.value.filter(u => u.id !== userId)
  } catch (error) {
    console.error('Failed to delete user:', error)
  }
}

const getActionText = (action: string) => {
  const actions = {
    login: '登录',
    register: '注册',
    create_post: '发布帖子',
    like_post: '点赞',
    favorite_post: '收藏',
    delete_post: '删除帖子',
    delete_comment: '删除评论',
    update_knowledge: '更新知识'
  }
  return actions[action] || action
}

const getResourceText = (log: any) => {
  if (!log.resource_type || !log.resource_id) return '-'
  return `${log.resource_type} #${log.resource_id}`
}

const getRoleText = (role: string) => {
  const roles = {
    user: '普通用户',
    admin: '管理员'
  }
  return roles[role] || role
}

const getActivityIcon = (action: string) => {
  const icons = {
    login: 'fas fa-sign-in-alt',
    register: 'fas fa-user-plus',
    create_post: 'fas fa-edit',
    like_post: 'fas fa-heart',
    delete_post: 'fas fa-trash'
  }
  return icons[action] || 'fas fa-circle'
}

const getActivityText = (activity: any) => {
  const userText = activity.user_id ? `用户${activity.user_id}` : '系统'
  const actionText = getActionText(activity.action)
  return `${userText} ${actionText}`
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(async () => {
  console.log('Admin page mounted')

  // 先检查认证状态
  await userStore.checkAuth()

  console.log('userStore.isAdmin:', userStore.isAdmin)
  console.log('userStore.user:', userStore.user)
  console.log('localStorage.isAdmin:', localStorage.getItem('isAdmin'))

  if (!userStore.isAdmin) {
    alert('需要管理员权限')
    router.push('/')
    return
  }

  fetchStats()
  fetchRecentActivities()
})

// 算法管理相关函数
const fetchAlgorithms = async () => {
  try {
    const response = await axios.get('/api/algorithms?per_page=1000')
    algorithms.value = response.data.algorithms
  } catch (error) {
    console.error('Failed to fetch algorithms:', error)
  }
}

const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/categories')
    categories.value = response.data.categories
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

const editAlgorithm = (algorithm: any) => {
  editingAlgorithmId.value = algorithm.id
  algorithmForm.value = {
    name: algorithm.name,
    chinese_name: algorithm.chinese_name || '',
    description: algorithm.description,
    category_id: algorithm.category_id.toString(),
    difficulty: algorithm.difficulty,
    tags: algorithm.tags ? algorithm.tags.join(', ') : '',
    paper_url: algorithm.paper_url || '',
    code_url: algorithm.code_url || ''
  }
  showEditAlgorithmModal.value = true
}

const deleteAlgorithm = async (algorithmId: number) => {
  if (!confirm('确定要删除这个算法吗？此操作不可撤销。')) {
    return
  }

  try {
    await axios.delete(`/api/admin/algorithms/${algorithmId}`)
    await fetchAlgorithms()
    await fetchStats() // 更新统计数据
    alert('算法删除成功')
  } catch (error: any) {
    console.error('Failed to delete algorithm:', error)
    alert(error.response?.data?.message || '删除算法失败')
  }
}

const submitAlgorithm = async () => {
  try {
    const formData = {
      ...algorithmForm.value,
      category_id: parseInt(algorithmForm.value.category_id),
      tags: algorithmForm.value.tags ? algorithmForm.value.tags.split(',').map((tag: string) => tag.trim()).filter(Boolean) : []
    }

    if (showEditAlgorithmModal.value && editingAlgorithmId.value) {
      // 更新算法
      await axios.put(`/api/admin/algorithms/${editingAlgorithmId.value}`, formData)
      alert('算法更新成功')
    } else {
      // 创建算法
      await axios.post('/api/admin/algorithms', formData)
      alert('算法创建成功')
    }

    await fetchAlgorithms()
    await fetchStats() // 更新统计数据
    closeModals()
  } catch (error: any) {
    console.error('Failed to submit algorithm:', error)
    alert(error.response?.data?.message || '操作失败')
  }
}

const closeModals = () => {
  showAddAlgorithmModal.value = false
  showEditAlgorithmModal.value = false
  editingAlgorithmId.value = null
  algorithmForm.value = {
    name: '',
    chinese_name: '',
    description: '',
    category_id: '',
    difficulty: '',
    tags: '',
    paper_url: '',
    code_url: ''
  }
}

// 数据分析相关函数
const fetchAnalyticsData = async () => {
  try {
    console.log('Fetching analytics data...')

    // 获取用户活动排行榜
    const userRankingsResponse = await axios.get('/api/admin/analytics/user-activity')
    console.log('User rankings response:', userRankingsResponse.data)
    userActivityRankings.value = userRankingsResponse.data.rankings || []

    // 获取帖子热度排行榜
    const postRankingsResponse = await axios.get('/api/admin/analytics/post-popularity')
    console.log('Post rankings response:', postRankingsResponse.data)
    postPopularityRankings.value = postRankingsResponse.data.rankings || []

    // 获取系统统计
    const systemStatsResponse = await axios.get('/api/admin/analytics/system-stats')
    console.log('System stats response:', systemStatsResponse.data)
    systemStats.value = systemStatsResponse.data.stats || {
      avgSessionTime: '0 minutes',
      avgPageViews: '0 pages',
      growthRate: '0'
    }

    console.log('Analytics data loaded successfully')
  } catch (error) {
    console.error('Failed to fetch analytics data:', error)
    // 设置默认值以防止显示问题
    userActivityRankings.value = []
    postPopularityRankings.value = []
    systemStats.value = {
      avgSessionTime: 'N/A',
      avgPageViews: 'N/A',
      growthRate: '0'
    }
  }
}

const fetchDatabaseStats = async () => {
  // 这里可以获取数据库统计信息
  console.log('Fetching database stats...')
}

// 数据库管理相关函数
const cleanupInactiveUsers = async () => {
  if (!confirm('Are you sure you want to clean up inactive users?\n\nThis will permanently delete users who haven\'t been active for 90+ days and have no posts or comments.\n\nThis action cannot be undone!')) return

  isProcessing.value = true
  try {
    const response = await axios.post('/api/admin/database/cleanup-users')
    alert(`Cleanup completed! ${response.data.deleted_count} inactive users were removed.`)
  } catch (error) {
    console.error('Failed to cleanup users:', error)
    alert('Cleanup failed. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const exportUserData = async () => {
  if (!confirm('Export all user data to JSON file?')) return

  isProcessing.value = true
  try {
    const response = await axios.get('/api/admin/database/export-users', {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'users_export.json')
    document.body.appendChild(link)
    link.click()
    link.remove()
    alert('User data export completed!')
  } catch (error) {
    console.error('Failed to export user data:', error)
    alert('Export failed. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const cleanupOldPosts = async () => {
  if (!confirm('Are you sure you want to clean up old posts?\n\nThis will permanently delete posts older than 1 year with very low engagement (less than 5 views, 2 likes, and no comments).\n\nThis action cannot be undone!')) return

  isProcessing.value = true
  try {
    const response = await axios.post('/api/admin/database/cleanup-posts')
    alert(`Cleanup completed! ${response.data.deleted_count} old posts were removed.`)
  } catch (error) {
    console.error('Failed to cleanup posts:', error)
    alert('Cleanup failed. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const exportContentData = async () => {
  if (!confirm('Export all content data (posts and comments) to JSON file?')) return

  isProcessing.value = true
  try {
    const response = await axios.get('/api/admin/database/export-content', {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'content_export.json')
    document.body.appendChild(link)
    link.click()
    link.remove()
    alert('Content data export completed!')
  } catch (error) {
    console.error('Failed to export content data:', error)
    alert('Export failed. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const backupDatabase = async () => {
  if (!confirm('Create a backup of the current database?')) return

  isProcessing.value = true
  try {
    const response = await axios.post('/api/admin/database/backup')
    alert(`Database backup completed!\nBackup file: ${response.data.backup_file}`)
  } catch (error) {
    console.error('Failed to backup database:', error)
    alert('Backup failed. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const optimizeDatabase = async () => {
  if (!confirm('Run database optimization?\n\nThis will optimize database performance but may temporarily slow down the system.')) return

  isProcessing.value = true
  try {
    await axios.post('/api/admin/database/optimize')
    alert('Database optimization completed successfully!')
  } catch (error) {
    console.error('Failed to optimize database:', error)
    alert('Optimization failed. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const changeTab = async (tabId: string) => {
  activeTab.value = tabId
  await handleTabChange(tabId)
}

// 当切换到不同标签页时获取数据
const handleTabChange = async (tabId: string) => {
  if (tabId === 'algorithms') {
    await Promise.all([fetchAlgorithms(), fetchCategories()])
  } else if (tabId === 'posts') {
    await fetchAdminPosts()
  } else if (tabId === 'users') {
    await fetchAdminUsers()
  } else if (tabId === 'logs') {
    await fetchLogs()
  } else if (tabId === 'analytics') {
    await fetchAnalyticsData()
  } else if (tabId === 'database') {
    await fetchDatabaseStats()
  }
}
</script>

<style scoped>
.admin-page {
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

.admin-tabs {
  display: flex;
  background: var(--light-panel);
  border-radius: 0.75rem 0.75rem 0 0;
  padding: 0 2rem;
  box-shadow: var(--shadow-soft);
}

.tab {
  padding: 1rem 1.5rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  font-weight: 500;
}

.tab.active {
  border-bottom-color: var(--accent-color);
  color: var(--accent-color);
}

.admin-content {
  background: var(--light-panel);
  border-radius: 0 0 0.75rem 0.75rem;
  padding: 2rem;
  box-shadow: var(--shadow-soft);
  color: var(--text-dark);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.content-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

.filters {
  display: flex;
  gap: 1rem;
}

.filters select,
.filters input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.search-box input {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  width: 250px;
}

.logs-table {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 2fr;
  background: var(--light-panel);
  padding: 1rem;
  font-weight: 600;
  color: var(--text-dark);
  border-bottom: 1px solid #e5e7eb;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 2fr;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  transition: background 0.2s;
}

.table-row:hover {
  background: #f3f4f6;
}

.table-row div {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.posts-list,
.users-list {
  display: grid;
  gap: 1rem;
}

.post-item,
.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.post-item:hover,
.user-item:hover {
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.post-info,
.user-info {
  flex: 1;
}

.post-info h3,
.user-info h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.post-info p,
.user-info p {
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.post-stats,
.user-stats {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.user-role {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.user-role.user {
  background: #dbeafe;
  color: #1e40af;
}

.user-role.admin {
  background: #fef3c7;
  color: #92400e;
}

.post-actions,
.user-actions {
  display: flex;
  gap: 0.5rem;
}

.no-data {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  background: var(--light-panel);
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.stat-icon {
  font-size: 2rem;
  color: var(--accent-color);
  margin-right: 1rem;
}

.stat-info h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.stat-info p {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.recent-activity h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.activity-list {
  display: grid;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

.activity-icon {
  font-size: 1.25rem;
  color: var(--accent-color);
  margin-right: 1rem;
}

.activity-info p {
  font-weight: 500;
  color: var(--text-dark);
  margin-bottom: 0.25rem;
}

.activity-info span {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* Utility: visually hidden (accessible labels) */
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

@media (max-width: 768px) {
  .page-header {
    padding-top: calc(var(--nav-height) + 1rem); /* 避免导航栏遮挡 */
    margin-bottom: 2rem;
  }

  .page-header h1 {
    font-size: 2rem;
    margin-bottom: 0.75rem;
  }

  .page-header p {
    font-size: 1rem;
  }

  .admin-tabs {
    flex-wrap: wrap;
  }

  .content-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .filters {
    flex-direction: column;
  }

  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .post-item,
  .user-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .post-actions,
  .user-actions {
    align-self: flex-end;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .algorithms-table {
    margin-top: 2rem;
  }

  .table-row {
    grid-template-columns: 60px 2fr 1fr 100px 150px 150px;
  }
}

/* 算法管理样式 */
.algorithms-table {
  background: var(--light-panel);
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  margin-top: 2rem;
}

.algorithms-table .table-header,
.algorithms-table .table-row {
  display: grid;
  grid-template-columns: 60px 2fr 1fr 100px 150px 150px;
  gap: 1rem;
  padding: 1rem;
  align-items: center;
}

.algorithms-table .table-header {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.algorithms-table .table-row {
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s;
}

.algorithms-table .table-row:hover {
  background: #f8fafc;
}

.algorithms-table .table-row:last-child {
  border-bottom: none;
}

.difficulty-beginner {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.difficulty-intermediate {
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.difficulty-advanced {
  background: #dc2626;
  color: #ffffff;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  border-radius: 0.375rem;
}

.btn-secondary {
  background: #6b7280;
  color: white;
  border: none;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-danger {
  background: #b91c1c;
  color: white;
  border: none;
}

.btn-danger:hover {
  background: #991b1b;
}

/* 数据分析样式 */
.analytics-section {
  margin-bottom: 3rem;
}

.analytics-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.rankings-table {
  background: var(--light-panel);
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  margin-bottom: 2rem;
}

.rankings-table .table-header,
.rankings-table .table-row {
  display: grid;
  grid-template-columns: 80px 2fr 1fr 100px 100px 100px 120px;
  gap: 1rem;
  padding: 1rem;
  align-items: center;
}

.rankings-table .table-header {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.rankings-table .table-row {
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s;
}

.rankings-table .table-row:hover {
  background: #f8fafc;
}

.rankings-table .table-row:last-child {
  border-bottom: none;
}

/* 数据库管理样式 */
.db-management-section {
  margin-bottom: 3rem;
  padding: 2rem;
  background: var(--light-panel);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-soft);
}

.db-management-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-dark);
  margin-bottom: 0.5rem;
}

.section-description {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.management-actions {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.action-item {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  transition: all 0.2s;
}

.action-item:hover {
  border-color: #6b46c1;
  box-shadow: 0 4px 8px rgba(107, 70, 193, 0.1);
}

.action-item .btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  align-self: flex-start;
  position: relative;
}

.action-item .btn i {
  font-size: 0.875rem;
}

.action-item .btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-item .btn:disabled::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  margin: auto;
  border: 2px solid transparent;
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: button-loading-spinner 1s ease infinite;
}

@keyframes button-loading-spinner {
  from {
    transform: rotate(0turn);
  }
  to {
    transform: rotate(1turn);
  }
}

.action-description {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.page-btn {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.page-btn:hover:not(:disabled) {
  background: #6b46c1;
  color: white;
  border-color: #6b46c1;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(107, 70, 193, 0.2);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background: #f3f4f6;
  color: #9ca3af;
}

.page-number {
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  background: white;
  border: 1px solid #d1d5db;
}

.page-number:hover,
.page-number.active {
  background: #6b46c1;
  color: white;
  border-color: #6b46c1;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(107, 70, 193, 0.2);
}

.page-ellipsis {
  padding: 0.75rem 0.5rem;
  color: #6b7280;
  cursor: default;
  user-select: none;
  font-weight: 400;
  border: none;
  background: transparent;
}

/* Darken the ellipsis color specifically for the logs pagination to improve contrast */
.admin-content .logs-table + .pagination .page-ellipsis {
  color: #374151;
}

/* Analytics actions */
.analytics-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 0.75rem;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #374151;
}

.algorithm-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}
</style>
