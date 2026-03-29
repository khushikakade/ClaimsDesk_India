import React, { useEffect, useState } from 'react'
import { api } from '../services/api'
import { Link, useSearchParams } from 'react-router-dom'
import { 
  Filter, 
  Search, 
  ChevronRight, 
  ArrowUpDown 
} from 'lucide-react'

const ClaimsQueue = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const currentFilter = searchParams.get('status') || 'All'
  
  const [claims, setClaims] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    const fetchClaims = async () => {
      setLoading(true)
      try {
        const data = await api.getClaims(currentFilter)
        setClaims(data)
      } catch (err) {
        console.error("Failed to fetch claims", err)
      } finally {
        setLoading(false)
      }
    }
    fetchClaims()
  }, [currentFilter])

  const filteredClaims = claims.filter(c => 
    c.claimant_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.claim_id.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const tabs = ['All', 'Urgent', 'Suspicious', 'Missing Docs', 'Escalated']

  return (
    <div className="claims-queue">
      <header className="page-header">
        <h1 className="h1">Claims Workbench</h1>
        <p className="text-muted">Review and triage incoming claims. All items are pre-analyzed by AI.</p>
      </header>

      <div className="card toolbar">
        <div className="tabs">
          {tabs.map(tab => (
            <button 
              key={tab} 
              className={`tab ${currentFilter === tab ? 'active' : ''}`}
              onClick={() => setSearchParams({ status: tab })}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="search-group">
          <div className="search-input-wrapper">
            <Search size={18} />
            <input 
              type="text" 
              placeholder="Search by ID or name..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="filter-btn">
            <Filter size={18} />
            Filters
          </button>
        </div>
      </div>

      <div className="card table-container">
        <table className="claims-table">
          <thead>
            <tr>
              <th><div className="th-content">Claim ID <ArrowUpDown size={14} /></div></th>
              <th>Claimant</th>
              <th>Type</th>
              <th>Amount</th>
              <th>AI Priority</th>
              <th>Risk Level</th>
              <th>Status</th>
              <th>Date</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="9" className="loading-row">Retrieving operational data...</td></tr>
            ) : filteredClaims.length === 0 ? (
              <tr><td colSpan="9" className="empty-row">No claims found for this filter.</td></tr>
            ) : filteredClaims.map(claim => (
              <tr key={claim.claim_id} className="claim-row">
                <td><Link to={`/claims/${claim.claim_id}`} className="claim-id-link">{claim.claim_id}</Link></td>
                <td><span className="claimant-name">{claim.claimant_name}</span></td>
                <td><span className="claim-type-text">{claim.claim_type.replace(/_/g, ' ')}</span></td>
                <td><span className="claim-amount-text">₹{claim.amount.toLocaleString('en-IN')}</span></td>
                <td>
                  <span className={`priority-pill ${claim.ai_priority}`}>
                    {claim.ai_priority}
                  </span>
                </td>
                <td>
                  <div className="risk-indicator">
                    <div 
                      className="risk-bar" 
                      style={{ 
                        width: `${claim.suspicion_level * 100}%`,
                        backgroundColor: claim.suspicion_level > 0.6 ? 'var(--color-danger)' : 
                                        claim.suspicion_level > 0.3 ? 'var(--color-warning)' : 
                                        'var(--color-success)'
                      }} 
                    />
                    <span className="risk-value">{Math.round(claim.suspicion_level * 100)}%</span>
                  </div>
                </td>
                <td>
                  <span className={`badge badge-neutral ${claim.status}`}>
                    {claim.status.replace('_', ' ')}
                  </span>
                </td>
                <td><span className="date-text">{claim.submission_date}</span></td>
                <td>
                  <Link to={`/claims/${claim.claim_id}`} className="action-btn">
                    <ChevronRight size={18} />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <style>{`
        .toolbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 1.5rem;
          margin-bottom: 1.5rem;
          border-radius: var(--radius-md);
        }

        .tabs { display: flex; gap: 0.5rem; }

        .tab {
          padding: 0.5rem 1rem;
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--color-text-muted);
          border-radius: var(--radius-sm);
        }

        .tab:hover { background: var(--color-bg); color: var(--color-text-main); }
        .tab.active { background: var(--color-primary-light); color: var(--color-primary); }

        .search-group { display: flex; gap: 1rem; }

        .search-input-wrapper {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: var(--color-bg);
          padding: 0.5rem 0.75rem;
          border-radius: var(--radius-md);
          border: 1px solid var(--color-border);
          width: 300px;
        }

        .search-input-wrapper input {
          border: none;
          background: none;
          outline: none;
          font-size: 0.875rem;
          flex: 1;
        }

        .filter-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          font-size: 0.875rem;
          font-weight: 500;
        }

        .table-container { padding: 0; overflow: hidden; }

        .claims-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.875rem;
        }

        .claims-table th {
          text-align: left;
          padding: 1rem 1.5rem;
          background: #F9FAFB;
          border-bottom: 1px solid var(--color-border);
          color: var(--color-text-muted);
          font-weight: 600;
          font-size: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .th-content { display: flex; align-items: center; gap: 0.25rem; }

        .claim-row {
          border-bottom: 1px solid var(--color-border);
          transition: background 0.2s;
        }

        .claim-row:hover { background: #F9FAFB; }
        .claim-row:last-child { border-bottom: none; }

        .claims-table td { padding: 1rem 1.5rem; }

        .claim-id-link { color: var(--color-primary); font-weight: 600; }
        .claimant-name { font-weight: 500; color: var(--color-text-main); }
        .claim-type-text { text-transform: capitalize; }
        .claim-amount-text { font-weight: 600; }

        .priority-pill {
          padding: 0.125rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .priority-pill.high { background: #FEE2E2; color: #DC2626; }
        .priority-pill.medium { background: #FFEDD5; color: #EA580C; }
        .priority-pill.low { background: #E0E7FF; color: #4338CA; }

        .risk-indicator {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          width: 120px;
        }

        .risk-bar {
          height: 6px;
          background: #E5E7EB;
          border-radius: 9999px;
          overflow: hidden;
          position: relative;
        }

        .risk-value { font-size: 0.75rem; font-weight: 600; color: var(--color-text-muted); min-width: 30px; }

        .action-btn { color: var(--color-text-muted); }
        .action-btn:hover { color: var(--color-primary); }

        .loading-row, .empty-row {
          text-align: center;
          padding: 4rem !important;
          color: var(--color-text-muted);
        }

        /* Status colors */
        .badge.approved { background: var(--color-success-light); color: var(--color-success); border: 1px solid #A7F3D0; }
        .badge.denied { background: var(--color-danger-light); color: var(--color-danger); border: 1px solid #FECACA; }
        .badge.escalated { background: #E0E7FF; color: #4338CA; border: 1px solid #C7D2FE; }
        .badge.pending_review { background: #F3F4F6; color: #374151; border: 1px solid #D1D5DB; }
      `}</style>
    </div>
  )
}

export default ClaimsQueue
