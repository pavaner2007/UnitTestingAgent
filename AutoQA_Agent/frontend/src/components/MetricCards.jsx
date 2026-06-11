import { FileCode2, Route, Layers, Target, FolderGit2, Download } from 'lucide-react'

function getConfidenceColor(score) {
  if (score == null) return '#64748B'
  if (score >= 80)   return '#10B981'
  if (score >= 60)   return '#F59E0B'
  return '#EF4444'
}

function MetricCard({ icon: Icon, value, label, accent, delay = 0 }) {
  return (
    <div
      style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 16,
        padding: '20px 22px',
        position: 'relative',
        overflow: 'hidden',
        transition: 'transform 0.2s, box-shadow 0.2s, border-color 0.2s',
        animation: `fadeSlideUp 0.5s ease ${delay}ms both`,
        cursor: 'default',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'translateY(-3px)'
        e.currentTarget.style.boxShadow = `0 8px 32px ${accent}20`
        e.currentTarget.style.borderColor = `${accent}30`
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = ''
        e.currentTarget.style.boxShadow = ''
        e.currentTarget.style.borderColor = 'var(--border)'
      }}
    >
      {/* Background glow blob */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: `radial-gradient(ellipse 80% 60% at 10% 20%, ${accent}09 0%, transparent 70%)`,
      }} />

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 9,
          background: `${accent}18`, border: `1px solid ${accent}28`,
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}>
          <Icon size={15} color={accent} />
        </div>
        <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
          {label}
        </span>
      </div>
      <div style={{
        fontSize: 26, fontWeight: 800, color: 'var(--text-primary)',
        letterSpacing: '-0.02em', lineHeight: 1,
        wordBreak: 'break-all',
        fontFamily: typeof value === 'number' ? 'Inter, sans-serif' : 'JetBrains Mono, monospace',
      }}>
        {value ?? '—'}
      </div>
    </div>
  )
}

function ConfidenceCard({ score, delay = 0, onDownload, pdfLoading }) {
  const color = getConfidenceColor(score)
  const label = score >= 80 ? 'High Confidence' : score >= 60 ? 'Medium' : 'Low Confidence'
  const radius = 36
  const circumference = 2 * Math.PI * radius
  const strokeDash = score != null ? ((score / 100) * circumference) : 0

  return (
    <div
      style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 16,
        padding: '20px 22px',
        position: 'relative',
        overflow: 'hidden',
        transition: 'transform 0.2s, box-shadow 0.2s',
        animation: `fadeSlideUp 0.5s ease ${delay}ms both`,
        display: 'flex', flexDirection: 'column',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'translateY(-3px)'
        e.currentTarget.style.boxShadow = `0 8px 32px ${color}20`
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = ''
        e.currentTarget.style.boxShadow = ''
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 9,
            background: `${color}18`, border: `1px solid ${color}28`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Target size={15} color={color} />
          </div>
          <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
            Confidence
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* SVG ring */}
        <svg width={86} height={86} style={{ flexShrink: 0 }}>
          <circle cx={43} cy={43} r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={7} />
          <circle
            cx={43} cy={43} r={radius} fill="none"
            stroke={color} strokeWidth={7}
            strokeDasharray={`${strokeDash} ${circumference}`}
            strokeLinecap="round"
            transform="rotate(-90 43 43)"
            style={{ transition: 'stroke-dasharray 1s ease' }}
          />
          <text x={43} y={47} textAnchor="middle" fontSize={16} fontWeight={800} fill={color} fontFamily="Inter">
            {score != null ? `${Math.round(score)}%` : '—'}
          </text>
        </svg>
        <div>
          <div style={{ fontSize: 13, fontWeight: 700, color, marginBottom: 4 }}>{label}</div>
          {onDownload && (
            <button
              onClick={onDownload}
              disabled={pdfLoading}
              style={{
                display: 'flex', alignItems: 'center', gap: 6,
                background: 'linear-gradient(135deg, #3B82F6, #8B5CF6)',
                color: '#fff', border: 'none', borderRadius: 8,
                padding: '7px 14px', fontSize: 11, fontWeight: 700,
                cursor: pdfLoading ? 'not-allowed' : 'pointer',
                opacity: pdfLoading ? 0.7 : 1,
                fontFamily: 'Inter, sans-serif',
                transition: 'opacity 0.2s',
                marginTop: 2,
                letterSpacing: '-0.01em',
              }}
            >
              <Download size={11} />
              {pdfLoading ? 'Generating…' : 'Download PDF'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default function MetricCards({ report, onDownload, pdfLoading }) {
  if (!report) return null

  const techCount = Object.values(report.technology_stack || {})
    .flat().filter(Boolean).length

  const cards = [
    {
      icon: FolderGit2,
      value: report.repository_name,
      label: 'Repository',
      accent: '#6366F1',
    },
    {
      icon: FileCode2,
      value: report.number_of_files,
      label: 'Files Scanned',
      accent: '#06B6D4',
    },
    {
      icon: Route,
      value: report.number_of_apis_discovered,
      label: 'APIs Found',
      accent: '#10B981',
    },
    {
      icon: Layers,
      value: techCount,
      label: 'Technologies',
      accent: '#A78BFA',
    },
  ]

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 12, marginBottom: 24 }}>
      {cards.map((c, i) => (
        <MetricCard key={c.label} {...c} delay={i * 60} />
      ))}
      <ConfidenceCard
        score={report.confidence_score}
        delay={cards.length * 60}
        onDownload={onDownload}
        pdfLoading={pdfLoading}
      />
    </div>
  )
}
