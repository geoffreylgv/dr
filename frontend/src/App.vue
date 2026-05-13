<template>
  <div id="app">
    <header>
      <h1>Docker Doctor</h1>
      <p class="tagline">Security score + actionable fixes for your containers</p>
    </header>

    <main>
      <section class="containers">
        <div v-if="loading" class="state-msg">Loading containers...</div>
        <div v-else-if="error" class="state-msg error">{{ error }}</div>
        <template v-else>
          <div
            v-for="c in containers"
            :key="c.id"
            class="container-card"
            :class="{ selected: selected?.id === c.id }"
            @click="selectContainer(c)"
          >
            <div class="card-info">
              <span class="name">{{ c.name }}</span>
              <span class="image">{{ c.image }}</span>
            </div>
            <ScoreDisplay v-if="scores[c.id]" :score="scores[c.id].score" :compact="true" />
            <button
              class="scan-btn"
              :disabled="scanning[c.id]"
              @click.stop="scanContainer(c)"
            >
              {{ scanning[c.id] ? 'Scanning…' : 'Scan' }}
            </button>
          </div>
        </template>
      </section>

      <section v-if="selected && scores[selected.id]" class="detail">
        <ScoreDisplay :score="scores[selected.id].score" />
        <FindingsList :result="scores[selected.id]" />
      </section>

      <section v-if="selected" class="logs">
        <h2>Live logs — {{ selected.name }}</h2>
        <LogViewer :container-id="selected.full_id" />
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ScoreDisplay from './components/ScoreDisplay.vue'
import FindingsList from './components/FindingsList.vue'
import LogViewer from './components/LogViewer.vue'

const containers = ref([])
const loading = ref(true)
const error = ref(null)
const selected = ref(null)
const scores = ref({})
const scanning = ref({})

onMounted(async () => {
  try {
    const res = await fetch('/api/containers')
    if (!res.ok) throw new Error(await res.text())
    containers.value = await res.json()
  } catch (e) {
    error.value = `Could not reach Docker: ${e.message}`
  } finally {
    loading.value = false
  }
})

function selectContainer(c) {
  selected.value = c
}

async function scanContainer(c) {
  scanning.value[c.id] = true
  try {
    const res = await fetch(`/api/scan/${c.id}`, { method: 'POST' })
    if (!res.ok) throw new Error(await res.text())
    scores.value[c.id] = await res.json()
    selected.value = c
  } catch (e) {
    alert(`Scan failed: ${e.message}`)
  } finally {
    scanning.value[c.id] = false
  }
}
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, sans-serif; background: #0f1117; color: #e2e8f0; }
#app { max-width: 1200px; margin: 0 auto; padding: 24px; }
header { margin-bottom: 32px; }
header h1 { font-size: 2rem; font-weight: 700; color: #63b3ed; }
.tagline { color: #718096; margin-top: 4px; }
main { display: grid; grid-template-columns: 340px 1fr; gap: 24px; }
.containers { display: flex; flex-direction: column; gap: 8px; }
.container-card {
  background: #1a202c; border: 1px solid #2d3748; border-radius: 8px;
  padding: 12px 16px; cursor: pointer; display: flex; align-items: center;
  gap: 12px; transition: border-color .15s;
}
.container-card:hover, .container-card.selected { border-color: #63b3ed; }
.card-info { flex: 1; min-width: 0; }
.name { display: block; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.image { display: block; font-size: .75rem; color: #718096; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.scan-btn {
  padding: 6px 14px; background: #2b6cb0; color: white; border: none;
  border-radius: 6px; cursor: pointer; font-size: .85rem; white-space: nowrap;
}
.scan-btn:disabled { opacity: .5; cursor: not-allowed; }
.detail { background: #1a202c; border: 1px solid #2d3748; border-radius: 8px; padding: 24px; }
.logs { grid-column: 1 / -1; background: #1a202c; border: 1px solid #2d3748; border-radius: 8px; padding: 16px; }
.logs h2 { font-size: 1rem; margin-bottom: 12px; color: #a0aec0; }
.state-msg { color: #718096; padding: 16px; }
.state-msg.error { color: #fc8181; }
</style>
