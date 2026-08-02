
# Cyberpunk 2030: Complete Dependency Landscape

**Generated:** `ggen sync run`
**Source:** packs/cyberpunk-2030-pack/ontology.ttl

## Overview

| Metric | Value |
|--------|-------|
| **Total Projects** | 12 |
| **Total Unique Packages** | 845 |
| **Framework Distribution** | 6 Nuxt, 6 Next.js |
| **Nuxt Versions** | v3.8.0, v3.14.1592, v3.15.3, v4.0.3, v4.1.3 |
| **Next.js Versions** | v15.2.4, v15.5.5, v16.0.1, v16.2.9 |

## Projects

### Nuxt Projects (6)
1. **dashboard.bak** — Dashboard (Nuxt 4.0.3)
2. **cns** — Backend (Nuxt 3.8.0)
3. **.chat** — Chat Application (Nuxt 4.1.3)
4. **app** — Generic App (Nuxt 3.15.3)
5. **nuxt-layer** — Library (Nuxt 3.14.1592)
6. **full-stack-rubric** — Full Stack (Nuxt 4.0.3)

### Next.js Projects (6)
1. **ai-chatbot** — AI Application (Next.js 16.0.1)
2. **ai** — AI Application (Next.js unversioned)
3. **optimus** — AI Platform (Next.js 15.5.5)
4. **kgc-sidecar** — Sidecar Service (Next.js 15.2.4)
5. **clap-web** — Web Application (Next.js 16.2.9)
6. **benchmark-site** — Benchmarking (Next.js unversioned)

## Dependency Categories

