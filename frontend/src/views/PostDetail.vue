<template>
  <div class="post-detail-page">
    <div class="container">
      <!-- 返回按钮 -->
      <div class="back-button">
        <button class="btn btn-secondary" @click="$router.go(-1)">
          <i class="fas fa-arrow-left"></i> Back
        </button>
      </div>

      <!-- 帖子内容 -->
      <div v-if="post" class="post-content">
        <div class="post-header">
          <div class="post-author">
            <div class="author-avatar">
              <img :src="post.author?.avatar || '/assets/profile.jpg'" alt="author avatar" style="width:48px;height:48px;border-radius:50%;object-fit:cover;" />
            </div>
            <div class="author-info">
              <span class="author-name">{{ post.author?.username }}</span>
              <span class="post-time">{{ formatDate(post.created_at) }}</span>
            </div>
          </div>
          <div class="post-actions">
            <button v-if="userStore.isAdmin" class="btn btn-danger" @click="deletePost">
              <i class="fas fa-trash"></i> Delete
            </button>
            <button class="action-btn" @click="toggleLike">
              <i class="fas" :class="isLiked ? 'fa-heart' : 'fa-heart-o'"></i>
              {{ isLiked ? 'Liked' : 'Like' }}
            </button>
            <button class="action-btn" @click="toggleFavorite">
              <i class="fas" :class="isFavorited ? 'fa-bookmark' : 'fa-bookmark-o'"></i>
              {{ isFavorited ? 'Saved' : 'Save' }}
            </button>
          </div>
        </div>

        <h1 class="post-title">{{ post.title }}</h1>

        <div class="post-body">
          <div class="post-text" v-html="formatContent(post.content)"></div>
        </div>

        <div class="post-footer">
          <div class="post-stats">
            <span class="stat">
              <i class="fas fa-eye"></i> {{ post.view_count }}
            </span>
            <span class="stat">
              <i class="fas fa-thumbs-up"></i> {{ post.like_count }}
            </span>
            <span class="stat">
              <i class="fas fa-comments"></i> {{ post.comment_count }}
            </span>
          </div>
          <div class="post-tags">
            <span v-if="post.is_featured" class="tag featured">
              <i class="fas fa-star"></i> Featured
            </span>
          </div>
        </div>
      </div>

      <!-- 评论区域 -->
      <div class="comments-section">
        <h3>Comments ({{ comments.length }})</h3>

        <!-- 发表评论 -->
        <div v-if="userStore.isLoggedIn" class="comment-form">
          <div class="comment-input">
            <label class="sr-only" for="comment-input">Write your comment</label>
            <textarea
              id="comment-input"
              aria-label="Write your comment"
              v-model="newComment"
              placeholder="Write your comment..."
              rows="3"
            ></textarea>
            <button class="btn btn-primary" @click="submitComment" :disabled="!newComment.trim()">
              Post Comment
            </button>
          </div>
        </div>
        <div v-else class="login-prompt">
          <p>Please <router-link to="/login">sign in</router-link> to join the discussion</p>
        </div>

        <!-- 评论列表 -->
        <div class="comments-list">
          <div
            v-for="comment in comments"
            :key="comment.id"
            class="comment-item"
            :class="{ 'reply-comment': comment.parent_id }"
          >
            <div class="comment-header">
              <div class="comment-author">
                <div class="author-avatar">
                  <img :src="comment.author?.avatar || '/assets/profile.jpg'" alt="author avatar" style="width:40px;height:40px;border-radius:50%;object-fit:cover;" />
                </div>
                <div class="author-info">
                  <span class="author-name">{{ comment.author?.username }}</span>
                  <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
                </div>
              </div>
              <div class="comment-actions">
                <button class="reply-btn" @click="showReplyForm(comment.id)">
                  <i class="fas fa-reply"></i> Reply
                </button>
                <button
                  v-if="userStore.isLoggedIn && (userStore.user?.id === comment.author?.id || userStore.isAdmin)"
                  class="delete-btn"
                  @click="deleteComment(comment.id)"
                >
                  <i class="fas fa-trash"></i> Delete
                </button>
              </div>
            </div>

            <div class="comment-body">
              <p>{{ comment.content }}</p>
            </div>

            <!-- 回复表单 -->
            <div v-if="replyingTo === comment.id" class="reply-form">
              <label class="sr-only" :for="'reply-input-' + comment.id">Write your reply</label>
              <textarea
                :id="'reply-input-' + comment.id"
                :aria-label="'Write your reply to comment ' + comment.id"
                v-model="replyContent"
                placeholder="Write your reply..."
                rows="2"
              ></textarea>
              <div class="reply-actions">
                <button class="btn btn-secondary" @click="cancelReply">Cancel</button>
                <button class="btn btn-primary" @click="submitReply(comment.id)" :disabled="!replyContent.trim()">
                  Reply
                </button>
              </div>
            </div>

            <!-- 子回复 -->
            <div v-if="comment.replies && comment.replies.length > 0" class="comment-replies">
              <div
                v-for="reply in comment.replies"
                :key="reply.id"
                class="comment-item reply-comment"
              >
                <div class="comment-header">
                  <div class="comment-author">
                    <div class="author-avatar">
                      <img :src="reply.author?.avatar || '/assets/profile.jpg'" alt="author avatar" style="width:32px;height:32px;border-radius:50%;object-fit:cover;" />
                    </div>
                    <div class="author-info">
                      <span class="author-name">{{ reply.author?.username }}</span>
                      <span class="comment-time">{{ formatDate(reply.created_at) }}</span>
                    </div>
                  </div>
                  <div class="comment-actions">
                    <button
                      v-if="userStore.isLoggedIn && (userStore.user?.id === reply.author?.id || userStore.isAdmin)"
                      class="delete-btn"
                      @click="deleteComment(reply.id)"
                    >
                      <i class="fas fa-trash"></i> 删除
                    </button>
                  </div>
                </div>
                <div class="comment-body">
                  <p>{{ reply.content }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()

const post = ref<any>(null)
const comments = ref<any[]>([])
const newComment = ref('')
const replyContent = ref('')
const replyingTo = ref<number | null>(null)
const isLiked = ref(false)
const isFavorited = ref(false)

const fetchPost = async () => {
  try {
    const postId = route.params.id
    const response = await axios.get(`/api/posts/${postId}`)
    post.value = response.data.post

    // 获取评论
    await fetchComments()

    // 获取用户的交互状态
    if (userStore.isLoggedIn) {
      await checkInteractions()
    }

  } catch (error) {
    console.error('Failed to fetch post:', error)
  }
}

const fetchComments = async () => {
  try {
    const response = await axios.get(`/api/posts/${route.params.id}/comments`)
    comments.value = response.data.comments || []
  } catch (error) {
    console.error('Failed to fetch comments:', error)
  }
}

const checkInteractions = async () => {
  try {
    // 检查点赞状态
    const likesResponse = await axios.get('/api/user/likes')
    const likedPostIds = likesResponse.data.likes?.map((l: any) => l.post_id) || []
    isLiked.value = likedPostIds.includes(Number(route.params.id))

    // 检查收藏状态
    const favoritesResponse = await axios.get('/api/favorites')
    const favoritedPostIds = favoritesResponse.data.favorites?.map((f: any) => f.id) || []
    isFavorited.value = favoritedPostIds.includes(Number(route.params.id))

  } catch (error) {
    console.error('Failed to check interactions:', error)
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return

  try {
    await axios.post(`/api/posts/${route.params.id}/comments`, {
      content: newComment.value
    })

    newComment.value = ''
    await fetchComments()
    post.value.comment_count++

  } catch (error) {
    console.error('Failed to submit comment:', error)
  }
}

const showReplyForm = (commentId: number) => {
  replyingTo.value = commentId
  replyContent.value = ''
}

const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
}

const submitReply = async (parentCommentId: number) => {
  if (!replyContent.value.trim()) return

  try {
    await axios.post(`/api/posts/${route.params.id}/comments`, {
      content: replyContent.value,
      parent_id: parentCommentId
    })

    cancelReply()
    await fetchComments()
    post.value.comment_count++

  } catch (error) {
    console.error('Failed to submit reply:', error)
  }
}

const deleteComment = async (commentId: number) => {
  if (!confirm('Are you sure you want to delete this comment?')) return

  try {
    await axios.delete(`/api/comments/${commentId}`)
    await fetchComments()
    post.value.comment_count--
  } catch (error) {
    console.error('Failed to delete comment:', error)
  }
}

const deletePost = async () => {
  if (!confirm('Are you sure you want to delete this post?')) return

  try {
    await axios.delete(`/api/admin/posts/${route.params.id}`)
    // 跳转回帖子列表
    router.push('/posts')
  } catch (error) {
    console.error('Failed to delete post:', error)
  }
}

const toggleLike = async () => {
  if (!userStore.isLoggedIn) {
    alert('Please sign in')
    return
  }

  try {
    await axios.post(`/api/posts/${route.params.id}/like`)
    isLiked.value = !isLiked.value
    post.value.like_count += isLiked.value ? 1 : -1
  } catch (error) {
    console.error('Failed to toggle like:', error)
  }
}

const toggleFavorite = async () => {
  if (!userStore.isLoggedIn) {
    alert('Please sign in')
    return
  }

  try {
    await axios.post(`/api/posts/${route.params.id}/favorite`)
    isFavorited.value = !isFavorited.value
  } catch (error) {
    console.error('Failed to toggle favorite:', error)
  }
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes} minutes ago`
  if (hours < 24) return `${hours} hours ago`
  if (days < 7) return `${days} days ago`
  return date.toLocaleDateString('en-US')
}

const formatContent = (content: string) => {
  // 简单的文本格式化，将换行转换为<br>
  return content.replace(/\n/g, '<br>')
}

// 监听全局键盘事件
const handleToggleFavorite = () => {
  toggleFavorite()
}

onMounted(() => {
  fetchPost()
  // 监听全局键盘事件
  window.addEventListener('toggle-post-favorite', handleToggleFavorite)
})

onBeforeUnmount(() => {
  window.removeEventListener('toggle-post-favorite', handleToggleFavorite)
})
</script>

<style scoped>
.post-detail-page {
  padding: 2rem 0;
  background: var(--brand-bg);
  min-height: 100vh;
}

.back-button {
  margin-bottom: 2rem;
}

.post-content {
  background: var(--light-panel);
  color: var(--text-dark);
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-soft);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.author-avatar img { width:48px;height:48px;border-radius:50%;object-fit:cover;display:block; }

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 500;
  color: var(--text-dark);
}

.post-time {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.post-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.action-btn:hover {
  border-color: #6b46c1;
  color: #6b46c1;
}

.post-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--heading-color);
  margin-bottom: 1.5rem;
  line-height: 1.3;
}

.post-body {
  margin-bottom: 2rem;
}

.post-text {
  font-size: 1.125rem;
  line-height: 1.7;
  color: var(--text-dark);
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.post-stats {
  display: flex;
  gap: 1.5rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.post-tags {
  display: flex;
  gap: 0.5rem;
}

.tag {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.tag.featured {
  background: #fef3c7;
  color: #92400e;
}

.comments-section {
  background: var(--light-panel);
  color: var(--text-dark);
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: var(--shadow-soft);
}

.comments-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-dark);
  margin-bottom: 1.5rem;
}

.comment-form {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--light-panel);
  border-radius: 0.5rem;
}

.comment-input {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comment-input textarea {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  resize: vertical;
  font-family: inherit;
}

.login-prompt {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}

.comments-list {
  display: grid;
  gap: 1.5rem;
}

.comment-item {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.comment-item.reply-comment {
  margin-left: 2rem;
  border-left: 3px solid #6b46c1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.comment-actions {
  display: flex;
  gap: 0.5rem;
}

.reply-btn,
.delete-btn {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.reply-btn:hover {
  color: #6b46c1;
}

.delete-btn:hover {
  color: #dc2626;
}

.comment-body {
  margin-bottom: 1rem;
}

.comment-body p {
  color: #374151;
  line-height: 1.6;
}

.reply-form {
  margin-top: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.375rem;
}

.reply-form textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
  resize: vertical;
  font-family: inherit;
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

.reply-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.comment-replies {
  margin-top: 1rem;
  padding-left: 1rem;
  border-left: 2px solid #e5e7eb;
}

@media (max-width: 768px) {
  .post-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
    margin-top: calc(var(--nav-height) + 1rem); /* 避免导航栏遮挡 */
  }

  .post-actions {
    align-self: flex-end;
  }

  .post-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .comment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .comment-actions {
    align-self: flex-end;
  }
}
</style>
