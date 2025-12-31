<template>
  <div class="ai-analysis">
    <div class="analysis-header">
      <h3>🤖 AI Learning Analysis</h3>
      <p>Get personalized insights about your learning progress and recommendations</p>
    </div>

    <div class="analysis-controls">
      <button
        class="btn btn-primary generate-report-btn"
        @click="generateLearningReport"
        :disabled="generatingReport"
      >
        <i class="fas fa-chart-line"></i>
        {{ generatingReport ? 'Analyzing...' : 'Generate Learning Report' }}
      </button>
    </div>

    <div v-if="learningReport" class="report-content">
      <div class="report-header">
        <h4>📊 Your Learning Report</h4>
        <span class="report-date">{{ formatDate(new Date()) }}</span>
      </div>

      <div class="report-body">
        <VueMarkdownRender :source="learningReport" />
      </div>
    </div>

    <div v-else-if="!generatingReport" class="no-report">
      <i class="fas fa-brain fa-2x"></i>
      <h4>Ready for AI Analysis</h4>
      <p>Click the button above to let AI analyze your learning data and provide personalized suggestions</p>
    </div>

    <div v-if="generatingReport" class="loading-report">
      <div class="loading-spinner">
        <div class="spinner"></div>
      </div>
      <h4>AI is analyzing your learning data...</h4>
      <p>This may take a few seconds, please be patient</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import VueMarkdownRender from 'vue-markdown-render'

const userStore = useUserStore()

// AI分析相关
const learningReport = ref('')
const generatingReport = ref(false)

// 生成学习报告
const generateLearningReport = async () => {
  if (!userStore.isLoggedIn) {
    alert('Please login first')
    return
  }

  generatingReport.value = true
  try {
    const response = await axios.post('/api/ai/generate-learning-report')

    if (response.data.success) {
      learningReport.value = response.data.report
      console.log('AI learning report generated successfully:', response.data)
    } else {
      alert('Failed to generate report: ' + response.data.message)
    }
  } catch (error: any) {
    console.error('Failed to generate learning report:', error)
    alert('Failed to generate report, please try again later: ' + (error.response?.data?.message || error.message))
  } finally {
    generatingReport.value = false
  }
}

// 格式化日期
const formatDate = (date: Date) => {
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 重置报告（可选，用于外部调用）
const resetReport = () => {
  learningReport.value = ''
}

defineExpose({
  generateLearningReport,
  resetReport
})
</script>

<style scoped>
.ai-analysis {
  background: var(--brand-panel);
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-soft);
  color: var(--text-dark);
}

.analysis-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-dark);
}

.analysis-header p {
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

.analysis-controls {
  margin-bottom: 2rem;
}

.generate-report-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  color: #ffffff;
}

.generate-report-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.report-content {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-top: 1rem;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.report-header h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-dark);
  margin: 0;
}

.report-date {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.report-body {
  line-height: 1.6;
  color: var(--text-dark);
}

/* Markdown content styling */
.report-body :deep(h1),
.report-body :deep(h2),
.report-body :deep(h3),
.report-body :deep(h4),
.report-body :deep(h5),
.report-body :deep(h6) {
  color: var(--text-dark);
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  line-height: 1.3;
}

.report-body :deep(h3) {
  font-size: 1.1rem;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}

.report-body :deep(p) {
  margin-bottom: 1rem;
  line-height: 1.6;
}

.report-body :deep(ul),
.report-body :deep(ol) {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.report-body :deep(li) {
  margin-bottom: 0.25rem;
  line-height: 1.5;
}

.report-body :deep(strong),
.report-body :deep(b) {
  font-weight: 600;
  color: var(--text-dark);
}

.report-body :deep(em),
.report-body :deep(i) {
  font-style: italic;
}

.report-body :deep(code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875em;
  color: #d73a49;
}

.report-body :deep(pre) {
  background: rgba(0, 0, 0, 0.05);
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 1rem 0;
}

.report-body :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}

.report-body :deep(blockquote) {
  border-left: 4px solid #e5e7eb;
  padding-left: 1rem;
  margin: 1rem 0;
  color: var(--text-muted);
  font-style: italic;
}

.report-body :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 1.5rem 0;
}

.report-body h3 {
  color: var(--text-dark);
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.report-body ul {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.report-body li {
  margin-bottom: 0.25rem;
}

.no-report {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}

.no-report i {
  color: #9ca3af;
  margin-bottom: 1rem;
  display: block;
}

.no-report h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-dark);
}

.loading-report {
  text-align: center;
  padding: 2rem;
}

.loading-spinner {
  display: inline-block;
  margin-bottom: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #1e40af; /* darker blue for better contrast */
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-report h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-dark);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-analysis {
    padding: 1rem;
  }

  .report-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .generate-report-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
