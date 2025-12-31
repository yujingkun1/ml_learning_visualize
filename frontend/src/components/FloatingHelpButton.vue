<template>
  <div class="floating-help-container">
    <button
      class="floating-help-button"
      :aria-expanded="isOpen.toString()"
      :aria-label="isMac ? 'Keyboard help - Press ? to toggle (Mac: Use ⌥ Option or ⌘ Cmd + A for accessibility mode)' : 'Keyboard help - Press ? to toggle'"
      @click="toggle"
    >
    <div class="button-content">
  <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" focusable="false">
    <rect x="2" y="5" width="20" height="14" rx="2" stroke="currentColor" stroke-width="1.5" fill="none"/>
    <rect x="4" y="8" width="2" height="2" rx="0.4" fill="currentColor"/>
    <rect x="8" y="8" width="2" height="2" rx="0.4" fill="currentColor"/>
    <rect x="12" y="8" width="2" height="2" rx="0.4" fill="currentColor"/>
    <rect x="16" y="8" width="2" height="2" rx="0.4" fill="currentColor"/>
    <rect x="4" y="12" width="12" height="2" rx="0.4" fill="currentColor"/>
  </svg>
      <span class="shortcut-hint">?</span>
    </div>
    </button>

    <!-- Accessibility mode toggle -->
    <button
      class="accessibility-toggle"
      :class="{ active: accessibilityStore.accessibilityMode }"
      :aria-pressed="accessibilityStore.accessibilityMode.toString()"
      :aria-label="isMac ? 'Toggle accessibility mode - Press ⌥ Option or ⌘ Cmd + A' : 'Toggle accessibility mode - Press Alt+A'"
      @click="toggleAccessibility"
    >
      <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" fill="currentColor"/>
      </svg>
      <span class="accessibility-hint">A</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAccessibilityStore } from '@/stores/accessibility'
import KeyboardHelpModal from './KeyboardHelpModal.vue'

// 检测操作系统
const isMac = computed(() => {
  return navigator.platform.toUpperCase().indexOf('MAC') >= 0
})

const accessibilityStore = useAccessibilityStore()
const isOpen = ref(false)

const toggle = () => {
  isOpen.value = !isOpen.value
  // Prefer calling exposed function if available for reliability
  const win = window as any
  if (typeof win.toggleKeyboardHelp === 'function') {
    win.toggleKeyboardHelp()
    return
  }
  // fallback to event
  window.dispatchEvent(new CustomEvent('keyboard-help-toggle', { detail: { open: isOpen.value } }))
}

const toggleAccessibility = () => {
  accessibilityStore.toggleAccessibilityMode()
}
</script>

<style scoped>
.floating-help-button {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--accent-color);
  color: var(--text-light);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.25rem;
  box-shadow: 0 6px 20px rgba(39,64,96,0.18);
  border: none;
  cursor: pointer;
  z-index: 120;
  transition: transform 0.12s ease;
}
.floating-help-button:active { transform: scale(0.98); }

.button-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.shortcut-hint {
  font-size: 0.75rem;
  font-weight: 600;
  opacity: 0.9;
  line-height: 1;
}

.floating-help-container {
  position: fixed;
  right: 20px;
  bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 120;
}

.accessibility-toggle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--bg-light);
  color: var(--text-dark);
  border: 2px solid var(--border-color);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.12s ease;
}

.accessibility-toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.accessibility-toggle:active {
  transform: scale(0.95);
}

.accessibility-toggle.active {
  background: var(--accent-color);
  color: var(--text-light);
  border-color: var(--accent-color);
}

.accessibility-toggle svg {
  display: block;
}

.accessibility-hint {
  font-size: 0.6rem;
  font-weight: 600;
  opacity: 0.8;
  line-height: 1;
  margin-top: 1px;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .floating-help-container {
    right: 16px;
    bottom: 16px;
  }

  .floating-help-button,
  .accessibility-toggle {
    width: 48px;
    height: 48px;
  }
}
</style>


