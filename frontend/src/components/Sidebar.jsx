import { NavLink } from "react-router-dom";

function Sidebar() {
  const navigationItems = [
    {
      path: "/",
      label: "Dashboard",
      icon: "▦",
    },
    {
      path: "/cases",
      label: "Cases",
      icon: "◫",
    },
    {
      path: "/data-quality",
      label: "Data Quality",
      icon: "✓",
    },
    {
      path: "/data-ingestion",
      label: "Data Ingestion",
      icon: "⇩",
    },
    {
      path: "/reconciliation",
      label: "Reconciliation",
      icon: "⇄",
    },
    {
      path: "/review",
      label: "Human Review",
      icon: "◉",
    },
    {
      path: "/audit",
      label: "Audit Trail",
      icon: "◌",
    },
    {
      path: "/analytics",
      label: "Analytics",
      icon: "↗",
    },
  ];

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-logo">
        <div className="logo-mark">T</div>

        <div className="logo-text">
          <h2>TANGLE</h2>
          <span>Finance Intelligence</span>
        </div>
      </div>

      {/* Navigation */}
      <div className="sidebar-section-title">WORKSPACE</div>

      <nav className="sidebar-nav">
        {navigationItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              isActive ? "nav-item active" : "nav-item"
            }
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom status */}
      <div className="sidebar-footer">
        <div className="system-status">
          <span className="status-dot"></span>

          <div>
            <strong>System Operational</strong>
            <small>All services running</small>
          </div>
        </div>

        <div className="sidebar-version">
          TANGLE Enterprise
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;