import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        <div className="logo-mark">T</div>

        <div>
          <h2>TANGLE</h2>
          <span>Finance Intelligence</span>
        </div>
      </div>

      <nav className="sidebar-nav">

        <NavLink
          to="/"
          className={({ isActive }) =>
            isActive ? "nav-item active" : "nav-item"
          }
        >
          <span>📊</span>
          Dashboard
        </NavLink>

        <NavLink
          to="/cases"
          className={({ isActive }) =>
            isActive ? "nav-item active" : "nav-item"
          }
        >
          <span>📁</span>
          Cases
        </NavLink>

        <NavLink
          to="/review"
          className={({ isActive }) =>
            isActive ? "nav-item active" : "nav-item"
          }
        >
          <span>👤</span>
          Human Review
        </NavLink>

        <NavLink
          to="/analytics"
          className={({ isActive }) =>
            isActive ? "nav-item active" : "nav-item"
          }
        >
          <span>📈</span>
          Analytics
        </NavLink>

      </nav>

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