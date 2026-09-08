
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import api from "../services/api";


function formatTimestamp(timestamp) {
  if (!timestamp) {
    return "—";
  }

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}


function getActionLabel(action) {
  const labels = {
    CASE_CREATED: "Case Created",
    INVESTIGATION_STARTED: "Investigation Started",
    SUBMITTED_FOR_REVIEW: "Submitted for Review",
    HUMAN_REVIEW: "Human Review",
    CASE_APPROVED: "Case Approved",
    CASE_REJECTED: "Case Rejected",
    CASE_ESCALATED: "Case Escalated",
    CASE_RESOLVED: "Case Resolved",
    STATUS_CHANGED: "Status Changed",
  };

  return labels[action] || action || "Audit Event";
}


function getActionClass(action) {
  if (action === "CASE_APPROVED") {
    return "audit-action-approved";
  }

  if (action === "CASE_REJECTED") {
    return "audit-action-rejected";
  }

  if (action === "CASE_ESCALATED") {
    return "audit-action-escalated";
  }

  if (action === "HUMAN_REVIEW") {
    return "audit-action-review";
  }

  if (action === "CASE_CREATED") {
    return "audit-action-created";
  }

  return "audit-action-default";
}


function StatusBadge({ status }) {
  if (!status) {
    return null;
  }

  return (
    <span
      className={`audit-status-badge audit-status-${status
        .toLowerCase()
        .replaceAll("_", "-")}`}
    >
      {status.replaceAll("_", " ")}
    </span>
  );
}


function AuditEvent({ event, isLast }) {
  return (
    <div className="audit-event">

      <div className="audit-event-rail">

        <div
          className={`audit-event-dot ${getActionClass(
            event.action
          )}`}
        >
          <span />
        </div>

        {!isLast && (
          <div className="audit-event-line" />
        )}

      </div>


      <div className="audit-event-card">

        <div className="audit-event-top">

          <div>
            <span
              className={`audit-action-label ${getActionClass(
                event.action
              )}`}
            >
              {getActionLabel(event.action)}
            </span>

            <h3>
              {event.new_status
                ? event.new_status.replaceAll("_", " ")
                : "STATUS CHANGE"}
            </h3>
          </div>

          <time>
            {formatTimestamp(event.timestamp)}
          </time>

        </div>


        <div className="audit-transition">

          <div className="audit-transition-item">

            <span className="audit-field-label">
              Previous Status
            </span>

            <div>
              {event.previous_status ? (
                <StatusBadge
                  status={event.previous_status}
                />
              ) : (
                <span className="audit-muted">
                  Initial State
                </span>
              )}
            </div>

          </div>


          <div className="audit-transition-arrow">
            →
          </div>


          <div className="audit-transition-item">

            <span className="audit-field-label">
              New Status
            </span>

            <div>
              <StatusBadge
                status={event.new_status}
              />
            </div>

          </div>

        </div>


        <div className="audit-event-meta">

          <div>
            <span className="audit-field-label">
              Changed By
            </span>

            <strong>
              {event.changed_by || "—"}
            </strong>
          </div>

          <div>
            <span className="audit-field-label">
              Event ID
            </span>

            <strong>
              #{event.id}
            </strong>
          </div>

        </div>


        {event.reason && (
          <div className="audit-reason">

            <span className="audit-field-label">
              Reason
            </span>

            <p>
              {event.reason}
            </p>

          </div>
        )}

      </div>

    </div>
  );
}


