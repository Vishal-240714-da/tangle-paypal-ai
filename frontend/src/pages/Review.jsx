import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";


function Review() {

  const navigate = useNavigate();

  const [reviews, setReviews] = useState([]);

  const [summary, setSummary] = useState(null);

  const [selectedCase, setSelectedCase] = useState(null);

  const [decision, setDecision] = useState("");

  const [comment, setComment] = useState("");

  const [loading, setLoading] = useState(true);

  const [submitting, setSubmitting] = useState(false);

  const [error, setError] = useState("");

  const [success, setSuccess] = useState("");


  // ============================================================
  // LOAD REVIEW DATA
  // ============================================================

  const loadReviewData = async () => {

    try {

      setLoading(true);

      setError("");

      const [
        pendingResponse,
        summaryResponse,
      ] = await Promise.all([

        api.get("/api/review/pending"),

        api.get("/api/review/summary"),

      ]);


      setReviews(
        Array.isArray(pendingResponse.data)
          ? pendingResponse.data
          : []
      );


      setSummary(
        summaryResponse.data
      );

    } catch (error) {

      console.error(
        "Failed to load review data:",
        error
      );

      setError(
        "Unable to load human review data. Please make sure the FastAPI backend is running."
      );

    } finally {

      setLoading(false);

    }

  };


  // ============================================================
  // INITIAL LOAD
  // ============================================================

  useEffect(() => {

    loadReviewData();

  }, []);


  // ============================================================
  // SELECT CASE
  // ============================================================

  const handleSelectCase = (review) => {

    setSelectedCase(review);

    setDecision("");

    setComment("");

    setError("");

    setSuccess("");

  };


  // ============================================================
  // SUBMIT REVIEW
  // ============================================================

  const handleSubmitReview = async () => {

    if (!selectedCase) {

      return;

    }


    if (!decision) {

      setError(
        "Please select APPROVE, REJECT, or ESCALATE."
      );

      return;

    }


    setSubmitting(true);

    setError("");

    setSuccess("");


    try {

      const response = await api.post(
        `/api/review/${selectedCase.case_id}`,
        {
          reviewer_decision: decision,
          reviewer_comment: comment,
        }
      );


      setSuccess(
        response.data?.message ||
        `Case ${selectedCase.case_id} successfully reviewed.`
      );


      /*
       * Refresh the queue and summary.
       */

      await loadReviewData();


      /*
       * Clear the selected case after
       * successful submission.
       */

      setSelectedCase(null);

      setDecision("");

      setComment("");

    } catch (error) {

      console.error(
        "Failed to submit review:",
        error
      );


      const message =
        error.response?.data?.detail ||
        "Unable to submit the review.";


      setError(message);

    } finally {

      setSubmitting(false);

    }

  };


  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {

    return (

      <div className="page">

        <div className="page-header">

          <h1>
            Human Review
          </h1>

          <p>
            Loading pending review cases...
          </p>

        </div>

      </div>

    );

  }


  // ============================================================
  // MAIN PAGE
  // ============================================================

  return (

    <div className="page">

      <div className="review-page">


        {/* ======================================================
            PAGE HEADER
        ====================================================== */}

        <div className="page-header">

          <h1>
            Human Review
          </h1>

          <p>
            Review AI-investigated cases and make
            governed business decisions.
          </p>

        </div>


        {/* ======================================================
            SUMMARY CARDS
        ====================================================== */}

        {summary && (

          <div className="review-summary-grid">


            <div className="review-summary-card">

              <span>
                Total Reviews
              </span>

              <strong>
                {summary.total_reviews ?? 0}
              </strong>

            </div>


            <div className="review-summary-card">

              <span>
                Pending
              </span>

              <strong>
                {summary.pending ?? 0}
              </strong>

            </div>


            <div className="review-summary-card">

              <span>
                Approved
              </span>

              <strong>
                {summary.approved ?? 0}
              </strong>

            </div>


            <div className="review-summary-card">

              <span>
                Rejected
              </span>

              <strong>
                {summary.rejected ?? 0}
              </strong>

            </div>


            <div className="review-summary-card">

              <span>
                Escalated
              </span>

              <strong>
                {summary.escalated ?? 0}
              </strong>

            </div>


          </div>

        )}


        {/* ======================================================
            ERROR
        ====================================================== */}

        {error && (

          <div className="review-message review-error">

            {error}

          </div>

        )}


        {/* ======================================================
            SUCCESS
        ====================================================== */}

        {success && (

          <div className="review-message review-success">

            {success}

          </div>

        )}


        {/* ======================================================
            REVIEW WORKSPACE
        ====================================================== */}

        <div className="review-workspace">


          {/* ====================================================
              LEFT — PENDING QUEUE
          ==================================================== */}

          <div className="review-queue">


            <div className="review-section-header">

              <div>

                <h2>
                  Pending Review
                </h2>

                <p>
                  Select a case to review.
                </p>

              </div>


              <span className="review-count">

                {reviews.length}

              </span>

            </div>


            {reviews.length === 0 ? (

              <div className="review-empty">

                <strong>
                  No pending cases
                </strong>

                <p>
                  All cases have been reviewed.
                </p>

              </div>

            ) : (

              <div className="review-case-list">

                {reviews.map((item) => (

                  <button
                    key={item.case_id}
                    type="button"
                    className={
                      selectedCase?.case_id ===
                      item.case_id
                        ? "review-case-item selected"
                        : "review-case-item"
                    }
                    onClick={() =>
                      handleSelectCase(item)
                    }
                  >


                    {/* CASE ID + RISK */}

                    <div className="review-case-top">

                      <strong>
                        {item.case_id}
                      </strong>


                      <span
                        className={
                          `review-risk-badge ${
                            String(
                              item.risk_level || ""
                            ).toLowerCase()
                          }`
                        }
                      >

                        {item.risk_level ||
                          "UNKNOWN"}

                      </span>

                    </div>


                    {/* CATEGORY + PRIORITY */}

                    <div className="review-case-middle">

                      <span>

                        {item.category ||
                          "Transaction Exception"}

                      </span>


                      <span>

                        Priority:{" "}
                        {item.priority_score ??
                          "—"}

                      </span>

                    </div>


                    {/* STATUS */}

                    <div className="review-case-bottom">

                      <span>

                        {item.case_status ||
                          "PENDING_REVIEW"}

                      </span>


                      <span>

                        {item.human_review_required
                          ? "Review Required"
                          : ""}

                      </span>

                    </div>


                  </button>

                ))}

              </div>

            )}

          </div>


          {/* ====================================================
              RIGHT — REVIEW PANEL
          ==================================================== */}

          <div className="review-panel">


            {!selectedCase ? (

              <div className="review-panel-empty">

                <div className="review-empty-icon">
                  ✓
                </div>


                <h2>
                  Select a case
                </h2>


                <p>
                  Choose a pending case from the
                  review queue to begin your analysis.
                </p>

              </div>

            ) : (

              <>


                {/* ==============================================
                    CASE HEADER
                ============================================== */}

                <div className="review-detail-header">

                  <div>

                    <span>
                      CASE
                    </span>

                    <h2>
                      {selectedCase.case_id}
                    </h2>

                  </div>


                  <button
                    type="button"
                    className="review-investigate-button"
                    onClick={() =>
                      navigate(
                        `/investigation/${selectedCase.case_id}`
                      )
                    }
                  >
                    View Investigation
                  </button>

                </div>


                {/* ==============================================
                    CASE INFORMATION
                ============================================== */}

                <div className="review-detail-grid">


                  <div>

                    <span>
                      Risk Level
                    </span>

                    <strong>
                      {selectedCase.risk_level ||
                        "—"}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Priority Score
                    </span>

                    <strong>
                      {selectedCase.priority_score ??
                        "—"}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Exception
                    </span>

                    <strong>
                      {selectedCase.category ||
                        "—"}
                    </strong>

                  </div>


                  <div>

                    <span>
                      AI Decision
                    </span>

                    <strong>
                      {selectedCase.decision ||
                        "INVESTIGATE"}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Outstanding
                    </span>

                    <strong>

                      $
                      {Number(
                        selectedCase.outstanding_amount ||
                        0
                      ).toFixed(2)}

                    </strong>

                  </div>


                  <div>

                    <span>
                      Payment Coverage
                    </span>

                    <strong>

                      {selectedCase.payment_coverage_percent !=
                      null
                        ? `${Number(
                            selectedCase.payment_coverage_percent
                          ).toFixed(2)}%`
                        : "—"}

                    </strong>

                  </div>


                </div>


                {/* ==============================================
                    AI INVESTIGATION SUMMARY
                ============================================== */}

                <div className="review-ai-box">

                  <div className="review-ai-title">

                    AI Investigation Summary

                  </div>


                  <div className="review-ai-row">

                    <span>
                      Finding
                    </span>

                    <p>

                      {selectedCase.investigation_finding ||
                        selectedCase.reason ||
                        "Review the complete investigation before making a decision."}

                    </p>

                  </div>


                  <div className="review-ai-row">

                    <span>
                      Recommended Action
                    </span>

                    <p>

                      {selectedCase.recommended_action ||
                        selectedCase.suggested_action ||
                        "See the case investigation for the AI recommendation."}

                    </p>

                  </div>

                </div>


                {/* ==============================================
                    REVIEWER DECISION
                ============================================== */}

                <div className="review-decision-section">

                  <h3>
                    Reviewer Decision
                  </h3>


                  <p>
                    The final decision is made by the
                    human reviewer, not automatically
                    by the AI.
                  </p>


                  <div className="review-decision-buttons">


                    <button
                      type="button"
                      className={
                        decision === "APPROVE"
                          ? "review-decision-button approve selected"
                          : "review-decision-button approve"
                      }
                      onClick={() =>
                        setDecision("APPROVE")
                      }
                      disabled={submitting}
                    >
                      APPROVE
                    </button>


                    <button
                      type="button"
                      className={
                        decision === "REJECT"
                          ? "review-decision-button reject selected"
                          : "review-decision-button reject"
                      }
                      onClick={() =>
                        setDecision("REJECT")
                      }
                      disabled={submitting}
                    >
                      REJECT
                    </button>


                    <button
                      type="button"
                      className={
                        decision === "ESCALATE"
                          ? "review-decision-button escalate selected"
                          : "review-decision-button escalate"
                      }
                      onClick={() =>
                        setDecision("ESCALATE")
                      }
                      disabled={submitting}
                    >
                      ESCALATE
                    </button>


                  </div>

                </div>


                {/* ==============================================
                    REVIEW COMMENT
                ============================================== */}

                <div className="review-comment-section">

                  <label htmlFor="review-comment">

                    Reviewer Comment

                  </label>


                  <textarea
                    id="review-comment"
                    value={comment}
                    onChange={(event) =>
                      setComment(event.target.value)
                    }
                    placeholder="Enter your review comments..."
                    rows={5}
                    disabled={submitting}
                  />

                </div>


                {/* ==============================================
                    SUBMIT
                ============================================== */}

                <div className="review-submit-area">

                  <button
                    type="button"
                    className="review-submit-button"
                    onClick={handleSubmitReview}
                    disabled={
                      submitting ||
                      !decision
                    }
                  >

                    {submitting
                      ? "Submitting..."
                      : "Submit Review"}

                  </button>

                </div>


              </>

            )}

          </div>


        </div>

      </div>

    </div>

  );
}


export default Review;