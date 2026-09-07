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
  // LOAD INVESTIGATION DATA
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
  const investigation = data.ai_investigation || {};
  const risk = data.risk || {};
  const review = data.review || {};


  // ============================================================
  // MAIN PAGE
  // ============================================================

  return (

    <div className="page">

      <div className="investigation-page">


        {/* ======================================================
            HEADER
        ====================================================== */}

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
              Detailed investigation and financial
              analysis for {caseId}
            </p>

          </div>


          <div className="investigation-case-id">

            <span>CASE ID</span>

            <strong>
              {caseId}
            </strong>

          </div>

        </div>


        {/* ======================================================
            SUMMARY CARDS
        ====================================================== */}

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
              Human Review
            </span>

            <strong className="investigation-card-value">

              {risk.human_review_required
                ? "Required"
                : "Not Required"}

            </strong>

          </div>


          <div className="investigation-info-card">

            <span className="investigation-card-label">
              AI Decision
            </span>

            <strong className="investigation-card-value">
              {caseData.decision || "N/A"}
            </strong>

          </div>

        </div>


        {/* ======================================================
            TRANSACTION INFORMATION
        ====================================================== */}

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
              <span>Exception Category</span>
              <strong>
                {caseData.category || "—"}
              </strong>
            </div>


            <div>
              <span>Confidence</span>
              <strong>
                {caseData.confidence ?? "—"}
              </strong>
            </div>


            <div>
              <span>Suggested Action</span>
              <strong>
                {caseData.suggested_action || "—"}
              </strong>
            </div>

          </div>

        </div>


        {/* ======================================================
            FINANCIAL ANALYSIS
        ====================================================== */}

        <div className="investigation-section">

          <h2>
            Financial Analysis
          </h2>


          <div className="investigation-detail-grid">

            <div>
              <span>Invoice Amount</span>

              <strong>
                $
                {Number(
                  financial.original_invoice_amount ??
                  caseData.original_invoice_amount ??
                  0
                ).toFixed(2)}
              </strong>

            </div>


            <div>
              <span>Payment Amount</span>

              <strong>
                $
                {Number(
                  financial.payment_amount ??
                  caseData.payment_amount ??
                  0
                ).toFixed(2)}
              </strong>

            </div>


            <div>
              <span>Bank Amount</span>

              <strong>
                $
                {Number(
                  financial.bank_amount ??
                  caseData.bank_amount ??
                  0
                ).toFixed(2)}
              </strong>

            </div>


            <div>
              <span>Outstanding Amount</span>

              <strong>
                $
                {Number(
                  financial.outstanding_amount ??
                  caseData.outstanding_amount ??
                  0
                ).toFixed(2)}
              </strong>

            </div>


            <div>
              <span>Payment Coverage</span>

              <strong>
                {Number(
                  financial.payment_coverage_percent ??
                  caseData.payment_coverage_percent ??
                  0
                ).toFixed(2)}
                %
              </strong>

            </div>


            <div>
              <span>Financial Status</span>

              <strong>
                {financial.financial_status ||
                  caseData.financial_status ||
                  "—"}
              </strong>

            </div>


            <div>
              <span>Financial Impact</span>

              <strong>
                {financial.financial_impact ||
                  caseData.financial_impact ||
                  "—"}
              </strong>

            </div>


            <div>
              <span>Payment Fee</span>

              <strong>
                $
                {Number(
                  caseData.payment_fee || 0
                ).toFixed(2)}
              </strong>

            </div>

          </div>

        </div>


        {/* ======================================================
            AI INVESTIGATION
        ====================================================== */}

        <div className="investigation-section">

          <h2>
            AI Investigation
          </h2>


          <div className="investigation-text-list">

            <div className="investigation-text-block">

              <span>Finding</span>

              <p>
                {investigation.investigation_finding ||
                  "No finding available."}
              </p>

            </div>


            <div className="investigation-text-block">

              <span>Likely Cause</span>

              <p>
                {investigation.likely_cause ||
                  "No cause identified."}
              </p>

            </div>


            <div className="investigation-text-block">

              <span>Recommended Action</span>

              <p>
                {investigation.recommended_action ||
                  "No recommendation available."}
              </p>

            </div>


            <div className="investigation-text-block">

              <span>Reasoning</span>

              <p>
                {investigation.reasoning_steps ||
                  investigation.rationale ||
                  "No reasoning available."}
              </p>

            </div>


            <div className="investigation-text-block">

              <span>Evidence Summary</span>

              <p>
                {investigation.evidence_summary ||
                  "No evidence summary available."}
              </p>

            </div>

          </div>

        </div>


        {/* ======================================================
            RISK ASSESSMENT
        ====================================================== */}

        <div className="investigation-section">

          <h2>
            Risk Assessment
          </h2>


          <div className="investigation-text-block">

            <span>Risk Reason</span>

            <p>
              {risk.risk_reason ||
                "No risk reason available."}
            </p>

          </div>

        </div>


        {/* ======================================================
            GOVERNANCE
        ====================================================== */}

        <div className="investigation-section">

          <h2>
            Governance & Review
          </h2>


          <div className="investigation-detail-grid">

            <div>
              <span>Case Status</span>

              <strong>
                {review.case_status || "PENDING_REVIEW"}
              </strong>
            </div>


            <div>
              <span>Review Status</span>

              <strong>
                {review.review_status || "PENDING"}
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

        </div>


        {/* ======================================================
            ACTIONS
        ====================================================== */}

        <div className="investigation-actions">

          <button
            className="investigation-back-button"
            onClick={() => navigate("/cases")}
          >
            ← Back to Cases
          </button>


          {risk.human_review_required && (

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