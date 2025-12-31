import { defineStore } from 'pinia'
import axios from 'axios'

interface User {
  id: number
  username: string
  email: string
  role: 'user' | 'admin'
  avatar?: string
}

interface UserKnowledge {
  algorithm_id: number
  progress: number
  interests: string[]
  last_accessed: string
}

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as User | null,
    knowledge: [] as UserKnowledge[],
    isLoading: false,
    error: null as string | null
  }),

  getters: {
    isLoggedIn: (state) => !!state.user,
    isAdmin: (state) => state.user?.role === 'admin',
    getKnowledgeByAlgorithm: (state) => (algorithmId: number) => {
      return state.knowledge.find(k => k.algorithm_id === algorithmId)
    }
  },

  actions: {
    async login(credentials: { username: string; password: string }) {
      this.isLoading = true
      this.error = null
      try {
        // Debugging: ensure login requests are being sent from the frontend
        // (helps trace situations where the form appears to submit but no network request is observed)
        // eslint-disable-next-line no-console
        console.log('[userStore] login attempt', { username: credentials.username })
        const response = await axios.post('/api/auth/login', credentials)
        this.user = response.data.user
        this.knowledge = response.data.knowledge || []
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('isAdmin', this.user.role === 'admin' ? 'true' : 'false')
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`
      } catch (error: any) {
        this.error = error.response?.data?.message || '登录失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async register(userData: { username: string; email: string; password: string }) {
      this.isLoading = true
      this.error = null
      try {
        const response = await axios.post('/api/auth/register', userData)
        this.user = response.data.user
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('isAdmin', this.user.role === 'admin' ? 'true' : 'false')
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`
      } catch (error: any) {
        this.error = error.response?.data?.message || '注册失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      try {
        await axios.post('/api/auth/logout')
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.user = null
        this.knowledge = []
        localStorage.removeItem('token')
        localStorage.removeItem('isAdmin')
        delete axios.defaults.headers.common['Authorization']
      }
    },

    async checkAuth() {
      const token = localStorage.getItem('token')
      if (!token) return

      try {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        const response = await axios.get('/api/auth/me')
        this.user = response.data.user
        this.knowledge = response.data.knowledge || []
        localStorage.setItem('isAdmin', this.user.role === 'admin' ? 'true' : 'false')
      } catch (error) {
        this.logout()
      }
    },

    async updateKnowledge(algorithmId: number, progress: number, interests: string[]) {
      try {
        await axios.put(`/api/user/knowledge/${algorithmId}`, { progress, interests })
        const existing = this.knowledge.find(k => k.algorithm_id === algorithmId)
        if (existing) {
          existing.progress = progress
          existing.interests = interests
          existing.last_accessed = new Date().toISOString()
        } else {
          this.knowledge.push({
            algorithm_id: algorithmId,
            progress,
            interests,
            last_accessed: new Date().toISOString()
          })
        }
      } catch (error) {
        console.error('Update knowledge error:', error)
      }
    }
  }
})
