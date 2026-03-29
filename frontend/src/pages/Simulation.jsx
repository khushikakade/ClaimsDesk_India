import React, { useEffect, useState } from 'react'
import { api } from '../services/api'
import { 
  Play, 
  RotateCcw, 
  Terminal, 
  Activity, 
  Target, 
  Award, 
  ChevronRight,
  Info
} from 'lucide-react'

const Simulation = () => {
  const [tasks, setTasks] = useState([])
  const [selectedTask, setSelectedTask] = useState(null)
  const [session, setSession] = useState(null)
  const [lastResult, setLastResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionType, setActionType] = useState('view_claim_summary')

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const data = await api.getTasks()
        setTasks(data)
        if (data.length > 0) setSelectedTask(data[0].id)
      } catch (err) {
        console.error("Failed to fetch tasks", err)
      } finally {
        setLoading(false)
      }
    }
    fetchTasks()
  }, [])

  const handleReset = async () => {
    if (!selectedTask) return
    setLoading(true)
    try {
      const data = await api.resetSimulation(selectedTask)
      setSession(data)
      setLastResult(null)
    } catch (err) {
      alert("Reset failed")
    } finally {
      setLoading(false)
    }
  }

  const handleStep = async () => {
    if (!session) return
    setLoading(true)
    try {
      const data = await api.stepSimulation({ action_type: actionType })
      setLastResult(data)
      setSession({ ...session, observation: data.observation })
    } catch (err) {
      alert("Step failed")
    } finally {
      setLoading(false)
    }
  }

  const ALL_ACTIONS = [
    "view_claim_summary", "view_policy_details", "view_repair_estimate", 
    "view_witness_statement", "view_police_report", "request_police_report", 
    "request_repair_invoice", "mark_fraud_suspected", "flag_inconsistency",
    "approve_claim", "deny_claim", "offer_partial_settlement"
  ]

  return (
    <div className="simulation">
      <header className="page-header">
        <h1 className="h1">Benchmark Simulation</h1>
        <p className="text-muted">Interact directly with the OpenEnv execution environment. Monitor real-world reasoning trajectories.</p>
      </header>

      <div className="sim-layout">
        <div className="sim-controls-col">
          <section className="card control-panel">
            <h2 className="h3">Task Configuration</h2>
            <div className="task-selector">
              <label>Select Task Environment</label>
              <select 
                value={selectedTask} 
                onChange={(e) => setSelectedTask(e.target.value)}
                disabled={session !== null}
              >
                {tasks.map(t => (
                  <option key={t.id} value={t.id}>{t.id} ({t.difficulty})</option>
                ))}
              </select>
            </div>
            
            <div className="control-actions">
              <button 
                className="sim-btn reset" 
                onClick={handleReset}
                disabled={loading}
              >
                <RotateCcw size={18} /> {session ? 'Restart Session' : 'Start Session'}
              </button>
            </div>
          </section>

          {session && (
            <section className="card action-panel">
              <h2 className="h3">Environment Interaction</h2>
              <div className="action-select-group">
                <label>Next Action</label>
                <select value={actionType} onChange={(e) => setActionType(e.target.value)}>
                  {ALL_ACTIONS.map(a => (
                    <option key={a} value={a}>{a.replace(/_/g, ' ')}</option>
                  ))}
                </select>
              </div>
              <button 
                className="sim-btn step" 
                onClick={handleStep}
                disabled={loading || (lastResult && lastResult.done)}
              >
                <Play size={18} /> Execute Step
              </button>
              
              {lastResult && lastResult.done && (
                <div className="completion-alert">
                  <Award size={18} />
                  <span>Episode Completed</span>
                </div>
              )}
            </section>
          )}

          {lastResult && (
             <section className="card stats-panel">
                <h3 className="h3">Step Feedback</h3>
                <div className="stat-row">
                   <span className="stat-label">Last Reward</span>
                   <span className={`stat-val ${lastResult.reward >= 0 ? 'pos' : 'neg'}`}>
                      {lastResult.reward > 0 ? '+' : ''}{lastResult.reward.toFixed(2)}
                   </span>
                </div>
                <div className="stat-row">
                   <span className="stat-label">Budget Remaining</span>
                   <span className="stat-val">{session.observation.episode.investigation_budget_remaining}</span>
                </div>
                <div className="stat-row">
                   <span className="stat-label">Currency Context</span>
                   <span className="stat-val">INR (₹)</span>
                </div>
             </section>
          )}
        </div>

        <div className="sim-view-col">
          <div className="view-tabs">
             <button className="view-tab active">Current Observation</button>
             <button className="view-tab">Trajectory History</button>
          </div>

          <div className="card observation-card">
            <div className="obs-header">
               <Terminal size={18} />
               <span>Raw Observation State</span>
            </div>
            {session ? (
              <pre className="json-pre">
                {JSON.stringify(session.observation, null, 2)}
              </pre>
            ) : (
              <div className="obs-empty">
                <Info size={32} className="text-muted" />
                <p>Start a session to view environment state.</p>
              </div>
            )}
          </div>
          
          {lastResult && lastResult.trajectory && (
            <div className="card trajectory-card">
               <h3 className="h3">Action Trajectory</h3>
               <div className="traj-list">
                  {lastResult.trajectory.actions.map((act, i) => (
                    <div key={i} className="traj-item">
                       <span className="traj-index">Step {i+1}</span>
                       <span className="traj-action">{act}</span>
                       <ChevronRight size={14} className="text-muted" />
                    </div>
                  ))}
               </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .sim-layout { display: grid; grid-template-columns: 320px 1fr; gap: 2rem; align-items: flex-start; }
        
        .control-panel, .action-panel, .stats-panel { margin-bottom: 1.5rem; }
        
        .task-selector, .action-select-group { 
          display: flex; 
          flex-direction: column; 
          gap: 0.5rem; 
          margin-top: 1rem;
          margin-bottom: 1.5rem;
        }

        .task-selector label, .action-select-group label {
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--color-text-muted);
          text-transform: uppercase;
        }

        select {
          padding: 0.625rem;
          border-radius: var(--radius-md);
          border: 1px solid var(--color-border);
          background: white;
          font-size: 0.875rem;
          outline: none;
        }

        .sim-btn {
          width: 100%;
          padding: 0.75rem;
          border-radius: var(--radius-md);
          font-weight: 600;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          transition: all 0.2s;
        }

        .sim-btn.reset { border: 1px solid var(--color-primary); color: var(--color-primary); }
        .sim-btn.reset:hover { background: var(--color-primary-light); }

        .sim-btn.step { background: var(--color-primary); color: white; margin-top: 1rem; }
        .sim-btn.step:hover:not(:disabled) { background: var(--color-primary-dark); }
        .sim-btn.step:disabled { opacity: 0.5; cursor: not-allowed; }

        .completion-alert {
          margin-top: 1.25rem;
          background: var(--color-success-light);
          color: var(--color-success);
          padding: 0.75rem;
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 600;
          font-size: 0.875rem;
        }

        .stat-row { 
          display: flex; 
          justify-content: space-between; 
          padding: 0.5rem 0;
          font-size: 0.875rem;
        }
        .stat-label { color: var(--color-text-muted); }
        .stat-val { font-weight: 600; }
        .stat-val.pos { color: var(--color-success); }
        .stat-val.neg { color: var(--color-danger); }

        .view-tabs { display: flex; gap: 1rem; margin-bottom: 1rem; }
        .view-tab { 
          padding: 0.5rem 1rem; 
          font-weight: 600; 
          font-size: 0.875rem; 
          color: var(--color-text-muted); 
          border-bottom: 2px solid transparent;
        }
        .view-tab.active { color: var(--color-primary); border-bottom-color: var(--color-primary); }

        .observation-card { padding: 0; background: #1E293B; border-color: #334155; }
        .obs-header { 
          padding: 0.75rem 1.25rem; 
          border-bottom: 1px solid #334155; 
          display: flex; 
          align-items: center; 
          gap: 0.5rem; 
          color: #94A3B8;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .json-pre {
          padding: 1.25rem;
          color: #E2E8F0;
          font-family: 'Monaco', 'Consolas', monospace;
          font-size: 0.8125rem;
          max-height: 500px;
          overflow-y: auto;
          line-height: 1.5;
        }

        .obs-empty {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 5rem;
          color: #64748B;
        }

        .trajectory-card { margin-top: 1.5rem; }
        .traj-list { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1rem; }
        .traj-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 0.5rem 1rem;
          background: var(--color-bg);
          border-radius: var(--radius-sm);
        }
        .traj-index { font-size: 0.75rem; font-weight: 700; color: var(--color-text-muted); width: 60px; }
        .traj-action { font-size: 0.875rem; font-weight: 600; flex: 1; }
      `}</style>
    </div>
  )
}

export default Simulation
