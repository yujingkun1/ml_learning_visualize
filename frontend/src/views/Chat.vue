<template>
  <div class="chat-page">
    <div class="container">
      <div class="page-header">
        <h1>Friends & Chat</h1>
        <p>Connect with other ML learners and share your knowledge</p>
      </div>

      <div class="chat-container">
        <!-- 左侧好友列表 -->
        <div class="friends-sidebar">
          <!-- 好友搜索 -->
          <div class="friends-search">
            <input
              type="search"
              aria-label="Search friends"
              v-model="friendSearchQuery"
              @input="debouncedSearchFriends"
              placeholder="Search friends..."
              class="search-input"
            >
            <i class="fas fa-search search-icon"></i>
          </div>

          <!-- 添加好友按钮 -->
          <button class="add-friend-btn" @click="showAddFriendModal = true">
            <i class="fas fa-user-plus"></i> Add Friend
          </button>

          <!-- 好友请求 -->
          <div v-if="friendRequests.received.length > 0 || friendRequests.sent.length > 0" class="friend-requests">
            <h3>Friend Requests</h3>
            <div class="requests-list">
              <div
                v-for="request in friendRequests.received"
                :key="request.id"
                class="request-item"
              >
                <div class="request-info">
                  <img :src="request.user?.avatar || '/assets/profile.jpg'" alt="avatar" class="request-avatar">
                  <span>{{ request.user?.username }}</span>
                </div>
                <div class="request-actions">
                  <button class="accept-btn" @click="respondFriendRequest(request.id, 'accept')">Accept</button>
                  <button class="reject-btn" @click="respondFriendRequest(request.id, 'reject')">Reject</button>
                </div>
              </div>
              <div
                v-for="request in friendRequests.sent"
                :key="request.id"
                class="request-item sent"
              >
                <div class="request-info">
                  <img :src="request.friend?.avatar || '/assets/profile.jpg'" alt="avatar" class="request-avatar">
                  <span>{{ request.friend?.username }} (pending)</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 好友列表 -->
          <div class="friends-list">
            <h3>Friends</h3>
            <div
              v-for="friend in filteredFriends"
              :key="friend.id"
              class="friend-item"
              :class="{ active: selectedFriend?.id === friend.id }"
              @click="selectFriend(friend)"
            >
              <div class="friend-avatar">
                <img :src="friend.avatar || '/assets/profile.jpg'" alt="avatar">
                <div v-if="getUnreadCount(friend.id) > 0" class="unread-badge">
                  {{ getUnreadCount(friend.id) }}
                </div>
              </div>
              <div class="friend-info">
                <div class="friend-name">{{ friend.username }}</div>
                <div class="last-message">
                  {{ getLastMessagePreview(friend.id) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧聊天区域 -->
        <div class="chat-main">
          <div v-if="!selectedFriend" class="no-chat-selected">
            <i class="fas fa-comments fa-3x"></i>
            <h3>Select a friend to start chatting</h3>
            <p>Choose a friend from the list to begin your conversation</p>
          </div>

          <div v-else class="chat-window">
            <!-- 聊天头部 -->
            <div class="chat-header">
              <div class="chat-friend-info">
                <img :src="selectedFriend.avatar || '/assets/profile.jpg'" alt="avatar" class="chat-avatar">
                <div>
                  <h4>{{ selectedFriend.username }}</h4>
                  <span class="online-status">Online</span>
                </div>
              </div>
              <div class="chat-actions">
                <button class="view-profile-btn" @click="viewProfile(selectedFriend.id)">
                  <i class="fas fa-user"></i> Profile
                </button>
              </div>
            </div>

            <!-- 消息列表 -->
            <div class="messages-container" ref="messagesContainer">
              <div
                v-for="message in messages"
                :key="message.id"
                class="message-item"
                :class="{ 'own-message': message.sender_id === userStore.user?.id }"
              >
                <div class="message-avatar">
                  <img :src="message.sender?.avatar || '/assets/profile.jpg'" alt="avatar">
                </div>
                <div class="message-content">
                  <div class="message-text">{{ message.content }}</div>
                  <div class="message-time">{{ formatMessageTime(message.created_at) }}</div>
                </div>
              </div>
            </div>

            <!-- 消息输入框 -->
            <div class="message-input-container">
              <div class="message-input-wrapper">
                <input
                  type="text"
                  v-model="newMessage"
                  @keyup.enter="sendMessage"
                  placeholder="Type a message..."
                  class="message-input"
                  :disabled="sendingMessage"
                >
                <button
                  class="send-btn"
                  @click="sendMessage"
                  :disabled="!newMessage.trim() || sendingMessage"
                >
                  <i class="fas fa-paper-plane"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加好友模态框 -->
    <div v-if="showAddFriendModal" class="modal-overlay" @click="showAddFriendModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add Friend</h3>
          <button class="close-btn" @click="showAddFriendModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="search-users">
            <input
              type="search"
              aria-label="Search users"
              v-model="userSearchQuery"
              @input="debouncedSearchUsers"
              placeholder="Search users by username or email..."
              class="search-input"
            >
          </div>

          <div class="users-list">
            <div v-if="searchLoading" class="loading">Searching...</div>
            <div v-else-if="searchResults.length === 0 && userSearchQuery" class="no-results">
              No users found
            </div>
            <div
              v-for="user in searchResults"
              :key="user.id"
              class="user-item"
              :class="{ 'already-friend': user.friend_status }"
            >
              <div class="user-info">
                <img :src="user.avatar || '/assets/profile.jpg'" alt="avatar" class="user-avatar">
                <div>
                  <div class="username">{{ user.username }}</div>
                  <div class="email">{{ user.email }}</div>
                </div>
              </div>
              <div class="user-actions">
                <button
                  v-if="!user.friend_status"
                  class="add-btn"
                  @click="sendFriendRequest(user.id)"
                  :disabled="user.id === userStore.user?.id"
                >
                  <i class="fas fa-user-plus"></i> Add
                </button>
                <span v-else-if="user.friend_status === 'accepted'" class="friend-status">
                  <i class="fas fa-check"></i> Friends
                </span>
                <span v-else-if="user.friend_status === 'pending'" class="friend-status pending">
                  <i class="fas fa-clock"></i> {{ user.is_sender ? 'Sent' : 'Received' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户简介模态框 -->
    <div v-if="showProfileModal" class="modal-overlay" @click="showProfileModal = false">
      <div class="modal-content profile-modal" @click.stop>
        <div class="modal-header">
          <h3>User Profile</h3>
          <button class="close-btn" @click="showProfileModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div v-if="profileData" class="modal-body">
          <div class="profile-header">
            <img :src="profileData.avatar || '/assets/profile.jpg'" alt="avatar" class="profile-avatar">
            <div class="profile-info">
              <h4>{{ profileData.username }}</h4>
              <p class="user-role">{{ getRoleText(profileData.role) }}</p>
            </div>
          </div>

          <div class="profile-stats">
            <div class="stat">
              <span class="stat-number">{{ profileData.stats.posts_count }}</span>
              <span class="stat-label">Posts</span>
            </div>
            <div class="stat">
              <span class="stat-number">{{ profileData.stats.likes_received }}</span>
              <span class="stat-label">Likes</span>
            </div>
            <div class="stat">
              <span class="stat-number">{{ profileData.stats.comments_count }}</span>
              <span class="stat-label">Comments</span>
            </div>
          </div>

          <div v-if="profileData.recent_posts && profileData.recent_posts.length > 0" class="recent-posts">
            <h5>Recent Posts</h5>
            <div
              v-for="post in profileData.recent_posts"
              :key="post.id"
              class="recent-post-item"
              @click="$router.push(`/posts/${post.id}`)"
            >
              <h6>{{ post.title }}</h6>
              <p>{{ post.content.substring(0, 100) }}...</p>
              <small>{{ formatDate(post.created_at) }}</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

// 状态管理
const friends = ref([])
const conversations = ref([])
const selectedFriend = ref(null)
const messages = ref([])
const friendRequests = ref({ received: [], sent: [] })

// UI状态
const showAddFriendModal = ref(false)
const showProfileModal = ref(false)
const searchLoading = ref(false)
const sendingMessage = ref(false)

// 搜索和输入
const friendSearchQuery = ref('')
const userSearchQuery = ref('')
const newMessage = ref('')
const searchResults = ref([])
const profileData = ref(null)

// 防抖搜索
let searchTimeout = null
let userSearchTimeout = null

const filteredFriends = computed(() => {
  if (!friendSearchQuery.value) return friends.value
  return friends.value.filter(friend =>
    friend.username.toLowerCase().includes(friendSearchQuery.value.toLowerCase())
  )
})

const debouncedSearchFriends = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    // 过滤好友列表
  }, 300)
}

const debouncedSearchUsers = () => {
  if (userSearchTimeout) clearTimeout(userSearchTimeout)
  userSearchTimeout = setTimeout(() => {
    searchUsers()
  }, 500)
}

const getUnreadCount = (friendId) => {
  const conversation = conversations.value.find(conv => conv.friend.id === friendId)
  return conversation ? conversation.unread_count : 0
}

const getLastMessagePreview = (friendId) => {
  const conversation = conversations.value.find(conv => conv.friend.id === friendId)
  if (conversation && conversation.latest_message) {
    const msg = conversation.latest_message
    return msg.sender_id === userStore.user?.id ? `You: ${msg.content}` : msg.content
  }
  return 'No messages yet'
}

// API调用
const fetchFriends = async () => {
  try {
    const response = await axios.get('/api/friends')
    friends.value = response.data.friends
  } catch (error) {
    console.error('Failed to fetch friends:', error)
  }
}

const fetchConversations = async () => {
  try {
    const response = await axios.get('/api/chat/conversations')
    conversations.value = response.data.conversations
  } catch (error) {
    console.error('Failed to fetch conversations:', error)
  }
}

const fetchFriendRequests = async () => {
  try {
    const response = await axios.get('/api/friends/requests')
    friendRequests.value = response.data
  } catch (error) {
    console.error('Failed to fetch friend requests:', error)
  }
}

const searchUsers = async () => {
  if (!userSearchQuery.value.trim()) {
    searchResults.value = []
    return
  }

  searchLoading.value = true
  try {
    const response = await axios.get('/api/friends/search', {
      params: { q: userSearchQuery.value }
    })
    searchResults.value = response.data.users
  } catch (error) {
    console.error('Failed to search users:', error)
  } finally {
    searchLoading.value = false
  }
}

const sendFriendRequest = async (friendId) => {
  try {
    await axios.post('/api/friends/request', { friend_id: friendId })
    alert('Friend request sent!')
    searchUsers() // 重新搜索以更新状态
    fetchFriendRequests() // 更新好友请求列表
  } catch (error) {
    console.error('Failed to send friend request:', error)
    alert('Failed to send friend request')
  }
}

const respondFriendRequest = async (requestId, action) => {
  try {
    await axios.put(`/api/friends/requests/${requestId}`, { action })
    alert(`Friend request ${action}ed!`)
    fetchFriendRequests()
    if (action === 'accept') {
      fetchFriends()
    }
  } catch (error) {
    console.error('Failed to respond to friend request:', error)
    alert('Failed to respond to friend request')
  }
}

const selectFriend = async (friend) => {
  selectedFriend.value = friend
  await fetchMessages(friend.id)
}

const fetchMessages = async (friendId) => {
  try {
    const response = await axios.get('/api/chat/messages', {
      params: { friend_id: friendId }
    })
    messages.value = response.data.messages
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Failed to fetch messages:', error)
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedFriend.value) return

  sendingMessage.value = true
  try {
    const response = await axios.post('/api/chat/messages', {
      receiver_id: selectedFriend.value.id,
      content: newMessage.value.trim()
    })

    messages.value.push(response.data.chat_message)
    newMessage.value = ''
    await nextTick()
    scrollToBottom()

    // 更新对话列表
    fetchConversations()
  } catch (error) {
    console.error('Failed to send message:', error)
    alert('Failed to send message')
  } finally {
    sendingMessage.value = false
  }
}

const viewProfile = async (userId) => {
  try {
    const response = await axios.get(`/api/users/${userId}/profile`)
    profileData.value = response.data.profile
    showProfileModal.value = true
  } catch (error) {
    console.error('Failed to fetch user profile:', error)
  }
}

const scrollToBottom = () => {
  const container = document.querySelector('.messages-container')
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

// 工具函数
const formatMessageTime = (dateStr) => {
  // 确保时间字符串是UTC格式，如果没有Z后缀则添加
  let utcDateStr = dateStr
  if (!utcDateStr.includes('Z') && utcDateStr.includes('T')) {
    utcDateStr += 'Z'  // 明确标记为UTC时间
  } else if (!utcDateStr.includes('T')) {
    utcDateStr = utcDateStr + 'T00:00:00Z'
  }

  // 创建UTC时间对象
  const date = new Date(utcDateStr)
  const now = new Date()

  // 确保两个时间都在同一时区（UTC）进行比较
  const utcDate = new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(),
                          date.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds())
  const utcNow = new Date(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(),
                         now.getUTCHours(), now.getUTCMinutes(), now.getUTCSeconds())

  const diff = utcNow.getTime() - utcDate.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))

  if (hours < 1) {
    const minutes = Math.floor(diff / (1000 * 60))
    return minutes <= 1 ? 'Just now' : `${minutes} min ago`
  } else if (hours < 24) {
    return `${hours} hours ago`
  } else if (hours < 48) {
    return 'Yesterday'
  } else {
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr + (dateStr.includes('T') ? '' : 'T00:00:00'))
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getRoleText = (role) => {
  const roles = {
    user: 'User',
    admin: 'Admin'
  }
  return roles[role] || role
}

