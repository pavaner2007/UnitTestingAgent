import { LayoutDashboard, History, Github, Zap } from 'lucide-react'

export default function Sidebar({ activePage, onNavigate, historyCount = 0 }) {
  const navItems = [
    { id: 'home',    label: 'Dashboard', icon: LayoutDashboard },
    { id: 'history', label: 'History',   icon: History, badge: historyCount },
  ]

  return (
    <aside style={{
      width: 'var(--sidebar-width)',
      flexShrink: 0,
      height: '100vh',
      position: 'sticky',
      top: 0,
      display: 'flex',
      flexDirection: 'column',
      background: 'rgba(11,16,32,0.85)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderRight: '1px solid var(--border)',
      zIndex: 100,
    }}>
      {/* Logo */}
      <div style={{ padding: '24px 20px 20px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 34, height: 34, borderRadius: 9,
            background: 'linear-gradient(135deg, #3B82F6, #8B5CF6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
            boxShadow: '0 4px 14px rgba(59,130,246,0.35)',
          }}>
            <Zap size={17} color="#fff" fill="#fff" />
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: 14, letterSpacing: '-0.02em', color: 'var(--text-primary)', lineHeight: 1 }}>
              AutoQA
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2, letterSpacing: '0.05em' }}>
              AGENT
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ padding: '12px 10px', flex: 1 }}>
        {navItems.map(({ id, label, icon: Icon, badge }) => {
          const isActive = activePage === id
          return (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              style={{
                width: '100%',
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '9px 12px', borderRadius: 10,
                background: isActive ? 'rgba(59,130,246,0.12)' : 'transparent',
                border: isActive ? '1px solid rgba(59,130,246,0.2)' : '1px solid transparent',
                color: isActive ? '#3B82F6' : 'var(--text-secondary)',
                fontFamily: 'Inter, sans-serif',
                fontSize: 13, fontWeight: isActive ? 600 : 500,
                cursor: 'pointer',
                transition: 'all 0.15s',
                marginBottom: 2,
                textAlign: 'left',
              }}
              onMouseEnter={e => {
                if (!isActive) {
                  e.currentTarget.style.background = 'rgba(255,255,255,0.035)'
                  e.currentTarget.style.color = 'var(--text-primary)'
                }
              }}
              onMouseLeave={e => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--text-secondary)'
                }
              }}
            >
              <Icon size={15} />
              <span style={{ flex: 1 }}>{label}</span>
              {badge > 0 && (
                <span style={{
                  fontSize: 10, fontWeight: 700, minWidth: 18, height: 18,
                  borderRadius: 99, background: 'rgba(59,130,246,0.2)',
                  color: '#3B82F6', display: 'flex',
                  alignItems: 'center', justifyContent: 'center', padding: '0 5px',
                }}>
                  {badge}
                </span>
              )}
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border)' }}>
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'flex', alignItems: 'center', gap: 8,
            color: 'var(--text-muted)', fontSize: 12, textDecoration: 'none',
            transition: 'color 0.15s',
          }}
          onMouseEnter={e => e.currentTarget.style.color = 'var(--text-secondary)'}
          onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
        >
          <Github size={13} />
          <span>Open Source</span>
        </a>
        <div style={{ marginTop: 8, fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
          Code-First · Local-First
        </div>
      </div>
    </aside>
  )
}
