import { useEffect, useMemo, useState } from "react";
import api from "../services/api";

function DataQuality() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadDataQuality = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const response = await api.get("/api/data-quality");

      setData(response.data);
    } catch (err) {
      console.error("Data quality request failed:", err);

      setError(
        "Unable to load data quality information. Please make sure the FastAPI backend is running."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDataQuality();
  }, []);

  const checkRows = useMemo(() => {
    if (!data) {
      return [];
    }

    const summary = data.issue_summary || {};

    return [
      {
        name: "Duplicate Records",
        key: "DUPLICATE_RECORD",
      },
      {
        name: "Missing IDs",
        key: "MISSING_ID",
      },
      {
        name: "Invalid Amounts",
        key: "INVALID_AMOUNT",
      },
      {
        name: "Invalid Dates",
        key: "INVALID_DATE",
      },
      {
        name: "Missing Relationships",
        key: "MISSING_RELATIONSHIP",
      },
      {
        name: "Negative Values",
        key: "NEGATIVE_VALUE",
      },
      {
        name: "Currency Problems",
        key: "CURRENCY_PROBLEM",
      },
      {
        name: "Malformed Records",
        key: "MALFORMED_RECORD",
      },
    ].map((check) => ({
      ...check,
      count: summary[check.key] || 0,
    }));
  }, [data]);

  const qualityClass = useMemo(() => {
    if (!data) {
      return "";
    }

    if (data.quality_score >= 95) {
      return "excellent";
    }

    if (data.quality_score >= 80) {
      return "good";
    }

    if (data.quality_score >= 60) {
      return "warning";
    }

    return "critical";
  }, [data]);

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Data Quality</h1>
          <p>
            Validate incoming financial data before reconciliation.
          </p>
        </div>

        <div className="dq-loading">
          Running data quality checks...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Data Quality</h1>
          <p>
            Validate incoming financial data before reconciliation.
          </p>
        </div>

        <div className="dq-message dq-error">
          {error}
        </div>

        <button
          className="dq-refresh-button"
          onClick={() => loadDataQuality(true)}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="page data-quality-page">

      {/* ==================================================
          HEADER
      ================================================== */}

      <div className="dq-header">

        <div className="page-header">
          <div className="dq-eyebrow">
            TANGLE CONTROL LAYER
          </div>

          <h1>Data Quality</h1>

          <p>
            Validate incoming financial data before it reaches
            reconciliation and exception processing.
          </p>
        </div>

        <button
          className="dq-refresh-button"
          onClick={() => loadDataQuality(true)}
          disabled={refreshing}
        >
          {refreshing ? "Checking..." : "Refresh Check"}
        </button>

      </div>


      {/* ==================================================
          QUALITY HERO
      ================================================== */}

      <section className="dq-quality-hero">

        <div className="dq-score-block">

          <div className={`dq-score ${qualityClass}`}>
            {data.quality_score.toFixed(1)}%
          </div>

          <div>
            <div className="dq-score-label">
              DATA QUALITY
            </div>

            <div className="dq-score-description">
              Overall quality of incoming financial records
            </div>
          </div>

        </div>

        <div className="dq-quality-bar">

          <div
            className={`dq-quality-fill ${qualityClass}`}
            style={{
              width: `${Math.min(
                Math.max(data.quality_score, 0),
                100
              )}%`,
            }}
          />

        </div>

      </section>


      {/* ==================================================
          KPI CARDS
      ================================================== */}

      <section className="dq-kpi-grid">

        <div className="dq-kpi-card">
          <span>Total Records</span>
          <strong>
            {data.total_records}
          </strong>
          <small>
            Incoming records scanned
          </small>
        </div>

        <div className="dq-kpi-card valid">
          <span>Valid Records</span>
          <strong>
            {data.valid_records}
          </strong>
          <small>
            Passed quality validation
          </small>
        </div>

        <div className="dq-kpi-card warning">
          <span>Warnings</span>
          <strong>
            {data.warnings}
          </strong>
          <small>
            Require attention
          </small>
        </div>

        <div className="dq-kpi-card error">
          <span>Errors</span>
          <strong>
            {data.errors}
          </strong>
          <small>
            Blocking data problems
          </small>
        </div>

      </section>


      {/* ==================================================
          QUALITY CHECKS
      ================================================== */}

      <section className="dq-section">

        <div className="dq-section-header">
          <div>
            <h2>Quality Checks</h2>
            <p>
              Validation rules applied to incoming data.
            </p>
          </div>
        </div>

        <div className="dq-check-grid">

          {checkRows.map((check) => {

            const passed = check.count === 0;

            return (
              <div
                className={`dq-check-row ${
                  passed ? "passed" : "flagged"
                }`}
                key={check.key}
              >

                <div className="dq-check-icon">
                  {passed ? "✓" : "!"}
                </div>

                <div className="dq-check-content">

                  <strong>
                    {check.name}
                  </strong>

                  <span>
                    {passed
                      ? "No issues detected"
                      : `${check.count} issue${
                          check.count === 1 ? "" : "s"
                        } detected`}
                  </span>

                </div>

                <div
                  className={`dq-check-status ${
                    passed ? "pass" : "warning"
                  }`}
                >
                  {passed ? "PASS" : "REVIEW"}
                </div>

              </div>
            );

          })}

        </div>

      </section>


      {/* ==================================================
          DATASETS
      ================================================== */}

      <section className="dq-section">

        <div className="dq-section-header">
          <div>
            <h2>Source Datasets</h2>
            <p>
              Record-level quality status by incoming dataset.
            </p>
          </div>
        </div>

        <div className="dq-dataset-grid">

          {Object.entries(data.datasets || {}).map(
            ([datasetName, dataset]) => {

              const datasetQuality =
                dataset.total_records > 0
                  ? (
                      dataset.valid_records /
                      dataset.total_records
                    ) * 100
                  : 100;

              return (
                <div
                  className="dq-dataset-card"
                  key={datasetName}
                >

                  <div className="dq-dataset-top">

                    <div>
                      <span className="dq-dataset-label">
                        SOURCE
                      </span>

                      <h3>
                        {datasetName
                          .replaceAll("_", " ")
                          .replace(/\b\w/g, (letter) =>
                            letter.toUpperCase()
                          )}
                      </h3>
                    </div>

                    <strong>
                      {datasetQuality.toFixed(1)}%
                    </strong>

                  </div>

                  <div className="dq-mini-bar">
                    <div
                      style={{
                        width: `${datasetQuality}%`,
                      }}
                    />
                  </div>

                  <div className="dq-dataset-stats">

                    <span>
                      <strong>
                        {dataset.valid_records}
                      </strong>{" "}
                      valid
                    </span>

                    <span>
                      {dataset.total_records} total
                    </span>

                    <span>
                      {dataset.warnings} warnings
                    </span>

                    <span>
                      {dataset.errors} errors
                    </span>

                  </div>

                </div>
              );
            }
          )}

        </div>

      </section>


      {/* ==================================================
          DETECTED ISSUES
      ================================================== */}

      <section className="dq-section">

        <div className="dq-section-header">
          <div>
            <h2>Detected Issues</h2>
            <p>
              Problems identified during the latest quality scan.
            </p>
          </div>

          <span className="dq-issue-count">
            {data.issues.length} issue
            {data.issues.length === 1 ? "" : "s"}
          </span>
        </div>

        {data.issues.length === 0 ? (

          <div className="dq-empty">
            <div className="dq-empty-icon">
              ✓
            </div>

            <strong>
              No data quality issues detected
            </strong>

            <p>
              All incoming records passed the current
              validation rules.
            </p>
          </div>

        ) : (

          <div className="dq-issues-table">

            <div className="dq-issue-header">
              <span>Severity</span>
              <span>Dataset</span>
              <span>Record</span>
              <span>Issue</span>
              <span>Details</span>
            </div>

            {data.issues.map((issue, index) => (

              <div
                className="dq-issue-row"
                key={`${issue.dataset}-${issue.record_id}-${index}`}
              >

                <span>
                  <span
                    className={`dq-severity ${issue.severity.toLowerCase()}`}
                  >
                    {issue.severity}
                  </span>
                </span>

                <strong>
                  {issue.dataset}
                </strong>

                <span className="dq-record-id">
                  {issue.record_id || "—"}
                </span>

                <span>
                  {issue.issue_type
                    .replaceAll("_", " ")}
                </span>

                <span className="dq-issue-message">
                  {issue.message}
                </span>

              </div>

            ))}

          </div>

        )}

      </section>


      {/* ==================================================
          MILESTONE
      ================================================== */}

      <section className="dq-milestone">

        <div className="dq-milestone-icon">
          ✓
        </div>

        <div>

          <div className="dq-milestone-label">
            PHASE 5 MILESTONE
          </div>

          <h2>
            TANGLE doesn't blindly trust incoming
            financial data.
          </h2>

          <p>
            Every incoming record is validated before
            reconciliation and downstream exception processing.
          </p>

        </div>

      </section>

    </div>
  );
}

export default DataQuality;