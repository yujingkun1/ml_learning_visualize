<template>
  <teleport to="body">
    <div v-if="visible" class="keyboard-help-overlay" @click.self="close" role="dialog" aria-modal="true" aria-label="Keyboard shortcuts help">
      <div class="keyboard-help-panel" ref="panel" tabindex="-1">
      <header class="kbd-header">
        <h3>键盘快捷键</h3>
        <button class="close" @click="close" aria-label="Close keyboard help">✕</button>
      </header>

      <div class="kbd-body">
        <div class="kbd-content">
          <div class="shortcut-group">
            <h4 class="group-title">导航快捷键</h4>
            <ul class="shortcuts">
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">1</kbd></span>：跳转到首页 (Home)</li>
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">2</kbd></span>：跳转到算法学习页 (Learn)</li>
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">3</kbd></span>：跳转到社区页面 (Community)</li>
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">4</kbd></span>：跳转到聊天页面 (Chat)</li>
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">5</kbd></span>：跳转到个人资料页 (Profile)</li>
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">6</kbd></span>：跳转到管理页面 (Admin)</li>
            </ul>
          </div>

          <div class="shortcut-group">
            <h4 class="group-title">页面操作</h4>
            <ul class="shortcuts">
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">+</kbd></span>：在社区页面创建新帖子</li>
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">P</kbd></span>：在帖子详情页收藏/取消收藏</li>
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">K</kbd></span>：聚焦搜索框</li>
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">G</kbd></span>：跳转到当前页面的第N个帖子</li>
            </ul>
          </div>

          <div class="shortcut-group">
            <h4 class="group-title">辅助功能模式</h4>
            <ul class="shortcuts">
              <li v-if="isMac">
                <span class="kbd"><kbd class="kbd-key highlight">⌥ Option</kbd> / <kbd class="kbd-key highlight">⌘ Cmd</kbd> + <kbd class="kbd-key highlight">A</kbd></span>：开启/关闭辅助功能模式
              </li>
              <li v-else>
                <span class="kbd"><kbd class="kbd-key highlight">Alt</kbd> + <kbd class="kbd-key highlight">A</kbd></span>：开启/关闭辅助功能模式
              </li>
              <li v-if="isMac">
                <span class="kbd"><kbd class="kbd-key highlight">⌥ Option</kbd> / <kbd class="kbd-key highlight">⌘ Cmd</kbd> + <kbd class="kbd-key highlight">1-9</kbd></span>：快速跳转到对应序号的帖子（辅助模式下）
              </li>
              <li v-else>
                <span class="kbd"><kbd class="kbd-key highlight">Alt</kbd> + <kbd class="kbd-key highlight">1-9</kbd></span>：快速跳转到对应序号的帖子（辅助模式下）
              </li>
            </ul>
            <p class="group-desc">启用辅助功能模式后，每个帖子卡片会显示快捷键提示，让您可以通过键盘快速导航。</p>
            <p v-if="isMac" class="group-note mac-note">
              <strong>Mac用户提示：</strong> 可以使用 <kbd>⌥ Option</kbd> 键或 <kbd>⌘ Cmd</kbd> + A 来切换辅助模式，<kbd>⌥ Option</kbd> / <kbd>⌘ Cmd</kbd> + 数字键来快速跳转。
            </p>
          </div>

          <div class="shortcut-group">
            <h4 class="group-title">通用操作</h4>
          <ul class="shortcuts">
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">[</kbd></span>：历史后退</li>
              <li><span class="kbd"><kbd class="kbd-key highlight">Ctrl</kbd> + <kbd class="kbd-key highlight">]</kbd></span>：历史前进</li>
              <li><span class="kbd"><kbd class="kbd-key">?</kbd></span>：显示/隐藏键盘帮助</li>
              <li><span class="kbd"><kbd class="kbd-key">Space</kbd></span>：播放/暂停（交互演示）</li>
              <li><span class="kbd"><kbd class="kbd-key">C</kbd></span>：关闭模态框/返回上一级</li>
              <li><span class="kbd"><kbd class="kbd-key">Esc</kbd></span>：关闭键盘帮助</li>
          </ul>
          </div>
        </div>
      </div>
      <footer class="kbd-footer">
        <small>按 <kbd>Esc</kbd> 或点击空白处关闭。颜色与站点主题一致。</small>
        <div v-if="isMac" class="mac-info">
          <small>💡 Mac用户：使用 <kbd>⌥ Option</kbd> 键代替 <kbd>Alt</kbd> 键</small>
        </div>
      </footer>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'

