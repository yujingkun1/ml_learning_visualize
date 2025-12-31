<template>
  <div id="app">
    <nav class="nav nav-light">
      <div class="container nav-content">
        <router-link to="/" class="nav-brand" aria-label="Home">
          <img src="/assets/logo.svg" alt="ML Learner logo" class="logo-mark" />
          <h1 class="brand-title">ML Learner</h1>
        </router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">Home</router-link>
          <router-link to="/algorithms" class="nav-link">Learn</router-link>
          <router-link to="/posts" class="nav-link">Community</router-link>
          <router-link v-if="isLoggedIn" to="/chat" class="nav-link">Chat</router-link>
          <router-link v-if="isLoggedIn" to="/profile" class="nav-link">Profile</router-link>
          <router-link v-if="userStore.isAdmin" to="/admin" class="nav-link">Admin</router-link>
          <router-link v-if="!isLoggedIn" to="/login" class="nav-link btn-ghost">Sign In</router-link>
          <button v-if="isLoggedIn" @click="logout" class="btn btn-outline">Sign Out</button>
        </div>

        <!-- Mobile menu button -->
        <button
          class="mobile-menu-btn"
          @click="toggleMobileMenu"
          aria-label="Toggle mobile menu"
          :aria-expanded="mobileMenuOpen"
        >
          <i class="fas" :class="mobileMenuOpen ? 'fa-times' : 'fa-bars'"></i>
        </button>
      </div>

      <!-- Mobile menu overlay -->
      <div v-if="mobileMenuOpen" class="mobile-menu-overlay" @click="toggleMobileMenu">
        <div class="mobile-menu" @click.stop>
          <div class="mobile-menu-header">
            <h3>Menu</h3>
            <button @click="toggleMobileMenu" class="mobile-menu-close">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <nav class="mobile-menu-nav">
            <router-link to="/" class="mobile-menu-link" @click="toggleMobileMenu">
              <i class="fas fa-home"></i>
              Home
            </router-link>
            <router-link to="/algorithms" class="mobile-menu-link" @click="toggleMobileMenu">
              <i class="fas fa-graduation-cap"></i>
              Learn
            </router-link>
            <router-link to="/posts" class="mobile-menu-link" @click="toggleMobileMenu">
              <i class="fas fa-users"></i>
              Community
            </router-link>
            <router-link v-if="isLoggedIn" to="/chat" class="mobile-menu-link" @click="toggleMobileMenu">
              <i class="fas fa-comments"></i>
              Chat
            </router-link>
            <router-link v-if="isLoggedIn" to="/profile" class="mobile-menu-link" @click="toggleMobileMenu">
              <i class="fas fa-user"></i>
              Profile
            </router-link>
            <router-link v-if="userStore.isAdmin" to="/admin" class="mobile-menu-link" @click="toggleMobileMenu">
              <i class="fas fa-cog"></i>
              Admin
            </router-link>
            <div class="mobile-menu-divider"></div>
            <router-link v-if="!isLoggedIn" to="/login" class="mobile-menu-link btn-ghost" @click="toggleMobileMenu">
              <i class="fas fa-sign-in-alt"></i>
              Sign In
            </router-link>
            <button v-if="isLoggedIn" @click="logout" class="mobile-menu-link mobile-logout-btn">
              <i class="fas fa-sign-out-alt"></i>
              Sign Out
            </button>
          </nav>
        </div>
      </div>
    </nav>
    <!-- spacer to prevent fixed nav overlapping content -->
    <div class="nav-spacer" aria-hidden="true"></div>
    <main>
      <router-view :key="$route.fullPath" />
      <!-- keyboard help modal + floating button inserted globally -->
      <KeyboardHelpModal />
      <FloatingHelpButton />
    </main>
    <footer class="site-footer" role="contentinfo">
      <div class="container">
        <div>
          <div class="footer-brand">
            <img src="/assets/logo.svg" alt="ML Learner logo" class="logo-mark" />
            <div>
              <h3 class="brand-title" style="margin-bottom:6px;color:var(--text-dark);">ML Learner</h3>
              <p style="margin:0;color:var(--text-muted);max-width:320px;">Beautifully designed learning paths, interactive demos and a supportive community.</p>
            </div>
          </div>
        </div>

        <div class="footer-links" aria-label="Site links">
          <strong style="color:#000000;margin-bottom:8px;display:block;">Explore</strong>
          <a href="/">Home</a>
          <a href="/algorithms">Algorithms</a>
          <a href="/posts">Community</a>
        </div>

        <div class="footer-links" aria-label="Resources">
          <strong style="color:#000000;margin-bottom:8px;display:block;">Resources</strong>
          <a href="/register">Get started</a>
          <a href="/profile">Your profile</a>
          <a href="/admin">Admin</a>
        </div>
      </div>
      <div class="footer-bottom">© <span id="year">{{ new Date().getFullYear() }}</span> ML Learner · Crafted with care</div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAccessibilityStore } from '@/stores/accessibility'
import KeyboardHelpModal from '@/components/KeyboardHelpModal.vue'
import FloatingHelpButton from '@/components/FloatingHelpButton.vue'
import { useKeyboardManager } from '@/composables/useKeyboardManager'

const router = useRouter()
const userStore = useUserStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const mobileMenuOpen = ref(false)

const logout = async () => {
  await userStore.logout()
  router.push('/')
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

// add scroll behavior to nav: toggles .scrolled when page is scrolled
const onScroll = () => {
  const nav = document.querySelector('.nav') as HTMLElement | null
  if (!nav) return
  if (window.scrollY > 24) {
    nav.classList.add('scrolled')
    nav.classList.add('nav-dark')
    nav.classList.remove('nav-light')
  } else {
    nav.classList.remove('scrolled')
    nav.classList.add('nav-light')
    nav.classList.remove('nav-dark')
  }
}

onMounted(() => {
  // Keep nav behavior simple and stable:
  // - nav is fixed at top (CSS)
  // - when scrolled past threshold, switch to dark theme; otherwise light theme
  const nav = document.querySelector('.nav') as HTMLElement | null
  window.addEventListener('scroll', onScroll, { passive: true })
  // initial state
  if (nav) {
    if (window.scrollY > 24) {
      nav.classList.add('nav-dark')
      nav.classList.remove('nav-light')
    } else {
      nav.classList.add('nav-light')
      nav.classList.remove('nav-dark')
    }
  }

  // Initialize accessibility store
  const accessibilityStore = useAccessibilityStore()
  accessibilityStore.initAccessibilityMode()
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
})

// initialize global keyboard manager
useKeyboardManager(router)
</script>
 
