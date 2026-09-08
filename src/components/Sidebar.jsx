import {
  LayoutDashboard,
  FolderKanban,
  UsersRound,
  TriangleAlert,
  HeartHandshake,
  ChartNoAxesCombined,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import "../App.css";

const navigationItems = [
  {
    label: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Cases",
    path: "/cases",
    icon: FolderKanban,
  },
  {
    label: "Victims",
    path: "/victims",
    icon: UsersRound,
  },
  {
    label: "Priority Cases",
    path: "/priority-cases",
    icon: TriangleAlert,
  },
  {
    label: "Welfare Follow-up",
    path: "/welfare",
    icon: HeartHandshake,
  },
  {
    label: "Analytics",
    path: "/analytics",
    icon: ChartNoAxesCombined,
  },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">P</div>

        <div className="brand-copy">
          <h1>PAWS</h1>
          <span>Officer Portal</span>
        </div>
      </div>

      <nav className="navigation">
        {navigationItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <Icon
                className="nav-icon"
                size={17}
                strokeWidth={1.8}
              />

              <span className="nav-label">
                {item.label}
              </span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="security-note">
          <div className="security-icon">
            ✓
          </div>

          <div>
            <strong>Secure workspace</strong>
            <small>Role-based access</small>
          </div>
        </div>

        <button className="profile">
          <div className="avatar">AS</div>

          <div className="profile-copy">
            <strong>Officer Sharma</strong>
            <small>Case Coordinator</small>
          </div>

          <span className="profile-arrow">›</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;