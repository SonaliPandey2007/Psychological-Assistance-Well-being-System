import { useParams } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";
import "../App.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
);

// -----------------------------------------------------------------------------
// Demo case data
// -----------------------------------------------------------------------------
// This is prototype data for the SIH demo flow.
// DDI is presented as a screening/risk indicator, not a diagnosis.
const caseData = {
  "CASE-2026-014": {
    caseType: "Atrocity response",
    stage: "Court / Delay",
    counsellor: "Dr. Meera Kapoor",
    risk: "High concern",
    riskClass: "high",
    ddi: 72,
    previousDdi: 48,
    trend: "Increasing",

    ddiHistory: [34, 41, 48, 55, 72],

    chartLabels: [
      "Baseline",
      "Check-in",
      "Case event",
      "Follow-up",
      "Current",
    ],

    factors: [
      {
        icon: "↑",
        title: "Fear-related responses",
        text: "Recent check-ins contain more fear/stress-related language.",
      },
      {
        icon: "↓",
        title: "Reduced engagement",
        text: "Interaction has decreased compared with the personal baseline.",
      },
      {
        icon: "!",
        title: "Recent case event",
        text: "A court delay is temporally associated with the recent increase.",
      },
      {
        icon: "↑",
        title: "Worsening distress trend",
        text: "The recent trajectory has moved upward.",
      },
    ],

    recommendation:
      "Counsellor review and appropriate safety/support assessment.",

    welfareNeeds: [
      {
        icon: "C",
        title: "Counsellor review",
        text: "Pending human verification",
      },
      {
        icon: "L",
        title: "Legal / court support",
        text: "Coordination required around the current case stage",
      },
    ],

    coordination: {
      counsellor: "Dr. Meera Kapoor",
      lastReview: "Not yet reviewed",

      action: "Human review recommended",
    },

    journey: [
      {
        title: "Complaint",
        status: "Completed",
        state: "complete",
      },
      {
        title: "Investigation",
        status: "Completed",
        state: "complete",
      },
      {
        title: "Threat / Intimidation",
        status: "Relevant event",
        state: "current",
      },
      {
        title: "Court / Delay",
        status: "Current stage",
        state: "current",
      },
      {
        title: "Compensation",
        status: "Upcoming",
        state: "upcoming",
      },
      {
        title: "Rehabilitation",
        status: "Upcoming",
        state: "upcoming",
      },
    ],
  },

  "CASE-2026-011": {
    caseType: "Atrocity response",
    stage: "Investigation",
    counsellor: "Assigned",
    risk: "Moderate",
    riskClass: "moderate",
    ddi: 58,
    previousDdi: 52,
    trend: "Stable",

    ddiHistory: [30, 36, 45, 39, 58],

    chartLabels: [
      "Baseline",
      "Check-in",
      "Case event",
      "Follow-up",
      "Current",
    ],

    factors: [
      {
        icon: "→",
        title: "Stable recent pattern",
        text: "Recent check-ins remain broadly consistent with the personal baseline.",
      },
      {
        icon: "→",
        title: "Engagement maintained",
        text: "Recent interaction frequency shows no significant drop from baseline.",
      },
      {
        icon: "i",
        title: "Routine case monitoring",
        text: "No newly recorded case event is currently driving an elevated concern signal.",
      },
    ],

    recommendation:
      "Continue routine monitoring and scheduled follow-up.",

    welfareNeeds: [
      {
        icon: "W",
        title: "Financial support",
        text: "Coordination currently in progress",
      },
      {
        icon: "F",
        title: "Scheduled follow-up",
        text: "Continue routine check-in schedule",
      },
    ],

    coordination: {
      counsellor: "Assigned",
      lastReview: "Recent review completed",
      action: "Continue routine monitoring",
    },

    journey: [
      {
        title: "Complaint",
        status: "Completed",
        state: "complete",
      },
      {
        title: "Investigation",
        status: "Current stage",
        state: "current",
      },
      {
        title: "Trial",
        status: "Upcoming",
        state: "upcoming",
      },
      {
        title: "Compensation",
        status: "Upcoming",
        state: "upcoming",
      },
      {
        title: "Rehabilitation",
        status: "Upcoming",
        state: "upcoming",
      },
    ],
  },

  "CASE-2026-009": {
    caseType: "Atrocity response",
    stage: "Trial",
    counsellor: "Assigned",
    risk: "Low",
    riskClass: "low",
    ddi: 31,
    previousDdi: 36,
    trend: "Stable",

    ddiHistory: [42, 40, 36, 34, 31],

    chartLabels: [
      "Baseline",
      "Check-in",
      "Case event",
      "Follow-up",
      "Current",
    ],

    factors: [
      {
        icon: "→",
        title: "Low current concern",
        text: "Recent signals remain within the lower concern range.",
      },
      {
        icon: "→",
        title: "Engagement maintained",
        text: "Recent check-in participation remains consistent.",
      },
      {
        icon: "↓",
        title: "Stable-to-improving trend",
        text: "Recent values show a gradual downward movement.",
      },
    ],

    recommendation:
      "Continue the current support plan and monitor upcoming case milestones.",

    welfareNeeds: [
      {
        icon: "L",
        title: "Hearing support",
        text: "Current support coordination completed",
      },
      {
        icon: "R",
        title: "Routine follow-up",
        text: "Continue scheduled monitoring",
      },
    ],

    coordination: {
      counsellor: "Assigned",
      lastReview: "Recent review completed",
      action: "Continue current support plan",
    },

    journey: [
      {
        title: "Complaint",
        status: "Completed",
        state: "complete",
      },
      {
        title: "Investigation",
        status: "Completed",
        state: "complete",
      },
      {
        title: "Trial",
        status: "Current stage",
        state: "current",
      },
      {
        title: "Compensation",
        status: "Upcoming",
        state: "upcoming",
      },
      {
        title: "Rehabilitation",
        status: "Upcoming",
        state: "upcoming",
      },
    ],
  },
};

