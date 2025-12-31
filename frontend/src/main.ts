import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import router from './router'
import App from './App.vue'
import './style.css'

// 配置axios - 不设置默认Content-Type，让浏览器自动处理FormData

// 请求拦截器：在每次请求中添加token
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // 对于FormData请求，不要设置Content-Type，让浏览器自动处理
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理401错误
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)
app.use(createPinia())
app.use(router)

app.mount('#app')

// 检查用户认证状态（异步执行）
import('./stores/user').then(({ useUserStore }) => {
  const userStore = useUserStore()
  userStore.checkAuth()
})
