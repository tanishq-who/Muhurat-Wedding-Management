import { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/enquiries', icon: 'folder_open', label: 'Enquiries' },
  { to: '/agreements', icon: 'description', label: 'Agreements' },
  { to: '/quotes', icon: 'receipt_long', label: 'Quotes' },
  { to: '/wedding-plan', icon: 'event_note', label: 'Wedding Plan' },
  { to: '/muhurat-timeline', icon: 'schedule', label: 'Muhurat Timeline' },
  { to: '/settlement', icon: 'payments', label: 'Settlement' },
  { to: '/season-review', icon: 'bar_chart', label: 'Season Review' },
]

export default function Layout({ onSignOut }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const navigate = useNavigate()

  const handleSignOut = () => {
    setSidebarOpen(false)
    if (onSignOut) onSignOut()
  }

  return (
    <div className="app-shell">
      {/* Mobile overlay */}
      <div
        className={`sidebar-overlay${sidebarOpen ? ' show' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <aside className={`sidebar${sidebarOpen ? ' open' : ''}`}>
        {/* Brand */}
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">
            <div className="sidebar-logo-mark" />
            <span className="sidebar-brand-name">Muhurat</span>
          </div>
          <div className="sidebar-sub">The Royal Knot</div>
          <div className="sidebar-tagline">Palace Wedding Operations</div>
        </div>

        {/* Nav */}
        <nav className="sidebar-nav">
          {NAV_ITEMS.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <span className="material-symbols-outlined">{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Heritage Badge */}
        <div className="sidebar-footer">
          <div className="heritage-badge">
            <span className="material-symbols-outlined" style={{ color: 'var(--gold)', fontSize: 18 }}>fort</span>
            <div>
              <div className="heritage-badge-text">Heritage Network</div>
              <div className="heritage-badge-sub">Jaipur &amp; Udaipur</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Right column: topbar + content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden' }}>
        {/* Topbar */}
        <header className="topbar">
          {/* Mobile hamburger */}
          <button
            className="btn-ghost hide-desktop"
            style={{ padding: '6px', display: 'flex' }}
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
          >
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>menu</span>
          </button>

          <div className="topbar-chip hide-mobile">
            <span className="material-symbols-outlined">location_on</span>
            Jaipur &amp; Udaipur HQ
          </div>
          <div className="topbar-chip gold hide-mobile">
            <span className="material-symbols-outlined">brightness_5</span>
            Auspicious Muhurat: 19:42 IST
          </div>

          <div className="topbar-search">
            <span className="material-symbols-outlined">search</span>
            <input type="text" placeholder="Search royales, dates, folios…" />
          </div>

          <button className="topbar-btn-primary hide-mobile">
            <span className="material-symbols-outlined">add</span>
            Quick Entry
          </button>

          <div className="topbar-profile">
            <div className="topbar-avatar">PR</div>
            <div className="topbar-profile-text">
              <div className="topbar-profile-name">Pooja Rathore</div>
              <div className="topbar-profile-role">Founder</div>
            </div>
          </div>

          <button className="topbar-signout" onClick={handleSignOut}>
            <span className="material-symbols-outlined">logout</span>
            <span className="hide-mobile">Sign out</span>
          </button>
        </header>

        {/* Page content */}
        <div className="main-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
