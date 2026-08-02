<template>
  <main class="shell">
    <header class="masthead">
      <div>
        <p class="eyebrow">Universal diagram I/O</p>
        <h1>mmdio</h1>
        <p class="lede">
          Machines operate the computers. Diagrams let humans govern the resulting institution.
        </p>
      </div>
      <UBadge color="neutral" variant="outline" size="lg">PARTIAL_ALIVE</UBadge>
    </header>

    <section class="principles" aria-label="Control-plane principles">
      <UCard>
        <p class="metric-label">Representation</p>
        <p class="metric-value">Mermaid 11.16</p>
      </UCard>
      <UCard>
        <p class="metric-label">Canonical runtime</p>
        <p class="metric-value">Nuxt 4 + FastAPI</p>
      </UCard>
      <UCard>
        <p class="metric-label">Authority</p>
        <p class="metric-value">No ambient DO</p>
      </UCard>
    </section>

    <MermaidWorkbench />
  </main>
</template>
