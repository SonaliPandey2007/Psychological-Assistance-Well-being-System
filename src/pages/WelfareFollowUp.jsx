import { useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import "../App.css";

const welfareItems = [
  {
    id: "WF-014",
    type: "Counsellor review",
    caseId: "CASE-2026-014",
    victimId: "V-1048",
    assignedTo: "Dr. Meera Kapoor",
    status: "Pending",
    statusClass: "pending",
    waiting: "2 days",
    due: "Today",
    priority: "High",
    priorityClass: "high",
    description:
      "Human review requested following a change in well-being signals.",
  },
  {
    id: "WF-011",
    type: "Financial support",
    caseId: "CASE-2026-011",
    victimId: "V-1051",
    assignedTo: "District welfare coordination",
    status: "In progress",
    statusClass: "progress",
    waiting: "3 days",
    due: "In progress",
    priority: "Moderate",
    priorityClass: "moderate",
    description:
      "Financial support coordination is currently underway.",
  },
  {
    id: "WF-009",
    type: "Hearing support",
    caseId: "CASE-2026-009",
    victimId: "V-1062",
    assignedTo: "Legal coordination",
    status: "Completed",
    statusClass: "done",
    waiting: "Completed",
    due: "Completed",
    priority: "Low",
    priorityClass: "low",
    description:
      "Support for the recent hearing milestone has been completed.",
  },
  {
    id: "WF-018",
    type: "Routine follow-up",
    caseId: "CASE-2026-018",
    victimId: "V-1074",
    assignedTo: "Assigned counsellor",
    status: "Pending",
    statusClass: "pending",
    waiting: "3 days",
    due: "Tomorrow",
    priority: "High",
    priorityClass: "high",
    description:
      "Scheduled follow-up has not yet been recorded.",
  },
];

function WelfareFollowUp() {
  const [statusFilter, setStatusFilter] = useState("All");
  const [items, setItems] = useState(welfareItems);

  const filteredItems = items.filter((item) => {
    return (
      statusFilter === "All" ||
      item.status === statusFilter
    );
  });

  const pendingCount = items.filter(
    (item) => item.status === "Pending"
  ).length;

  const progressCount = items.filter(
    (item) => item.status === "In progress"
  ).length;

  const completedCount = items.filter(
    (item) => item.status === "Completed"
  ).length;
  const handleUpdateFollowUp = (itemId) => {
  setItems((currentItems) =>
    currentItems.map((item) => {
      if (item.id !== itemId) {
        return item;
      }

      if (item.status === "Pending") {
        return {
          ...item,
          status: "In progress",
          statusClass: "progress",
          due: "In progress",
        };
      }

      if (item.status === "In progress") {
        return {
          ...item,
          status: "Completed",
          statusClass: "done",
          waiting: "Completed",
          due: "Completed",
        };
      }

      return item;
    })
  );
};

  return (
    <div className="app">
      <Sidebar />

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">
              WELFARE COORDINATION
            </p>

            <h2>Welfare Follow-up</h2>

            <p className="subtitle">
              Track support requests, assigned services, and follow-up completion.
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
              <p>Pending</p>
              <h3>{pendingCount}</h3>

              <span className="stat-detail">
                Requires coordination
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">◷</div>

            <div>
              <p>In Progress</p>
              <h3>{progressCount}</h3>

              <span className="stat-detail">
                Support being coordinated
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">✓</div>

            <div>
              <p>Completed</p>
              <h3>{completedCount}</h3>

              <span className="stat-detail">
                Recorded interventions
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">♡</div>

            <div>
              <p>Total Open Needs</p>
              <h3>11</h3>

              <span className="stat-detail">
                Across assigned cases
              </span>
            </div>
          </article>
        </section>

        <section className="welfare-flow">
          <div className="welfare-flow-step complete">
            <span>1</span>

            <div>
              <strong>Need identified</strong>
              <small>Support requirement recorded</small>
            </div>
          </div>

          <div className="welfare-flow-line" />

          <div className="welfare-flow-step current">
            <span>2</span>

            <div>
              <strong>Coordination</strong>
              <small>Service or counsellor follow-up</small>
            </div>
          </div>

          <div className="welfare-flow-line" />

          <div className="welfare-flow-step">
            <span>3</span>

            <div>
              <strong>Completion</strong>
              <small>Outcome recorded by authorised staff</small>
            </div>
          </div>
        </section>

        <section className="panel welfare-page-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">
                FOLLOW-UP QUEUE
              </p>

              <h3>Support coordination</h3>
            </div>

            <span className="status-pill">
              11 open needs
            </span>
          </div>

          <div className="welfare-controls">
            <div>
              <p>
                Review current support items and their coordination status.
              </p>
            </div>

            <select
              className="risk-filter welfare-filter"
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(event.target.value)
              }
              aria-label="Filter welfare items by status"
            >
              <option value="All">All statuses</option>
              <option value="Pending">Pending</option>
              <option value="In progress">In progress</option>
              <option value="Completed">Completed</option>
            </select>
          </div>

          <div className="welfare-list-page">
            {filteredItems.map((item) => (
              <article
                className="welfare-card"
                key={item.id}
              >
                <div className="welfare-card-type">
                  <div className="welfare-card-icon">
                    {item.type === "Counsellor review"
                      ? "C"
                      : item.type === "Financial support"
                      ? "₹"
                      : item.type === "Hearing support"
                      ? "L"
                      : "✓"}
                  </div>

                  <span>{item.type}</span>
                </div>

                <div className="welfare-card-main">
                  <div className="welfare-card-title">
                    <div>
                      <span className="case-id">
                        {item.caseId}
                      </span>

                      <h3>{item.victimId}</h3>

                      <p>{item.description}</p>
                    </div>

                    <span
                      className={`risk-badge ${item.priorityClass}`}
                    >
                      {item.priority}
                    </span>
                  </div>

                  <div className="welfare-card-details">
                    <div>
                      <span>Assigned to</span>
                      <strong>{item.assignedTo}</strong>
                    </div>

                    <div>
                      <span>Status</span>

                      <span
                        className={`mini-status ${item.statusClass}`}
                      >
                        {item.status}
                      </span>
                    </div>

                    <div>
                      <span>Waiting</span>
                      <strong>{item.waiting}</strong>
                    </div>

                    <div>
                      <span>Due / milestone</span>
                      <strong>{item.due}</strong>
                    </div>
                  </div>

                  <div className="welfare-card-actions">
                    <Link
                      className="secondary-button"
                      to={`/cases/${item.caseId}`}
                    >
                      View case
                    </Link>

                    {item.status !== "Completed" && (
                      <button
                         className="primary-button"
                         onClick={() => handleUpdateFollowUp(item.id)}
                      >
                         {item.status === "Pending"
                           ? "Start follow-up"
                           : "Mark completed"}
                      </button>
                    )}
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <div className="page-note">
          Welfare status represents coordination progress and recorded
          support actions. Final decisions remain with authorised personnel.
        </div>

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

export default WelfareFollowUp;