function CaseDetails() {
  const { caseId } = useParams();

  const displayCaseId = caseId || "CASE-2026-014";

  const currentCase =
    caseData[displayCaseId] || caseData["CASE-2026-014"];

  const chartData = {
  labels: currentCase.chartLabels,
  datasets: [
    {
      label: "Dynamic Distress Index",
      data: currentCase.ddiHistory,
      borderColor: "#2D5B79",
      backgroundColor: "#2D5B79",
      borderWidth: 3,
      tension: 0.35,
      pointRadius: (context) => {
        const lastIndex = context.dataset.data.length - 1;
        return context.dataIndex === lastIndex ? 7 : 4;
      },

      pointHoverRadius: (context) => {
        const lastIndex = context.dataset.data.length - 1;
        return context.dataIndex === lastIndex ? 8 : 6;
      },

      pointBackgroundColor: "#2D5B79",
      pointBorderColor: "#ffffff",
      pointBorderWidth: 2,
    },
  ],
};
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        displayColors: false,
        callbacks: {
          label: (context) => ` DDI: ${context.parsed.y}/100`,
        },
      },
    },
    scales: {
      y: {
        min: 0,
        max: 100,
        ticks: {
          stepSize: 20,
        },
        grid: {
          color: "#e9edf2",
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <Sidebar />
      

      {/* Main content */}
      <main className="main-content">
        <header className="topbar">
          <div>
            <a className="back-link" href="/cases">
              ← Back to cases
            </a>

            <p className="eyebrow case-detail-eyebrow">
              CASE DETAIL
            </p>

            <h2>{displayCaseId}</h2>

            <p className="subtitle">
              High-level case and well-being coordination view.
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

        {/* Case summary */}
        <section className="case-summary-grid">
          <article className="detail-card">
            <span className="detail-label">CASE TYPE</span>
            <strong>{currentCase.caseType}</strong>
          </article>

          <article className="detail-card">
            <span className="detail-label">CURRENT STAGE</span>
            <strong>{currentCase.stage}</strong>
          </article>

          <article className="detail-card">
            <span className="detail-label">COUNSELLOR</span>
            <strong>{currentCase.counsellor}</strong>
          </article>

          <article className="detail-card risk-detail-card">
            <span className="detail-label">CURRENT RISK</span>

            <span
              className={`risk-badge ${currentCase.riskClass}`}
            >
              {currentCase.risk}
            </span>
          </article>
        </section>

        {/* DDI + Explainable alert */}
        <section className="detail-main-grid">
          <article className="panel ddi-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  WELL-BEING SIGNAL
                </p>

                <h3>Dynamic Distress Index</h3>
              </div>

              <span
                className={`trend-pill ${currentCase.riskClass}`}
              >
                {currentCase.trend === "Increasing"
                  ? "↑ Increasing"
                  : currentCase.trend === "Stable"
                  ? "→ Stable"
                  : "↓ Improving"}
              </span>
            </div>

            <div className="ddi-overview">
              <div className="ddi-current">
                <span>Current DDI</span>

                <strong>
                  {currentCase.ddi}
                  <small>/100</small>
                </strong>
              </div>

              <div className="ddi-change">
                <span>Recent change</span>

                <strong>
                  {currentCase.previousDdi} → {currentCase.ddi}
                </strong>

                <small>
                  {currentCase.risk === "High concern"
                    ? "Elevated concern"
                    : currentCase.risk === "Moderate"
                    ? "Moderate concern"
                    : "Lower concern"}
                </small>
              </div>
            </div>

            <div className="real-chart">
              <Line data={chartData} options={chartOptions} />
            </div>

            <p className="chart-note">
              Trend shown against the victim’s personal baseline.
              Values are illustrative prototype data.
            </p>
          </article>

          <article className="panel alert-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  EXPLAINABLE ALERT
                </p>

                <h3>
                  {currentCase.risk === "High concern"
                    ? "Why concern increased"
                    : "Current well-being signal"}
                </h3>
              </div>

              <span
                className={`risk-badge ${currentCase.riskClass}`}
              >
                {currentCase.risk}
              </span>
            </div>

            <div className="alert-box">
              {currentCase.factors.map((factor) => (
                <div
                  className="alert-factor"
                  key={factor.title}
                >
                  <span>{factor.icon}</span>

                  <div>
                    <strong>{factor.title}</strong>

                    <p>{factor.text}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="human-review-note">
              <strong>Recommended next step</strong>

              <p>{currentCase.recommendation}</p>
            </div>
          </article>
        </section>

        {/* Justice–well-being timeline */}
        <section className="panel journey-detail-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">
                SIGNATURE FEATURE
              </p>

              <h3>Justice–well-being journey</h3>
            </div>

            <span className="status-pill">
              Current stage · {currentCase.stage}
            </span>
          </div>

          <div className="journey-horizontal">
            {currentCase.journey.map((step, index) => (
              <div
                className="journey-wrapper"
                key={step.title}
              >
                <div
                  className={`journey-node ${step.state}`}
                >
                  <div className="journey-circle">
                    {step.state === "complete"
                      ? "✓"
                      : step.state === "current"
                      ? "●"
                      : "○"}
                  </div>

                  <strong>{step.title}</strong>
                  <span>{step.status}</span>
                </div>

                {index < currentCase.journey.length - 1 && (
                  <div
                    className={`journey-connector ${
                      step.state === "complete"
                        ? "complete-connector"
                        : ""
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Counsellor + welfare */}
        <section className="detail-bottom-grid">
          <article className="panel coordination-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  HUMAN FOLLOW-UP
                </p>

                <h3>Counsellor coordination</h3>
              </div>

              <span className="mini-status pending">
                Follow-up
              </span>
            </div>

            <div className="coordination-content">
              <div className="coordination-row">
                <span>Assigned counsellor</span>
                <strong>
                  {currentCase.coordination.counsellor}
                </strong>
              </div>

              <div className="coordination-row">
                <span>Last review</span>
                <strong>
                  {currentCase.coordination.lastReview}
                </strong>
              </div>

              <div className="coordination-row">
                <span>Recommended action</span>
                <strong>
                  {currentCase.coordination.action}
                </strong>
              </div>
            </div>
          </article>

          <article className="panel welfare-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  WELFARE
                </p>

                <h3>Support needs</h3>
              </div>

              <span className="status-pill">
                {currentCase.welfareNeeds.length} open
              </span>
            </div>

            <div className="welfare-list">
              {currentCase.welfareNeeds.map((need) => (
                <div
                  className="welfare-item"
                  key={need.title}
                >
                  <span className="welfare-icon">
                    {need.icon}
                  </span>

                  <div>
                    <strong>{need.title}</strong>

                    <small>{need.text}</small>
                  </div>
                </div>
              ))}
            </div>
          </article>
        </section>

        <div className="disclaimer">
          High-level risk information is intended for coordination
          and human review. DDI is a screening/risk indicator,
          not a diagnosis.
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

export default CaseDetails;