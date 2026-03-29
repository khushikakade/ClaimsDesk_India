import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import { 
  ArrowLeft, 
  ExternalLink, 
  FileText, 
  AlertCircle, 
  ShieldCheck, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Info,
  ChevronDown
} from 'lucide-react'

const ClaimDetail = () => {
  const { claimId } = useParams()
  const [claim, setClaim] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    const fetchClaim = async () => {
      try {
        const data = await api.getClaim(claimId)
        setClaim(data)
      } catch (err) {
        console.error("Failed to fetch claim", err)
      } finally {
        setLoading(false)
      }
    }
    fetchClaim()
  }, [claimId])

  const handleAction = async (actionType, amountInr = null) => {
    setActionLoading(true)
    try {
      const res = await api.takeAction(claimId, actionType, amountInr)
      if (res.status === 'success') {
        setClaim({ ...claim, status: res.new_status })
      }
    } catch (err) {
      alert("Action failed")
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) return <div>Loading claim details...</div>
  if (!claim) return <div>Claim not found.</div>

  return (
    <div className="claim-detail">
      <header className="detail-header">
        <div className="breadcrumb">
          <Link to="/claims" className="back-link"><ArrowLeft size={16} /> Back to Queue</Link>
          <div className="breadcrumb-meta">
             <span className="claim-id">{claim.claim_id}</span>
             <span className="separator">/</span>
             <span className="claimant-name">{claim.claimant_name}</span>
          </div>
        </div>
        <div className="header-main">
          <div className="header-title-group">
            <h1 className="h1">{claim.claim_type.replace(/_/g, ' ')} Claim</h1>
            <div className="header-badges">
              <span className={`badge ${claim.status}`}>{claim.status.replace(/_/g, ' ')}</span>
              <span className={`priority-pill ${claim.ai_priority}`}>{claim.ai_priority} Priority</span>
            </div>
          </div>
          <div className="header-actions">
            <button className="secondary-btn">Print Summary</button>
            <button className="secondary-btn">Share Case</button>
          </div>
        </div>
      </header>

      <div className="detail-grid">
        <div className="detail-main-col">
          <section className="card section-card">
            <h2 className="h3">Claim Summary</h2>
            <div className="summary-grid">
              <div className="data-item">
                <span className="data-label">Claimant</span>
                <span className="data-value">{claim.claimant_name}</span>
              </div>
              <div className="data-item">
                <span className="data-label">Incident Date</span>
                <span className="data-value">{claim.incident_date}</span>
              </div>
              <div className="data-item">
                <span className="data-label">Claim Amount</span>
                <span className="data-value">₹{claim.amount.toLocaleString('en-IN')}</span>
              </div>
              <div className="data-item">
                <span className="data-label">Policy Type</span>
                <span className="data-value">{claim.policy_type.replace(/_/g, ' ')}</span>
              </div>
              <div className="data-item">
                <span className="data-label">Submission Date</span>
                <span className="data-value">{claim.submission_date}</span>
              </div>
            </div>
          </section>

          <section className="card section-card">
            <h2 className="h3">Incident Narrative</h2>
            <p className="narrative-text">
              {claim.description}
            </p>
            <div className="extracted-facts">
              <div className="fact-item">
                <CheckCircle size={14} className="success-icon" />
                <span>Asset: {claim.asset_descriptor || "Verified Portfolio Asset"}</span>
              </div>
              <div className="fact-item">
                <CheckCircle size={14} className="success-icon" />
                <span>Location: {claim.reported_location || "Verified Geo-coordinates"}</span>
              </div>
              <div className="fact-item">
                <AlertCircle size={14} className="warning-icon" />
                <span>Possible time discrepancy detected in narrative.</span>
              </div>
            </div>
          </section>

          <section className="card section-card">
            <div className="section-header-row">
              <h2 className="h3">Evidence & Documents</h2>
              <span className="text-muted">3 documents uploaded</span>
            </div>
            <div className="documents-list">
              <div className="doc-item">
                <div className="doc-info">
                  <FileText size={20} className="doc-icon" />
                  <div className="doc-meta">
                    <span className="doc-name">Repair_Estimate_ShopA.pdf</span>
                    <span className="doc-size">1.2 MB • Uploaded 2d ago</span>
                  </div>
                </div>
                <button className="doc-action"><ExternalLink size={16} /></button>
              </div>
              <div className="doc-item">
                <div className="doc-info">
                  <FileText size={20} className="doc-icon" />
                  <div className="doc-meta">
                    <span className="doc-name">Incident_Photos_Scene.zip</span>
                    <span className="doc-size">8.4 MB • Uploaded 2d ago</span>
                  </div>
                </div>
                <button className="doc-action"><ExternalLink size={16} /></button>
              </div>
              <div className="doc-item missing">
                <div className="doc-info">
                  <AlertCircle size={20} className="warning-icon" />
                  <div className="doc-meta">
                    <span className="doc-name">Police_Incident_Report.pdf</span>
                    <span className="doc-status">Pending Request</span>
                  </div>
                </div>
                <button className="request-doc-btn">Request Now</button>
              </div>
            </div>
          </section>
        </div>

        <div className="detail-side-col">
          <section className="card ai-card">
            <div className="ai-header">
              <ShieldCheck size={24} className="ai-brand-icon" />
              <div className="ai-title-group">
                 <h2 className="ai-title">AI Intelligence</h2>
                 <span className="ai-tag">VERIFIED CONTENT</span>
              </div>
            </div>

            <div className="ai-confidence-box">
              <div className="confidence-header">
                <span className="conf-label">Operational Confidence</span>
                <span className="conf-value">{Math.round(claim.ai_analysis.ai_confidence * 100)}%</span>
              </div>
              <div className="confidence-meter">
                <div className="conf-fill" style={{ width: `${claim.ai_analysis.ai_confidence * 100}%` }} />
              </div>
            </div>

            <div className="ai-insight-list">
              <div className="ai-insight-item">
                <span className="insight-label">Suspicion Signals</span>
                <div className="insight-content">
                  {claim.ai_analysis.suspicion_signals.map((s, i) => (
                    <span key={i} className="signal-pill">{s}</span>
                  ))}
                </div>
              </div>
              <div className="ai-insight-item">
                <span className="insight-label">Recommendation</span>
                <p className="insight-text">
                  <strong>{claim.ai_analysis.recommended_next_action.replace('_', ' ')}</strong>. 
                  {claim.ai_analysis.reasoning_summary}
                </p>
              </div>
            </div>

            <div className="ai-info-alert">
              <Info size={16} />
              <p>AI suggests partial settlement of ₹{(claim.amount * 0.85).toLocaleString('en-IN')} based on regional tariff rates.</p>
            </div>
          </section>

          <section className="card action-card">
            <h2 className="h3">Human Action Console</h2>
            <div className="action-buttons">
              <button 
                className="action-btn-main approve" 
                onClick={() => handleAction('approve')}
                disabled={actionLoading || claim.status === 'approved'}
              >
                Approve for Payment
              </button>
              <button 
                className="action-btn-main secondary"
                onClick={() => handleAction('escalate')}
                disabled={actionLoading || claim.status === 'escalated'}
              >
                Escalate to Fraud
              </button>
              <div className="action-btn-group">
                <button className="action-btn-sub">Request Docs</button>
                <button 
                   className="action-btn-sub deny"
                   onClick={() => handleAction('deny')}
                   disabled={actionLoading || claim.status === 'denied'}
                >
                   Deny Claim
                </button>
              </div>
            </div>
          </section>

          <section className="timeline-section">
             <h3 className="h3">Activity Log</h3>
             <div className="timeline">
                <div className="timeline-item">
                   <div className="timeline-bullet" />
                   <div className="timeline-content">
                      <span className="timeline-time">Today, 2:15 PM</span>
                      <p className="timeline-text">Case assigned to <strong>Jane Doe</strong></p>
                   </div>
                </div>
                <div className="timeline-item">
                   <div className="timeline-bullet ai" />
                   <div className="timeline-content">
                      <span className="timeline-time">Today, 1:48 PM</span>
                      <p className="timeline-text">AI analysis completed. Risk flagged at 45%.</p>
                   </div>
                </div>
                <div className="timeline-item">
                   <div className="timeline-bullet" />
                   <div className="timeline-content">
                      <span className="timeline-time">Yesterday, 9:20 AM</span>
                      <p className="timeline-text">Claim submitted via Mobile App.</p>
                   </div>
                </div>
             </div>
          </section>
        </div>
      </div>

      <style>{`
        .detail-header { margin-bottom: 2rem; }
        .back-link { 
          display: flex; 
          align-items: center; 
          gap: 0.5rem; 
          font-size: 0.875rem; 
          color: var(--color-primary); 
          font-weight: 600; 
          margin-bottom: 1rem;
        }

        .breadcrumb-meta { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: var(--color-text-muted); }
        .separator { color: var(--color-border); }

        .header-main { display: flex; justify-content: space-between; align-items: flex-end; }
        .header-title-group { display: flex; flex-direction: column; gap: 0.5rem; }
        .header-badges { display: flex; gap: 0.5rem; }

        .header-actions { display: flex; gap: 0.75rem; }
        .secondary-btn { 
          padding: 0.5rem 1rem; 
          border: 1px solid var(--color-border); 
          border-radius: var(--radius-md);
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--color-text-main);
          background: white;
        }

        .detail-grid { display: grid; grid-template-columns: 1fr 380px; gap: 2rem; }
        .section-card { margin-bottom: 1.5rem; }

        .summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-top: 1rem; }
        .data-item { display: flex; flex-direction: column; gap: 0.25rem; }
        .data-label { font-size: 0.75rem; color: var(--color-text-muted); text-transform: uppercase; font-weight: 600; }
        .data-value { font-weight: 600; font-size: 1rem; }

        .narrative-text { font-size: 0.9375rem; line-height: 1.6; color: var(--color-text-main); margin: 1rem 0; }
        .extracted-facts { display: flex; flex-direction: column; gap: 0.5rem; background: var(--color-bg); padding: 1rem; border-radius: var(--radius-md); }
        .fact-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8125rem; }
        .success-icon { color: var(--color-success); }
        .warning-icon { color: var(--color-warning); }

        .section-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
        .documents-list { display: flex; flex-direction: column; gap: 0.75rem; }
        .doc-item { 
          display: flex; 
          justify-content: space-between; 
          align-items: center; 
          padding: 0.75rem 1rem; 
          background: var(--color-bg); 
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
        }
        .doc-info { display: flex; align-items: center; gap: 0.75rem; }
        .doc-meta { display: flex; flex-direction: column; }
        .doc-name { font-size: 0.875rem; font-weight: 600; }
        .doc-size, .doc-status { font-size: 0.75rem; color: var(--color-text-muted); }

        .doc-item.missing { background: #FFFBEB; border-color: #FDE68A; }
        .request-doc-btn { padding: 0.375rem 0.75rem; background: var(--color-primary); color: white; border-radius: var(--radius-sm); font-size: 0.75rem; font-weight: 600; }

        /* AI Side Card */
        .ai-card { background: #1E1B4B; color: white; border: none; }
        .ai-header { display: flex; gap: 0.75rem; margin-bottom: 1.5rem; }
        .ai-brand-icon { color: #818CF8; }
        .ai-tag { font-size: 0.625rem; font-weight: 700; background: rgba(255,255,255,0.1); padding: 0.125rem 0.375rem; border-radius: 4px; }
        .ai-title { font-size: 1.125rem; font-weight: 600; }

        .ai-confidence-box { margin-bottom: 1.5rem; }
        .confidence-header { display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.8125rem; }
        .confidence-meter { height: 6px; background: rgba(255,255,255,0.1); border-radius: 99px; overflow: hidden; }
        .conf-fill { height: 100%; background: linear-gradient(90deg, #6366F1, #818CF8); }

        .ai-insight-item { margin-bottom: 1.25rem; }
        .insight-label { font-size: 0.75rem; font-weight: 600; color: #818CF8; text-transform: uppercase; margin-bottom: 0.5rem; display: block; }
        .signal-pill { display: inline-block; background: rgba(255,255,255,0.05); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-right: 0.5rem; margin-bottom: 0.5rem; border: 1px solid rgba(255,255,255,0.1); }
        .insight-text { font-size: 0.875rem; line-height: 1.5; color: #E0E7FF; }
        .ai-info-alert { display: flex; gap: 0.75rem; background: rgba(129, 140, 248, 0.1); padding: 0.75rem; border-radius: var(--radius-md); font-size: 0.75rem; color: #C7D2FE; }

        /* Action Console */
        .action-card { margin-top: 1.5rem; }
        .action-buttons { display: flex; flex-direction: column; gap: 1rem; margin-top: 1rem; }
        .action-btn-main { width: 100%; padding: 0.875rem; border-radius: var(--radius-md); font-weight: 600; font-size: 0.9375rem; transition: all 0.2s; }
        .action-btn-main.approve { background: var(--color-success); color: white; }
        .action-btn-main.approve:hover:not(:disabled) { background: #059669; }
        .action-btn-main.secondary { background: white; border: 1px solid var(--color-border); color: var(--color-text-main); }
        .action-btn-main.secondary:hover { background: var(--color-bg); }

        .action-btn-group { display: flex; gap: 1rem; }
        .action-btn-sub { flex: 1; padding: 0.625rem; border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: 0.8125rem; font-weight: 500; }
        .action-btn-sub.deny { color: var(--color-danger); border-color: #FECACA; }

        /* Timeline */
        .timeline-section { margin-top: 2rem; padding: 0 0.5rem; }
        .timeline { position: relative; padding-left: 1.5rem; border-left: 1px solid var(--color-border); margin-top: 1.5rem; }
        .timeline-item { position: relative; margin-bottom: 1.5rem; }
        .timeline-bullet { 
          position: absolute; 
          left: -1.875rem; 
          top: 0.25rem; 
          width: 9px; 
          height: 9px; 
          background: white; 
          border: 2px solid var(--color-text-muted); 
          border-radius: 50%;
        }
        .timeline-bullet.ai { border-color: var(--color-primary); background: var(--color-primary); }
        .timeline-time { display: block; font-size: 0.75rem; color: var(--color-text-muted); margin-bottom: 0.25rem; }
        .timeline-text { font-size: 0.875rem; }
      `}</style>
    </div>
  )
}

export default ClaimDetail