### 1. Framework Layer (7 packages, 12 projects)
- **nuxt** — 6 projects (dashboard.bak, cns, .chat, app, nuxt-layer, full-stack-rubric)
- **next** — 6 projects (ai-chatbot, ai, optimus, kgc-sidecar, clap-web, benchmark-site)
- **vue** — 2 projects (cns, app)
- **react** — 5 projects (ai-chatbot, optimus, kgc-sidecar, clap-web, benchmark-site)
- **react-dom** — 5 projects (same)
- **@angular/** — Low adoption (not in primary projects)
- **@angular/material** — Minimal

### 2. AI/LLM Stack (9 packages, 4 projects) ⭐
**Critical integration layer for ai-chatbot, .chat, optimus, benchmark-site**

| Package | Versions | Projects |
|---------|----------|----------|
| **ai** | ^5.0.81, ^5.0.68, ^5.0.73 | ai-chatbot, .chat, optimus, benchmark-site |
| **@ai-sdk/openai** | ^2.0.52, ^1.0.0 | .chat, optimus, benchmark-site |
| **@ai-sdk/react** | ^2.0.73, ^3.0.118 | optimus, benchmark-site |
| **@ai-sdk/vue** | ^2.0.68 | .chat |
| **@ai-sdk/anthropic** | ^2.0.38 | optimus |
| **@ai-sdk/gateway** | ^1.0.39 | .chat |
| **ollama-ai-provider-v2** | ^1.5.0, ^1.4.1 | optimus, kgc-sidecar |
| **ollama-ai-provider** | ^1.2.0 | optimus |
| **@anthropic-ai/sdk** | (implicit via ai) | optimus |

**Version Conflicts:**
- ai: ^5.0.81 vs ^5.0.68 vs ^5.0.73 → Minor patch variance, semver compatible
- @ai-sdk/openai: ^2.0.52 vs ^1.0.0 → Major version mismatch (v1 vs v2)
- @ai-sdk/react: ^2.0.73 vs ^3.0.118 → Major version mismatch (v2 vs v3)

### 3. UI Components (30+ packages, 2 primary projects)
**@radix-ui/react-* components (30 variants) used in ai-chatbot and optimus**

| Component | Projects |
|-----------|----------|
| @radix-ui/react-avatar | ai-chatbot, optimus |
| @radix-ui/react-collapsible | ai-chatbot, optimus |
| @radix-ui/react-dialog | ai-chatbot, optimus |
| @radix-ui/react-dropdown-menu | ai-chatbot, optimus |
| @radix-ui/react-hover-card | ai-chatbot, optimus |
| @radix-ui/react-progress | ai-chatbot, optimus |
| @radix-ui/react-scroll-area | ai-chatbot, optimus |
| @radix-ui/react-select | ai-chatbot, optimus |
| @radix-ui/react-slot | ai-chatbot, optimus |
| @radix-ui/react-tabs | optimus |
| @radix-ui/react-tooltip | ai-chatbot, optimus |
| @radix-ui/react-use-controllable-state | ai-chatbot, optimus |
| lucide-react | ai-chatbot, optimus |
| @nuxt/ui | dashboard.bak, .chat, full-stack-rubric |
| tailwindcss / tailwind-merge | ai-chatbot, optimus, kgc-sidecar |

### 4. Observability & Tracing (17 @opentelemetry packages, 2 projects)
**Comprehensive OpenTelemetry instrumentation in cns and optimus**

| Component | Role | Projects |
|-----------|------|----------|
| @opentelemetry/api | Core tracing API | cns, optimus |
| @opentelemetry/sdk-node | Node.js SDK | cns, optimus |
| @opentelemetry/auto-instrumentations-node | Auto-instrument Node.js | cns, optimus |
| @opentelemetry/auto-instrumentations-web | Auto-instrument browser | cns |
| @opentelemetry/exporter-trace-otlp-http | OTLP HTTP exporter | cns, optimus |
| @opentelemetry/instrumentation-http | HTTP tracing | cns |
| @opentelemetry/resources | Resource definitions | cns, optimus |
| @opentelemetry/semantic-conventions | Tracing conventions | cns, optimus |
| @vercel/otel | Vercel OpenTelemetry | optimus |

**Version Considerations:**
- cns uses @opentelemetry/* v0.203.0, v1.25.1 (mixed major versions)
- optimus uses @opentelemetry/* v0.206.0, v0.207.0, v1.37.0, v2.1.0 (highly fragmented)

### 5. Data & ORM (5 packages, 2 projects)
| Package | Projects | Version |
|---------|----------|---------|
| **drizzle-orm** | .chat | ^0.44.6 |
| **pg** | .chat | ^8.16.3 |
| **better-sqlite3** | full-stack-rubric | ^12.2.0 |
| **prisma** | (not yet adopted) | — |
| **typeorm** | (not yet adopted) | — |

### 6. RDF & Semantic Web (13 @unrdf packages + @rdfjs, 1 project)
**Unique adoption in optimus**

| Package | Version | Packages |
|---------|---------|----------|
| **@unrdf/*** | — | 13 packages |
| **@rdfjs/data-model** | ^2.1.1 | optimus |
| **unrdf** | ^3.0.3 | optimus |
| **@comunica/query-sparql** | (in full dataset) | Full dependency analysis available |

### 7. Utilities (zod, date-fns, nanoid, etc., 5+ projects)
| Package | Projects | Version Range |
|---------|----------|----------------|
| **zod** | dashboard.bak, app, optimus | ^3.25.76, ^3.24.2, ^4.1.12 |
| **date-fns** | dashboard.bak, .chat | ^4.1.0 |
| **nanoid** | ai-chatbot, optimus | ^5.1.6 |
| **clsx** | ai-chatbot, optimus | ^2.1.1 |
| **class-variance-authority** | ai-chatbot, optimus | ^0.7.1 |
| **tailwind-merge** | ai-chatbot, optimus, kgc-sidecar | ^3.3.1 |

### 8. Visualization & Graphics (12 packages, 1-3 projects)
| Category | Packages | Projects |
|----------|----------|----------|
| **Graph/Flow** | @xyflow/react | ai-chatbot, optimus |
| **3D Graphics** | three, @react-three/fiber, @tresjs | optimus (minimal) |
| **Charts** | chart.js, react-chartjs-2, recharts | optimus |
| **Maps & Geo** | @deck.gl/* (6 packages) | optimus |
| **D3** | d3 | optimus |

### 9. State Management (xstate, minimal adoption)
| Package | Projects | Version |
|---------|----------|---------|
| **xstate** | optimus | ^5.23.0 |
| **@xstate/core** | (transitive) | — |
| **pinia** | (not yet adopted) | — |
| **zustand** | (not yet adopted) | — |

### 10. Backend Frameworks (express, NestJS, Phoenix, 2 projects)
| Package | Projects | Version |
|---------|----------|---------|
| **express** | cns, kgc-sidecar | ^4.19.2 |
| **@nestjs/common** | kgc-sidecar | ^11.0.0 |
| **@nestjs/core** | kgc-sidecar | ^11.0.0 |
| **@nestjs/platform-express** | kgc-sidecar | ^11.0.0 |
| **phoenix** | cns | ^1.7.0 |
| **body-parser** | cns | ^1.20.3 |
| **cors** | cns | ^2.8.5 |

---

## Combinatorial Analysis

### High-Risk Version Conflicts
1. **@ai-sdk/openai** — v1 vs v2 (benchmark-site vs .chat, optimus)
2. **@ai-sdk/react** — v2 vs v3 (optimus vs benchmark-site)
3. **zod** — v3 vs v4 (multiple projects)
4. **@opentelemetry/*** — Fragmented v0.203–v2.1.0 across cns/optimus

### Opportunity: Unified Version Strategy
**Candidates for standardization:**
- **Framework layer:** Align Nuxt (v3 → v4), Next.js (v15 → v16)
- **AI/LLM:** Pin ai SDK versions across projects (v5.0.8x)
- **UI:** Consolidate radix-ui + tailwind versions
- **Observability:** Standardize OpenTelemetry v2.x across all projects

### Zero-Adoption Opportunities
- **Prisma** — No current adoption (potential DB standardization)
- **Pinia** — No adoption (Vue state management candidate)
- **Redux** — No adoption (React alternative to xstate)

---

## Generated Statistics

- **Total dependency instances:** 250+ across all projects
- **Packages appearing in multiple projects:** ~45 (5% of 845)
- **Single-project packages:** 800 (95%)
- **Monorepo candidates:** dashboard.bak + full-stack-rubric (both Nuxt v4.0.3)
- **Shared component library opportunity:** ai-chatbot + optimus (radix-ui + tailwind ecosystem)

---

**Next steps:** Use this matrix for:
1. Version conflict resolution strategy
2. Shared library extraction (especially UI components)
3. Dependency upgrade planning
4. Monorepo consolidation feasibility study
