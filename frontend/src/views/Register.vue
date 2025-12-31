<template>
  <div class="auth-page">
    <div class="container">
      <div class="auth-card">
        <div class="auth-header">
          <h1>Sign Up</h1>
          <p>Join our learning community and start your AI learning journey</p>
        </div>

        <div v-if="generalError" class="auth-error" role="alert">{{ generalError }}</div>

        <form @submit.prevent="handleRegister" class="auth-form">
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
            <label for="email">Email</label>
            <input
              id="email"
              type="email"
              v-model="form.email"
              required
              placeholder="Enter your email address"
              class="form-input"
              :class="{ error: errors.email }"
            >
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              type="password"
              v-model="form.password"
              required
              placeholder="Enter password (at least 6 characters)"
              class="form-input"
              :class="{ error: errors.password }"
            >
            <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              v-model="form.confirmPassword"
              required
              placeholder="Confirm your password"
              class="form-input"
              :class="{ error: errors.confirmPassword }"
            >
            <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
          </div>

          <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
            {{ loading ? 'Signing up...' : 'Sign Up' }}
          </button>
        </form>

        <div class="auth-footer">
          <p>Already have an account? <router-link to="/login">Sign in</router-link></p>
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
  email: '',
  password: '',
  confirmPassword: ''
})

const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})
const generalError = ref('')

const validateForm = () => {
  // Clear previous errors
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })

  let isValid = true

  // Username validation
  if (!form.username.trim()) {
    errors.username = 'Please enter a username'
    isValid = false
  } else if (form.username.length < 3) {
    errors.username = 'Username must be at least 3 characters'
    isValid = false
  } else if (!/^[a-zA-Z0-9_]+$/.test(form.username)) {
    errors.username = 'Username may only contain letters, numbers and underscores'
    isValid = false
  }

  // 邮箱验证
  if (!form.email.trim()) {
    errors.email = 'Please enter an email address'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Please enter a valid email address'
    isValid = false
  }

  // 密码验证
  if (!form.password) {
    errors.password = 'Please enter a password'
    isValid = false
  } else if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    isValid = false
  } else {
    const hasLower = /[a-z]/.test(form.password)
    const hasUpper = /[A-Z]/.test(form.password)
    const hasDigit = /\d/.test(form.password)
    const hasSymbol = /[^A-Za-z0-9]/.test(form.password)
    if (!hasLower || !hasUpper || !hasDigit || !hasSymbol) {
      errors.password = 'Password must include uppercase, lowercase, number and symbol'
      isValid = false
    }
  }

  // 确认密码验证
  if (!form.confirmPassword) {
    errors.confirmPassword = 'Please confirm your password'
    isValid = false
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
    isValid = false
  }

  return isValid
}

const handleRegister = async () => {
  // 清除之前的错误
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
  generalError.value = ''

  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    await userStore.register({
      username: form.username.trim(),
      email: form.email.trim(),
      password: form.password
    })

    // 注册成功，跳转到首页
    router.push('/')

  } catch (error) {
    // 清除之前的错误（但不清除表单内容）
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

      // 优先显示后端字段级错误（假设格式 { errors: { username: '', email: '' } }）
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
        // 根据状态码和消息内容给出更明确的提示
        if (status === 400) {
          // 客户端错误 - 检查具体字段
          const msg = (data.message || '').toLowerCase()
          if (msg.includes('username') && msg.includes('exists')) {
            errors.username = 'This username is already taken'
          } else if (msg.includes('email') && msg.includes('exists')) {
            errors.email = 'This email address is already registered'
          } else if (msg.includes('username') && msg.includes('invalid')) {
            errors.username = 'Username contains invalid characters'
          } else if (msg.includes('email') && msg.includes('invalid')) {
            errors.email = 'Please enter a valid email address'
          } else if (msg.includes('password') && msg.includes('weak')) {
            errors.password = 'Password is too weak'
          } else {
            generalError.value = data.message || 'Please check your input and try again'
          }
        } else if (status === 409) {
          // 冲突错误 - 通常是重复注册
          const msg = (data.message || '').toLowerCase()
          if (msg.includes('username')) {
            errors.username = 'This username is already taken'
          } else if (msg.includes('email')) {
            errors.email = 'This email address is already registered'
          } else {
            generalError.value = data.message || 'Registration conflict'
          }
        } else if (status === 422) {
          // 验证错误
          generalError.value = data.message || 'Please check your input data'
        } else if (status >= 500) {
          // 服务器错误
          generalError.value = 'Server error — please try again later'
        } else {
          generalError.value = data.message
        }
      } else {
        generalError.value = `Registration failed (HTTP ${status})`
      }
    } else if (error.request) {
      // 请求发送但没有收到响应
      generalError.value = 'Unable to reach server — please check your network connection'
    } else {
      // 其他错误
      generalError.value = error.message || 'Registration failed — please try again later'
    }
  } finally {
    // 确保loading状态最终会被设置为false
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
  background: var(--light-panel);
  border-radius: 0.75rem;
  padding: 3rem;
  box-shadow: var(--shadow);
  width: 100%;
  max-width: 420px;
  color: var(--text-dark);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-dark);
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
  border-color: #6b46c1;
  box-shadow: 0 0 0 3px rgba(107, 70, 193, 0.1);
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
  color: #6b46c1;
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
