import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function formatCurrency(value, currency = "INR") {
  if (value === null || value === undefined) {
    return "—";
  }

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPercent(value) {
  if (value === null || value === undefined) {
    return "—";
  }

  return `${Number(value).toFixed(2)}%`;
}

function formatScore(value) {
  if (value === null || value === undefined) {
    return "—";
  }

  return Number(value).toFixed(0);
}

function formatConfidence(value) {
  if (value === null || value === undefined) {
    return "—";
  }

  return `${(Number(value) * 100).toFixed(0)}%`;
}

function parseReasoning(value) {
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

    return [String(parsed)];
  } catch {
    return String(value)
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);
  }
}

function getRiskClass(riskLevel) {
  switch (riskLevel) {
    case "CRITICAL":
      return "review-risk-critical";

    case "HIGH":
      return "review-risk-high";

    case "MEDIUM":
      return "review-risk-medium";

    case "LOW":
      return "review-risk-low";

    default:
      return "review-risk-default";
  }
}

function getCategoryLabel(category) {
  if (!category) {
    return "UNCLASSIFIED";
  }

  return category
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}

function MetricCard({
  label,
  value,
  supporting,
  emphasis = "",
}) {
  return (
    <div className={`review-metric-card ${emphasis}`}>
      <span className="review-metric-label">
        {label}
      </span>

      <strong className="review-metric-value">
        {value}
      </strong>

      {supporting && (
        <span className="review-metric-supporting">
          {supporting}
        </span>
      )}
    </div>
  );
}

function EvidenceCard({ item }) {
  return (
    <div className="review-evidence-card">
      <div className="review-evidence-top">
        <span className="review-evidence-label">
          {item.label}
        </span>

        {item.source && (
          <span className="review-evidence-source">
            {item.source}
          </span>
        )}
      </div>

      <strong className="review-evidence-value">
        {item.value}
      </strong>
    </div>
  );
}

