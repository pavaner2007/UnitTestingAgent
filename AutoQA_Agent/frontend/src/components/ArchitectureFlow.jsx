import { Network } from 'lucide-react'

// Derive architecture layers from the report — deduplicating across all arrays
function getLayers(report) {
  if (!report) return []
  const stack = report.technology_stack || {}
  const layers = []

  // Deduplicate helper: returns unique items in `arr` not already seen
  const seen = new Set()
  function unique(arr = []) {
    return arr.filter(v => {
      const key = v.toLowerCase().trim()
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  }

  // Process strictly in layer order so earlier layers "claim" their techs first
  const feItems = unique(stack.frontend || [])
  const beItems = unique(stack.backend || [])
  const fwItems = unique(stack.frameworks || [])
  const dbItems = unique(stack.databases || [])

  const apis = report.number_of_apis_discovered

  if (feItems.length)   layers.push({ label: 'Frontend',       value: feItems.join(', '),           color: '#6366F1', icon: '🎨' })
  if (apis > 0)         layers.push({ label: 'API Layer',       value: `${apis} endpoints`,          color: '#3B82F6', icon: '⚡' })
  const beLogic = [...beItems, ...fwItems]
  if (beLogic.length)   layers.push({ label: 'Business Logic', value: beLogic.join(', '),            color: '#06B6D4', icon: '⚙️' })
  if (dbItems.length)   layers.push({ label: 'Database',       value: dbItems.join(', '),            color: '#F59E0B', icon: '🗄️' })

  // Need at least 2 layers to show a meaningful diagram
  if (layers.length < 2) return []

  return layers
}

function Arrow() {
  return (
    <div style={{
      display: 'flex', justifyContent: 'center', padding: '2px 0',
      color: 'var(--text-muted)',
    }}>
      <svg width="16" height="20" viewBox="0 0 16 20" fill="none">
        <line x1="8" y1="0" x2="8" y2="14" stroke="rgba(148,163,184,0.25)" strokeWidth="1.5" strokeDasharray="3 2" />
        <path d="M4 11L8 16L12 11" stroke="rgba(148,163,184,0.3)" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
  )
}

export default function ArchitectureFlow({ report }) {
  const layers = getLayers(report)
  if (layers.length < 2) return null

  return (
    <div style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border)',
      borderRadius: 18,
      overflow: 'hidden',
      animation: 'fadeSlideUp 0.5s ease 0.4s both',
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 24px', borderBottom: '1px solid var(--border)',
        display: 'flex', alignItems: 'center', gap: 10,
        background: 'linear-gradient(90deg, rgba(59,130,246,0.04) 0%, transparent 60%)',
      }}>
        <div style={{
          width: 34, height: 34, borderRadius: 9,
          background: 'rgba(59,130,246,0.1)',
          border: '1px solid rgba(59,130,246,0.2)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Network size={16} color="#93C5FD" />
        </div>
        <div>
          <h3 style={{ fontWeight: 700, fontSize: 15, lineHeight: 1 }}>Project Architecture</h3>
          <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3 }}>
            Auto-generated from detected stack
          </p>
        </div>
      </div>

      {/* Flow diagram */}
      <div style={{ padding: '28px 24px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {layers.map((layer, i) => (
          <div key={layer.label} style={{ width: '100%', maxWidth: 400 }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '14px 18px', borderRadius: 12,
              background: `${layer.color}0A`,
              border: `1px solid ${layer.color}22`,
              transition: 'all 0.2s',
              animation: `fadeSlideUp 0.4s ease ${i * 80}ms both`,
            }}
              onMouseEnter={e => {
                e.currentTarget.style.background = `${layer.color}14`
                e.currentTarget.style.borderColor = `${layer.color}35`
                e.currentTarget.style.transform = 'translateX(3px)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = `${layer.color}0A`
                e.currentTarget.style.borderColor = `${layer.color}22`
                e.currentTarget.style.transform = ''
              }}
            >
              <span style={{ fontSize: 20, flexShrink: 0 }}>{layer.icon}</span>
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, color: layer.color, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 2 }}>
                  {layer.label}
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 500 }}>
                  {layer.value}
                </div>
              </div>
            </div>
            {i < layers.length - 1 && <Arrow />}
          </div>
        ))}
      </div>
    </div>
  )
}
