import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  RefreshCw,
  SlidersHorizontal,
  ChevronRight,
  FileSearch,
  AlertCircle,
} from "lucide-react";

import api from "../services/api";

function Cases() {
  const [cases, setCases] = useState([]);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [decisionFilter, setDecisionFilter] = useState("All");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  // ============================================================
  // LOAD CASES
  // ============================================================

  const loadCases = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/api/cases");

      const data = response.data;

      setCases(
        Array.isArray(data?.items)
          ? data.items
          : []
      );
    } catch (error) {
      console.error("Failed to load cases:", error);

      setError(
        "Unable to load cases. Please make sure the FastAPI backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, []);

  // ============================================================
  // FILTER OPTIONS
  // ============================================================

  const categories = useMemo(() => {
    const values = cases
      .map((item) => item.category)
      .filter(Boolean);

    return ["All", ...new Set(values)];
  }, [cases]);

  const decisions = useMemo(() => {
    const values = cases
      .map((item) => item.decision)
      .filter(Boolean);

    return ["All", ...new Set(values)];
  }, [cases]);

  // ============================================================
  // SEARCH + FILTER
  // ============================================================

  const filteredCases = useMemo(() => {
    const searchText = search.trim().toLowerCase();

    return cases.filter((item) => {
      const matchesSearch =
        !searchText ||
        item.case_id?.toLowerCase().includes(searchText) ||
        item.record_id?.toLowerCase().includes(searchText) ||
        item.invoice_id?.toLowerCase().includes(searchText) ||
        item.category?.toLowerCase().includes(searchText) ||
        item.record_type?.toLowerCase().includes(searchText) ||
        item.financial_status?.toLowerCase().includes(searchText) ||
        item.decision?.toLowerCase().includes(searchText);

      const matchesCategory =
        categoryFilter === "All" ||
        item.category === categoryFilter;

      const matchesDecision =
        decisionFilter === "All" ||
        item.decision === decisionFilter;

      return (
        matchesSearch &&
        matchesCategory &&
        matchesDecision
      );
    });
  }, [
    cases,
    search,
    categoryFilter,
    decisionFilter,
  ]);

  // ============================================================
  // HELPERS
  // ============================================================

  const getDecisionClass = (decision) => {
    const value = String(decision || "").toLowerCase();

    if (
      value.includes("reject") ||
      value.includes("critical")
    ) {
      return "tangle-case-badge tangle-case-badge-danger";
    }

    if (
      value.includes("review") ||
      value.includes("pending") ||
      value.includes("escalat")
    ) {
      return "tangle-case-badge tangle-case-badge-warning";
    }

    if (
      value.includes("approv") ||
      value.includes("resolved")
    ) {
      return "tangle-case-badge tangle-case-badge-success";
    }

    return "tangle-case-badge tangle-case-badge-neutral";
  };

  const getFinancialClass = (status) => {
    const value = String(status || "").toLowerCase();

    if (
      value.includes("overdue") ||
      value.includes("unpaid") ||
      value.includes("outstanding")
    ) {
      return "tangle-case-financial-danger";
    }

    if (
      value.includes("partial") ||
      value.includes("pending")
    ) {
      return "tangle-case-financial-warning";
    }

    if (
      value.includes("paid") ||
      value.includes("complete")
    ) {
      return "tangle-case-financial-success";
    }

    return "";
  };

  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return (
      <div className="tangle-cases-page">
        <div className="tangle-cases-loading">
          <RefreshCw
            size={20}
            className="tangle-spin"
          />
          <span>Loading TANGLE cases...</span>
        </div>
      </div>
    );
  }

  // ============================================================
  // ERROR
  // ============================================================

  if (error) {
    return (
      <div className="tangle-cases-page">
        <div className="tangle-cases-error">
          <div className="tangle-cases-error-icon">
            <AlertCircle size={22} />
          </div>

          <div>
            <h2>Unable to load cases</h2>
            <p>{error}</p>
          </div>

          <button
            className="tangle-cases-retry"
            onClick={loadCases}
          >
            <RefreshCw size={16} />
            Retry
          </button>
        </div>
      </div>
    );
  }

  // ============================================================
  // MAIN PAGE
  // ============================================================

  return (
    <div className="tangle-cases-page">

      {/* ======================================================
          PAGE HEADER
      ====================================================== */}

      <div className="tangle-cases-header">

        <div>
          <div className="tangle-cases-eyebrow">
            EXCEPTION MANAGEMENT
          </div>

          <h1>Cases</h1>

          <p>
            Review and investigate transaction anomalies
            detected by TANGLE.
          </p>
        </div>

        <button
          className="tangle-cases-refresh"
          onClick={loadCases}
        >
          <RefreshCw size={16} />
          Refresh
        </button>

      </div>

      {/* ======================================================
          SUMMARY
      ====================================================== */}

      <div className="tangle-cases-summary">

        <div className="tangle-case-summary-card">
          <div className="tangle-summary-icon blue">
            <FileSearch size={18} />
          </div>

          <div>
            <span>Total Cases</span>
            <strong>{cases.length}</strong>
          </div>
        </div>

        <div className="tangle-case-summary-card">
          <div className="tangle-summary-icon orange">
            <AlertCircle size={18} />
          </div>

          <div>
            <span>Filtered Cases</span>
            <strong>{filteredCases.length}</strong>
          </div>
        </div>

        <div className="tangle-case-summary-card">
          <div className="tangle-summary-icon purple">
            <SlidersHorizontal size={18} />
          </div>

          <div>
            <span>Categories</span>
            <strong>
              {Math.max(categories.length - 1, 0)}
            </strong>
          </div>
        </div>

      </div>

      {/* ======================================================
          FILTER BAR
      ====================================================== */}

      <div className="tangle-cases-toolbar">

        <div className="tangle-cases-search">

          <Search size={17} />

          <input
            type="text"
            placeholder="Search case, invoice, record, category..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />

          {search && (
            <button
              className="tangle-search-clear"
              onClick={() => setSearch("")}
              type="button"
            >
              Clear
            </button>
          )}

        </div>

        <div className="tangle-cases-filter">

          <SlidersHorizontal size={16} />

          <select
            value={categoryFilter}
            onChange={(event) =>
              setCategoryFilter(event.target.value)
            }
          >
            {categories.map((category) => (
              <option
                key={category}
                value={category}
              >
                {category === "All"
                  ? "All categories"
                  : category}
              </option>
            ))}
          </select>

        </div>

        <div className="tangle-cases-filter">

          <select
            value={decisionFilter}
            onChange={(event) =>
              setDecisionFilter(event.target.value)
            }
          >
            {decisions.map((decision) => (
              <option
                key={decision}
                value={decision}
              >
                {decision === "All"
                  ? "All decisions"
                  : decision}
              </option>
            ))}
          </select>

        </div>

      </div>

      {/* ======================================================
          TABLE HEADER
      ====================================================== */}

      <div className="tangle-cases-table-card">

        <div className="tangle-cases-table-header">

          <div>
            <h2>Transaction Cases</h2>

            <p>
              Showing{" "}
              <strong>{filteredCases.length}</strong>{" "}
              of{" "}
              <strong>{cases.length}</strong>{" "}
              cases
            </p>
          </div>

          <span className="tangle-live-badge">
            Live data
          </span>

        </div>

        {/* ====================================================
            TABLE
        ==================================================== */}

        <div className="tangle-cases-table-wrapper">

          <table className="tangle-cases-table">

            <thead>
              <tr>
                <th>Case</th>
                <th>Category</th>
                <th>Type</th>
                <th>Invoice</th>
                <th>Financial Status</th>
                <th>Outstanding</th>
                <th>Coverage</th>
                <th>Decision</th>
                <th></th>
              </tr>
            </thead>

            <tbody>

              {filteredCases.map((item) => (

                <tr key={item.case_id}>

                  <td>
                    <div className="tangle-case-id">
                      <span className="tangle-case-id-icon">
                        <FileSearch size={15} />
                      </span>

                      <div>
                        <strong>
                          {item.case_id}
                        </strong>

                        <small>
                          {item.record_id || "No record ID"}
                        </small>
                      </div>
                    </div>
                  </td>

                  <td>
                    <span className="tangle-category-badge">
                      {item.category || "N/A"}
                    </span>
                  </td>

                  <td>
                    <span className="tangle-muted">
                      {item.record_type || "—"}
                    </span>
                  </td>

                  <td>
                    <span className="tangle-mono">
                      {item.invoice_id || "—"}
                    </span>
                  </td>

                  <td>
                    <span
                      className={`tangle-financial-status ${getFinancialClass(
                        item.financial_status
                      )}`}
                    >
                      {item.financial_status || "—"}
                    </span>
                  </td>

                  <td>
                    <strong className="tangle-amount">
                      $
                      {Number(
                        item.outstanding_amount || 0
                      ).toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </strong>
                  </td>

                  <td>
                    {item.payment_coverage_percent !==
                      null &&
                    item.payment_coverage_percent !==
                      undefined ? (
                      <div className="tangle-coverage">
                        <div className="tangle-coverage-bar">
                          <span
                            style={{
                              width: `${Math.min(
                                Number(
                                  item.payment_coverage_percent
                                ),
                                100
                              )}%`,
                            }}
                          />
                        </div>

                        <small>
                          {Number(
                            item.payment_coverage_percent
                          ).toFixed(2)}
                          %
                        </small>
                      </div>
                    ) : (
                      <span className="tangle-muted">
                        —
                      </span>
                    )}
                  </td>

                  <td>
                    <span
                      className={getDecisionClass(
                        item.decision
                      )}
                    >
                      {item.decision || "Pending"}
                    </span>
                  </td>

                  <td>
                    <button
                      className="tangle-investigate-button"
                      onClick={() =>
                        navigate(
                          `/investigation/${item.case_id}`
                        )
                      }
                    >
                      Investigate
                      <ChevronRight size={15} />
                    </button>
                  </td>

                </tr>

              ))}

            </tbody>

          </table>

          {/* ==================================================
              EMPTY STATE
          ================================================== */}

          {filteredCases.length === 0 && (
            <div className="tangle-cases-empty">
              <FileSearch size={30} />

              <h3>No cases found</h3>

              <p>
                Try changing your search or filter
                criteria.
              </p>
            </div>
          )}

        </div>

      </div>

    </div>
  );
}

export default Cases;