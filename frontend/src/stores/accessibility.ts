import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAccessibilityStore = defineStore('accessibility', () => {
  const accessibilityMode = ref(false)

  const toggleAccessibilityMode = () => {
    accessibilityMode.value = !accessibilityMode.value
    // 保存到localStorage
    localStorage.setItem('accessibility-mode', accessibilityMode.value.toString())
    // 触发自定义事件通知组件更新
    window.dispatchEvent(new CustomEvent('accessibility-mode-changed', {
      detail: { enabled: accessibilityMode.value }
    }))
  }

  const setAccessibilityMode = (enabled: boolean) => {
    accessibilityMode.value = enabled
    localStorage.setItem('accessibility-mode', enabled.toString())
    window.dispatchEvent(new CustomEvent('accessibility-mode-changed', {
      detail: { enabled }
    }))
  }

  // 初始化时从localStorage读取设置
  const initAccessibilityMode = () => {
    const saved = localStorage.getItem('accessibility-mode')
    if (saved !== null) {
      accessibilityMode.value = saved === 'true'
    }
  }

  return {
    accessibilityMode: computed(() => accessibilityMode.value),
    toggleAccessibilityMode,
    setAccessibilityMode,
    initAccessibilityMode
  }
})
