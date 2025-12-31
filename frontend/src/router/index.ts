import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Posts from '@/views/Posts.vue'
import PostDetail from '@/views/PostDetail.vue'
import CreatePost from '@/views/CreatePost.vue'
import Algorithm from '@/views/Algorithm.vue'
import Profile from '@/views/Profile.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Admin from '@/views/Admin.vue'
import Chat from '@/views/Chat.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'ML Learner - Machine Learning Visualization Platform' }
  },
  {
    path: '/algorithms',
    name: 'Algorithms',
    component: () => import('@/views/Algorithms.vue'),
    meta: { title: 'Algorithms - ML Learner' }
  },
  {
    path: '/posts',
    name: 'Posts',
    component: Posts,
    meta: { title: 'Community - ML Learner' }
  },
  {
    path: '/posts/:id',
    name: 'PostDetail',
    component: PostDetail,
    meta: { title: 'Post Details - ML Learner' }
  },
  {
    path: '/create-post',
    name: 'CreatePost',
    component: CreatePost,
    meta: { title: 'Create Post - ML Learner' }
  },
  {
    path: '/algorithms/:id',
    name: 'Algorithm',
    component: Algorithm,
    meta: { title: 'Algorithm Learning - ML Learner' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: {
      title: 'Profile - ML Learner'
      // requiresAuth: true  // 暂时移除认证要求进行测试
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: 'Sign In - ML Learner' }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: 'Sign Up - ML Learner' }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat,
    meta: { title: 'Chat - ML Learner', requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { title: 'Admin Panel - ML Learner', requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || 'ML Learner'

  // 检查认证要求
  const token = localStorage.getItem('token')
  const isLoggedIn = !!token

  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
    return
  }

  if (to.meta.requiresAdmin && (!isLoggedIn || !localStorage.getItem('isAdmin'))) {
    next('/')
    return
  }

  next()
})

export default router
