export interface DiagramDetection {
  diagram_type: string
  source_length: number
}

export function useMmdioApi() {
  const config = useRuntimeConfig()
  const apiBase = computed(() => String(config.public.apiBase))

  async function detectDiagram(source: string): Promise<DiagramDetection> {
    return await $fetch<DiagramDetection>('/api/v1/diagrams/detect', {
      baseURL: apiBase.value,
      method: 'POST',
      body: { source }
    })
  }

  return { apiBase, detectDiagram }
}
