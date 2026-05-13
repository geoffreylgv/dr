<template>
  <div class="findings-list">
    <section data-section="cve">
      <h3>CVE findings <span class="count">{{ result.cve_findings.length }}</span></h3>
      <div v-if="result.cve_findings.length === 0" class="empty">No CVEs found</div>
      <div v-for="f in result.cve_findings" :key="f.id" class="finding" :class="f.severity.toLowerCase()">
        <div class="finding-header">
          <span class="sev-badge">{{ f.severity }}</span>
          <span class="vuln-id">{{ f.id }}</span>
          <span class="pkg">{{ f.package }}@{{ f.installed_version }}</span>
        </div>
        <div v-if="f.title" class="finding-title">{{ f.title }}</div>
        <div v-if="f.fixed_version" class="fix-hint">Fix: upgrade to {{ f.fixed_version }}</div>
      </div>
    </section>

    <section data-section="config">
      <h3>Config issues <span class="count">{{ result.config_findings.length }}</span></h3>
      <div v-if="result.config_findings.length === 0" class="empty">No config issues found</div>
      <div v-for="f in result.config_findings" :key="f.rule" class="finding" :class="f.severity.toLowerCase()">
        <div class="finding-header">
          <span class="sev-badge">{{ f.severity }}</span>
          <span class="rule-id">{{ f.rule }}</span>
        </div>
        <div class="finding-title">{{ f.message }}</div>
        <FixSnippet :yaml="f.fix_yaml" />
      </div>
    </section>
  </div>
</template>

<script setup>
import FixSnippet from './FixSnippet.vue'

defineProps({
  result: { type: Object, required: true },
})
</script>

<style scoped>
.findings-list { display: flex; flex-direction: column; gap: 24px; }
section h3 {
  font-size: .85rem; text-transform: uppercase; letter-spacing: .05em;
  color: #a0aec0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
}
.count {
  background: #2d3748; color: #e2e8f0; border-radius: 9999px;
  padding: 1px 8px; font-size: .75rem;
}
.finding {
  background: #171e2e; border-left: 3px solid #4a5568;
  border-radius: 0 6px 6px 0; padding: 10px 12px; margin-bottom: 8px;
}
.finding.critical { border-left-color: #fc8181; }
.finding.high { border-left-color: #f6ad55; }
.finding.medium { border-left-color: #faf089; }
.finding.low { border-left-color: #68d391; }
.finding-header { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.sev-badge {
  font-size: .7rem; font-weight: 700; text-transform: uppercase;
  padding: 2px 6px; border-radius: 4px; background: #2d3748;
}
.finding.critical .sev-badge { color: #fc8181; }
.finding.high .sev-badge { color: #f6ad55; }
.finding.medium .sev-badge { color: #faf089; }
.finding.low .sev-badge { color: #68d391; }
.vuln-id, .rule-id { font-family: monospace; font-size: .85rem; color: #90cdf4; }
.pkg { font-size: .8rem; color: #718096; }
.finding-title { font-size: .85rem; color: #cbd5e0; margin-bottom: 6px; }
.fix-hint { font-size: .8rem; color: #68d391; }
.empty { color: #4a5568; font-size: .85rem; }
</style>
