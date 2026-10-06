import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function Investigation() {
  const { caseId } = useParams();
  const navigate = useNavigate();

  // ============================================================
  // STATE
  // ============================================================

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ============================================================
  // LOAD INVESTIGATION
  // ============================================================

  useEffect(() => {
    let mounted = true;

    const loadInvestigation = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(
          `/api/investigation/${caseId}`
        );

        if (mounted) {
          setData(response.data);
        }
      } catch (err) {
        console.error(
          "Failed to load investigation:",
          err
        );

        if (mounted) {
          setError(
            "Unable to load investigation data."
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    if (caseId) {
      loadInvestigation();
    }

    return () => {
      mounted = false;
    };
  }, [caseId]);

  // ============================================================
  // HELPERS
  // ============================================================

  const formatAmount = (value, currency = "INR") => {
    if (
      value === null ||
      value === undefined ||
      value === "" ||
      Number.isNaN(Number(value))
    ) {
      return "—";
    }

    try {
      return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency,
        maximumFractionDigits: 2,
      }).format(Number(value));
    } catch {
      return `${currency} ${Number(value).toFixed(2)}`;
    }
  };

  const formatPercent = (value) => {
    if (
      value === null ||
      value === undefined ||
      value === "" ||
      Number.isNaN(Number(value))
    ) {
      return "—";
    }

    return `${Number(value).toFixed(2)}%`;
  };

  const formatConfidence = (value) => {
    if (
      value === null ||
      value === undefined ||
      value === "" ||
      Number.isNaN(Number(value))
    ) {
      return "—";
    }

    return `${Math.round(Number(value) * 100)}%`;
  };

  const confidenceValue = (value) => {
    if (
      value === null ||
      value === undefined ||
      value === "" ||
      Number.isNaN(Number(value))
    ) {
      return 0;
    }

    return Math.min(
      Math.max(Number(value) * 100, 0),
      100
    );
  };

  const formatReasoning = (value) => {
    if (!value) {
      return [];
    }

    if (Array.isArray(value)) {
      return value;
    }

    try {
      const parsed = JSON.parse(value);

      if (Array.isArray(parsed)) {
        return parsed;
      }
    } catch {
      // Plain text reasoning
    }

    return String(value)
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);
  };

  const cleanText = (
    value,
    fallback = "—"
  ) => {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return fallback;
    }

    return String(value);
  };

  const getRiskClass = (riskLevel) => {
    const level = String(
      riskLevel || ""
    ).toUpperCase();

    if (
      level === "HIGH" ||
      level === "CRITICAL"
    ) {
      return "risk-high";
    }

    if (
      level === "MEDIUM" ||
      level === "MODERATE"
    ) {
      return "risk-medium";
    }

    if (level === "LOW") {
      return "risk-low";
    }

    return "risk-neutral";
  };

  const getStatusClass = (status) => {
    const value = String(
      status || ""
    ).toUpperCase();

    if (
      value.includes("APPROVED") ||
      value.includes("RESOLVED") ||
      value.includes("CLOSED")
    ) {
      return "status-success";
    }

    if (
      value.includes("REJECTED") ||
      value.includes("FAILED")
    ) {
      return "status-danger";
    }

    if (
      value.includes("PENDING") ||
      value.includes("REVIEW")
    ) {
      return "status-warning";
    }

    return "status-neutral";
  };

  // ============================================================
  // NORMALIZED DATA
  // ============================================================

  const normalized = useMemo(() => {
    if (!data) {
      return null;
    }

    const caseData = data.case || {};
    const financial = data.financial || {};
    const investigation =
      data.ai_investigation || {};
    const risk = data.risk || {};
    const review = data.review || {};

    const exceptionCategory =
      caseData.category ||
      caseData.exception_type ||
      "UNKNOWN";

    const riskLevel =
      risk.risk_level || "N/A";

    const confidence =
      investigation.confidence ??
      caseData.confidence;

    const humanReviewRequired = Boolean(
      risk.human_review_required ??
        caseData.human_review_required
    );

    const currentStatus =
      review.case_status ||
      caseData.status ||
      "—";

    const reasoning = formatReasoning(
      investigation.reasoning
    );

    const evidence = Array.isArray(
      investigation.evidence
    )
      ? investigation.evidence
      : [];

    return {
      caseData,
      financial,
      investigation,
      risk,
      review,
      exceptionCategory,
      riskLevel,
      confidence,
      humanReviewRequired,
      currentStatus,
      reasoning,
      evidence,
      currency:
        financial.currency || "INR",
    };
  }, [data]);

  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return (
      <div className="investigation-shell">
        <div className="investigation-state">
          <div className="state-icon">T</div>

          <div>
            <h2>Loading Investigation</h2>

            <p>
              Preparing investigation workspace for{" "}
              <strong>{caseId}</strong>
            </p>
          </div>
        </div>
      </div>
    );
  }

  // ============================================================
  // ERROR
  // ============================================================

  if (error) {
    return (
      <div className="investigation-shell">
        <div className="investigation-state error-state">
          <div className="state-icon">!</div>

          <h2>
            Investigation unavailable
          </h2>

          <p>{error}</p>

          <button
            className="investigation-primary-button"
            onClick={() =>
              navigate("/cases")
            }
          >
            ← Back to Cases
          </button>
        </div>
      </div>
    );
  }

  // ============================================================
  // NO DATA
  // ============================================================

  if (!normalized) {
    return (
      <div className="investigation-shell">
        <div className="investigation-state">
          <h2>
            No investigation data found
          </h2>

          <button
            className="investigation-primary-button"
            onClick={() =>
              navigate("/cases")
            }
          >
            ← Back to Cases
          </button>
        </div>
      </div>
    );
  }

  const {
    caseData,
    financial,
    investigation,
    risk,
    review,
    exceptionCategory,
    riskLevel,
    confidence,
    humanReviewRequired,
    currentStatus,
    reasoning,
    evidence,
    currency,
  } = normalized;

  const confidenceWidth =
    confidenceValue(confidence);

  const decision =
    caseData.decision ||
    caseData.suggested_action ||
    investigation.recommendation ||
    "Pending";

  // ============================================================
  // MAIN PAGE
  // ============================================================

  return (
    <div className="investigation-shell">
      <main className="investigation-container">

        {/* =====================================================
            TOP BAR
        ===================================================== */}

        <header className="investigation-topbar">

          <button
            className="investigation-back-link"
            onClick={() =>
              navigate("/cases")
            }
          >
            <span>←</span>
            Back to Cases
          </button>

          <div className="workspace-indicator">
            <span className="workspace-dot" />
            Investigation Workspace
          </div>

        </header>

        {/* =====================================================
            CASE HEADER
        ===================================================== */}

        <section className="case-header">

          <div className="case-header-left">

            <div className="case-overline">
              CASE INVESTIGATION
            </div>

            <div className="case-title-row">

              <div>
                <h1>{caseId}</h1>

                <p>
                  Explainable AI investigation
                  and transaction intelligence
                </p>
              </div>

              <div
                className={`case-status ${getStatusClass(
                  currentStatus
                )}`}
              >
                <span className="status-dot" />

                {currentStatus}
              </div>

            </div>

          </div>

          <div className="case-header-actions">

            <div
              className={`risk-chip-large ${getRiskClass(
                riskLevel
              )}`}
            >
              <span>RISK</span>
              <strong>{riskLevel}</strong>
            </div>

            {humanReviewRequired && (
              <div className="review-required-chip">
                <span>●</span>
                Human Review Required
              </div>
            )}

          </div>

        </section>

        {/* =====================================================
            KPI STRIP
        ===================================================== */}

        <section className="investigation-kpi-strip">

          <Metric
            label="Exception"
            value={exceptionCategory}
          />

          <Metric
            label="Risk Score"
            value={
              risk.risk_score ??
              "—"
            }
          />

          <Metric
            label="Priority Score"
            value={
              risk.priority_score ??
              "—"
            }
          />

          <Metric
            label="AI Confidence"
            value={formatConfidence(
              confidence
            )}
            highlight
          />

          <Metric
            label="Outstanding"
            value={formatAmount(
              financial.outstanding_amount,
              currency
            )}
            financial
          />

        </section>

        {/* =====================================================
            MAIN INVESTIGATION GRID
        ===================================================== */}

        <section className="investigation-main-grid">

          {/* =================================================
              LEFT — AI INVESTIGATION
          ================================================= */}

          <div className="investigation-primary-column">

            <section className="ai-investigation-card">

              <div className="ai-card-header">

                <div>

                  <div className="ai-label">
                    EXPLAINABLE AI
                  </div>

                  <h2>
                    TANGLE Investigation
                  </h2>

                  <p>
                    Evidence-driven analysis
                    of the detected transaction
                    anomaly.
                  </p>

                </div>

                <div className="ai-confidence-box">

                  <span>
                    AI CONFIDENCE
                  </span>

                  <strong>
                    {formatConfidence(
                      confidence
                    )}
                  </strong>

                  <div className="confidence-track">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${confidenceWidth}%`,
                      }}
                    />
                  </div>

                </div>

              </div>

              {/* AI DECISION */}

              <div className="ai-decision-banner">

                <div className="decision-icon">
                  AI
                </div>

                <div className="decision-content">

                  <span>
                    AI ASSESSMENT
                  </span>

                  <h3>
                    {exceptionCategory}
                  </h3>

                  <p>
                    {investigation.finding ||
                      "No investigation finding is available."}
                  </p>

                </div>

                <div className="decision-result">

                  <span>
                    DECISION
                  </span>

                  <strong>
                    {cleanText(decision)}
                  </strong>

                </div>

              </div>

              {/* CONCLUSION */}

              <div className="ai-conclusion-grid">

                <InsightCard
                  label="Likely Cause"
                  value={
                    investigation.likely_cause ||
                    "No likely cause has been identified."
                  }
                />

                <InsightCard
                  label="Recommended Action"
                  value={
                    investigation.recommendation ||
                    "No recommendation is available."
                  }
                />

              </div>

            </section>

            {/* =================================================
                INVESTIGATION JOURNEY
            ================================================= */}

            <section className="journey-card">

              <div className="section-heading">

                <div>
                  <span className="section-overline">
                    INVESTIGATION JOURNEY
                  </span>

                  <h2>
                    How TANGLE reached this conclusion
                  </h2>

                  <p>
                    Follow the evidence and
                    reasoning behind the AI
                    assessment.
                  </p>
                </div>

              </div>

              <div className="journey">

                <InvestigationStep
                  number="01"
                  title="Detection"
                  description={
                    investigation.finding ||
                    "No investigation finding is available."
                  }
                >
                  {investigation.rationale && (
                    <DetailBox
                      label="Detection rationale"
                      value={
                        investigation.rationale
                      }
                    />
                  )}
                </InvestigationStep>

                <InvestigationStep
                  number="02"
                  title="Reasoning"
                  description="The reasoning path connecting transaction evidence to the investigation conclusion."
                >
                  {reasoning.length > 0 ? (
                    <div className="reasoning-list">

                      {reasoning.map(
                        (step, index) => (
                          <div
                            className="reasoning-item"
                            key={index}
                          >
                            <div className="reasoning-index">
                              {String(
                                index + 1
                              ).padStart(
                                2,
                                "0"
                              )}
                            </div>

                            <div>
                              {step}
                            </div>
                          </div>
                        )
                      )}

                    </div>
                  ) : (
                    <EmptyState
                      text="No structured reasoning is available."
                    />
                  )}
                </InvestigationStep>

                <InvestigationStep
                  number="03"
                  title="Evidence"
                  description="Financial facts used by TANGLE during the investigation."
                >

                  {evidence.length > 0 ? (
                    <div className="evidence-grid">

                      {evidence.map(
                        (item, index) => (
                          <div
                            className="evidence-item"
                            key={`${item.label || "evidence"}-${index}`}
                          >
                            <span>
                              {item.source ||
                                "Evidence"}
                            </span>

                            <small>
                              {item.label}
                            </small>

                            <strong>
                              {item.value}
                            </strong>
                          </div>
                        )
                      )}

                    </div>
                  ) : (
                    <EmptyState
                      text="No structured evidence is available."
                    />
                  )}

                  {investigation.evidence_summary && (
                    <DetailBox
                      label="Evidence Summary"
                      value={
                        investigation.evidence_summary
                      }
                    />
                  )}

                </InvestigationStep>

                <InvestigationStep
                  number="04"
                  title="Likely Cause"
                  description={
                    investigation.likely_cause ||
                    "No likely cause has been identified."
                  }
                />

                <InvestigationStep
                  number="05"
                  title="Confidence Assessment"
                  description="TANGLE's confidence in the detected exception and investigation conclusion."
                >

                  <div className="confidence-analysis">

                    <div className="confidence-number">
                      {formatConfidence(
                        confidence
                      )}
                    </div>

                    <div className="confidence-analysis-content">

                      <div className="confidence-analysis-track">

                        <div
                          className="confidence-analysis-fill"
                          style={{
                            width: `${confidenceWidth}%`,
                          }}
                        />

                      </div>

                      <p>
                        Confidence supports
                        investigation but does
                        not replace human
                        governance.
                      </p>

                    </div>

                  </div>

                </InvestigationStep>

                <InvestigationStep
                  number="06"
                  title="Recommended Action"
                  description={
                    investigation.recommendation ||
                    "No recommendation is available."
                  }
                  last
                >

                  <div className="governance-mini-grid">

                    <div>
                      <span>
                        Human Review
                      </span>

                      <strong
                        className={
                          humanReviewRequired
                            ? "metric-required"
                            : "metric-clear"
                        }
                      >
                        {humanReviewRequired
                          ? "Required"
                          : "Not Required"}
                      </strong>
                    </div>

                    <div>
                      <span>
                        Current Status
                      </span>

                      <strong>
                        {currentStatus}
                      </strong>
                    </div>

                  </div>

                </InvestigationStep>

              </div>

            </section>

          </div>

          {/* =================================================
              RIGHT — INTELLIGENCE SIDEBAR
          ================================================= */}

          <aside className="investigation-side-column">

            {/* RISK */}

            <section className="side-card risk-panel">

              <div className="side-card-heading">

                <div>
                  <span>
                    RISK & GOVERNANCE
                  </span>

                  <h3>
                    Risk Assessment
                  </h3>
                </div>

                <div
                  className={`risk-badge ${getRiskClass(
                    riskLevel
                  )}`}
                >
                  {riskLevel}
                </div>

              </div>

              <div className="risk-score-display">

                <span>
                  RISK SCORE
                </span>

                <strong>
                  {risk.risk_score ??
                    "—"}
                </strong>

              </div>

              <div className="side-metrics">

                <SideMetric
                  label="Priority Score"
                  value={
                    risk.priority_score ??
                    "—"
                  }
                />

                <SideMetric
                  label="Human Review"
                  value={
                    humanReviewRequired
                      ? "Required"
                      : "Not Required"
                    }
                  />

              </div>

              <div className="risk-reason">

                <span>
                  Risk Reason
                </span>

                <p>
                  {risk.risk_reason ||
                    "No risk reason available."}
                </p>

              </div>

            </section>

            {/* FINANCIAL */}

            <section className="side-card">

              <div className="side-card-heading">

                <div>
                  <span>
                    FINANCIAL EVIDENCE
                  </span>

                  <h3>
                    Financial Snapshot
                  </h3>
                </div>

                <div className="side-icon">
                  ₹
                </div>

              </div>

              <div className="financial-primary">

                <span>
                  OUTSTANDING
                </span>

                <strong>
                  {formatAmount(
                    financial.outstanding_amount,
                    currency
                  )}
                </strong>

              </div>

              <div className="financial-list">

                <SideMetric
                  label="Invoice Amount"
                  value={formatAmount(
                    financial.invoice_amount,
                    currency
                  )}
                />

                <SideMetric
                  label="Payment Amount"
                  value={formatAmount(
                    financial.payment_amount,
                    currency
                  )}
                />

                <SideMetric
                  label="Bank Amount"
                  value={formatAmount(
                    financial.bank_amount,
                    currency
                  )}
                />

                <SideMetric
                  label="Payment Coverage"
                  value={formatPercent(
                    financial.payment_coverage_percent
                  )}
                />

                <SideMetric
                  label="Financial Status"
                  value={
                    financial.financial_status ||
                    "—"
                  }
                />

              </div>

            </section>

            {/* TRANSACTION */}

            <section className="side-card">

              <div className="side-card-heading">

                <div>
                  <span>
                    TRANSACTION
                  </span>

                  <h3>
                    Case Information
                  </h3>
                </div>

                <div className="side-icon">
                  #
                </div>

              </div>

              <div className="transaction-list">

                <SideMetric
                  label="Record Type"
                  value={
                    caseData.record_type
                  }
                />

                <SideMetric
                  label="Record ID"
                  value={
                    caseData.record_id
                  }
                />

                <SideMetric
                  label="Invoice ID"
                  value={
                    caseData.invoice_id
                  }
                />

                <SideMetric
                  label="Payment ID"
                  value={
                    caseData.payment_id
                  }
                />

                <SideMetric
                  label="Category"
                  value={
                    exceptionCategory
                  }
                />

              </div>

            </section>

          </aside>

        </section>

        {/* =====================================================
            GOVERNANCE
        ===================================================== */}

        <section className="governance-card">

          <div className="governance-header">

            <div>

              <span className="section-overline">
                HUMAN OVERSIGHT
              </span>

              <h2>
                Governance & Review
              </h2>

              <p>
                Human decision and final case
                governance state.
              </p>

            </div>

            <div
              className={`review-status ${getStatusClass(
                review.review_status ||
                  "PENDING"
              )}`}
            >
              <span className="status-dot" />

              {review.review_status ||
                "PENDING"}
            </div>

          </div>

          <div className="review-grid">

            <ReviewItem
              label="Case Status"
              value={
                review.case_status
              }
            />

            <ReviewItem
              label="Review Status"
              value={
                review.review_status ||
                "PENDING"
              }
            />

            <ReviewItem
              label="Reviewer"
              value={
                review.reviewer
              }
            />

            <ReviewItem
              label="Reviewer Decision"
              value={
                review.reviewer_decision
              }
            />

            <ReviewItem
              label="Final Status"
              value={
                review.final_status
              }
            />

          </div>

          {review.comment && (
            <div className="review-comment">

              <span>
                REVIEWER COMMENT
              </span>

              <p>
                {review.comment}
              </p>

            </div>
          )}

        </section>

        {/* =====================================================
            FINAL ACTION BAR
        ===================================================== */}

        <footer className="investigation-action-bar">

          <button
            className="action-secondary"
            onClick={() =>
              navigate("/cases")
            }
          >
            ← Back to Cases
          </button>

          <div className="action-right">

            {humanReviewRequired && (
              <button
                className="action-primary"
                onClick={() =>
                  navigate("/review")
                }
              >
                Go to Human Review
                <span>→</span>
              </button>
            )}

          </div>

        </footer>

      </main>
    </div>
  );
}

// ================================================================
// METRIC
// ================================================================

function Metric({
  label,
  value,
  highlight = false,
  financial = false,
}) {
  return (
    <div
      className={`investigation-metric-box ${
        highlight
          ? "metric-highlight"
          : ""
      }`}
    >
      <span>{label}</span>

      <strong
        className={
          financial
            ? "metric-financial"
            : ""
        }
      >
        {value}
      </strong>
    </div>
  );
}

// ================================================================
// INSIGHT CARD
// ================================================================

function InsightCard({
  label,
  value,
}) {
  return (
    <div className="insight-card">

      <span>{label}</span>

      <p>{value}</p>

    </div>
  );
}

// ================================================================
// SIDE METRIC
// ================================================================

function SideMetric({
  label,
  value,
}) {
  return (
    <div className="side-metric">

      <span>{label}</span>

      <strong>
        {value === null ||
        value === undefined ||
        value === ""
          ? "—"
          : value}
      </strong>

    </div>
  );
}

// ================================================================
// DETAIL BOX
// ================================================================

function DetailBox({
  label,
  value,
}) {
  return (
    <div className="detail-box">

      <span>{label}</span>

      <p>{value}</p>

    </div>
  );
}

// ================================================================
// REVIEW ITEM
// ================================================================

function ReviewItem({
  label,
  value,
}) {
  return (
    <div className="review-item">

      <span>{label}</span>

      <strong>
        {value === null ||
        value === undefined ||
        value === ""
          ? "—"
          : value}
      </strong>

    </div>
  );
}

// ================================================================
// EMPTY STATE
// ================================================================

function EmptyState({ text }) {
  return (
    <div className="investigation-empty">
      <span>○</span>
      {text}
    </div>
  );
}

// ================================================================
// INVESTIGATION STEP
// ================================================================

function InvestigationStep({
  number,
  title,
  description,
  children,
  last = false,
}) {
  return (
    <div
      className={`investigation-step ${
        last
          ? "investigation-step-last"
          : ""
      }`}
    >

      <div className="step-marker">
        {number}
      </div>

      {!last && (
        <div className="step-line" />
      )}

      <div className="step-body">

        <div className="step-title">
          {title}
        </div>

        <p className="step-description">
          {description}
        </p>

        {children && (
          <div className="step-extra">
            {children}
          </div>
        )}

      </div>

    </div>
  );
}

export default Investigation;