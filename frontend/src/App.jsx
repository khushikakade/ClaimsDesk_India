import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  ClipboardList, 
  PlayCircle, 
  Search, 
  Bell, 
  User,
  ShieldCheck
} from 'lucide-react'

// Placeholder Pages - to be implemented next
import Dashboard from './pages/Dashboard'
import ClaimsQueue from './pages/ClaimsQueue'
import ClaimDetail from './pages/ClaimDetail'
import Simulation from './pages/Simulation'

const SidebarItem = ({ icon: Icon, label, to, active }) => (
  <Link 
    to={to} 
    className={`sidebar-item ${active ? 'active' : ''}`}
  >
    <Icon size={20} />
    <span className="sidebar-label">{label}</span>
  </Link>
)

const Layout = ({ children }) => {
  const location = useLocation();
  
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="logo-section">
          <ShieldCheck size={32} color="var(--color-primary)" />
          <span className="logo-text">ClaimsDesk</span>
        </div>
        
        <nav className="sidebar-nav">
          <SidebarItem 
            icon={LayoutDashboard} 
            label="Dashboard" 
            to="/" 
            active={location.pathname === '/'} 
          />
          <SidebarItem 
            icon={ClipboardList} 
            label="Claims Queue" 
            to="/claims" 
            active={location.pathname.startsWith('/claims')} 
          />
          <SidebarItem 
            icon={PlayCircle} 
            label="Simulation" 
            to="/simulation" 
            active={location.pathname === '/simulation'} 
          />
        </nav>
        
        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="avatar">KS</div>
            <div className="user-info">
              <span className="user-name">Kavit Shah</span>
              <span className="user-role">Senior Adjuster</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="top-header">
          <div className="search-bar">
            <Search size={18} className="text-muted" />
            <input type="text" placeholder="Search claims, policies, or claimants..." />
          </div>
          <div className="header-actions">
            <button className="header-icon-btn"><Bell size={20} /></button>
            <button className="header-icon-btn"><User size={20} /></button>
          </div>
        </header>
        
        <div className="page-wrapper">
          {children}
        </div>
      </main>

      <style>{`
        .app-layout {
          display: flex;
          min-height: 100vh;
        }

        .sidebar {
          width: 260px;
          background: #111827;
          color: white;
          display: flex;
          flex-direction: column;
          padding: 1.5rem 0;
          border-right: 1px solid var(--color-border);
        }

        .logo-section {
          padding: 0 1.5rem 2rem;
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .logo-text {
          font-size: 1.5rem;
          font-weight: 700;
          letter-spacing: -0.025em;
        }

        .sidebar-nav {
          flex: 1;
        }

        .sidebar-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1.5rem;
          color: #9CA3AF;
          transition: all 0.2s ease;
          border-left: 2px solid transparent;
        }

        .sidebar-item:hover {
          color: white;
          background: rgba(255, 255, 255, 0.05);
        }

        .sidebar-item.active {
          color: white;
          background: rgba(255, 255, 255, 0.1);
          border-left-color: var(--color-primary);
        }

        .sidebar-label {
          font-weight: 500;
        }

        .sidebar-footer {
          margin-top: auto;
          padding: 1.5rem;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .user-profile {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .avatar {
          width: 32px;
          height: 32px;
          background: var(--color-primary);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.875rem;
          font-weight: 600;
        }

        .user-info {
          display: flex;
          flex-direction: column;
        }

        .user-name { font-size: 0.875rem; font-weight: 600; }
        .user-role { font-size: 0.75rem; color: #9CA3AF; }

        .top-header {
          height: 64px;
          background: white;
          border-bottom: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 2rem;
          position: sticky;
          top: 0;
          z-index: 10;
        }

        .search-bar {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: var(--color-bg);
          padding: 0.5rem 1rem;
          border-radius: var(--radius-md);
          width: 400px;
        }

        .search-bar input {
          border: none;
          background: none;
          outline: none;
          width: 100%;
          font-size: 0.875rem;
        }

        .header-actions {
          display: flex;
          gap: 1rem;
        }

        .header-icon-btn {
          color: var(--color-text-muted);
          transition: color 0.2s;
        }

        .header-icon-btn:hover { color: var(--color-text-main); }

        .page-wrapper {
          padding: 2rem;
        }
      `}</style>
    </div>
  )
}

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/claims" element={<ClaimsQueue />} />
          <Route path="/claims/:claimId" element={<ClaimDetail />} />
          <Route path="/simulation" element={<Simulation />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
