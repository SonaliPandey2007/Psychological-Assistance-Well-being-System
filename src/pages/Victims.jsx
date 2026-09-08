import { useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import "../App.css";

const victims = [
  {
    id: "V-1048",
    caseId: "CASE-2026-014",
    stage: "Court / Delay",
    risk: "High concern",
    riskClass: "high",
    ddi: 72,
    lastCheckIn: "2 days ago",
    support: "Counsellor review pending",
    engagement: "Reduced",
  },
  {
    id: "V-1051",
    caseId: "CASE-2026-011",
    stage: "Investigation",
    risk: "Moderate",
    riskClass: "moderate",
    ddi: 58,
    lastCheckIn: "1 day ago",
    support: "Financial support in progress",
    engagement: "Maintained",
  },
  {
    id: "V-1062",
    caseId: "CASE-2026-009",
    stage: "Trial",
    risk: "Low",
    riskClass: "low",
    ddi: 31,
    lastCheckIn: "4 days ago",
    support: "Hearing support completed",
    engagement: "Consistent",
  },
];

function Victims() {
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");

  const filteredVictims = victims.filter((victim) => {
    const search = searchTerm.toLowerCase();

    const matchesSearch =
      victim.id.toLowerCase().includes(search) ||
      victim.caseId.toLowerCase().includes(search) ||
      victim.stage.toLowerCase().includes(search);

    const matchesRisk =
      riskFilter === "All" ||
      victim.risk === riskFilter;

    return matchesSearch && matchesRisk;
  });

  return (
    <div className="app">
      <Sidebar />

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">VICTIM MANAGEMENT</p>

            <h2>Victims</h2>

            <p className="subtitle">
              Coordinate support around the person, their case, and current needs.
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
                Across assigned cases
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">♡</div>

            <div>
              <p>Open Support Needs</p>
              <h3>11</h3>

              <span className="stat-detail">
                Awaiting or in progress
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon">◷</div>

            <div>
              <p>Recent Check-ins</p>
              <h3>19</h3>

              <span className="stat-detail">
                Recorded this week
              </span>
            </div>
          </article>

          <article className="stat-card">
            <div className="stat-icon alert">!</div>

            <div>
              <p>Priority Support</p>
              <h3>08</h3>

              <span className="stat-detail">
                Human review recommended
              </span>
            </div>
          </article>
        </section>

        {/* Support snapshot */}
        <section className="victim-support-grid">
          <article className="panel support-overview-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  SUPPORT SNAPSHOT
                </p>

                <h3>Current coordination</h3>
              </div>

              <span className="status-pill">
                11 open
              </span>
            </div>

            <div className="support-metric-grid">
              <div className="support-metric">
                <span>Pending counsellor reviews</span>
                <strong>4</strong>
              </div>

              <div className="support-metric">
                <span>Financial support</span>
                <strong>3</strong>
              </div>

              <div className="support-metric">
                <span>Legal / court support</span>
                <strong>2</strong>
              </div>

              <div className="support-metric">
                <span>Rehabilitation coordination</span>
                <strong>2</strong>
              </div>
            </div>
          </article>

          <article className="panel engagement-overview-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  ENGAGEMENT
                </p>

                <h3>Recent participation</h3>
              </div>
            </div>

            <div className="engagement-visual">
              <div className="engagement-ring">
                <strong>84%</strong>
                <span>maintained</span>
              </div>

              <div className="engagement-copy">
                <strong>19 recent check-ins</strong>

                <p>
                  Most assigned victims continue to participate in
                  scheduled interactions.
                </p>

                <span>
                  Engagement is interpreted against each person's own
                  baseline.
                </span>
              </div>
            </div>
          </article>
        </section>

        {/* Victim list */}
        <section className="panel victims-page-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">
                AUTHORISED VICTIMS
              </p>

              <h3>Victim overview</h3>
            </div>

            <span className="status-pill">
              128 active
            </span>
          </div>

          <div className="case-controls">
            <div className="case-search">
              <span className="search-icon">⌕</span>

              <input
                type="text"
                placeholder="Search victim ID, case ID or stage..."
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
              aria-label="Filter victims by risk"
            >
              <option value="All">All risk levels</option>
              <option value="High concern">
                High concern
              </option>
              <option value="Moderate">Moderate</option>
              <option value="Low">Low</option>
            </select>
          </div>

          <div className="cases-table victims-table">
            <div className="victims-table-header">
              <span>Victim</span>
              <span>Case</span>
              <span>Stage</span>
              <span>Support</span>
              <span>Engagement</span>
              <span>Risk</span>
              <span>Last check-in</span>
            </div>

            {filteredVictims.length > 0 ? (
              filteredVictims.map((victim) => (
                <Link
                  key={victim.id}
                  className="victim-table-row"
                  to={`/victims/${victim.id}`}
                >
                  <div className="victim-identity">
                    <div className="victim-avatar">V</div>

                    <div>
                      <strong>{victim.id}</strong>

                      <span>
                        Authorised profile
                      </span>
                    </div>
                  </div>

                  <div className="victim-case-id">
                    {victim.caseId}
                  </div>

                  <div className="case-table-stage">
                    {victim.stage}
                  </div>

                  <div className="case-table-followup">
                    {victim.support}
                  </div>

                  <div className="engagement-cell">
                    <span
                      className={`engagement-status ${
                        victim.engagement === "Reduced"
                          ? "reduced"
                          : "maintained"
                      }`}
                    >
                      {victim.engagement}
                    </span>
                  </div>

                  <div>
                    <span
                      className={`risk-badge ${victim.riskClass}`}
                    >
                      {victim.risk}
                    </span>
                  </div>

                  <div className="victim-checkin">
                    {victim.lastCheckIn}
                  </div>
                </Link>
              ))
            ) : (
              <div className="empty-state">
                <strong>No matching victims</strong>

                <span>
                  Try another victim ID, case ID, stage or risk level.
                </span>
              </div>
            )}
          </div>
        </section>

        <div className="page-note">
          Operational view uses pseudonymous victim IDs and high-level
          information for case and welfare coordination.
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

export default Victims;