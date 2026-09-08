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

  // ============================================================
  // MAIN PAGE
  // ============================================================

  return (
    <div className="page">
      <div className="investigation-page">

        {/* ====================================================
            HEADER
        ==================================================== */}

        <div className="investigation-header">

          <div>

            <button
              className="investigation-back-button"
              onClick={() => navigate("/cases")}
            >
              ← Back to Cases
            </button>

            <h1>
              Case Investigation
            </h1>

            <p>
              Explainable AI investigation and
              financial evidence for {caseId}
            </p>

          </div>

          <div className="investigation-case-id">
            <span>CASE ID</span>

            <strong>
              {caseId}
            </strong>
          </div>

        </div>


        {/* ====================================================
            SUMMARY
        ==================================================== */}

        <div className="investigation-summary-grid">

          <div className="investigation-info-card">
            <span className="investigation-card-label">
              Risk Level
            </span>

            <strong className="investigation-card-value">
              {risk.risk_level || "N/A"}
            </strong>
          </div>


          <div className="investigation-info-card">
            <span className="investigation-card-label">
              Priority Score
            </span>

            <strong className="investigation-card-value">
              {risk.priority_score ?? "N/A"}
            </strong>
          </div>


          <div className="investigation-info-card">
            <span className="investigation-card-label">
              AI Confidence
            </span>

            <strong className="investigation-card-value">
              {formatConfidence(confidence)}
            </strong>
          </div>


          <div className="investigation-info-card">
            <span className="investigation-card-label">
              Human Review
            </span>

            <strong className="investigation-card-value">
              {humanReviewRequired
                ? "Required"
                : "Not Required"}
            </strong>
          </div>

        </div>


        {/* ====================================================
            TRANSACTION INFORMATION
        ==================================================== */}

        <div className="investigation-section">

          <h2>
            Transaction Information
          </h2>

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
                {caseData.category ||
                  caseData.exception_type ||
                  "—"}
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

        <div className="investigation-section">

          <h2>
            Financial Analysis
          </h2>

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
                {financial.financial_status ||
                  "—"}
              </strong>
            </div>


            <div>
              <span>Financial Impact</span>

              <strong>
                {financial.financial_impact ||
                  "—"}
              </strong>
            </div>

          </div>

        </div>


        {/* ====================================================
            EXPLAINABLE AI INVESTIGATION
        ==================================================== */}

        <div className="investigation-section explainable-investigation">

          <div className="investigation-section-heading">

            <div>
              <h2>
                AI Investigation
              </h2>

              <p>
                Every AI conclusion is supported
                by transaction evidence.
              </p>
            </div>

            <div className="ai-confidence-badge">
              <span>
                Confidence
              </span>

              <strong>
                {formatConfidence(confidence)}
              </strong>
            </div>

          </div>


          {/* FINDING */}

          <div className="investigation-explain-block">

            <div className="investigation-step-number">
              1
            </div>

            <div className="investigation-step-content">

              <span>
                Finding
              </span>

              <p>
                {investigation.finding ||
                  "No finding available."}
              </p>

            </div>

          </div>


          {/* LIKELY CAUSE */}

          <div className="investigation-explain-block">

            <div className="investigation-step-number">
              2
            </div>

            <div className="investigation-step-content">

              <span>
                Likely Cause
              </span>

              <p>
                {investigation.likely_cause ||
                  "No likely cause identified."}
              </p>

            </div>

          </div>


          {/* EVIDENCE */}

          <div className="investigation-evidence-container">

            <div className="investigation-step-number">
              3
            </div>

            <div className="investigation-step-content">

              <span>
                Evidence
              </span>

              <p className="investigation-evidence-intro">
                The investigation is based on
                the following financial facts:
              </p>


              {evidence.length > 0 ? (

                <div className="investigation-evidence-grid">

                  {evidence.map(
                    (item, index) => (

                      <div
                        className="investigation-evidence-card"
                        key={`${item.label}-${index}`}
                      >

                        <span>
                          {item.label}
                        </span>

                        <strong>
                          {item.value}
                        </strong>

                        {item.source && (
                          <small>
                            Source: {item.source}
                          </small>
                        )}

                      </div>

                    )
                  )}

                </div>

              ) : (

                <div className="investigation-no-evidence">
                  No structured evidence available.
                </div>

              )}

            </div>

          </div>


          {/* CONFIDENCE */}

          <div className="investigation-explain-block">

            <div className="investigation-step-number">
              4
            </div>

            <div className="investigation-step-content">

              <span>
                Confidence
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
                          Number(confidence || 0) *
                            100,
                          0
                        ),
                        100
                      )}%`,
                    }}
                  />

                </div>

              </div>

            </div>

          </div>


          {/* RECOMMENDATION */}

          <div className="investigation-explain-block">

            <div className="investigation-step-number">
              5
            </div>

            <div className="investigation-step-content">

              <span>
                Recommendation
              </span>

              <p className="investigation-recommendation">
                {investigation.recommendation ||
                  "No recommendation available."}
              </p>

            </div>

          </div>


          {/* REASONING */}

          {reasoning.length > 0 && (

            <div className="investigation-reasoning-container">

              <span>
                Investigation Reasoning
              </span>

              <ol>

                {reasoning.map(
                  (step, index) => (

                    <li key={index}>
                      {step}
                    </li>

                  )
                )}

              </ol>

            </div>

          )}

        </div>


        {/* ====================================================
            RISK ASSESSMENT
        ==================================================== */}

        <div className="investigation-section">

          <h2>
            Risk Assessment
          </h2>

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

          <h2>
            Governance & Review
          </h2>

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