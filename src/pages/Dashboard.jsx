import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import "../App.css";

function Dashboard() {
  return (
    <div className="app">
      <Sidebar />

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">OFFICER DASHBOARD</p>

            <h2>Good evening, Officer Sharma</h2>

            <p className="subtitle">
              Here’s a clear view of your current case and welfare priorities.
            </p>
          </div>

          <div className="topbar-actions">
            <button
              className="icon-button"
              aria-label="Notifications"
            >
              ♢
            </button>

            <button className="user-chip">
              <div className="avatar small">AS</div>
              <span>Officer Sharma</span>
              <span>⌄</span>
            </button>
          </div>
        </header>

        {/* Summary */}
        <section className="stats-grid">
          <article className="stat-card">
            <div className="stat-icon">◉</div>

            <div>
              <p>Active Victims</p>
              <h3>128</h3>

              <span className="stat-detail">
                Across your assigned cases
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">▣</div>

            <div>
              <p>Active Cases</p>
              <h3>24</h3>

              <span className="stat-detail">
                6 require recent follow-up
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon alert">!</div>

            <div>
              <p>High Concern</p>
              <h3>08</h3>

              <span className="stat-detail">
                Human review recommended
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">♡</div>

            <div>
              <p>Welfare Needs</p>
              <h3>11</h3>

              <span className="stat-detail">
                Pending coordination
              </span>
            </div>
          </article>
        </section>

        {/* Main dashboard */}
        <section className="dashboard-grid">
          {/* Priority cases */}
          <article className="panel priority-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  ATTENTION NEEDED
                </p>

                <h3>Priority cases</h3>
              </div>

              <Link
                className="text-button"
                to="/priority-cases"
              >
                View all →
              </Link>
            </div>

            <div className="case-list">
              <Link
                className="case-row case-link"
                to="/cases/CASE-2026-014"
              >
                <div className="case-main">
                  <div className="case-id">
                    CASE-2026-014
                  </div>

                  <strong>
                    Active case · Court / Delay
                  </strong>

                  <span>
                    Last check-in · 2 days ago
                  </span>
                </div>

                <div className="case-status">
                  <span className="risk-badge high">
                    High concern
                  </span>

                  <span className="ddi">
                    DDI 72
                  </span>
                </div>
              </Link>

              <Link
                className="case-row case-link"
                to="/cases/CASE-2026-011"
              >
                <div className="case-main">
                  <div className="case-id">
                    CASE-2026-011
                  </div>

                  <strong>
                    Active case · Investigation
                  </strong>

                  <span>
                    Last check-in · 1 day ago
                  </span>
                </div>

                <div className="case-status">
                  <span className="risk-badge moderate">
                    Moderate
                  </span>

                  <span className="ddi">
                    DDI 58
                  </span>
                </div>
              </Link>

              <Link
                className="case-row case-link"
                to="/cases/CASE-2026-009"
              >
                <div className="case-main">
                  <div className="case-id">
                    CASE-2026-009
                  </div>

                  <strong>
                    Active case · Trial
                  </strong>

                  <span>
                    Last check-in · 4 days ago
                  </span>
                </div>

                <div className="case-status">
                  <span className="risk-badge low">
                    Low
                  </span>

                  <span className="ddi">
                    DDI 31
                  </span>
                </div>
              </Link>
            </div>
          </article>

          {/* Case journey */}
          <article className="panel journey-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  CASE JOURNEY
                </p>

                <h3>CASE-2026-014</h3>
              </div>

              <span className="status-pill">
                Active
              </span>
            </div>

            <p className="journey-description">
              Current stage:{" "}
              <strong>Court / Delay</strong>
            </p>

            <div className="timeline">
              <div className="timeline-step complete">
                <span className="timeline-dot">
                  ✓
                </span>

                <div>
                  <strong>Complaint</strong>
                  <small>Completed</small>
                </div>
              </div>

              <div className="timeline-line complete-line" />

              <div className="timeline-step complete">
                <span className="timeline-dot">
                  ✓
                </span>

                <div>
                  <strong>Investigation</strong>
                  <small>Completed</small>
                </div>
              </div>

              <div className="timeline-line complete-line" />

              <div className="timeline-step current">
                <span className="timeline-dot">
                  ●
                </span>

                <div>
                  <strong>Court / Delay</strong>
                  <small>Current stage</small>
                </div>
              </div>

              <div className="timeline-line" />

              <div className="timeline-step">
                <span className="timeline-dot">
                  ○
                </span>

                <div>
                  <strong>Compensation</strong>
                  <small>Upcoming</small>
                </div>
              </div>

              <div className="timeline-line" />

              <div className="timeline-step">
                <span className="timeline-dot">
                  ○
                </span>

                <div>
                  <strong>Rehabilitation</strong>
                  <small>Upcoming</small>
                </div>
              </div>
            </div>
          </article>
        </section>

        {/* Bottom section */}
        <section className="bottom-grid">
          <article className="panel insight-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  WELL-BEING SIGNAL
                </p>

                <h3>CASE-2026-014</h3>
              </div>

              <span className="risk-badge high">
                High concern
              </span>
            </div>

            <div className="insight-score">
              <div>
                <span>Dynamic Distress Index</span>

                <strong>
                  72
                  <span>/100</span>
                </strong>
              </div>

              <div className="trend-up">
                ↑ Increasing
              </div>
            </div>

            <p className="insight-text">
              Recent changes indicate increased distress
              compared with this victim’s personal baseline.
            </p>

            <Link
              className="primary-button"
              to="/cases/CASE-2026-014"
            >
              Open case details
            </Link>
          </article>

          <article className="panel followup-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  COORDINATION
                </p>

                <h3>Follow-up queue</h3>
              </div>

              <Link
                className="text-button"
                to="/welfare"
              >
                View all →
              </Link>
            </div>

            <div className="followup-list">
              <div className="followup-item">
                <div className="followup-icon">
                  C
                </div>

                <div>
                  <strong>Counsellor review</strong>

                  <span>
                    CASE-2026-014 · Pending
                  </span>
                </div>

                <span className="mini-status pending">
                  Pending
                </span>
              </div>

              <div className="followup-item">
                <div className="followup-icon">
                  W
                </div>

                <div>
                  <strong>Welfare support</strong>

                  <span>
                    CASE-2026-011 · Financial support
                  </span>
                </div>

                <span className="mini-status progress">
                  In progress
                </span>
              </div>

              <div className="followup-item">
                <div className="followup-icon">
                  L
                </div>

                <div>
                  <strong>Legal coordination</strong>

                  <span>
                    CASE-2026-009 · Hearing support
                  </span>
                </div>

                <span className="mini-status done">
                  Completed
                </span>
              </div>
            </div>
          </article>
        </section>

        <footer className="app-footer">
          <span>
            PAWS · Officer Case & Welfare Coordination
          </span>

          <span>
            Demo data · Prototype environment
          </span>
        </footer>
      </main>
    </div>
  );
}

export default Dashboard;