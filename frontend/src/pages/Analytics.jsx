import { useEffect, useMemo, useState } from "react";
import api from "../services/api";


function Analytics() {
  const [summary, setSummary] = useState(null);
  const [riskData, setRiskData] = useState([]);
  const [exceptionData, setExceptionData] = useState([]);
  const [lifecycleData, setLifecycleData] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  // ============================================================
  // LOAD ANALYTICS DATA
  // ============================================================

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoading(true);
        setError("");

        const [
          summaryResponse,
          riskResponse,
          exceptionResponse,
          lifecycleResponse,
        ] = await Promise.all([
          api.get("/api/analytics/summary"),
          api.get("/api/analytics/risk"),
          api.get("/api/analytics/exceptions"),
          api.get("/api/analytics/lifecycle"),
        ]);

        const summaryData = summaryResponse.data || {};

        setSummary(summaryData);

        setRiskData(
          Object.entries(
            riskResponse.data || {}
          ).map(([level, count]) => ({
            level,
            count,
          }))
        );

        setExceptionData(
          Object.entries(
            exceptionResponse.data || {}
          ).map(([category, count]) => ({
            category,
            count,
          }))
        );

        setLifecycleData(
          Object.entries(
            lifecycleResponse.data || {}
          ).map(([status, count]) => ({
            status,
            count,
          }))
        );
      } catch (error) {
        console.error(
          "Failed to load analytics:",
          error
        );

        setError(
          "Unable to load analytics data. Please make sure the FastAPI backend is running."
        );
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);


  // ============================================================
  // DERIVED DATA
  // ============================================================

  const riskDistribution =
    summary?.risk_distribution || {};

  const decisionDistribution =
    summary?.decision_distribution || {};

  const humanReview =
    summary?.human_review || {};

  const reviewOutcomes =
    summary?.review_outcomes || {};

  const financial =
    summary?.financial || {};

  const priority =
    summary?.priority || {};


  const totalCases =
    summary?.total_cases ??
    Object.values(riskDistribution).reduce(
      (total, count) =>
        total + Number(count || 0),
      0
    );


  const highRiskCases =
    summary?.high_risk_cases ??
    (
      Number(riskDistribution.HIGH || 0) +
      Number(riskDistribution.CRITICAL || 0)
    );


  const criticalCases =
    summary?.critical_cases ??
    Number(riskDistribution.CRITICAL || 0);


  const pendingReviewCases =
    summary?.pending_review_cases ??
    Number(
      summary?.lifecycle_distribution
        ?.PENDING_REVIEW || 0
    );


  const resolvedCases =
    summary?.resolved_cases ??
    Number(
      summary?.lifecycle_distribution
        ?.RESOLVED || 0
    );


  const humanReviewRequired =
    humanReview.required ?? 0;


  const humanReviewRate =
    humanReview.rate ?? 0;


  const approvedReviews =
    reviewOutcomes.approved ?? 0;


  const rejectedReviews =
    reviewOutcomes.rejected ?? 0;


  const escalatedReviews =
    reviewOutcomes.escalated ?? 0;


  const pendingReviews =
    reviewOutcomes.pending ?? 0;


  const reviewCompletionRate =
    reviewOutcomes.completion_rate ?? 0;


  const outstandingBalance =
    financial.outstanding_balance ?? 0;


  const averagePaymentCoverage =
    financial.average_payment_coverage ?? 0;


  const totalInvoiceAmount =
    financial.total_invoice_amount ?? 0;


  const totalPaymentAmount =
    financial.total_payment_amount ?? 0;


  const totalBankAmount =
    financial.total_bank_amount ?? 0;


  const averagePriority =
    priority.average ?? 0;


  const maximumPriority =
    priority.maximum ?? 0;


  const minimumPriority =
    priority.minimum ?? 0;


  // ============================================================
  // FORMATTING
  // ============================================================

  const formatCurrency = (value) =>
    `₹${Number(value || 0).toLocaleString(
      "en-IN",
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }
    )}`;


  const formatNumber = (value) =>
    Number(value || 0).toLocaleString(
      "en-IN"
    );


  // ============================================================
  // DERIVED INSIGHTS
  // ============================================================

  const topRisk =
    useMemo(() => {
      if (!riskData.length) {
        return null;
      }

      return [...riskData].sort(
        (a, b) => b.count - a.count
      )[0];
    }, [riskData]);


  const topException =
    useMemo(() => {
      if (!exceptionData.length) {
        return null;
      }

      return [...exceptionData].sort(
        (a, b) => b.count - a.count
      )[0];
    }, [exceptionData]);


  const coverageStatus =
    averagePaymentCoverage >= 100
      ? "Fully covered"
      : averagePaymentCoverage >= 90
        ? "Near complete"
        : "Coverage gap";


  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Analytics</h1>

          <p>
            Loading TANGLE operational analytics...
          </p>
        </div>
      </div>
    );
  }


  // ============================================================
  // ERROR
  // ============================================================

  if (error) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Analytics</h1>

          <p>{error}</p>
        </div>
      </div>
    );
  }


  // ============================================================
  // MAIN PAGE
  // ============================================================

  return (
    <div className="page analytics-page">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="page-header analytics-page-header">

        <div>
          <span className="analytics-eyebrow">
            TANGLE / OPERATIONS
          </span>

          <h1>
            Analytics
          </h1>

          <p>
            Operational, financial, and governance
            intelligence across transaction exceptions.
          </p>
        </div>

        <div className="analytics-header-status">
          <span className="analytics-live-dot" />
          Live from PostgreSQL
        </div>

      </div>


      {/* ======================================================
          KPI GRID
      ====================================================== */}

      <div className="analytics-summary-grid">

        <div className="analytics-card analytics-card-primary">
          <span>Total Cases</span>

          <strong>
            {formatNumber(totalCases)}
          </strong>

          <small>
            Active exception population
          </small>
        </div>


        <div className="analytics-card">
          <span>High Risk</span>

          <strong>
            {formatNumber(highRiskCases)}
          </strong>

          <small>
            {totalCases
              ? (
                  (highRiskCases / totalCases) *
                  100
                ).toFixed(1)
              : "0.0"}
            % of cases
          </small>
        </div>


        <div className="analytics-card">
          <span>Critical Cases</span>

          <strong>
            {formatNumber(criticalCases)}
          </strong>

          <small>
            Immediate attention
          </small>
        </div>


        <div className="analytics-card">
          <span>Human Review</span>

          <strong>
            {formatNumber(humanReviewRequired)}
          </strong>

          <small>
            {Number(humanReviewRate).toFixed(2)}
            % review rate
          </small>
        </div>


        <div className="analytics-card">
          <span>Pending Review</span>

          <strong>
            {formatNumber(pendingReviewCases)}
          </strong>

          <small>
            Awaiting governance decision
          </small>
        </div>


        <div className="analytics-card">
          <span>Outstanding</span>

          <strong>
            {formatCurrency(
              outstandingBalance
            )}
          </strong>

          <small>
            Current financial exposure
          </small>
        </div>

      </div>


      {/* ======================================================
          EXECUTIVE SNAPSHOT
      ====================================================== */}

      <div className="analytics-executive-grid">

        <div className="analytics-section analytics-executive-card">

          <div className="analytics-section-header">
            <div>
              <span className="analytics-section-kicker">
                EXECUTIVE SNAPSHOT
              </span>

              <h2>
                Risk & Governance Position
              </h2>

              <p>
                A high-level view of where TANGLE
                requires operational attention.
              </p>
            </div>
          </div>


          <div className="analytics-snapshot-grid">

            <div>
              <span>Dominant Risk</span>

              <strong>
                {topRisk?.level || "—"}
              </strong>

              <small>
                {formatNumber(
                  topRisk?.count || 0
                )} cases
              </small>
            </div>


            <div>
              <span>Top Exception</span>

              <strong className="analytics-value-small">
                {topException?.category || "—"}
              </strong>

              <small>
                {formatNumber(
                  topException?.count || 0
                )} occurrences
              </small>
            </div>


            <div>
              <span>Average Priority</span>

              <strong>
                {Number(
                  averagePriority
                ).toFixed(2)}
              </strong>

              <small>
                Range {Number(
                  minimumPriority
                ).toFixed(0)}
                {" – "}
                {Number(
                  maximumPriority
                ).toFixed(0)}
              </small>
            </div>


            <div>
              <span>Payment Coverage</span>

              <strong>
                {Number(
                  averagePaymentCoverage
                ).toFixed(2)}
                %
              </strong>

              <small>
                {coverageStatus}
              </small>
            </div>

          </div>

        </div>


        <div className="analytics-section analytics-governance-card">

          <div className="analytics-section-header">
            <div>
              <span className="analytics-section-kicker">
                HUMAN GOVERNANCE
              </span>

              <h2>
                Review Outcomes
              </h2>

              <p>
                Decisions recorded through the
                human review workflow.
              </p>
            </div>
          </div>


          <div className="analytics-governance-stats">

            <div>
              <span>Approved</span>
              <strong>
                {approvedReviews}
              </strong>
            </div>

            <div>
              <span>Rejected</span>
              <strong>
                {rejectedReviews}
              </strong>
            </div>

            <div>
              <span>Escalated</span>
              <strong>
                {escalatedReviews}
              </strong>
            </div>

            <div>
              <span>Pending</span>
              <strong>
                {pendingReviews}
              </strong>
            </div>

          </div>


          <div className="analytics-progress-block">

            <div className="analytics-progress-header">
              <span>
                Review completion
              </span>

              <strong>
                {Number(
                  reviewCompletionRate
                ).toFixed(2)}
                %
              </strong>
            </div>

            <div className="analytics-progress-track">
              <div
                className="analytics-progress-fill"
                style={{
                  width: `${Math.min(
                    Number(
                      reviewCompletionRate
                    ),
                    100
                  )}%`,
                }}
              />
            </div>

          </div>

        </div>

      </div>


      {/* ======================================================
          DISTRIBUTIONS
      ====================================================== */}

      <div className="analytics-grid">

        {/* ====================================================
            RISK DISTRIBUTION
        ==================================================== */}

        <div className="analytics-section">

          <div className="analytics-section-header">

            <div>
              <span className="analytics-section-kicker">
                RISK
              </span>

              <h2>
                Risk Distribution
              </h2>

              <p>
                Cases grouped by assessed risk level.
              </p>
            </div>

          </div>


          <div className="analytics-list">

            {riskData.length === 0 ? (

              <div className="analytics-empty">
                No risk data available.
              </div>

            ) : (

              riskData.map(
                (item, index) => {

                  const percentage =
                    totalCases
                      ? (
                          item.count /
                          totalCases
                        ) * 100
                      : 0;

                  return (
                    <div
                      className="analytics-row analytics-distribution-row"
                      key={`${item.level}-${index}`}
                    >

                      <div className="analytics-row-main">

                        <span
                          className={
                            `analytics-risk-badge ${
                              String(
                                item.level
                              ).toLowerCase()
                            }`
                          }
                        >
                          {item.level}
                        </span>

                        <div className="analytics-mini-bar">
                          <div
                            style={{
                              width: `${Math.min(
                                percentage,
                                100
                              )}%`,
                            }}
                          />
                        </div>

                      </div>

                      <strong>
                        {formatNumber(
                          item.count
                        )}
                      </strong>

                    </div>
                  );
                }
              )

            )}

          </div>

        </div>


        {/* ====================================================
            EXCEPTION DISTRIBUTION
        ==================================================== */}

        <div className="analytics-section">

          <div className="analytics-section-header">

            <div>
              <span className="analytics-section-kicker">
                EXCEPTIONS
              </span>

              <h2>
                Exception Distribution
              </h2>

              <p>
                Transaction anomaly categories detected
                by TANGLE.
              </p>
            </div>

          </div>


          <div className="analytics-list">

            {exceptionData.length === 0 ? (

              <div className="analytics-empty">
                No exception data available.
              </div>

            ) : (

              exceptionData.map(
                (item, index) => {

                  const percentage =
                    totalCases
                      ? (
                          item.count /
                          totalCases
                        ) * 100
                      : 0;

                  return (
                    <div
                      className="analytics-row analytics-distribution-row"
                      key={`${item.category}-${index}`}
                    >

                      <div className="analytics-row-main">

                        <span className="analytics-category-label">
                          {item.category}
                        </span>

                        <div className="analytics-mini-bar">
                          <div
                            style={{
                              width: `${Math.min(
                                percentage,
                                100
                              )}%`,
                            }}
                          />
                        </div>

                      </div>

                      <strong>
                        {formatNumber(
                          item.count
                        )}
                      </strong>

                    </div>
                  );
                }
              )

            )}

          </div>

        </div>


        {/* ====================================================
            CASE LIFECYCLE
        ==================================================== */}

        <div className="analytics-section">

          <div className="analytics-section-header">

            <div>
              <span className="analytics-section-kicker">
                WORKFLOW
              </span>

              <h2>
                Case Lifecycle
              </h2>

              <p>
                Current position of cases in the
                governance lifecycle.
              </p>
            </div>

          </div>


          <div className="analytics-list">

            {lifecycleData.length === 0 ? (

              <div className="analytics-empty">
                No lifecycle data available.
              </div>

            ) : (

              lifecycleData.map(
                (item, index) => {

                  const percentage =
                    totalCases
                      ? (
                          item.count /
                          totalCases
                        ) * 100
                      : 0;

                  return (
                    <div
                      className="analytics-row analytics-distribution-row"
                      key={`${item.status}-${index}`}
                    >

                      <div className="analytics-row-main">

                        <span className="analytics-category-label">
                          {item.status}
                        </span>

                        <div className="analytics-mini-bar">
                          <div
                            style={{
                              width: `${Math.min(
                                percentage,
                                100
                              )}%`,
                            }}
                          />
                        </div>

                      </div>

                      <strong>
                        {formatNumber(
                          item.count
                        )}
                      </strong>

                    </div>
                  );
                }
              )

            )}

          </div>

        </div>


        {/* ====================================================
            FINANCIAL ANALYSIS
        ==================================================== */}

        <div className="analytics-section">

          <div className="analytics-section-header">

            <div>
              <span className="analytics-section-kicker">
                FINANCIAL
              </span>

              <h2>
                Financial Exposure
              </h2>

              <p>
                Monetary values across the source
                transaction datasets.
              </p>
            </div>

          </div>


          <div className="analytics-list">

            <div className="analytics-row">
              <span>Invoice Amount</span>

              <strong>
                {formatCurrency(
                  totalInvoiceAmount
                )}
              </strong>
            </div>


            <div className="analytics-row">
              <span>Payment Amount</span>

              <strong>
                {formatCurrency(
                  totalPaymentAmount
                )}
              </strong>
            </div>


            <div className="analytics-row">
              <span>Bank Amount</span>

              <strong>
                {formatCurrency(
                  totalBankAmount
                )}
              </strong>
            </div>


            <div className="analytics-row analytics-financial-highlight">
              <span>Outstanding Balance</span>

              <strong>
                {formatCurrency(
                  outstandingBalance
                )}
              </strong>
            </div>

          </div>

        </div>


        {/* ====================================================
            PRIORITY ANALYSIS
        ==================================================== */}

        <div className="analytics-section">

          <div className="analytics-section-header">

            <div>
              <span className="analytics-section-kicker">
                PRIORITY
              </span>

              <h2>
                Investigation Priority
              </h2>

              <p>
                Priority scoring used to focus
                operational attention.
              </p>
            </div>

          </div>


          <div className="analytics-priority-grid">

            <div>
              <span>Average</span>

              <strong>
                {Number(
                  averagePriority
                ).toFixed(2)}
              </strong>
            </div>


            <div>
              <span>Maximum</span>

              <strong>
                {Number(
                  maximumPriority
                ).toFixed(2)}
              </strong>
            </div>


            <div>
              <span>Minimum</span>

              <strong>
                {Number(
                  minimumPriority
                ).toFixed(2)}
              </strong>
            </div>

          </div>


          <div className="analytics-decision-box">

            <span>
              Dominant AI Decision
            </span>

            <strong>
              {Object.entries(
                decisionDistribution
              ).sort(
                ([, a], [, b]) => b - a
              )[0]?.[0] || "—"}
            </strong>

          </div>

        </div>


        {/* ====================================================
            OPERATIONAL INSIGHTS
        ==================================================== */}

        <div className="analytics-section analytics-insight">

          <div className="analytics-section-header">

            <div>
              <span className="analytics-section-kicker">
                INTELLIGENCE
              </span>

              <h2>
                TANGLE Operational Insights
              </h2>

              <p>
                Analytics translated into actionable
                operational signals.
              </p>
            </div>

          </div>


          <div className="analytics-insight-list">

            <div className="analytics-insight-item">

              <strong>
                Risk concentration
              </strong>

              <p>
                {highRiskCases} of {totalCases} cases
                are classified as HIGH or CRITICAL risk,
                making risk concentration the primary
                operational focus.
              </p>

            </div>


            <div className="analytics-insight-item">

              <strong>
                Governance workload
              </strong>

              <p>
                {pendingReviewCases} cases are currently
                pending review, while {reviewCompletionRate.toFixed(2)}%
                of recorded reviews have reached a final
                decision.
              </p>

            </div>


            <div className="analytics-insight-item">

              <strong>
                Exception concentration
              </strong>

              <p>
                {topException?.category || "No dominant exception"}
                {" "}
                is currently the most frequent exception
                category with {topException?.count || 0}
                {" "}
                detected cases.
              </p>

            </div>


            <div className="analytics-insight-item">

              <strong>
                Financial exposure
              </strong>

              <p>
                TANGLE currently identifies{" "}
                {formatCurrency(
                  outstandingBalance
                )}
                {" "}
                in outstanding balance across the
                reconciliation case population.
              </p>

            </div>

          </div>

        </div>

      </div>


      {/* ======================================================
          FOOTER STATUS
      ====================================================== */}

      <div className="analytics-footer-status">

        <span>
          TANGLE Analytics Engine
        </span>

        <span>
          {formatNumber(totalCases)} cases analyzed
        </span>

        <span>
          {formatNumber(resolvedCases)} resolved
        </span>

        <span>
          Data synchronized from PostgreSQL
        </span>

      </div>

    </div>
  );
}


export default Analytics;