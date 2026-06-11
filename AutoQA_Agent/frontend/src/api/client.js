const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function analyzeRepository(githubUrl) {
  const response = await fetch(`${API_BASE_URL}/analyze-repository`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ github_url: githubUrl }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || 'Repository analysis failed')
  }
  return response.json()
}

export async function getAnalysis(id) {
  const response = await fetch(`${API_BASE_URL}/analysis/${id}`)
  if (!response.ok) throw new Error('Analysis not found')
  return response.json()
}

export async function getAnalyses() {
  try {
    const response = await fetch(`${API_BASE_URL}/analyses`)
    if (!response.ok) return []
    const data = await response.json()
    return Array.isArray(data) ? data : (data.analyses || [])
  } catch {
    return []
  }
}

export async function downloadPdf(analysisId, repoName) {
  const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}/pdf`)
  if (!response.ok) throw new Error('PDF generation failed')
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `autoqa-${repoName || analysisId}.pdf`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