function AuditTrail() {
  const [searchParams, setSearchParams] =
    useSearchParams();

  const initialCaseId =
    searchParams.get("case_id") || "CASE-0049";

  const [caseId, setCaseId] =
    useState(initialCaseId);

  const [auditData, setAuditData] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [hasSearched, setHasSearched] =
    useState(false);


  const loadAuditTrail = async (
    requestedCaseId
  ) => {
    const normalizedCaseId =
      requestedCaseId.trim().toUpperCase();

    if (!normalizedCaseId) {
      setError("Enter a valid Case ID.");
      setAuditData(null);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await api.get(
        `/api/audit/cases/${encodeURIComponent(
          normalizedCaseId
        )}`
      );

      setAuditData(response.data);

      setCaseId(normalizedCaseId);

      setSearchParams({
        case_id: normalizedCaseId,
      });

    } catch (requestError) {
      console.error(
        "Failed to load audit trail:",
        requestError
      );

      const detail =
        requestError.response?.data?.detail;

      setError(
        detail ||
          "Unable to load the audit trail."
      );

      setAuditData(null);

    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    if (initialCaseId) {
      loadAuditTrail(initialCaseId);
    }

    // Initial URL case ID only.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);


  const events = auditData?.events || [];


  const latestEvent = useMemo(() => {
    if (!events.length) {
      return null;
    }

    return events[events.length - 1];
  }, [events]);


  const handleSubmit = (event) => {
    event.preventDefault();

    setHasSearched(true);

    loadAuditTrail(caseId);
  };


  return (
    <div className="page audit-page">

      {/* ==================================================
          HEADER
          ================================================== */}

      <div className="page-header audit-page-header">

        <div>

          <div className="audit-eyebrow">
            GOVERNANCE / AUDIT
          </div>

          <h1>
            Audit Trail
          </h1>

          <p>
            Review the complete chronological record
            of decisions, lifecycle changes, and
            governance actions for a TANGLE case.
          </p>

        </div>

      </div>


      {/* ==================================================
          SEARCH
          ================================================== */}

      <section className="audit-search-card">

        <div className="audit-search-copy">

          <span className="audit-search-label">
            CASE AUDIT LOOKUP
          </span>

          <h2>
            Inspect a case history
          </h2>

          <p>
            Enter a Case ID to retrieve its
            authoritative lifecycle and audit events.
          </p>

        </div>


        <form
          className="audit-search-form"
          onSubmit={handleSubmit}
        >

          <div className="audit-input-wrapper">

            <span className="audit-input-prefix">
              #
            </span>

            <input
              type="text"
              value={caseId}
              onChange={(event) =>
                setCaseId(event.target.value)
              }
              placeholder="CASE-0049"
              aria-label="Case ID"
            />

          </div>

          <button
            type="submit"
            className="audit-search-button"
            disabled={loading}
          >
            {loading
              ? "Loading..."
              : "View Audit Trail"}
          </button>

        </form>

      </section>


      {/* ==================================================
          ERROR
          ================================================== */}

      {error && (
        <div className="audit-alert">

          <div className="audit-alert-icon">
            !
          </div>

          <div>
            <strong>
              Audit trail unavailable
            </strong>

            <p>
              {error}
            </p>
          </div>

        </div>
      )}


      {/* ==================================================
          LOADING
          ================================================== */}

      {loading && (
        <div className="audit-loading">

          <div className="audit-loading-spinner" />

          <p>
            Loading audit history...
          </p>

        </div>
      )}


      {/* ==================================================
          AUDIT RESULT
          ================================================== */}

      {!loading && auditData && (
        <>

          {/* SUMMARY */}

          <section className="audit-summary-grid">

            <div className="audit-summary-card">

              <span>
                CASE
              </span>

              <strong>
                {auditData.case_id}
              </strong>

            </div>


            <div className="audit-summary-card">

              <span>
                CURRENT STATUS
              </span>

              <strong>
                <StatusBadge
                  status={auditData.current_status}
                />
              </strong>

            </div>


            <div className="audit-summary-card">

              <span>
                AUDIT EVENTS
              </span>

              <strong>
                {auditData.total_events}
              </strong>

            </div>


            <div className="audit-summary-card">

              <span>
                LATEST ACTION
              </span>

              <strong>
                {latestEvent
                  ? getActionLabel(
                      latestEvent.action
                    )
                  : "—"}
              </strong>

            </div>

          </section>


          {/* TIMELINE */}

          <section className="audit-timeline-section">

            <div className="audit-section-header">

              <div>

                <span className="audit-section-kicker">
                  CHRONOLOGICAL RECORD
                </span>

                <h2>
                  Governance Timeline
                </h2>

              </div>

              <span className="audit-event-count">
                {events.length}{" "}
                {events.length === 1
                  ? "event"
                  : "events"}
              </span>

            </div>


            {events.length > 0 ? (
              <div className="audit-timeline">

                {events.map(
                  (event, index) => (
                    <AuditEvent
                      key={event.id}
                      event={event}
                      isLast={
                        index ===
                        events.length - 1
                      }
                    />
                  )
                )}

              </div>
            ) : (
              <div className="audit-empty">

                <h3>
                  No audit events found
                </h3>

                <p>
                  This case does not currently
                  contain lifecycle history.
                </p>

              </div>
            )}

          </section>


          {/* GOVERNANCE NOTE */}

          <section className="audit-governance-note">

            <div className="audit-governance-icon">
              ✓
            </div>

            <div>

              <strong>
                Authoritative governance record
              </strong>

              <p>
                Audit events are derived from TANGLE's
                case lifecycle history. Each transition
                records the previous status, new status,
                actor, timestamp, and reason.
              </p>

            </div>

          </section>

        </>
      )}


      {/* ==================================================
          INITIAL EMPTY STATE
          ================================================== */}

      {!loading &&
        !auditData &&
        !error &&
        !hasSearched && (
          <div className="audit-empty">

            <h3>
              Enter a Case ID
            </h3>

            <p>
              Search for a case to inspect its
              complete governance history.
            </p>

          </div>
        )}

    </div>
  );
}


export default AuditTrail;
