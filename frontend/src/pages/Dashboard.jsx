import React, { useEffect, useState } from 'react'
import { api } from '../services/api'
import { 
  BarChart3, 
  AlertTriangle, 
  Clock, 
  CheckCircle2, 
  ArrowUpRight 
} from 'lucide-react'
import { Link } from 'react-router-dom'

const KpiCard = ({ icon: Icon, label, value, color }) => (
  <div className="card kpi-card">
    <div className={`kpi-icon ${color}`}>
      <Icon size={24} />
    </div>
    <div className="kpi-info">
      <span className="text-muted">{label}</span>
      <h3 className="h2">{value}</h3>
    </div>
  </div>
)

const Dashboard = () => {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await api.getDashboardSummary()
        setSummary(data)
      } catch (err) {
        console.error("Failed to fetch dashboard summary", err)
      } finally {
        setLoading(false)
      }
    }
    fetchSummary()
  }, [])

  if (loading) return <div>Loading dashboard...</div>

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1 className="h1">Operational Overview</h1>
        <p className="text-muted">Welcome back. Here is the latest intelligence for your claims desk.</p>
      </div>

      <div className="kpi-grid">
        <KpiCard 
          icon={BarChart3} 
          label="Total Claims" 
          value={summary.stats.total_claims} 
          color="blue" 
        />
        <KpiCard 
          icon={Clock} 
          label="Pending Review" 
          value={summary.stats.pending_review} 
          color="orange" 
        />
        <KpiCard 
          icon={AlertTriangle} 
          label="Suspicious" 
          value={summary.stats.suspicious_claims} 
          color="red" 
        />
        <KpiCard 
          icon={CheckCircle2} 
          label="Avg. Processing" 
          value={summary.stats.avg_processing_time} 
          color="green" 
        />
      </div>

      <div className="dashboard-content-grid">
        <section className="dashboard-section">
          <div className="section-header">
            <h2 className="h3">High Risk Alerts</h2>
            <Link to="/claims?status=Suspicious" className="view-all-btn">
              View All <ArrowUpRight size={16} />
            </Link>
          </div>
          <div className="risk-list">
            {summary.high_risk.map(claim => (
              <Link to={`/claims/${claim.claim_id}`} key={claim.claim_id} className="card risk-item">
                <div className="risk-claim-info">
                  <span className="claim-id">{claim.claim_id}</span>
                  <span className="claim-name">{claim.claimant_name}</span>
                </div>
                <div className="risk-meta">
                  <span className="risk-amount">₹{claim.amount.toLocaleString('en-IN')}</span>
                  <span className={`badge ${claim.suspicion_level > 0.4 ? 'badge-danger' : 'badge-warning'}`}>
                    {Math.round(claim.suspicion_level * 100)}% Risk
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </section>

        <section className="dashboard-section">
          <div className="section-header">
            <h2 className="h3">AI Operational Insights</h2>
          </div>
          <div className="card insights-card">
            <div className="insight-item">
              <div className="insight-bullet" />
              <p>Large influx of <strong>Monsoon</strong> related claims from Mumbai and Pune; automated triage suggested.</p>
            </div>
            <div className="insight-item">
              <div className="insight-bullet danger" />
              <p>4 claims in <strong>Bengaluru (Electronic City)</strong> show suspicious repair patterns from the same workshop.</p>
            </div>
            <div className="insight-item">
              <div className="insight-bullet success" />
              <p>STP (Straight-Through Processing) at 88%; automation of <strong>Vahan</strong> database matching is improving efficiency.</p>
            </div>
          </div>
        </section>
      </div>

      <style>{`
        .page-header { margin-bottom: 2.5rem; }
        
        .kpi-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 1.5rem;
          margin-bottom: 2.5rem;
        }

        .kpi-card {
          display: flex;
          align-items: center;
          gap: 1.25rem;
        }

        .kpi-icon {
          width: 48px;
          height: 48px;
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .kpi-icon.blue { background: #E0E7FF; color: #4338CA; }
        .kpi-icon.orange { background: #FFEDD5; color: #EA580C; }
        .kpi-icon.red { background: #FEE2E2; color: #DC2626; }
        .kpi-icon.green { background: #D1FAE5; color: #059669; }

        .dashboard-content-grid {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 2rem;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.25rem;
        }

        .view-all-btn {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          color: var(--color-primary);
          font-size: 0.875rem;
          font-weight: 600;
        }

        .risk-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .risk-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          text-decoration: none;
          color: inherit;
          padding: 1rem 1.5rem;
        }

        .risk-claim-info { display: flex; flex-direction: column; }
        .claim-id { font-size: 0.75rem; font-weight: 600; color: var(--color-primary); }
        .claim-name { font-weight: 500; }

        .risk-meta { display: flex; align-items: center; gap: 1.5rem; }
        .risk-amount { font-weight: 600; }

        .insights-card {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          height: 100%;
        }

        .insight-item {
          display: flex;
          gap: 1rem;
        }

        .insight-bullet {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--color-primary);
          margin-top: 0.5rem;
          flex-shrink: 0;
        }

        .insight-bullet.danger { background: var(--color-danger); }
        .insight-bullet.success { background: var(--color-success); }

        .insight-item p {
          font-size: 0.875rem;
          line-height: 1.5;
          color: var(--color-text-main);
        }
      `}</style>
    </div>
  )
}

export default Dashboard