// 检测操作系统
const isMac = computed(() => {
  return navigator.platform.toUpperCase().indexOf('MAC') >= 0
})

const visible = ref(false)
const panel = ref<HTMLElement | null>(null)
const router = useRouter()


const open = () => {
  visible.value = true
  // trap focus
  setTimeout(() => panel.value?.focus(), 0)
  document.body.style.overflow = 'hidden'
}
const close = () => {
  visible.value = false
  document.body.style.overflow = ''
}

const onGlobalToggle = (e: Event) => {
  const detail = (e as CustomEvent).detail
  if (detail && typeof detail.open === 'boolean') {
    if (detail.open) open(); else close()
  } else {
    // simple toggle if no detail
    if (visible.value) close(); else open()
  }
}

const onKey = (ev: KeyboardEvent) => {
  if (!visible.value) return
  if (ev.key === 'Escape') { close(); return }
  // basic focus trap: keep tab within panel
  if (ev.key === 'Tab') {
    const container = panel.value
    if (!container) return
    const focusable = Array.from(container.querySelectorAll<HTMLElement>('a,button,input,select,textarea,[tabindex]:not([tabindex="-1"])'))
      .filter(el => !el.hasAttribute('disabled') && el.offsetParent !== null)
    if (!focusable.length) return
    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    if (!ev.shiftKey && document.activeElement === last) {
      first.focus()
      ev.preventDefault()
    } else if (ev.shiftKey && document.activeElement === first) {
      last.focus()
      ev.preventDefault()
    }
  }
}

onMounted(() => {
  window.addEventListener('keyboard-help-toggle', onGlobalToggle as EventListener)
  window.addEventListener('keydown', onKey)
  // expose a direct toggle function for reliability when other components call it
  ;(window as any).toggleKeyboardHelp = () => { if (visible.value) close(); else open() }
})
onBeforeUnmount(() => {
  window.removeEventListener('keyboard-help-toggle', onGlobalToggle as EventListener)
  window.removeEventListener('keydown', onKey)
  try { delete (window as any).toggleKeyboardHelp } catch (e) {}
})
</script>

<style scoped>
.keyboard-help-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10,10,10,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 110;
}
.keyboard-help-panel {
  width: min(920px, 94%);
  max-height: 86vh;
  background: var(--brand-panel);
  color: var(--text-dark);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 1rem;
  outline: none;
  display: flex;
  flex-direction: column;
}
.kbd-header {
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:0.5rem;
}
.kbd-header h3 { margin:0; }
.kbd-header .close {
  background: transparent;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
}
.kbd-body {
  overflow:auto;
  padding: 0.5rem 0;
}

.kbd-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.shortcut-group {
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

.shortcut-group:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.group-title {
  margin: 0 0 0.75rem 0;
  color: var(--text-dark);
  font-size: 1rem;
  font-weight: 600;
}
.kbd-image {
  max-width: 100%;
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(0,0,0,0.02), rgba(0,0,0,0.02));
}
.shortcuts { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:0.6rem; }
.shortcuts li { line-height:1.5; }
.shortcuts kbd { background:#f3f3f3; padding:0.12rem 0.4rem; border-radius:4px; border:1px solid #e3e3e3; }
.kbd-footer { margin-top:0.75rem; text-align:right; color:var(--text-muted); }
.shortcuts .kbd { display:inline-flex; gap:0.25rem; align-items:center; }
.kbd-key {
  display:inline-block;
  min-width:24px;
  text-align:center;
  padding:0.18rem 0.45rem;
  border-radius:6px;
  border:1px solid rgba(0,0,0,0.08);
  background: #f7f7f7;
  color: var(--text-dark);
  font-weight:600;
  box-shadow: 0 1px 0 rgba(0,0,0,0.03), inset 0 -1px 0 rgba(255,255,255,0.6);
}
.kbd-key.highlight {
  background: var(--accent-color);
  color: var(--text-light);
  border-color: rgba(0,0,0,0.06);
  box-shadow: 0 6px 18px rgba(39,64,96,0.16);
}

/* Mac-specific styles */
.mac-note {
  background: #e3f2fd;
  padding: 0.75rem;
  border-radius: 6px;
  border-left: 4px solid #2196f3;
  margin-top: 1rem;
}

.mac-info {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #fff3cd;
  border-radius: 4px;
  border: 1px solid #ffeaa7;
}

.mac-info small {
  color: #856404;
}
</style>


