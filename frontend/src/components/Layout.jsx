import {
  Bell,
  ChevronDown,
  Command,
  Search,
} from "lucide-react";

import Sidebar from "./Sidebar";

function Layout({ children }) {
  return (
    <div className="app-shell">
      <Sidebar />

      <div className="app-workspace">
        {/* Top application bar */}
        <header className="app-topbar">
          <div className="app-topbar-left">
            <div className="app-search">
              <Search size={17} strokeWidth={2} />

              <input
                type="search"
                placeholder="Search cases, transactions..."
                aria-label="Search"
              />

              <div className="app-search-shortcut">
                <Command size={12} strokeWidth={2} />
                <span>K</span>
              </div>
            </div>
          </div>

          <div className="app-topbar-right">
            <button
              type="button"
              className="app-icon-button"
              aria-label="Notifications"
            >
              <Bell size={19} strokeWidth={1.9} />
              <span className="notification-indicator"></span>
            </button>

            <div className="app-topbar-divider"></div>

            <button
              type="button"
              className="app-user-menu"
              aria-label="User menu"
            >
              <div className="app-user-avatar">TA</div>

              <div className="app-user-info">
                <span className="app-user-name">
                  TANGLE Admin
                </span>

                <span className="app-user-role">
                  Administrator
                </span>
              </div>

              <ChevronDown size={16} strokeWidth={1.8} />
            </button>
          </div>
        </header>

        {/* Page workspace */}
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}

export default Layout;