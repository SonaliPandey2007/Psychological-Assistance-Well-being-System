import { useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import "../App.css";

const cases = [
  {
    id: "CASE-2026-014",
    victimId: "V-1048",
    type: "Atrocity response",
    stage: "Court / Delay",
    counsellor: "Dr. Meera Kapoor",
    risk: "High concern",
    riskClass: "high",
    ddi: 72,
    status: "Active",
    statusClass: "active",
    lastCheckIn: "2 days ago",
    welfare: "Counsellor review pending",
  },
  {
    id: "CASE-2026-011",
    victimId: "V-1051",
    type: "Atrocity response",
    stage: "Investigation",
    counsellor: "Assigned",
    risk: "Moderate",
    riskClass: "moderate",
    ddi: 58,
    status: "Active",
    statusClass: "active",
    lastCheckIn: "1 day ago",
    welfare: "Financial support in progress",
  },
  {
    id: "CASE-2026-009",
    victimId: "V-1062",
    type: "Atrocity response",
    stage: "Trial",
    counsellor: "Assigned",
    risk: "Low",
    riskClass: "low",
    ddi: 31,
    status: "Active",
    statusClass: "active",
    lastCheckIn: "4 days ago",
    welfare: "Hearing support completed",
  },
];

function Cases() {
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");

  const filteredCases = cases.filter((item) => {
    const search = searchTerm.toLowerCase();

    const matchesSearch =
      item.id.toLowerCase().includes(search) ||
      item.victimId.toLowerCase().includes(search) ||
      item.stage.toLowerCase().includes(search);

    const matchesRisk =
      riskFilter === "All" || item.risk === riskFilter;

    return matchesSearch && matchesRisk;
  });

  return (
    <div className="app">
      <Sidebar />

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">CASE MANAGEMENT</p>

            <h2>Cases</h2>

            <p className="subtitle">
              Review authorised case journeys and current welfare priorities.
            </p>
          </div>

          <div className="topbar-actions">
            <button className="icon-button" aria-label="Notifications">
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
            <div className="stat-icon">▣</div>
            <div>
              <p>Active Cases</p>
              <h3>24</h3>
              <span className="stat-detail">
                Across your assigned cases
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
              <p>Welfare Follow-up</p>
              <h3>11</h3>
              <span className="stat-detail">
                Pending coordination
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">✓</div>
            <div>
              <p>Interventions</p>
              <h3>17</h3>
              <span className="stat-detail">
                Completed or in progress
              </span>
            </div>
          </article>
        </section>

        <section className="panel cases-page-panel">
          <div className="panel-heading cases-heading">
            <div>
              <p className="panel-kicker">AUTHORISED CASES</p>
              <h3>Case overview</h3>
            </div>

            <span className="status-pill">24 active</span>
          </div>

          <div className="case-controls">
            <div className="case-search">
              <span className="search-icon">⌕</span>

              <input
                type="text"
                placeholder="Search case, victim ID or stage..."
                value={searchTerm}
                onChange={(event) =>
                  setSearchTerm(event.target.value)
                }
              />
            </div>

            <select
              className="risk-filter"
              value={riskFilter}
              onChange={(event) =>
                setRiskFilter(event.target.value)
              }
              aria-label="Filter by risk"
            >
              <option value="All">All risk levels</option>
              <option value="High concern">High concern</option>
              <option value="Moderate">Moderate</option>
              <option value="Low">Low</option>
            </select>
          </div>

          <div className="cases-table">
            <div className="cases-table-header">
              <span>Case</span>
              <span>Victim</span>
              <span>Stage</span>
              <span>Risk</span>
              <span>DDI</span>
              <span>Status</span>
              <span>Follow-up</span>
            </div>

            {filteredCases.length > 0 ? (
              filteredCases.map((item) => (
                <Link
                  key={item.id}
                  className="case-table-row"
                  to={`/cases/${item.id}`}
                >
                  <div className="case-table-case">
                    <strong>{item.id}</strong>

                    <span>
                      {item.type} · Check-in {item.lastCheckIn}
                    </span>
                  </div>

                  <div className="case-table-victim">
                    {item.victimId}
                  </div>

                  <div className="case-table-stage">
                    {item.stage}
                  </div>

                  <div>
                    <span className={`risk-badge ${item.riskClass}`}>
                      {item.risk}
                    </span>
                  </div>

                  <div className="case-table-ddi">
                    {item.ddi}
                    <span>/100</span>
                  </div>

                  <div>
                    <span className={`case-status-badge ${item.statusClass}`}>
                      {item.status}
                    </span>
                  </div>

                  <div className="case-table-followup">
                    {item.welfare}
                  </div>
                </Link>
              ))
            ) : (
              <div className="empty-state">
                <strong>No matching cases</strong>

                <span>
                  Try a different case ID, victim ID, stage or risk filter.
                </span>
              </div>
            )}
          </div>
        </section>

        <div className="page-note">
          High-level risk information is shown for coordination and human
          review. DDI is a screening/risk indicator, not a diagnosis.
        </div>
      </main>
    </div>
  );
}

export default Cases;