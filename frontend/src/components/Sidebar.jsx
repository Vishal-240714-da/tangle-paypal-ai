import { NavLink } from "react-router-dom";
import {
  Activity,
  BarChart3,
  ClipboardCheck,
  Database,
  FileSearch,
  GitCompare,
  LayoutDashboard,
  ShieldCheck,
  Upload,
} from "lucide-react";

const navigationItems = [
  {
    path: "/",
    label: "Dashboard",
    description: "System overview",
    icon: LayoutDashboard,
  },
  {
    path: "/cases",
    label: "Cases",
    description: "Exception management",
    icon: FileSearch,
  },
  {
    path: "/data-quality",
    label: "Data Quality",
    description: "Data validation",
    icon: Database,
  },
  {
    path: "/data-ingestion",
    label: "Data Ingestion",
    description: "Import datasets",
    icon: Upload,
  },
  {
    path: "/reconciliation",
    label: "Reconciliation",
    description: "Transaction matching",
    icon: GitCompare,
  },
  {
    path: "/review",
    label: "Human Review",
    description: "Decision workspace",
    icon: ClipboardCheck,
  },
  {
    path: "/audit",
    label: "Audit Trail",
    description: "Governance history",
    icon: ShieldCheck,
  },
  {
    path: "/analytics",
    label: "Analytics",
    description: "Risk intelligence",
    icon: BarChart3,
  },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-mark">T</div>

        <div className="sidebar-brand-text">
          <div className="sidebar-brand-name">TANGLE</div>
          <div className="sidebar-brand-subtitle">
            Finance Intelligence
          </div>
        </div>
      </div>

      {/* Workspace navigation */}
      <div className="sidebar-navigation">
        <div className="sidebar-section-label">WORKSPACE</div>

        <nav className="sidebar-nav" aria-label="Primary navigation">
          {navigationItems.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === "/"}
                className={({ isActive }) =>
                  `sidebar-nav-item${isActive ? " active" : ""}`
                }
              >
                <span className="sidebar-nav-icon">
                  <Icon size={18} strokeWidth={1.9} />
                </span>

                <span className="sidebar-nav-content">
                  <span className="sidebar-nav-label">
                    {item.label}
                  </span>

                  <span className="sidebar-nav-description">
                    {item.description}
                  </span>
                </span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Bottom system status */}
      <div className="sidebar-bottom">
        <div className="sidebar-system-card">
          <div className="sidebar-system-icon">
            <Activity size={16} strokeWidth={2} />
          </div>

          <div className="sidebar-system-content">
            <div className="sidebar-system-title">
              <span className="sidebar-status-dot"></span>
              System Operational
            </div>

            <div className="sidebar-system-description">
              All services running
            </div>
          </div>
        </div>

        <div className="sidebar-footer">
          <span>TANGLE Enterprise</span>
          <span className="sidebar-footer-separator">•</span>
          <span>v1.0</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;