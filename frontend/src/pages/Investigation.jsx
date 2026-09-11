import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api";

function Investigation() {
  const { caseId } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ============================================================
  // LOAD INVESTIGATION
  // ============================================================

  useEffect(() => {
    const loadInvestigation = async () => {
      try {
        const response = await api.get(
          `/api/investigation/${caseId}`
        );

        setData(response.data);
      } catch (error) {
        console.error(
          "Failed to load investigation:",
          error
        );

        setError(
          "Unable to load investigation data."
        );
      } finally {
        setLoading(false);
      }
    };

    loadInvestigation();
  }, [caseId]);

  // ============================================================
  // HELPERS
  // ============================================================

  const formatAmount = (value, currency = "INR") => {
    if (
      value === null ||
      value === undefined ||
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
      Number.isNaN(Number(value))
    ) {
      return "—";
    }

    return `${(Number(value) * 100).toFixed(0)}%`;
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
      // Existing plain-text reasoning is supported.
    }

    return String(value)
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);
  };

  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Case Investigation</h1>
          <p>
            Loading investigation for {caseId}...
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
          <h1>Case Investigation</h1>

          <p>{error}</p>

          <button
            className="investigation-back-button"
            onClick={() => navigate("/cases")}
          >
            ← Back to Cases
          </button>
        </div>
      </div>
    );
  }

  // ============================================================
  // SAFETY CHECK
  // ============================================================

  if (!data) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>No investigation data found.</h1>
        </div>
      </div>
    );
  }

  // ============================================================
  // DATA
  // ============================================================

  const caseData = data.case || {};
  const financial = data.financial || {};
  const investigation =
    data.ai_investigation || {};
  const risk = data.risk || {};
  const review = data.review || {};

  const evidence = Array.isArray(
    investigation.evidence
  )
    ? investigation.evidence
    : [];

  const reasoning = formatReasoning(
    investigation.reasoning
  );

  const currency =
    financial.currency || "INR";

  const confidence =
    investigation.confidence ??
    caseData.confidence;

  const humanReviewRequired =
    Boolean(
      risk.human_review_required ??
        caseData.human_review_required
    );

  const exceptionCategory =
    caseData.category ||
    caseData.exception_type ||
    "UNKNOWN";

  const riskLevel =
    risk.risk_level || "N/A";

  const currentStatus =
    review.case_status ||
    caseData.status ||
    "—";

  // ============================================================
  // MAIN PAGE
  // ============================================================

  return (
    <div className="page">
      <div className="investigation-page">

        {/* ====================================================
            INVESTIGATION COMMAND HEADER
        ==================================================== */}

        <div className="investigation-command-header">

          <div className="investigation-command-top">

            <button
              className="investigation-back-button investigation-command-back"
              onClick={() => navigate("/cases")}
            >
              ← Back to Cases
            </button>

            <span className="investigation-command-label">
              INVESTIGATION WORKSPACE
            </span>

          </div>


          <div className="investigation-command-main">

            <div className="investigation-command-title">

              <div className="investigation-case-kicker">
                CASE
              </div>

              <h1>
                {caseId}
              </h1>

              <p>
                Explainable AI investigation and
                financial evidence
              </p>

            </div>


            <div className="investigation-command-status">

              <span className="investigation-status-label">
                CURRENT STATUS
              </span>

              <strong>
                {currentStatus}
              </strong>

            </div>

          </div>


          <div className="investigation-command-divider" />


          <div className="investigation-command-metrics">

            <div className="investigation-command-metric">

              <span>
                Exception
              </span>

              <strong className="investigation-command-exception">
                {exceptionCategory}
              </strong>

            </div>


            <div className="investigation-command-metric">

              <span>
                Risk Level
              </span>

              <strong className="investigation-risk-value">
                {riskLevel}
              </strong>

            </div>


            <div className="investigation-command-metric">

              <span>
                Priority Score
              </span>

              <strong>
                {risk.priority_score ?? "N/A"}
              </strong>

            </div>


            <div className="investigation-command-metric">

              <span>
                AI Confidence
              </span>

              <strong>
                {formatConfidence(confidence)}
              </strong>

            </div>


            <div className="investigation-command-metric">

              <span>
                Human Review
              </span>

              <strong
                className={
                  humanReviewRequired
                    ? "investigation-review-required"
                    : "investigation-review-not-required"
                }
              >
                {humanReviewRequired
                  ? "Required"
                  : "Not Required"}
              </strong>

            </div>

          </div>

        </div>


        {/* ====================================================
            TRANSACTION INFORMATION
        ==================================================== */}

        <div className="investigation-section">

          <div className="investigation-section-heading">

            <div>
              <span className="investigation-section-eyebrow">
                TRANSACTION
              </span>

              <h2>
                Transaction Information
              </h2>

              <p>
                Core identifiers and exception classification
                associated with this case.
              </p>
            </div>

          </div>


          <div className="investigation-detail-grid">

            <div>
              <span>Record Type</span>

              <strong>
                {caseData.record_type || "—"}
              </strong>
            </div>


            <div>
              <span>Record ID</span>

              <strong>
                {caseData.record_id || "—"}
              </strong>
            </div>


            <div>
              <span>Invoice ID</span>

              <strong>
                {caseData.invoice_id || "—"}
              </strong>
            </div>


            <div>
              <span>Payment ID</span>

              <strong>
                {caseData.payment_id || "—"}
              </strong>
            </div>


            <div>
              <span>Exception Category</span>

              <strong>
                {exceptionCategory}
              </strong>
            </div>


            <div>
              <span>Case Status</span>

              <strong>
                {caseData.status || "—"}
              </strong>
            </div>

          </div>

        </div>


        {/* ====================================================
            FINANCIAL ANALYSIS
        ==================================================== */}

        <div className="investigation-section investigation-financial-section">

          <div className="investigation-section-heading">

            <div>
              <span className="investigation-section-eyebrow">
                FINANCIAL EVIDENCE
              </span>

              <h2>
                Financial Analysis
              </h2>

              <p>
                Quantitative comparison of invoice, payment,
                bank and outstanding amounts.
              </p>
            </div>

          </div>


          <div className="investigation-detail-grid">

            <div>
              <span>Invoice Amount</span>

              <strong>
                {formatAmount(
                  financial.invoice_amount,
                  currency
                )}
              </strong>
            </div>


            <div>
              <span>Payment Amount</span>

              <strong>
                {formatAmount(
                  financial.payment_amount,
                  currency
                )}
              </strong>
            </div>


            <div>
              <span>Bank Amount</span>

              <strong>
                {formatAmount(
                  financial.bank_amount,
                  currency
                )}
              </strong>
            </div>


            <div>
              <span>Outstanding Amount</span>

              <strong>
                {formatAmount(
                  financial.outstanding_amount,
                  currency
                )}
              </strong>
            </div>


            <div>
              <span>Payment Coverage</span>

              <strong>
                {formatPercent(
                  financial.payment_coverage_percent
                )}
              </strong>
            </div>


            <div>
              <span>Invoice-Payment Difference</span>

              <strong>
                {formatAmount(
                  financial.invoice_payment_difference,
                  currency
                )}
              </strong>
            </div>


            <div>
              <span>Bank-Payment Difference</span>

              <strong>
                {formatAmount(
                  financial.bank_payment_difference,
                  currency
                )}
              </strong>
            </div>


            <div>
              <span>Payment Fee</span>

              <strong>
                {formatAmount(
                  financial.payment_fee,
                  currency
                )}
              </strong>
            </div>


            <div>
              <span>Financial Status</span>

              <strong>
                {financial.financial_status || "—"}
              </strong>
            </div>


            <div>
              <span>Financial Impact</span>

              <strong>
                {financial.financial_impact || "—"}
              </strong>
            </div>

          </div>

        </div>


        {/* ====================================================
            EXPLAINABLE AI INVESTIGATION
        ==================================================== */}

        <div className="investigation-section explainable-investigation investigation-ai-section">

          <div className="investigation-ai-header">

            <div>

              <span className="investigation-ai-eyebrow">
                EXPLAINABLE AI
              </span>

              <h2>
                AI Investigation
              </h2>

              <p>
                Trace how TANGLE moved from transaction
                evidence to its investigation conclusion.
              </p>

            </div>


            <div className="ai-confidence-badge">

              <span>
                AI Confidence
              </span>

              <strong>
                {formatConfidence(confidence)}
              </strong>

            </div>

          </div>


          {/* ====================================================
              EXPLAINABILITY SNAPSHOT
          ==================================================== */}

          <div className="investigation-ai-snapshot">

            <div className="investigation-ai-snapshot-item">

              <span>
                Exception
              </span>

              <strong>
                {exceptionCategory}
              </strong>

            </div>


            <div className="investigation-ai-snapshot-item">

              <span>
                AI Decision
              </span>

              <strong>
                {caseData.decision ||
                  caseData.suggested_action ||
                  "—"}
              </strong>

            </div>


            <div className="investigation-ai-snapshot-item">

              <span>
                Risk Level
              </span>

              <strong>
                {riskLevel}
              </strong>

            </div>


            <div className="investigation-ai-snapshot-item">

              <span>
                Priority
              </span>

              <strong>
                {risk.priority_score ?? "—"}
              </strong>

            </div>

          </div>

                    {/* ====================================================
              AI CONCLUSION
          ==================================================== */}

          <div className="investigation-ai-conclusion">

            <div className="investigation-ai-conclusion-main">

              <span className="investigation-ai-conclusion-eyebrow">
                AI CONCLUSION
              </span>

              <h3>
                {exceptionCategory}
              </h3>

              <p className="investigation-ai-conclusion-finding">
                {investigation.finding ||
                  "No investigation finding is available."}
              </p>

            </div>


            <div className="investigation-ai-conclusion-details">

              <div>
                <span>
                  Likely Cause
                </span>

                <p>
                  {investigation.likely_cause ||
                    "No likely cause has been identified."}
                </p>
              </div>


              <div>
                <span>
                  Recommended Action
                </span>

                <p>
                  {investigation.recommendation ||
                    "No recommendation is available."}
                </p>
              </div>

            </div>


            <div className="investigation-ai-conclusion-confidence">

              <span>
                CONFIDENCE
              </span>

              <strong>
                {formatConfidence(confidence)}
              </strong>

            </div>

          </div>

          {/* ====================================================
              1 — FINDING
          ==================================================== */}

          <div className="investigation-explain-block">

            <div className="investigation-step-number">
              1
            </div>

            <div className="investigation-step-content">

              <span>
                What TANGLE Found
              </span>

              <p className="investigation-primary-finding">
                {investigation.finding ||
                  "No investigation finding is available."}
              </p>


              {investigation.rationale && (

                <div className="investigation-rationale">

                  <strong>
                    Detection rationale
                  </strong>

                  <p>
                    {investigation.rationale}
                  </p>

                </div>

              )}

            </div>

          </div>


          {/* ====================================================
              2 — REASONING
          ==================================================== */}

          <div className="investigation-explain-block">

            <div className="investigation-step-number">
              2
            </div>

            <div className="investigation-step-content">

              <span>
                Why TANGLE Thinks This
              </span>

              <p className="investigation-step-description">
                The following reasoning path explains how
                the transaction evidence led to this conclusion.
              </p>


              {reasoning.length > 0 ? (

                <ol className="investigation-reasoning-timeline">

                  {reasoning.map(
                    (step, index) => (

                      <li key={index}>

                        <div className="investigation-reasoning-index">
                          {index + 1}
                        </div>

                        <div className="investigation-reasoning-text">
                          {step}
                        </div>

                      </li>

                    )
                  )}

                </ol>

              ) : (

                <div className="investigation-no-evidence">
                  No structured reasoning is available.
                </div>

              )}

            </div>

          </div>


          {/* ====================================================
              3 — EVIDENCE
          ==================================================== */}

          <div className="investigation-evidence-container">

            <div className="investigation-step-number">
              3
            </div>

            <div className="investigation-step-content">

              <span>
                Evidence Used
              </span>

              <p className="investigation-evidence-intro">
                These financial facts were used by TANGLE
                during the investigation.
              </p>


              {evidence.length > 0 ? (

                <div className="investigation-evidence-grid">

                  {evidence.map(
                    (item, index) => (

                      <div
                        className="investigation-evidence-card"
                        key={`${item.label}-${index}`}
                      >

                        <div className="investigation-evidence-source">
                          {item.source || "Evidence"}
                        </div>

                        <span>
                          {item.label}
                        </span>

                        <strong>
                          {item.value}
                        </strong>

                      </div>

                    )
                  )}

                </div>

              ) : (

                <div className="investigation-no-evidence">
                  No structured evidence is available.
                </div>

              )}


              {investigation.evidence_summary && (

                <div className="investigation-evidence-summary">

                  <strong>
                    Evidence Summary
                  </strong>

                  <p>
                    {investigation.evidence_summary}
                  </p>

                </div>

              )}

            </div>

          </div>


          {/* ====================================================
              4 — LIKELY CAUSE
          ==================================================== */}

          <div className="investigation-explain-block">

            <div className="investigation-step-number">
              4
            </div>

            <div className="investigation-step-content">

              <span>
                Likely Cause
              </span>

              <p>
                {investigation.likely_cause ||
                  "No likely cause has been identified."}
              </p>

            </div>

          </div>


          {/* ====================================================
              5 — CONFIDENCE
          ==================================================== */}

          <div className="investigation-explain-block">

            <div className="investigation-step-number">
              5
            </div>

            <div className="investigation-step-content">

              <span>
                Confidence Assessment
              </span>

              <div className="investigation-confidence-row">

                <strong>
                  {formatConfidence(confidence)}
                </strong>

                <div className="investigation-confidence-bar">

                  <div
                    className="investigation-confidence-fill"
                    style={{
                      width: `${Math.min(
                        Math.max(
                          Number(confidence || 0) * 100,
                          0
                        ),
                        100
                      )}%`,
                    }}
                  />

                </div>

              </div>


              <p className="investigation-confidence-description">
                Confidence represents TANGLE's certainty in
                the detected exception and investigation
                conclusion. It does not replace human review
                when governance rules require approval.
              </p>

            </div>

          </div>


          {/* ====================================================
              6 — RECOMMENDATION
          ==================================================== */}

          <div className="investigation-explain-block investigation-final-step">

            <div className="investigation-step-number">
              6
            </div>

            <div className="investigation-step-content">

              <span>
                Recommended Action
              </span>

              <p className="investigation-recommendation">
                {investigation.recommendation ||
                  "No recommendation is available."}
              </p>


              <div className="investigation-governance-note">

                <div>

                  <span>
                    Human Review
                  </span>

                  <strong>
                    {humanReviewRequired
                      ? "Required"
                      : "Not Required"}
                  </strong>

                </div>


                <div>

                  <span>
                    Current Case Status
                  </span>

                  <strong>
                    {currentStatus}
                  </strong>

                </div>

              </div>

            </div>

          </div>

        </div>


        {/* ====================================================
            RISK ASSESSMENT
        ==================================================== */}

        <div className="investigation-section">

          <div className="investigation-section-heading">

            <div>

              <span className="investigation-section-eyebrow">
                RISK & GOVERNANCE
              </span>

              <h2>
                Risk Assessment
              </h2>

              <p>
                TANGLE's risk classification and prioritization
                for this investigation.
              </p>

            </div>

          </div>


          <div className="investigation-detail-grid">

            <div>
              <span>Risk Level</span>

              <strong>
                {risk.risk_level || "—"}
              </strong>
            </div>


            <div>
              <span>Risk Score</span>

              <strong>
                {risk.risk_score ?? "—"}
              </strong>
            </div>


            <div>
              <span>Priority Score</span>

              <strong>
                {risk.priority_score ?? "—"}
              </strong>
            </div>


            <div>
              <span>Human Review</span>

              <strong>
                {humanReviewRequired
                  ? "Required"
                  : "Not Required"}
              </strong>
            </div>

          </div>


          <div className="investigation-text-block">

            <span>
              Risk Reason
            </span>

            <p>
              {risk.risk_reason ||
                "No risk reason available."}
            </p>

          </div>

        </div>


        {/* ====================================================
            GOVERNANCE
        ==================================================== */}

        <div className="investigation-section">

          <div className="investigation-section-heading">

            <div>

              <span className="investigation-section-eyebrow">
                HUMAN OVERSIGHT
              </span>

              <h2>
                Governance & Review
              </h2>

              <p>
                Human decision and final case governance state.
              </p>

            </div>

          </div>


          <div className="investigation-detail-grid">

            <div>
              <span>Case Status</span>

              <strong>
                {review.case_status || "—"}
              </strong>
            </div>


            <div>
              <span>Review Status</span>

              <strong>
                {review.review_status || "PENDING"}
              </strong>
            </div>


            <div>
              <span>Reviewer</span>

              <strong>
                {review.reviewer || "—"}
              </strong>
            </div>


            <div>
              <span>Reviewer Decision</span>

              <strong>
                {review.reviewer_decision || "—"}
              </strong>
            </div>


            <div>
              <span>Final Status</span>

              <strong>
                {review.final_status || "—"}
              </strong>
            </div>

          </div>


          {review.comment && (

            <div className="investigation-text-block">

              <span>
                Reviewer Comment
              </span>

              <p>
                {review.comment}
              </p>

            </div>

          )}

        </div>


        {/* ====================================================
            ACTIONS
        ==================================================== */}

        <div className="investigation-actions">

          <button
            className="investigation-back-button"
            onClick={() => navigate("/cases")}
          >
            ← Back to Cases
          </button>


          {humanReviewRequired && (

            <button
              className="investigation-review-button"
              onClick={() => navigate("/review")}
            >
              Go to Human Review
            </button>

          )}

        </div>

      </div>
    </div>
  );
}

export default Investigation;
