import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ScoreDisplay from '../components/ScoreDisplay.vue'
import FindingsList from '../components/FindingsList.vue'
import FixSnippet from '../components/FixSnippet.vue'

describe('ScoreDisplay', () => {
  it('renders score-danger class for score 0-40', () => {
    const w = mount(ScoreDisplay, { props: { score: 30 } })
    expect(w.classes()).toContain('score-danger')
  })

  it('renders score-warning class for score 41-70', () => {
    const w = mount(ScoreDisplay, { props: { score: 55 } })
    expect(w.classes()).toContain('score-warning')
  })

  it('renders score-good class for score 71-100', () => {
    const w = mount(ScoreDisplay, { props: { score: 85 } })
    expect(w.classes()).toContain('score-good')
  })
})

describe('FindingsList', () => {
  const mockResult = {
    score: 60,
    cve_findings: [
      { id: 'CVE-2024-1234', severity: 'HIGH', package: 'openssl', installed_version: '1.0', fixed_version: '1.1', title: 'Buffer overflow' }
    ],
    config_findings: [
      { rule: 'no_memory_limit', severity: 'MEDIUM', message: 'No memory limit set', fix_yaml: 'deploy:\n  resources:\n    limits:\n      memory: 512M' }
    ],
    breakdown: { cve_penalty: 8, config_penalty: 5 },
  }

  it('renders CVE and config findings in separate sections', () => {
    const w = mount(FindingsList, { props: { result: mockResult } })
    expect(w.find('[data-section="cve"]').exists()).toBe(true)
    expect(w.find('[data-section="config"]').exists()).toBe(true)
  })
})

describe('FixSnippet', () => {
  it('renders YAML in a code element with a copy button', () => {
    const w = mount(FixSnippet, { props: { yaml: 'restart: unless-stopped' } })
    expect(w.find('code').exists()).toBe(true)
    expect(w.find('[data-testid="copy-btn"]').exists()).toBe(true)
  })
})
