import { FileCode2, Route, Layers, Target, FolderGit2, Download } from 'lucide-react'

function getConfidenceColor(score) {
  if (score == null) return '#64748B'
  if (score >= 80) return '#10B981'
  if (score >= 60) return '#F59E0B'
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
  const sublabel = score >= 80 ? 'Analysis quality is high' : score >= 60 ? 'Moderate analysis quality' : 'Low analysis quality'
  const badge = score >= 80 ? 'High' : score >= 60 ? 'Medium' : 'Low'
  const radius = 42
  const circumference = 2 * Math.PI * radius
  const strokeDash = score != null ? ((score / 100) * circumference) : 0

  return (
    <div
      style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 16,
        padding: '20px 20px 16px',
        position: 'relative',
        overflow: 'hidden',
        transition: 'transform 0.2s, box-shadow 0.2s, border-color 0.2s',
        animation: `fadeSlideUp 0.5s ease ${delay}ms both`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'stretch',
        gap: 14,
      }}
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'translateY(-3px)'
        e.currentTarget.style.boxShadow = `0 8px 32px ${color}25`
        e.currentTarget.style.borderColor = `${color}30`
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = ''
        e.currentTarget.style.boxShadow = ''
        e.currentTarget.style.borderColor = 'var(--border)'
      }}
    >
      {/* Background glow */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: `radial-gradient(ellipse 80% 60% at 50% 0%, ${color}0A 0%, transparent 70%)`,
      }} />

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 30, height: 30, borderRadius: 8, flexShrink: 0,
            background: `${color}18`, border: `1px solid ${color}28`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Target size={14} color={color} />
          </div>
          <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
            Confidence
          </span>
        </div>
        {/* Badge */}
        <span style={{
          fontSize: 10, fontWeight: 700, padding: '3px 9px', borderRadius: 99,
          background: `${color}18`, border: `1px solid ${color}30`, color,
          letterSpacing: '0.04em',
        }}>
          {badge}
        </span>
      </div>

      {/* Centered ring */}
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <svg width={100} height={100}>
          {/* Track */}
          <circle cx={50} cy={50} r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={8} />
          {/* Progress */}
          <circle
            cx={50} cy={50} r={radius} fill="none"
            stroke={color} strokeWidth={8}
            strokeDasharray={`${strokeDash} ${circumference}`}
            strokeLinecap="round"
            transform="rotate(-90 50 50)"
            style={{ transition: 'stroke-dasharray 1.2s cubic-bezier(0.4,0,0.2,1)', filter: `drop-shadow(0 0 6px ${color}60)` }}
          />
          {/* Score text */}
          <text x={50} y={45} textAnchor="middle" fontSize={20} fontWeight={800} fill={color} fontFamily="Inter">
            {score != null ? `${Math.round(score)}%` : '—'}
          </text>
          <text x={50} y={63} textAnchor="middle" fontSize={9} fontWeight={600} fill="rgba(255,255,255,0.35)" fontFamily="Inter" letterSpacing="1">
            SCORE
          </text>
        </svg>
      </div>

      {/* Sub-label */}
      <div style={{ textAlign: 'center', marginTop: -6 }}>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{sublabel}</div>
      </div>

      {/* Download button */}
      {onDownload && (
        <button
          onClick={onDownload}
          disabled={pdfLoading}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
            width: '100%',
            background: 'linear-gradient(135deg, #3B82F6, #8B5CF6)',
            color: '#fff', border: 'none', borderRadius: 10,
            padding: '9px 14px', fontSize: 12, fontWeight: 700,
            cursor: pdfLoading ? 'not-allowed' : 'pointer',
            opacity: pdfLoading ? 0.7 : 1,
            fontFamily: 'Inter, sans-serif',
            transition: 'opacity 0.2s, transform 0.15s, box-shadow 0.15s',
            letterSpacing: '-0.01em',
            boxShadow: '0 2px 14px rgba(59,130,246,0.4)',
          }}
          onMouseEnter={e => { if (!pdfLoading) { e.currentTarget.style.transform = 'scale(1.02)'; e.currentTarget.style.boxShadow = '0 4px 20px rgba(59,130,246,0.55)' } }}
          onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '0 2px 14px rgba(59,130,246,0.4)' }}
        >
          <Download size={13} />
          {pdfLoading ? 'Generating…' : 'Download PDF'}
        </button>
      )}
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
