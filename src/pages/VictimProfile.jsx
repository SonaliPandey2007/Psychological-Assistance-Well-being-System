import { useParams, Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import "../App.css";

const victimData = {
  "V-1048": {
    caseId: "CASE-2026-014",
    stage: "Court / Delay",
    risk: "High concern",
    riskClass: "high",
    ddi: 72,
    lastCheckIn: "2 days ago",
    engagement: "Reduced",
    engagementClass: "reduced",
    counsellor: "Dr. Meera Kapoor",
    supportStatus: "2 open needs",

    supportNeeds: [
      {
        title: "Counsellor review",
        text: "Pending human verification",
        status: "Pending",
      },
      {
        title: "Legal / court support",
        text: "Coordination required around current case stage",
        status: "Open",
      },
    ],

    checkIns: [
      {
        date: "Today",
        label: "Scheduled follow-up",
        status: "Due",
      },
      {
        date: "2 days ago",
        label: "Routine check-in",
        status: "Completed",
      },
      {
        date: "9 days ago",
        label: "Routine check-in",
        status: "Completed",
      },
      {
        date: "16 days ago",
        label: "Routine check-in",
        status: "Completed",
      },
    ],
  },

  "V-1051": {
    caseId: "CASE-2026-011",
    stage: "Investigation",
    risk: "Moderate",
    riskClass: "moderate",
    ddi: 58,
    lastCheckIn: "1 day ago",
    engagement: "Maintained",
    engagementClass: "maintained",
    counsellor: "Assigned",
    supportStatus: "2 open needs",

    supportNeeds: [
      {
        title: "Financial support",
        text: "Coordination currently in progress",
        status: "In progress",
      },
      {
        title: "Scheduled follow-up",
        text: "Continue routine check-in schedule",
        status: "Active",
      },
    ],

    checkIns: [
      {
        date: "Yesterday",
        label: "Routine check-in",
        status: "Completed",
      },
      {
        date: "8 days ago",
        label: "Routine check-in",
        status: "Completed",
      },
      {
        date: "15 days ago",
        label: "Routine check-in",
        status: "Completed",
      },
    ],
  },

  "V-1062": {
    caseId: "CASE-2026-009",
    stage: "Trial",
    risk: "Low",
    riskClass: "low",
    ddi: 31,
    lastCheckIn: "4 days ago",
    engagement: "Consistent",
    engagementClass: "maintained",
    counsellor: "Assigned",
    supportStatus: "1 open need",

    supportNeeds: [
      {
        title: "Hearing support",
        text: "Current support coordination completed",
        status: "Completed",
      },
    ],

    checkIns: [
      {
        date: "4 days ago",
        label: "Routine check-in",
        status: "Completed",
      },
      {
        date: "11 days ago",
        label: "Routine check-in",
        status: "Completed",
      },
      {
        date: "18 days ago",
        label: "Routine check-in",
        status: "Completed",
      },
    ],
  },
};

function VictimProfile() {
  const { victimId } = useParams();

  const currentVictim =
    victimData[victimId] || victimData["V-1048"];

  return (
    <div className="app">
      <Sidebar />

      <main className="main-content">
        <header className="topbar">
          <div>
            <Link className="back-link" to="/victims">
              ← Back to victims
            </Link>

            <p className="eyebrow">
              VICTIM PROFILE
            </p>

            <h2>{victimId}</h2>

            <p className="subtitle">
              Person-level coordination view using authorised,
              high-level information.
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

        <section className="profile-hero">
          <div className="profile-identity-block">
            <div className="large-victim-avatar">
              V
            </div>

            <div>
              <p className="panel-kicker">
                AUTHORISED PROFILE
              </p>

              <h3>{victimId}</h3>

              <p>
                Associated case{" "}
                <strong>{currentVictim.caseId}</strong>
              </p>
            </div>
          </div>

          <div className="profile-overview-items">
            <div>
              <span>Current stage</span>
              <strong>{currentVictim.stage}</strong>
            </div>

            <div>
              <span>Assigned counsellor</span>
              <strong>{currentVictim.counsellor}</strong>
            </div>

            <div>
              <span>Current risk</span>

              <span
                className={`risk-badge ${currentVictim.riskClass}`}
              >
                {currentVictim.risk}
              </span>
            </div>
          </div>
        </section>

        <section className="profile-metric-grid">
          <article className="profile-metric-card">
            <span>Current DDI</span>

            <strong>{currentVictim.ddi}</strong>

            <small>
              Screening / risk indicator
            </small>
          </article>

          <article className="profile-metric-card">
            <span>Engagement</span>

            <strong>{currentVictim.engagement}</strong>

            <small>
              Compared with personal baseline
            </small>
          </article>

          <article className="profile-metric-card">
            <span>Last check-in</span>

            <strong>{currentVictim.lastCheckIn}</strong>

            <small>
              Most recent recorded interaction
            </small>
          </article>

          <article className="profile-metric-card">
            <span>Support status</span>

            <strong>{currentVictim.supportStatus}</strong>

            <small>
              Welfare coordination
            </small>
          </article>
        </section>

        <section className="profile-main-grid">
          <article className="panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  SUPPORT COORDINATION
                </p>

                <h3>Current support needs</h3>
              </div>

              <span className="status-pill">
                Open
              </span>
            </div>

            <div className="profile-support-list">
              {currentVictim.supportNeeds.map((need) => (
                <div
                  className="profile-support-item"
                  key={need.title}
                >
                  <div className="support-item-icon">
                    {need.status === "Completed"
                      ? "✓"
                      : "•"}
                  </div>

                  <div>
                    <strong>{need.title}</strong>
                    <p>{need.text}</p>
                  </div>

                  <span
                    className={`mini-status ${
                      need.status === "Completed"
                        ? "done"
                        : need.status === "In progress"
                        ? "progress"
                        : "pending"
                    }`}
                  >
                    {need.status}
                  </span>
                </div>
              ))}
            </div>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  ENGAGEMENT
                </p>

                <h3>Interaction history</h3>
              </div>

              <span
                className={`engagement-status ${currentVictim.engagementClass}`}
              >
                {currentVictim.engagement}
              </span>
            </div>

            <div className="checkin-history">
              {currentVictim.checkIns.map((checkIn) => (
                <div
                  className="checkin-item"
                  key={`${checkIn.date}-${checkIn.label}`}
                >
                  <div className="checkin-dot">
                    {checkIn.status === "Completed"
                      ? "✓"
                      : "○"}
                  </div>

                  <div>
                    <strong>{checkIn.label}</strong>
                    <span>{checkIn.date}</span>
                  </div>

                  <small>{checkIn.status}</small>
                </div>
              ))}
            </div>
          </article>
        </section>

        <section className="profile-detail-grid">
          <article className="panel profile-wellbeing-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  WELL-BEING SNAPSHOT
                </p>

                <h3>Current signal</h3>
              </div>

              <span
                className={`risk-badge ${currentVictim.riskClass}`}
              >
                {currentVictim.risk}
              </span>
            </div>

            <div className="profile-signal">
              <div className="profile-signal-score">
                <span>DDI</span>

                <strong>
                  {currentVictim.ddi}
                  <small>/100</small>
                </strong>
              </div>

              <div className="profile-signal-copy">
                <strong>
                  High-level monitoring signal
                </strong>

                <p>
                  This view helps coordinate support around the
                  person's current situation. Detailed trend analysis
                  is available through the associated case.
                </p>

                <Link
                  className="primary-button"
                  to={`/cases/${currentVictim.caseId}`}
                >
                  Open full case journey
                </Link>
              </div>
            </div>
          </article>

          <article className="panel profile-case-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  CASE CONNECTION
                </p>

                <h3>{currentVictim.caseId}</h3>
              </div>

              <span className="status-pill">
                Active
              </span>
            </div>

            <div className="case-connection-content">
              <div>
                <span>Case stage</span>
                <strong>{currentVictim.stage}</strong>
              </div>

              <div>
                <span>Counsellor</span>
                <strong>{currentVictim.counsellor}</strong>
              </div>

              <div>
                <span>Current DDI</span>
                <strong>{currentVictim.ddi}/100</strong>
              </div>
            </div>

            <Link
              className="secondary-button"
              to={`/cases/${currentVictim.caseId}`}
            >
              View case details →
            </Link>
          </article>
        </section>

        <div className="disclaimer">
          Pseudonymous operational profile. DDI is a screening/risk
          indicator and does not constitute a diagnosis.
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

export default VictimProfile;