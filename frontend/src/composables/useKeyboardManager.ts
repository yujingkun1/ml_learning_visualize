import { onMounted, onBeforeUnmount, computed } from 'vue'
import { Router } from 'vue-router'
import { useAccessibilityStore } from '@/stores/accessibility'

type ShortcutHandler = (event: KeyboardEvent) => void

// 检测操作系统
const isMac = computed(() => {
  return navigator.platform.toUpperCase().indexOf('MAC') >= 0
})

export function useKeyboardManager(router: Router) {
  const handlers: Record<string, ShortcutHandler> = {}
  const accessibilityStore = useAccessibilityStore()

  const register = (keyCombo: string, handler: ShortcutHandler) => {
    handlers[keyCombo] = handler
  }

  const globalKeydown = (ev: KeyboardEvent) => {
    // build a normalized combo string like "Ctrl+1" or "Ctrl+Plus" or "Space"
    const parts: string[] = []
    if (ev.ctrlKey) parts.push('Ctrl')
    if (ev.metaKey) parts.push('Meta')
    if (ev.altKey) parts.push('Alt')
    if (ev.shiftKey) parts.push('Shift')
    const keyName = ev.key.length === 1 ? ev.key.toUpperCase() : ev.key
    parts.push(keyName)
    const combo = parts.join('+')

    // exact match handlers
    if (handlers[combo]) {
      try { handlers[combo](ev) } catch (e) { console.error(e) }
      ev.preventDefault()
      return
    }

    // fallback / simpler mappings
    // Ctrl+1..7 -> navigation
    if (ev.ctrlKey && !ev.shiftKey && !ev.altKey) {
      if (/[1-7]/.test(ev.key)) {
        const map: Record<string,string> = {
          '1': 'Home',
          '2': 'Algorithms',
          '3': 'Posts',
          '4': 'Chat',
          '5': 'Profile',
          '6': 'Admin'
        }
        const name = map[ev.key]
        if (name) router.push({ name })
        ev.preventDefault()
        return
      }
      // Ctrl + + (plus) : open create post
      if (ev.key === '+') {
        window.dispatchEvent(new CustomEvent('open-create-post'))
        ev.preventDefault()
        return
      }
      // Ctrl + [ / ] history back/forward
      if (ev.key === '[') { window.history.back(); ev.preventDefault(); return }
      if (ev.key === ']') { window.history.forward(); ev.preventDefault(); return }
    }

    // Ctrl+G: prompt for post index on current page and go
    if (ev.ctrlKey && ev.key.toLowerCase() === 'g') {
      const index = window.prompt('跳转到当前页面的第几个帖子（1-12）：')
      if (index) {
        window.dispatchEvent(new CustomEvent('jump-to-post-by-index', { detail: { index: parseInt(index) } }))
      }
      ev.preventDefault()
      return
    }

    // Ctrl+P: toggle favorite on post detail page
    if (ev.ctrlKey && ev.key.toLowerCase() === 'p') {
      window.dispatchEvent(new CustomEvent('toggle-post-favorite'))
      ev.preventDefault()
      return
    }

    // Ctrl+K: try focus site search input if exists
    if (ev.ctrlKey && ev.key.toLowerCase() === 'k') {
      const search = document.querySelector<HTMLInputElement>('input[type="search"], input[aria-label="search"], .search-input, .site-search input')
      if (search) { search.focus(); ev.preventDefault(); return }
    }

    // ?: toggle keyboard help modal
    if (ev.key === '?') {
      window.dispatchEvent(new CustomEvent('keyboard-help-toggle'))
      ev.preventDefault()
      return
    }

    // Alt+A (Mac: Option+A) or Cmd+A: toggle accessibility mode
    if ((ev.altKey || (isMac.value && ev.metaKey)) && ev.key.toLowerCase() === 'a') {
      accessibilityStore.toggleAccessibilityMode()
      ev.preventDefault()
      return
    }

    // Alt+1-9 (Mac: Option+1-9): accessibility shortcuts for elements
    if ((ev.altKey || (isMac.value && ev.metaKey)) && accessibilityStore.accessibilityMode && /^[1-9]$/.test(ev.key)) {
      const index = parseInt(ev.key) - 1
      window.dispatchEvent(new CustomEvent('accessibility-shortcut', {
        detail: { index, type: 'post' }
      }))
      ev.preventDefault()
      return
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', globalKeydown)
    accessibilityStore.initAccessibilityMode()
  })
  onBeforeUnmount(() => {
    window.removeEventListener('keydown', globalKeydown)
  })

  return { register }
}


