import { useState, useEffect } from 'react'
import PolicyPanel from './components/PolicyPanel'
import InvestmentPanel from './components/InvestmentPanel'
import ClaimsPanel from './components/ClaimsPanel'
import ChaosPanel from './components/ChaosPanel'

export const API = import.meta.env.VITE_API_URL || 'http://localhost:3000'

const CUSTOMERS = ['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST005']
const TABS = [
  { id: 'overview',    label: 'Overview',     icon: '🏠' },
  { id: 'policy',      label: 'Policy',        icon: '📋' },
  { id: 'investments', label: 'Investments',   icon: '📈' },
  { id: 'claims',      label: 'Claims',        icon: '📝' },
  { id: 'chaos',       label: 'System Status', icon: '⚡' },
]

export default function App() {
  const [customer, setCustomer] = useState('CUST001')
  const [tab, setTab] = useState('overview')
  const [gwStatus, setGwStatus] = useState(null)

  useEffect(() => {
    fetch(`${API}/health`)
      .then(r => r.json())
      .then(d => setGwStatus(d.status === 'ok' ? 'online' : 'degraded'))
      .catch(() => setGwStatus('offline'))
  }, [])

  return (
    <div className="app">
      {/* ── Header ─────────────────────────────────── */}
      <header className="header">
        <div className="header-brand">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2L4 6.5V14C4 19.5 8.4 24.6 14 26C19.6 24.6 24 19.5 24 14V6.5L14 2Z" fill="white" fillOpacity="0.9"/>
            <path d="M10 14L13 17L18 11" stroke="#a20a29" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span className="brand-name">InsureWatch</span>
          <span className="brand-tag">Portal</span>
        </div>
        <div className="header-controls">
          <div className="customer-selector">
            <label>Customer</label>
            <select value={customer} onChange={e => setCustomer(e.target.value)}>
              {CUSTOMERS.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div className={`gw-badge gw-${gwStatus}`}>
            <span className="dot" />
            {gwStatus === 'online' ? 'Gateway Online' : gwStatus === 'offline' ? 'Gateway Offline' : 'Connecting…'}
          </div>
        </div>
      </header>

      {/* ── Tab bar ─────────────────────────────────── */}
      <nav className="tabbar">
        {TABS.map(t => (
          <button
            key={t.id}
            className={`tab-btn ${tab === t.id ? 'active' : ''}`}
            onClick={() => setTab(t.id)}
          >
            <span>{t.icon}</span> {t.label}
          </button>
        ))}
      </nav>

      {/* ── Content ─────────────────────────────────── */}
      <main className="content">
        {tab === 'overview'    && <Overview customer={customer} setTab={setTab} />}
        {tab === 'policy'      && <PolicyPanel customer={customer} />}
        {tab === 'investments' && <InvestmentPanel customer={customer} />}
        {tab === 'claims'      && <ClaimsPanel customer={customer} />}
        {tab === 'chaos'       && <ChaosPanel />}
      </main>

      {/* ── Footer ─────────────────────────────────── */}
      <footer className="footer">
        <p>Powered by <a href="https://otel.guru" target="_blank" rel="noopener noreferrer">otel.guru</a></p>
        <p>For demonstration purposes only</p>
      </footer>
    </div>
  )
}

/* ─── Overview tab (summary cards + quick links) ─── */
function Overview({ customer, setTab }) {
  const [policy, setPolicy] = useState(null)
  const [invest, setInvest] = useState(null)
  const [claims, setClaims] = useState(null)
  const [chaos, setChaos]   = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    setPolicy(null); setInvest(null); setClaims(null); setChaos(null)
    Promise.allSettled([
      fetch(`${API}/api/policy/${customer}`).then(r => r.json()),
      fetch(`${API}/api/investments/${customer}`).then(r => r.json()),
      fetch(`${API}/api/claims`).then(r => r.json()),
      fetch(`${API}/api/chaos/status`).then(r => r.json()),
    ]).then(([p, i, c, ch]) => {
      if (p.status === 'fulfilled') setPolicy(p.value)
      if (i.status === 'fulfilled') setInvest(i.value)
      if (c.status === 'fulfilled') setClaims(Array.isArray(c.value) ? c.value : [])
      if (ch.status === 'fulfilled') setChaos(ch.value)
      setLoading(false)
    })
  }, [customer])

  const activePolicy = Array.isArray(policy) ? policy.find(p => p.status === 'active') : null
  const healthyCount = chaos ? Object.values(chaos.services || {}).filter(s => s.healthy).length : 0
  const totalServices = chaos ? Object.keys(chaos.services || {}).length : 4
  const customerClaims = claims ? claims.filter(c => c.customerId === customer || c.customer_id === customer) : []

  return (
    <div className="overview">
      <h2 className="section-title">Welcome, <span className="accent">{customer}</span></h2>

      {loading ? (
        <div className="spinner-wrap"><div className="spinner" /></div>
      ) : (
        <>
          <div className="overview-grid">
            <SummaryCard
              icon="📋" title="Active Policy"
              value={activePolicy ? activePolicy.policyNumber : 'None'}
              sub={activePolicy ? `${activePolicy.policyType} · $${activePolicy.premiumAmount}/mo` : 'No active policy'}
              onClick={() => setTab('policy')} color="blue"
            />
            <SummaryCard
              icon="📈" title="Portfolio Value"
              value={invest?.totalValue ? `$${invest.totalValue.toLocaleString('en-US', { maximumFractionDigits: 0 })}` : '—'}
              sub={invest ? `${invest.holdings?.length || 0} holdings` : 'No portfolio'}
              onClick={() => setTab('investments')} color="green"
            />
            <SummaryCard
              icon="📝" title="Claims Filed"
              value={customerClaims.length}
              sub={customerClaims.length === 0 ? 'No claims on record' : `${customerClaims.filter(c => c.status === 'pending').length} pending`}
              onClick={() => setTab('claims')} color="amber"
            />
            <SummaryCard
              icon="⚡" title="System Health"
              value={`${healthyCount}/${totalServices}`}
              sub={healthyCount === totalServices ? 'All services healthy' : `${totalServices - healthyCount} service(s) degraded`}
              onClick={() => setTab('chaos')}
              color={healthyCount === totalServices ? 'green' : 'red'}
            />
          </div>

          {activePolicy && (
            <div className="overview-policy">
              <h3>Policy at a Glance</h3>
              <div className="coverage-bars">
                {activePolicy.coverages?.map(cov => (
                  <CoverageBar key={cov.type} coverage={cov} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

function SummaryCard({ icon, title, value, sub, onClick, color }) {
  return (
    <button className={`summary-card card-${color}`} onClick={onClick}>
      <div className="card-icon">{icon}</div>
      <div className="card-body">
        <div className="card-title">{title}</div>
        <div className="card-value">{value}</div>
        <div className="card-sub">{sub}</div>
      </div>
      <span className="card-arrow">→</span>
    </button>
  )
}

export function CoverageBar({ coverage }) {
  const pct = coverage.limit > 0 ? Math.min(100, (coverage.used / coverage.limit) * 100) : 0
  const color = pct > 80 ? '#a20a29' : pct > 50 ? '#b45309' : '#1a8f4e'
  return (
    <div className="cov-bar-wrap">
      <div className="cov-bar-header">
        <span className="cov-type">{coverage.type}</span>
        <span className="cov-nums">
          ${coverage.used?.toLocaleString()} used / ${coverage.limit?.toLocaleString()} limit
        </span>
      </div>
      <div className="cov-track">
        <div className="cov-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="cov-available" style={{ color }}>
        ${coverage.available?.toLocaleString()} remaining
      </span>
    </div>
  )
}
