<script setup lang="ts">
const starter = `flowchart LR
  O[Observed state] --> C[Candidate field]
  C --> J{Admitted?}
  J -->|No| X[Typed refusal]
  J -->|Yes| B[BRCE]
  B --> A[Observed consequence]
  A --> R[Receipt + replay]`

const source = ref(starter)
const svg = ref('')
const renderError = ref('')
const detectedType = ref('unknown')
const detecting = ref(false)
const { detectDiagram } = useMmdioApi()
let renderSequence = 0
let debounceTimer: ReturnType<typeof setTimeout> | undefined

async function renderDiagram() {
  renderError.value = ''
  const current = source.value.trim()
  if (!current) {
    svg.value = ''
    detectedType.value = 'unknown'
    return
  }

  try {
    const mermaid = (await import('mermaid')).default
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      theme: 'dark'
    })
    const result = await mermaid.render(`mmdio-${++renderSequence}`, current)
    svg.value = result.svg
  } catch (error) {
    svg.value = ''
    renderError.value = error instanceof Error ? error.message : String(error)
  }

  detecting.value = true
  try {
    const result = await detectDiagram(current)
    detectedType.value = result.diagram_type
  } catch {
    detectedType.value = 'api-unavailable'
  } finally {
    detecting.value = false
  }
}

watch(source, () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => void renderDiagram(), 250)
})

onMounted(() => void renderDiagram())
</script>

<template>
  <section class="workbench" aria-label="Mermaid workbench">
    <UCard class="editor-card">
      <template #header>
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Candidate input</p>
            <h2>Diagram source</h2>
          </div>
          <UBadge color="neutral" variant="soft">
            {{ detecting ? 'detecting' : detectedType }}
          </UBadge>
        </div>
      </template>

      <UTextarea
        v-model="source"
        :rows="22"
        autoresize
        aria-label="Mermaid source"
        class="source-editor"
      />

      <template #footer>
        <p class="footnote">
          Editing manufactures a candidate representation. It does not grant execution authority.
        </p>
      </template>
    </UCard>

    <UCard class="preview-card">
      <template #header>
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Human governance view</p>
            <h2>Live projection</h2>
          </div>
          <UBadge :color="renderError ? 'error' : 'success'" variant="subtle">
            {{ renderError ? 'REFUSED' : 'RENDERED' }}
          </UBadge>
        </div>
      </template>

      <div v-if="renderError" class="error-panel" role="alert">
        {{ renderError }}
      </div>
      <div v-else-if="svg" class="diagram" v-html="svg" />
      <div v-else class="empty-state">Enter Mermaid source to produce a projection.</div>
    </UCard>
  </section>
</template>