// 轮询新消息
let pollInterval = null
const startPolling = () => {
  pollInterval = setInterval(async () => {
    if (selectedFriend.value) {
      await fetchMessages(selectedFriend.value.id)
    }
    await fetchConversations()
    await fetchFriendRequests()
  }, 3000) // 每3秒轮询一次
}

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

onMounted(async () => {
  await Promise.all([
    fetchFriends(),
    fetchConversations(),
    fetchFriendRequests()
  ])
  startPolling()
})

// 组件销毁时停止轮询
import { onUnmounted } from 'vue'
onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.chat-page {
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
  color: var(--heading-color);
  margin-bottom: 0.5rem;
}

.page-header p {
  color: var(--text-muted);
  font-size: 1.125rem;
  margin-bottom: 2rem;
}

.chat-container {
  display: flex;
  gap: 2rem;
  height: calc(100vh - 200px);
  background: var(--light-panel);
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: var(--shadow-soft);
}

.friends-sidebar {
  width: 300px;
  border-right: 1px solid #e5e7eb;
  padding-right: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.friends-search {
  position: relative;
}

.friends-search .search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.friends-search .search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.add-friend-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  background: #6b46c1;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.2s;
}

.add-friend-btn:hover {
  background: #5a3ba8;
}

.friend-requests h3,
.friends-list h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-dark);
}

