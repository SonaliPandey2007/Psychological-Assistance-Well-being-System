import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import "../App.css";

const priorityCases = [
  {
    id: "CASE-2026-014",
    victimId: "V-1048",
    stage: "Court / Delay",
    risk: "High concern",
    riskClass: "high",
    ddi: 72,
    lastCheckIn: "2 days ago",
    waiting: "2 days",
    action: "Counsellor review",
    actionStatus: "Pending",
    actionClass: "pending",
    reasons: [
      "Fear-related responses increasing",
      "Engagement reduced from baseline",
      "Recent court delay",
      "Distress trend moving upward",
    ],
  },

  {
    id: "CASE-2026-018",
    victimId: "V-1074",
    stage: "Investigation",
    risk: "High concern",
    riskClass: "high",
    ddi: 69,
    lastCheckIn: "3 days ago",
    waiting: "3 days",
    action: "Welfare coordination",
    actionStatus: "Pending",
    actionClass: "pending",
    reasons: [
      "Recent support need unresolved",
      "Check-in overdue",
      "Engagement has decreased",
    ],
  },

  {
    id: "CASE-2026-021",
    victimId: "V-1091",
    stage: "Trial",
    risk: "Moderate",
    riskClass: "moderate",
    ddi: 61,
    lastCheckIn: "1 day ago",
    waiting: "1 day",
    action: "Follow-up review",
    actionStatus: "In progress",
    actionClass: "progress",
    reasons: [
      "Moderate concern signal",
      "Upcoming case milestone",
      "Routine follow-up due",
    ],
  },
];

function PriorityCases() {
  return (
    <div className="app">
      <Sidebar />

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">
              ATTENTION QUEUE
            </p>

            <h2>Priority Cases</h2>

            <p className="subtitle">
              Review cases that may require timely human attention or welfare coordination.
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

        <section className="stats-grid">
          <article className="stat-card">
            <div className="stat-icon alert">!</div>

            <div>
              <p>Cases Requiring Attention</p>
              <h3>08</h3>

              <span className="stat-detail">
                Current priority queue
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">◷</div>

            <div>
              <p>Oldest Pending Action</p>
              <h3>5d</h3>

              <span className="stat-detail">
                Needs follow-up
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">♡</div>

            <div>
              <p>Welfare Actions</p>
              <h3>04</h3>

              <span className="stat-detail">
                Awaiting coordination
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">✓</div>

            <div>
              <p>Reviewed Today</p>
              <h3>06</h3>

              <span className="stat-detail">
                Human review completed
              </span>
            </div>
          </article>
        </section>

        <section className="priority-queue">
          <div className="priority-queue-heading">
            <div>
              <p className="panel-kicker">
                ACTION QUEUE
              </p>

              <h3>
                Cases requiring attention
              </h3>
            </div>

            <span className="status-pill">
              8 priority
            </span>
          </div>

          {priorityCases.map((item, index) => (
            <article
              className="priority-card"
              key={item.id}
            >
              <div className="priority-rank">
                <span>
                  {String(index + 1).padStart(2, "0")}
                </span>
              </div>

              <div className="priority-content">
                <div className="priority-header">
                  <div>
                    <p className="case-id">
                      {item.id}
                    </p>

                    <h3>{item.stage}</h3>

                    <span className="priority-victim">
                      Victim {item.victimId}
                    </span>
                  </div>

                  <div className="priority-risk">
                    <span
                      className={`risk-badge ${item.riskClass}`}
                    >
                      {item.risk}
                    </span>

                    <strong>
                      DDI {item.ddi}
                    </strong>
                  </div>
                </div>

                <div className="priority-reasons">
                  <p>WHY THIS CASE IS HERE</p>

                  <div className="reason-list">
                    {item.reasons.map((reason) => (
                      <span key={reason}>
                        <i>•</i>
                        {reason}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="priority-footer">
                  <div className="priority-meta">
                    <span>
                      Last check-in
                      <strong>{item.lastCheckIn}</strong>
                    </span>

                    <span>
                      Waiting
                      <strong>{item.waiting}</strong>
                    </span>

                    <span>
                      Pending action
                      <strong>{item.action}</strong>
                    </span>
                  </div>

                  <div className="priority-actions">
                    <span
                      className={`mini-status ${item.actionClass}`}
                    >
                      {item.actionStatus}
                    </span>

                    <Link
                      className="priority-button"
                      to={`/cases/${item.id}`}
                    >
                      Open case →
                    </Link>
                  </div>
                </div>
              </div>
            </article>
          ))}
        </section>

        <div className="priority-note">
          Priority ordering is a coordination aid for human review.
          It does not represent an automated diagnosis or final judgement.
        </div>
      </main>
    </div>
  );
}

export default PriorityCases;