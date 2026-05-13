<template>
  <div :class="['score-display', tier, { compact }]" data-testid="score-display">
    <span class="number">{{ score }}</span>
    <span v-if="!compact" class="label">/ 100</span>
    <span v-if="!compact" class="tier-label">{{ tierLabel }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: { type: Number, required: true },
  compact: { type: Boolean, default: false },
})

const tier = computed(() => {
  if (props.score <= 40) return 'score-danger'
  if (props.score <= 70) return 'score-warning'
  return 'score-good'
})

const tierLabel = computed(() => {
  if (props.score <= 40) return 'Critical issues'
  if (props.score <= 70) return 'Needs attention'
  return 'Good'
})
</script>

<style scoped>
.score-display {
  display: flex; align-items: baseline; gap: 6px;
  font-weight: 700;
}
.score-display:not(.compact) {
  flex-direction: column; align-items: flex-start; margin-bottom: 24px;
}
.number { font-size: 3.5rem; line-height: 1; }
.compact .number { font-size: 1.1rem; }
.label { font-size: 1.2rem; color: #718096; }
.tier-label { font-size: .85rem; text-transform: uppercase; letter-spacing: .05em; }
.score-danger .number, .score-danger .tier-label { color: #fc8181; }
.score-warning .number, .score-warning .tier-label { color: #f6ad55; }
.score-good .number, .score-good .tier-label { color: #68d391; }
</style>