.requests-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.request-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.request-item.sent {
  opacity: 0.7;
}

.request-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.request-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.request-actions {
  display: flex;
  gap: 0.5rem;
}

.accept-btn {
  padding: 0.25rem 0.5rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
}

.reject-btn {
  padding: 0.25rem 0.5rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
}

.friends-list {
  flex: 1;
  overflow-y: auto;
}

.friend-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: background 0.2s;
  position: relative;
}

.friend-item:hover,
.friend-item.active {
  background: #f3f4f6;
}

.friend-avatar {
  position: relative;
}

.friend-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.unread-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.friend-info {
  flex: 1;
}

.friend-name {
  font-weight: 500;
  color: var(--text-dark);
}

.last-message {
  font-size: 0.75rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.no-chat-selected {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-dark);
  text-align: center;
}

.no-chat-selected i {
  margin-bottom: 1rem;
  color: #d1d5db;
}

.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.chat-friend-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.chat-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.chat-friend-info h4 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-dark);
}

.online-status {
  font-size: 0.75rem;
  color: #10b981;
}

.chat-actions {
  display: flex;
  gap: 0.5rem;
}

.view-profile-btn {
  padding: 0.5rem 1rem;
  background: #6b46c1;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.2s;
}

.view-profile-btn:hover {
  background: #5a3ba8;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.5rem;
  background: #f9fafb;
}