export default function Review() {
  const navigate = useNavigate();

  const [reviews, setReviews] = useState([]);
  const [summary, setSummary] = useState(null);
  const [selectedCaseId, setSelectedCaseId] =
    useState(null);

  const [decision, setDecision] =
    useState("APPROVE");

  const [comment, setComment] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const selectedCase = useMemo(
    () =>
      reviews.find(
        (item) =>
          item.case_id === selectedCaseId,
      ) || null,
    [reviews, selectedCaseId],
  );

  const loadReviewData = async (
    preserveSelection = true,
  ) => {
    try {
      setLoading(true);
      setError("");

      const [
        pendingResponse,
        summaryResponse,
      ] = await Promise.all([
        api.get("/api/reviews/pending"),
        api.get("/api/reviews/summary"),
      ]);

      const pending =
        Array.isArray(pendingResponse.data)
          ? pendingResponse.data
          : [];

      setReviews(pending);
      setSummary(summaryResponse.data);

      if (pending.length === 0) {
        setSelectedCaseId(null);
        return;
      }

      if (
        preserveSelection &&
        selectedCaseId &&
        pending.some(
          (item) =>
            item.case_id === selectedCaseId,
        )
      ) {
        return;
      }

      setSelectedCaseId(
        pending[0].case_id,
      );
    } catch (requestError) {
      console.error(
        "Failed to load review data:",
        requestError,
      );

      setError(
        requestError.response?.data?.detail ||
          "Unable to load human review data.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReviewData(false);
  }, []);

  useEffect(() => {
    if (!selectedCase) {
      return;
    }

    setDecision(
      selectedCase.reviewer_decision ||
        "APPROVE",
    );

    setComment(
      selectedCase.reviewer_comment ||
        "",
    );

    setSuccess("");
  }, [selectedCaseId]);

  const handleSubmit = async () => {
    if (!selectedCase) {
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      setSuccess("");

      const response = await api.post(
        `/api/reviews/${selectedCase.case_id}`,
        {
          reviewer_decision: decision,
          reviewer_comment: comment,
        },
      );

      const result = response.data;

      setSuccess(
        `Decision recorded successfully for ${result.case_id}.`,
      );

      await loadReviewData(false);
    } catch (requestError) {
      console.error(
        "Failed to submit review:",
        requestError,
      );

      setError(
        requestError.response?.data?.detail ||
          "Unable to submit the review.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="review-page">
        <div className="review-loading">
          <div className="review-loading-spinner" />
          <p>Loading human review workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="review-page">
      {/* ------------------------------------------------ */}
      {/* HEADER                                           */}
      {/* ------------------------------------------------ */}

      <div className="review-page-header">
        <div>
          <div className="review-eyebrow">
            GOVERNANCE / HUMAN REVIEW
          </div>

          <h1>Human Review Workspace</h1>

          <p>
            Review AI-detected exceptions, inspect
            supporting evidence, and record the
            final human decision.
          </p>
        </div>

        <button
          type="button"
          className="review-refresh-button"
          onClick={() =>
            loadReviewData(false)
          }
        >
          Refresh Queue
        </button>
      </div>

      {/* ------------------------------------------------ */}
      {/* SUMMARY                                          */}
      {/* ------------------------------------------------ */}

      <div className="review-summary-grid">
        <MetricCard
          label="Pending Review"
          value={summary?.pending ?? 0}
          supporting="Cases awaiting analyst action"
          emphasis="review-metric-primary"
        />

        <MetricCard
          label="Completed"
          value={summary?.completed ?? 0}
          supporting="Human decisions recorded"
        />

        <MetricCard
          label="Approved"
          value={summary?.approved ?? 0}
          supporting="Cases approved by reviewers"
        />

        <MetricCard
          label="Escalated"
          value={summary?.escalated ?? 0}
          supporting="Cases requiring deeper review"
        />
      </div>

      {/* ------------------------------------------------ */}
      {/* ALERTS                                           */}
      {/* ------------------------------------------------ */}

      {error && (
        <div className="review-alert review-alert-error">
          <strong>Review Error</strong>
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="review-alert review-alert-success">
          <strong>Decision Recorded</strong>
          <span>{success}</span>
        </div>
      )}

      {/* ------------------------------------------------ */}
      {/* EMPTY STATE                                      */}
      {/* ------------------------------------------------ */}

      {reviews.length === 0 ? (
        <div className="review-empty-state">
          <div className="review-empty-icon">
            ✓
          </div>

          <h2>Review queue is clear</h2>

          <p>
            There are currently no cases waiting
            for human review.
          </p>
        </div>
      ) : (
        <div className="review-workspace">
          {/* -------------------------------------------- */}
          {/* QUEUE                                        */}
          {/* -------------------------------------------- */}

          <aside className="review-queue-panel">
            <div className="review-panel-header">
              <div>
                <span className="review-panel-kicker">
                  PRIORITIZED QUEUE
                </span>

                <h2>Cases</h2>
              </div>

              <span className="review-queue-count">
                {reviews.length}
              </span>
            </div>

            <div className="review-queue-list">
              {reviews.map((item) => (
                <button
                  type="button"
                  key={item.case_id}
                  className={`review-queue-item ${
                    selectedCaseId ===
                    item.case_id
                      ? "active"
                      : ""
                  }`}
                  onClick={() => {
                    setSelectedCaseId(
                      item.case_id,
                    );
                    setError("");
                    setSuccess("");
                  }}
                >
                  <div className="review-queue-item-top">
                    <strong>
                      {item.case_id}
                    </strong>

                    <span
                      className={`review-risk-badge ${getRiskClass(
                        item.risk_level,
                      )}`}
                    >
                      {item.risk_level ||
                        "UNKNOWN"}
                    </span>
                  </div>

                  <div className="review-queue-category">
                    {getCategoryLabel(
                      item.category,
                    )}
                  </div>

                  <div className="review-queue-meta">
                    <span>
                      Priority{" "}
                      <strong>
                        {formatScore(
                          item.priority_score,
                        )}
                      </strong>
                    </span>

                    <span>
                      {item.record_id ||
                        "No record ID"}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </aside>

          {/* -------------------------------------------- */}
          {/* CASE DETAIL                                  */}
          {/* -------------------------------------------- */}

          {selectedCase && (
            <main className="review-detail-panel">
              {/* CASE HEADER */}

              <div className="review-case-header">
                <div>
                  <div className="review-case-id">
                    {selectedCase.case_id}
                  </div>

                  <h2>
                    {getCategoryLabel(
                      selectedCase.category,
                    )}
                  </h2>

                  <p>
                    {selectedCase.record_type ||
                      "Record"}{" "}
                    ·{" "}
                    {selectedCase.record_id ||
                      "Unknown record"}
                  </p>
                </div>

                <div className="review-case-status">
                  <span
                    className={`review-risk-badge ${getRiskClass(
                      selectedCase.risk_level,
                    )}`}
                  >
                    {selectedCase.risk_level}
                  </span>

                  <span className="review-status-badge">
                    {selectedCase.case_status}
                  </span>
                </div>
              </div>

              {/* CASE INFORMATION */}

              <section className="review-section">
                <div className="review-section-heading">
                  <div>
                    <span className="review-section-kicker">
                      CASE CONTEXT
                    </span>

                    <h3>
                      Case Information
                    </h3>
                  </div>
                </div>

                <div className="review-info-grid">
                  <div className="review-info-item">
                    <span>Invoice ID</span>
                    <strong>
                      {selectedCase.invoice_id ||
                        "—"}
                    </strong>
                  </div>

                  <div className="review-info-item">
                    <span>Payment ID</span>
                    <strong>
                      {selectedCase.payment_id ||
                        "—"}
                    </strong>
                  </div>

                  <div className="review-info-item">
                    <span>Record Type</span>
                    <strong>
                      {selectedCase.record_type ||
                        "—"}
                    </strong>
                  </div>

                  <div className="review-info-item">
                    <span>Record ID</span>
                    <strong>
                      {selectedCase.record_id ||
                        "—"}
                    </strong>
                  </div>

                  <div className="review-info-item">
                    <span>AI Decision</span>
                    <strong>
                      {selectedCase.decision ||
                        "—"}
                    </strong>
                  </div>

                  <div className="review-info-item">
                    <span>AI Confidence</span>
                    <strong>
                      {formatConfidence(
                        selectedCase.decision_confidence,
                      )}
                    </strong>
                  </div>
                </div>
              </section>

              {/* FINANCIAL IMPACT */}

              <section className="review-section">
                <div className="review-section-heading">
                  <div>
                    <span className="review-section-kicker">
                      FINANCIAL ANALYSIS
                    </span>

                    <h3>
                      Financial Impact
                    </h3>
                  </div>

                  <span className="review-financial-status">
                    {selectedCase.financial_status ||
                      "UNKNOWN"}
                  </span>
                </div>

                <div className="review-metrics-detail">
                  <MetricCard
                    label="Invoice Amount"
                    value={formatCurrency(
                      selectedCase.invoice_amount,
                      selectedCase.currency,
                    )}
                  />

                  <MetricCard
                    label="Payment Amount"
                    value={formatCurrency(
                      selectedCase.payment_amount,
                      selectedCase.currency,
                    )}
                  />

                  <MetricCard
                    label="Bank Amount"
                    value={formatCurrency(
                      selectedCase.bank_amount,
                      selectedCase.currency,
                    )}
                  />

                  <MetricCard
                    label="Outstanding"
                    value={formatCurrency(
                      selectedCase.outstanding_amount,
                      selectedCase.currency,
                    )}
                    emphasis={
                      selectedCase.outstanding_amount >
                      0
                        ? "review-metric-warning"
                        : ""
                    }
                  />

                  <MetricCard
                    label="Payment Coverage"
                    value={formatPercent(
                      selectedCase.payment_coverage_percent,
                    )}
                  />

                  <MetricCard
                    label="Priority"
                    value={formatScore(
                      selectedCase.priority_score,
                    )}
                    supporting="Risk prioritization score"
                  />
                </div>

                {selectedCase.financial_impact && (
                  <div className="review-impact-callout">
                    <span>
                      Financial Impact
                    </span>

                    <strong>
                      {selectedCase.financial_impact.replaceAll(
                        "_",
                        " ",
                      )}
                    </strong>
                  </div>
                )}
              </section>

              {/* AI INVESTIGATION */}

              <section className="review-section review-ai-section">
                <div className="review-section-heading">
                  <div>
                    <span className="review-section-kicker">
                      EXPLAINABLE AI
                    </span>

                    <h3>
                      Investigation
                    </h3>
                  </div>

                  <div className="review-confidence">
                    <span>
                      AI Confidence
                    </span>

                    <strong>
                      {formatConfidence(
                        selectedCase.investigation_confidence,
                      )}
                    </strong>
                  </div>
                </div>

                {selectedCase.investigation_finding && (
                  <div className="review-ai-finding">
                    <span className="review-ai-label">
                      FINDING
                    </span>

                    <p>
                      {
                        selectedCase.investigation_finding
                      }
                    </p>
                  </div>
                )}

                <div className="review-ai-grid">
                  <div className="review-ai-card">
                    <span className="review-ai-label">
                      LIKELY CAUSE
                    </span>

                    <p>
                      {selectedCase.likely_cause ||
                        "No cause identified."}
                    </p>
                  </div>

                  <div className="review-ai-card">
                    <span className="review-ai-label">
                      RECOMMENDED ACTION
                    </span>

                    <p>
                      {selectedCase.recommended_action ||
                        "No recommendation available."}
                    </p>
                  </div>
                </div>

                {/* EVIDENCE */}

                <div className="review-evidence-section">
                  <div className="review-subheading">
                    <h4>
                      Evidence
                    </h4>

                    <span>
                      {selectedCase.evidence
                        ?.length || 0}{" "}
                      signals
                    </span>
                  </div>

                  <div className="review-evidence-grid">
                    {(
                      selectedCase.evidence ||
                      []
                    ).map(
                      (item, index) => (
                        <EvidenceCard
                          key={`${item.label}-${index}`}
                          item={item}
                        />
                      ),
                    )}
                  </div>
                </div>

                {/* REASONING */}

                {selectedCase.reasoning_steps && (
                  <div className="review-reasoning">
                    <div className="review-subheading">
                      <h4>
                        Investigation Reasoning
                      </h4>
                    </div>

                    <ol>
                      {parseReasoning(
                        selectedCase.reasoning_steps,
                      ).map(
                        (step, index) => (
                          <li
                            key={`${step}-${index}`}
                          >
                            <span>
                              {index + 1}
                            </span>

                            <p>{step}</p>
                          </li>
                        ),
                      )}
                    </ol>
                  </div>
                )}

                <button
                  type="button"
                  className="review-investigation-button"
                  onClick={() =>
                    navigate(
                      `/investigation/${selectedCase.case_id}`,
                    )
                  }
                >
                  Open Full Investigation
                  <span>→</span>
                </button>
              </section>

              {/* HUMAN DECISION */}

              <section className="review-decision-section">
                <div className="review-section-heading">
                  <div>
                    <span className="review-section-kicker">
                      HUMAN GOVERNANCE
                    </span>

                    <h3>
                      Final Decision
                    </h3>

                    <p>
                      AI provides the recommendation.
                      The analyst owns the final
                      decision.
                    </p>
                  </div>
                </div>

                <div className="review-decision-options">
                  <button
                    type="button"
                    className={`review-decision-option approve ${
                      decision === "APPROVE"
                        ? "selected"
                        : ""
                    }`}
                    onClick={() =>
                      setDecision("APPROVE")
                    }
                    disabled={submitting}
                  >
                    <span className="review-decision-icon">
                      ✓
                    </span>

                    <span>
                      <strong>
                        Approve
                      </strong>

                      <small>
                        Accept the case resolution
                      </small>
                    </span>
                  </button>

                  <button
                    type="button"
                    className={`review-decision-option reject ${
                      decision === "REJECT"
                        ? "selected"
                        : ""
                    }`}
                    onClick={() =>
                      setDecision("REJECT")
                    }
                    disabled={submitting}
                  >
                    <span className="review-decision-icon">
                      ×
                    </span>

                    <span>
                      <strong>
                        Reject
                      </strong>

                      <small>
                        Reject the AI resolution
                      </small>
                    </span>
                  </button>

                  <button
                    type="button"
                    className={`review-decision-option escalate ${
                      decision === "ESCALATE"
                        ? "selected"
                        : ""
                    }`}
                    onClick={() =>
                      setDecision("ESCALATE")
                    }
                    disabled={submitting}
                  >
                    <span className="review-decision-icon">
                      ↗
                    </span>

                    <span>
                      <strong>
                        Escalate
                      </strong>

                      <small>
                        Send for deeper investigation
                      </small>
                    </span>
                  </button>
                </div>

                <div className="review-comment-area">
                  <label htmlFor="review-comment">
                    Analyst Comment
                  </label>

                  <textarea
                    id="review-comment"
                    value={comment}
                    onChange={(event) =>
                      setComment(
                        event.target.value,
                      )
                    }
                    placeholder="Document why this decision was made..."
                    maxLength={2000}
                    disabled={submitting}
                  />

                  <div className="review-comment-footer">
                    <span>
                      {comment.length} / 2000
                    </span>
                  </div>
                </div>

                <div className="review-submit-row">
                  <div>
                    <span className="review-submit-label">
                      SELECTED DECISION
                    </span>

                    <strong>
                      {decision}
                    </strong>
                  </div>

                  <button
                    type="button"
                    className="review-submit-button"
                    onClick={handleSubmit}
                    disabled={submitting}
                  >
                    {submitting
                      ? "Recording Decision..."
                      : "Submit Human Decision"}

                    {!submitting && (
                      <span>→</span>
                    )}
                  </button>
                </div>
              </section>
            </main>
          )}
        </div>
      )}
    </div>
  );
}