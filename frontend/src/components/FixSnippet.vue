<template>
  <div class="fix-snippet">
    <div class="snippet-header">
      <span class="snippet-label">Suggested fix</span>
      <button
        class="copy-btn"
        data-testid="copy-btn"
        :class="{ copied }"
        @click="copy"
      >
        {{ copied ? 'Copied!' : 'Copy' }}
      </button>
    </div>
    <code>{{ yaml }}</code>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  yaml: { type: String, required: true },
})

const copied = ref(false)

async function copy() {
  await navigator.clipboard.writeText(props.yaml)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>

<style scoped>
.fix-snippet {
  background: #0d1117; border: 1px solid #2d3748; border-radius: 6px;
  margin-top: 8px; overflow: hidden;
}
.snippet-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 4px 10px; background: #1a202c; border-bottom: 1px solid #2d3748;
}
.snippet-label { font-size: .7rem; color: #718096; text-transform: uppercase; letter-spacing: .05em; }
.copy-btn {
  font-size: .75rem; padding: 2px 10px; border: 1px solid #4a5568;
  background: transparent; color: #a0aec0; border-radius: 4px; cursor: pointer;
  transition: background .1s;
}
.copy-btn:hover { background: #2d3748; }
.copy-btn.copied { color: #68d391; border-color: #68d391; }
code {
  display: block; padding: 10px 12px; font-family: 'Fira Code', monospace;
  font-size: .8rem; color: #90cdf4; white-space: pre; overflow-x: auto;
}
</style>
