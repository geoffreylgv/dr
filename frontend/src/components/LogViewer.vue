<template>
  <div class="log-viewer">
    <div class="log-toolbar">
      <span class="status" :class="wsState">{{ statusLabel }}</span>
      <button class="clear-btn" @click="lines = []">Clear</button>
    </div>
    <div ref="logBox" class="log-box">
      <div v-for="(line, i) in lines" :key="i" class="log-line">{{ line }}</div>
      <div v-if="lines.length === 0" class="log-empty">No output yet</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  containerId: { type: String, required: true },
})

const lines = ref([])
const wsState = ref('connecting')
const logBox = ref(null)

let ws = null

const statusLabel = {
  connecting: 'Connecting…',
  open: 'Live',
  closed: 'Disconnected',
  error: 'Error',
}

function connect(containerId) {
  if (ws) ws.close()
  lines.value = []
  wsState.value = 'connecting'

  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  ws = new WebSocket(`${proto}://${location.host}/ws/logs/${containerId}`)

  ws.onopen = () => { wsState.value = 'open' }

  ws.onmessage = async (ev) => {
    const msg = JSON.parse(ev.data)
    if (msg.type === 'log') {
      lines.value.push(msg.line)
      if (lines.value.length > 500) lines.value.shift()
    } else if (msg.type === 'error') {
      wsState.value = 'closed'
    }
    await nextTick()
    if (logBox.value) logBox.value.scrollTop = logBox.value.scrollHeight
  }

  ws.onerror = () => { wsState.value = 'error' }

  ws.onclose = () => {
    if (wsState.value === 'open') {
      wsState.value = 'closed'
      setTimeout(() => connect(props.containerId), 2000)
    }
  }
}

watch(() => props.containerId, (id) => { if (id) connect(id) }, { immediate: true })

onUnmounted(() => { ws?.close() })
</script>

<style scoped>
.log-viewer { display: flex; flex-direction: column; gap: 8px; }
.log-toolbar { display: flex; justify-content: space-between; align-items: center; }
.status { font-size: .75rem; padding: 2px 8px; border-radius: 9999px; font-weight: 600; }
.status.open { background: #276749; color: #68d391; }
.status.connecting { background: #2d3748; color: #a0aec0; }
.status.closed, .status.error { background: #742a2a; color: #fc8181; }
.clear-btn {
  font-size: .75rem; padding: 2px 10px; border: 1px solid #4a5568;
  background: transparent; color: #a0aec0; border-radius: 4px; cursor: pointer;
}
.log-box {
  background: #0d1117; border: 1px solid #2d3748; border-radius: 6px;
  height: 320px; overflow-y: auto; padding: 10px 12px; font-family: 'Fira Code', monospace;
  font-size: .78rem; line-height: 1.6;
}
.log-line { color: #a0aec0; white-space: pre-wrap; word-break: break-all; }
.log-empty { color: #4a5568; }
</style>
