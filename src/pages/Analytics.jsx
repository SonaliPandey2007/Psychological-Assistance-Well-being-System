import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Line, Bar, Doughnut } from "react-chartjs-2";
import Sidebar from "../components/Sidebar";
import "../App.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
);

function Analytics() {
const stageData = useMemo(
  () => ({
    labels: [
      "Investigation",
      "Trial",
      "Court / Delay",
      "Compensation",
      "Rehabilitation",
    ],
    datasets: [
      {
        label: "Cases",
        data: [10, 6, 4, 2, 2],
        backgroundColor: [
          "#2D5B79",
          "#477594",
          "#628EA8",
          "#7DA5B8",
          "#9ABCC9",
        ],
        borderColor: "#ffffff",
        borderWidth: 1,
        borderRadius: 7,
        barThickness: 22,
      },
    ],
  }),
  []
);

  const riskData = useMemo(
  () => ({
    labels: ["Low", "Moderate", "High concern"],
    datasets: [
      {
        data: [51, 38, 11],
        backgroundColor: [
          "#63A883",
          "#E1A94A",
          "#D96561",
        ],
        borderColor: "#ffffff",
        borderWidth: 3,
        hoverOffset: 7,
      },
    ],
  }),
  []
);

  const welfareData = useMemo(
  () => ({
    labels: [
      "Counselling",
      "Financial support",
      "Legal support",
      "Safety support",
      "Rehabilitation",
    ],
    datasets: [
      {
        label: "Open support items",
        data: [4, 3, 2, 1, 1],
        backgroundColor: [
          "#2D5B79",
          "#477594",
          "#628EA8",
          "#7DA5B8",
          "#9ABCC9",
        ],
        borderColor: "#ffffff",
        borderWidth: 1,
        borderRadius: 7,
        barThickness: 20,
      },
    ],
  }),
  []
  );

const interventionTrendData = useMemo(
  () => ({
    labels: [
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
    ],
    datasets: [
      {
        label: "Interventions",
        data: [9, 12, 15, 13, 18, 22],
        borderColor: "#2D5B79",
        backgroundColor: "rgba(45, 91, 121, 0.10)",
        borderWidth: 3,
        tension: 0.35,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: "#2D5B79",
        pointBorderColor: "#ffffff",
        pointBorderWidth: 2,
        fill: true,
      },
    ],
  }),
  []
);

  const baseOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
  };

  const stageOptions = {
    ...baseOptions,
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 2,
        },
        grid: {
          color: "#e1e7ec",
        },
      },
    },
  };

  const welfareOptions = {
    ...baseOptions,
    indexAxis: "y",
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          stepSize: 2,
        },
        grid: {
          color: "#e9edf2",
        },
      },
      y: {
        grid: {
          display: false,
        },
      },
    },
  };

  const riskOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "68%",
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          boxWidth: 10,
          padding: 16,
          font: {
            size: 10,
          },
        },
      },
    },
  };

  const interventionOptions = {
    ...baseOptions,
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 5,
        },
        grid: {
          color: "#e9edf2",
        },
      },
    },
  };

  return (
    <div className="app">
      <Sidebar />

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">
              CASE & WELFARE ANALYTICS
            </p>

            <h2>Analytics</h2>

            <p className="subtitle">
              View aggregate patterns across the authorised caseload.
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

        {/* Aggregate summary */}
        <section className="analytics-summary">
          <article className="analytics-highlight">
            <span>Active cases</span>
            <strong>24</strong>
            <small>Assigned caseload</small>
          </article>

          <article className="analytics-highlight">
            <span>Active victims</span>
            <strong>128</strong>
            <small>Across assigned cases</small>
          </article>

          <article className="analytics-highlight">
            <span>Open welfare needs</span>
            <strong>11</strong>
            <small>Awaiting coordination</small>
          </article>

          <article className="analytics-highlight">
            <span>Interventions</span>
            <strong>17</strong>
            <small>Completed or in progress</small>
          </article>
        </section>

        {/* Key observations */}
        <section className="analytics-insights">
          <div>
            <p className="panel-kicker">
              CURRENT VIEW
            </p>

            <h3>What stands out</h3>
          </div>

          <div className="analytics-insight-grid">
            <article>
              <span className="analytics-insight-icon">!</span>

              <div>
                <strong>8 priority cases</strong>
                <p>
                  Current attention queue includes cases requiring
                  human review or timely coordination.
                </p>
              </div>
            </article>

            <article>
              <span className="analytics-insight-icon">♡</span>

              <div>
                <strong>11 open support needs</strong>
                <p>
                  Welfare coordination remains active across the
                  assigned caseload.
                </p>
              </div>
            </article>

            <article>
              <span className="analytics-insight-icon">↗</span>

              <div>
                <strong>Interventions increasing</strong>
                <p>
                  Recent months show a higher volume of recorded
                  support interventions.
                </p>
              </div>
            </article>
          </div>
        </section>

        {/* First chart row */}
        <section className="analytics-chart-grid">
          <article className="panel analytics-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  CASE DISTRIBUTION
                </p>

                <h3>Cases by justice stage</h3>
              </div>

              <span className="status-pill">
                24 active
              </span>
            </div>

            <div className="analytics-chart">
              <Bar
                data={stageData}
                options={stageOptions}
              />
            </div>

            <p className="analytics-note">
              Aggregate case-stage distribution for the current
              authorised caseload.
            </p>
          </article>

          <article className="panel analytics-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  RISK MIX
                </p>

                <h3>Current risk distribution</h3>
              </div>

              <span className="status-pill">
                Overview
              </span>
            </div>

            <div className="risk-chart-wrap">
              <Doughnut
                data={riskData}
                options={riskOptions}
              />

              <div className="risk-chart-center">
                <strong>100%</strong>
                <span>caseload</span>
              </div>
            </div>

            <p className="analytics-note">
              Risk categories are used as coordination signals and
              should not be interpreted as diagnoses.
            </p>
          </article>
        </section>

        {/* Welfare chart */}
        <section className="panel analytics-wide-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">
                WELFARE ACTIVITY
              </p>

              <h3>Support needs by category</h3>
            </div>

            <Link
              className="text-button"
              to="/welfare"
            >
              View welfare queue →
            </Link>
          </div>

          <div className="analytics-wide-chart">
            <Bar
              data={welfareData}
              options={welfareOptions}
            />
          </div>

          <p className="analytics-note">
            Counts represent current open or active support coordination
            items in the prototype caseload.
          </p>
        </section>

        {/* Trend chart */}
        <section className="panel analytics-wide-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">
                INTERVENTION TREND
              </p>

              <h3>Recorded interventions over time</h3>
            </div>

            <span className="status-pill">
              Last 6 months
            </span>
          </div>

          <div className="analytics-wide-chart trend-chart">
            <Line
              data={interventionTrendData}
              options={interventionOptions}
            />
          </div>

          <p className="analytics-note">
            Illustrative aggregate prototype data for workflow demonstration.
          </p>
        </section>

        {/* Privacy / interpretation */}
        <section className="analytics-footer-card">
          <div className="analytics-footer-icon">
            i
          </div>

          <div>
            <strong>
              Aggregate operational view
            </strong>

            <p>
              Analytics summarises authorised caseload patterns without
              exposing unnecessary individual-level information. Detailed
              case and victim information remains available through the
              appropriate operational screens.
            </p>
          </div>
        </section>

        <div className="page-note">
          Aggregate prototype analytics for coordination and planning.
          Individual-level risk and well-being signals should be reviewed
          by authorised personnel.
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

export default Analytics;