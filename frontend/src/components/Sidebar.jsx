import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside className="sidebar">

      {/* ==================================================
          LOGO
          ================================================== */}

      <div className="sidebar-logo">

        <div className="logo-mark">
          T
        </div>

        <div>
          <h2>TANGLE</h2>
          <span>Finance Intelligence</span>
        </div>

      </div>


      {/* ==================================================
          NAVIGATION
          ================================================== */}

      <nav className="sidebar-nav">

        {/* DASHBOARD */}

        <NavLink
          to="/"
          className={({ isActive }) =>
            isActive
              ? "nav-item active"
              : "nav-item"
          }
        >
          <span>▦</span>
          Dashboard
        </NavLink>


        {/* CASES */}

        <NavLink
          to="/cases"
          className={({ isActive }) =>
            isActive
              ? "nav-item active"
              : "nav-item"
          }
        >
          <span>□</span>
          Cases
        </NavLink>


        {/* DATA QUALITY */}

        <NavLink
          to="/data-quality"
          className={({ isActive }) =>
            isActive
              ? "nav-item active"
              : "nav-item"
          }
        >
          <span>✓</span>
          Data Quality
        </NavLink>


        {/* DATA INGESTION */}

        <NavLink
          to="/data-ingestion"
          className={({ isActive }) =>
            isActive
              ? "nav-item active"
              : "nav-item"
          }
        >
          <span>⇩</span>
          Data Ingestion
        </NavLink>


        {/* RECONCILIATION */}

        <NavLink
          to="/reconciliation"
          className={({ isActive }) =>
            isActive
              ? "nav-item active"
              : "nav-item"
          }
        >
          <span>⇄</span>
          Reconciliation
        </NavLink>


        {/* HUMAN REVIEW */}

        <NavLink
          to="/review"
          className={({ isActive }) =>
            isActive
              ? "nav-item active"
              : "nav-item"
          }
        >
          <span>◉</span>
          Human Review
        </NavLink>


        {/* AUDIT TRAIL */}

        <NavLink
          to="/audit"
          className={({ isActive }) =>
            isActive
              ? "nav-item active"
              : "nav-item"
          }
        >
          <span>◌</span>
          Audit Trail
        </NavLink>


        {/* ANALYTICS */}

        <NavLink
          to="/analytics"
          className={({ isActive }) =>
            isActive
              ? "nav-item active"
              : "nav-item"
          }
        >
          <span>↗</span>
          Analytics
        </NavLink>

      </nav>


      {/* ==================================================
          SYSTEM STATUS
          ================================================== */}

      <div className="sidebar-footer">

        <div className="system-status">

          <span className="status-dot"></span>

          System Operational

        </div>

      </div>

    </aside>
  );
}

export default Sidebar;