.message-item {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.message-item.own-message {
  flex-direction: row-reverse;
}

.message-avatar img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.message-content {
  max-width: 70%;
}

.message-text {
  background: white;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  color: var(--text-dark);
  word-wrap: break-word;
}

.own-message .message-text {
  background: #6b46c1;
  color: white;
}

.message-time {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
  text-align: left;
}

.own-message .message-time {
  text-align: right;
}

.message-input-container {
  padding: 1rem 1.5rem;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.message-input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.send-btn {
  padding: 0.75rem 1rem;
  background: #6b46c1;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #5a3ba8;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.profile-modal {
  max-width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  border: none;
  background: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
}

.modal-body {
  padding: 1.5rem;
}

.search-users {
  margin-bottom: 1rem;
}

.users-list {
  max-height: 400px;
  overflow-y: auto;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
}

.user-item.already-friend {
  opacity: 0.7;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.username {
  font-weight: 500;
  color: #1f2937;
}

.email {
  font-size: 0.875rem;
  color: #6b7280;
}

.user-actions {
  display: flex;
  align-items: center;
}

.add-btn {
  padding: 0.5rem 1rem;
  background: #6b46c1;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.2s;
}

.add-btn:hover {
  background: #5a3ba8;
}

.add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.friend-status {
  font-size: 0.875rem;
  color: #10b981;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.friend-status.pending {
  color: #f59e0b;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.profile-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.user-role {
  color: #6b7280;
  font-size: 0.875rem;
}

.profile-stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.profile-stats .stat {
  text-align: center;
}

.profile-stats .stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #6b46c1;
}

.profile-stats .stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.recent-posts h5 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1f2937;
}

.recent-post-item {
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: border-color 0.2s;
}

.recent-post-item:hover {
  border-color: #6b46c1;
}

.recent-post-item h6 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.recent-post-item p {
  margin: 0 0 0.5rem 0;
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
}

.recent-post-item small {
  color: #9ca3af;
  font-size: 0.75rem;
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

  .chat-container {
    flex-direction: column;
    height: auto;
  }

  .friends-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    padding-right: 0;
    padding-bottom: 1.5rem;
  }

  .chat-main {
    height: 500px;
  }

  .modal-content {
    width: 95%;
    margin: 1rem;
  }
}
</style>
