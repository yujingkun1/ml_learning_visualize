<template>
  <div class="auth-page">
    <div class="container">
      <div class="auth-card">
        <div class="auth-header">
          <h1>Sign In</h1>
          <p>Welcome back, continue your learning journey</p>
        </div>

        <div v-if="generalError" class="auth-error" role="alert">{{ generalError }}</div>

        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label for="username">Username</label>
            <input
              id="username"
              type="text"
              v-model="form.username"
              required
              placeholder="Enter your username"
              class="form-input"
              :class="{ error: errors.username }"
            >
            <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              type="password"
              v-model="form.password"
              required
              placeholder="Enter your password"
              class="form-input"
              :class="{ error: errors.password }"
            >
            <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          </div>

          <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>

        <div class="auth-footer">
          <p>Don't have an account? <router-link to="/register">Sign up</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const errors = reactive({
  username: '',
  password: ''
})
const generalError = ref('')

const handleLogin = async () => {
  // Debug: confirm handler invocation
  // eslint-disable-next-line no-console
  console.log('[Login.vue] handleLogin called', { username: form.username, password: form.password })

  // 清除之前的错误
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
  generalError.value = ''

  // Validate form
  if (!form.username.trim()) {
    errors.username = 'Please enter your username'
    return
  }

  if (!form.password) {
    errors.password = 'Please enter your password'
    return
  }

  loading.value = true

  try {
    await userStore.login({
      username: form.username.trim(),
      password: form.password
    })

    // 登录成功，跳转到首页
    router.push('/')

  } catch (error) {
    // 清理先前错误（但不清除表单内容）
    // 注意：这里我们不清除错误信息，因为loading状态变化后会重新渲染
    Object.keys(errors).forEach(key => {
      errors[key] = ''
    })
    generalError.value = ''

    // 延迟设置loading为false，确保错误信息有时间显示
    setTimeout(() => {
      loading.value = false
    }, 100)

    // 处理 HTTP 错误和后端返回的验证错误
    if (error.response) {
      const status = error.response.status
      const data = error.response.data || {}

      // 优先显示后端字段级错误（假设格式 { errors: { username: '', password: '' } }）
      if (data.errors && typeof data.errors === 'object') {
        for (const [field, msg] of Object.entries(data.errors)) {
          if (field in errors) {
            // @ts-ignore
            errors[field] = Array.isArray(msg) ? msg.join('; ') : String(msg)
          } else {
            generalError.value += (generalError.value ? ' ' : '') + String(msg)
          }
        }
      } else if (data.message) {
        // 根据状态码给出更明确的提示
        if (status === 400) {
          generalError.value = data.message || 'Bad request — please check your input'
        } else if (status === 401) {
          // Authentication failed — map backend messages to field errors when possible
          const msg = (data.message || '').toLowerCase()
          if (msg.includes('username')) {
            errors.username = 'Username not found.'
          } else if (msg.includes('password')) {
            errors.password = 'Incorrect password.'
          } else {
            generalError.value = data.message || 'Invalid username or password'
          }
        } else if (status === 403) {
          generalError.value = data.message || 'Access forbidden'
        } else if (status >= 500) {
          generalError.value = 'Server error — please try again later'
        } else {
          generalError.value = data.message
        }
      } else {
        generalError.value = `请求失败（HTTP ${status}）`
      }
    } else if (error.request) {
      // Request made but no response
      generalError.value = 'Unable to reach server — please check network or backend status'
    } else {
      // Other errors
      generalError.value = error.message || 'Login failed — please try again later'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: url('/assets/auth-bg.jpg');
  background-size: cover;
  background-position: center;
  padding: 2rem 0;
}

.auth-card {
  background: var(--brand-panel);
  border-radius: 0.75rem;
  padding: 3rem;
  box-shadow: var(--shadow);
  width: 100%;
  max-width: 420px;
  color: var(--text-light);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #000000;
  margin-bottom: 0.5rem;
}

.auth-header p {
  color: var(--text-muted);
}

.auth-form {
  display: grid;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px rgba(251, 191, 36, 0.12);
}

.form-input.error {
  border-color: #dc2626;
}

.error-message {
  color: #dc2626;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.btn-full {
  width: 100%;
  padding: 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-footer {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.auth-footer p {
  color: #6b7280;
}

.auth-footer a {
  color: var(--accent-color);
  font-weight: 500;
  text-decoration: none;
}

.auth-footer a:hover {
  text-decoration: underline;
}

.auth-error {
  background: #fffbeb;
  border: 1px solid #fef3c7;
  color: #92400e;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  font-weight: 500;
}

@media (max-width: 480px) {
  .auth-card {
    margin: 1rem;
    padding: 2rem;
  }

  .auth-header h1 {
    font-size: 1.5rem;
  }
}
</style>
