import {
  useEffect,
  useMemo,
  useState,
} from "react";

import api from "../services/api";

function Reconciliation() {
  const [items, setItems] = useState([]);

  const [summary, setSummary] = useState({
    total: 0,
    exact: 0,
    fuzzy: 0,
    merged_payment: 0,
    failed: 0,
    average_confidence: 0,
  });

  const [filter, setFilter] = useState("ALL");

  const [search, setSearch] = useState("");

  const [currentPage, setCurrentPage] = useState(1);

  const [selectedItem, setSelectedItem] =
    useState(null);

  const pageSize = 15;

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  useEffect(() => {
    async function loadReconciliation() {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(
          "/api/reconciliation"
        );

        setItems(
          Array.isArray(response.data?.items)
            ? response.data.items
            : []
        );

        if (response.data?.summary) {
          setSummary(response.data.summary);
        }
      } catch (err) {
        console.error(
          "Failed to load reconciliation:",
          err
        );

        setError(
          "Unable to load reconciliation data."
        );
      } finally {
        setLoading(false);
      }
    }

    loadReconciliation();
  }, []);

  const filteredItems = useMemo(() => {
    const normalizedSearch =
      search.trim().toLowerCase();

    return items.filter((item) => {
      const matchesFilter =
        filter === "ALL" ||
        item.match_type === filter;

      if (!matchesFilter) {
        return false;
      }

      if (!normalizedSearch) {
        return true;
      }

      return [
        item.invoice_id,
        item.payment_id,
        item.bank_transaction_id,
      ].some((value) =>
        String(value || "")
          .toLowerCase()
          .includes(normalizedSearch)
      );
    });
  }, [items, filter, search]);

  const totalPages = Math.max(
    1,
    Math.ceil(
      filteredItems.length / pageSize
    )
  );

  const paginatedItems = useMemo(() => {
    const startIndex =
      (currentPage - 1) * pageSize;

    return filteredItems.slice(
      startIndex,
      startIndex + pageSize
    );
  }, [
    filteredItems,
    currentPage,
    pageSize,
  ]);

  useEffect(() => {
    setCurrentPage(1);
  }, [filter, search]);

  function formatConfidence(value) {
    return `${(
      Number(value || 0) * 100
    ).toFixed(1)}%`;
  }

  function formatAmount(
    amount,
    currency
  ) {
    if (
      amount === null ||
      amount === undefined
    ) {
      return "—";
    }

    return `${currency || ""} ${Number(
      amount
    ).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    })}`;
  }

  function formatDifference(
    amount,
    currency
  ) {
    if (
      amount === null ||
      amount === undefined
    ) {
      return "—";
    }

    const numericAmount = Number(amount);

    const formatted = Math.abs(
      numericAmount
    ).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    });

    if (numericAmount === 0) {
      return `${currency || ""} 0.00`;
    }

    return numericAmount > 0
      ? `+${currency || ""} ${formatted}`
      : `-${currency || ""} ${formatted}`;
  }

  function getMatchClass(matchType) {
    if (matchType === "EXACT") {
      return "reconciliation-match exact";
    }

    if (matchType === "FUZZY") {
      return "reconciliation-match fuzzy";
    }

    if (
      matchType === "MERGED_PAYMENT"
    ) {
      return "reconciliation-match merged";
    }

    return "reconciliation-match";
  }

  function getDetailMatchClass(
    matchType
  ) {
    if (matchType === "EXACT") {
      return "reconciliation-detail-match exact";
    }

    if (matchType === "FUZZY") {
      return "reconciliation-detail-match fuzzy";
    }

    return "reconciliation-detail-match merged";
  }

  function goToPreviousPage() {
    setCurrentPage((page) =>
      Math.max(1, page - 1)
    );
  }

  function goToNextPage() {
    setCurrentPage((page) =>
      Math.min(totalPages, page + 1)
    );
  }

  function openDetails(item) {
    setSelectedItem(item);
  }

  function closeDetails() {
    setSelectedItem(null);
  }

  const firstVisibleRecord =
    filteredItems.length === 0
      ? 0
      : (currentPage - 1) *
          pageSize +
        1;

  const lastVisibleRecord =
    Math.min(
      currentPage * pageSize,
      filteredItems.length
    );

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Reconciliation</h1>

          <p>
            Match invoices, payments and bank
            transactions with confidence and
            evidence.
          </p>
        </div>
      </div>

      {error && (
        <div className="reconciliation-error">
          {error}
        </div>
      )}

      <div className="reconciliation-summary">
        <div className="reconciliation-stat">
          <span className="stat-label">
            Total Records
          </span>

          <strong>
            {summary.total}
          </strong>
        </div>

        <div className="reconciliation-stat">
          <span className="stat-label">
            Exact
          </span>

          <strong>
            {summary.exact}
          </strong>
        </div>

        <div className="reconciliation-stat">
          <span className="stat-label">
            Fuzzy
          </span>

          <strong>
            {summary.fuzzy}
          </strong>
        </div>

        <div className="reconciliation-stat">
          <span className="stat-label">
            Merged Payment
          </span>

          <strong>
            {summary.merged_payment}
          </strong>
        </div>

        <div className="reconciliation-stat">
          <span className="stat-label">
            Avg Confidence
          </span>

          <strong>
            {formatConfidence(
              summary.average_confidence
            )}
          </strong>
        </div>
      </div>

      <div className="reconciliation-toolbar">
        <div className="reconciliation-search">
          <input
            type="text"
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
            placeholder="Search invoice, payment or bank..."
            aria-label="Search reconciliation records"
          />
        </div>

        <div className="reconciliation-filters">
          {[
            ["ALL", "All"],
            ["EXACT", "Exact"],
            ["FUZZY", "Fuzzy"],
            [
              "MERGED_PAYMENT",
              "Merged Payment",
            ],
          ].map(
            ([value, label]) => (
              <button
                key={value}
                type="button"
                className={
                  filter === value
                    ? "reconciliation-filter active"
                    : "reconciliation-filter"
                }
                onClick={() => {
                  setFilter(value);
                }}
              >
                {label}
              </button>
            )
          )}
        </div>

        <span className="reconciliation-count">
          Showing{" "}
          {firstVisibleRecord}
          –
          {lastVisibleRecord}{" "}
          of{" "}
          {filteredItems.length}
        </span>
      </div>

      <div className="reconciliation-table-card">
        {loading ? (
          <div className="reconciliation-state">
            Loading reconciliation data...
          </div>
        ) : filteredItems.length ===
          0 ? (
          <div className="reconciliation-state">
            No reconciliation records
            found.
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="reconciliation-table">
              <thead>
                <tr>
                  <th>Invoice</th>

                  <th>Payment</th>

                  <th>
                    Bank Transaction
                  </th>

                  <th>
                    Invoice Amount
                  </th>

                  <th>
                    Payment Amount
                  </th>

                  <th>
                    Bank Amount
                  </th>

                  <th>Match</th>

                  <th>
                    Confidence
                  </th>

                  <th>
                    Rationale
                  </th>
                </tr>
              </thead>

              <tbody>
                {paginatedItems.map(
                  (item, index) => (
                    <tr
                      key={`${item.invoice_id}-${item.payment_id}-${item.bank_transaction_id}-${(currentPage - 1) * pageSize + index}`}
                      className="reconciliation-row"
                      onClick={() =>
                        openDetails(item)
                      }
                      tabIndex={0}
                      onKeyDown={(event) => {
                        if (
                          event.key ===
                          "Enter"
                        ) {
                          openDetails(item);
                        }
                      }}
                    >
                      <td>
                        <strong>
                          {item.invoice_id ||
                            "—"}
                        </strong>
                      </td>

                      <td>
                        {item.payment_id ||
                          "—"}
                      </td>

                      <td>
                        {item.bank_transaction_id ||
                          "—"}
                      </td>

                      <td>
                        {formatAmount(
                          item.invoice_amount,
                          item.invoice_currency
                        )}
                      </td>

                      <td>
                        {formatAmount(
                          item.payment_amount,
                          item.payment_currency
                        )}
                      </td>

                      <td>
                        {formatAmount(
                          item.bank_amount,
                          item.bank_currency
                        )}
                      </td>

                      <td>
                        <span
                          className={getMatchClass(
                            item.match_type
                          )}
                        >
                          {item.match_type}
                        </span>
                      </td>

                      <td>
                        <div className="confidence-cell">
                          <span>
                            {formatConfidence(
                              item.confidence
                            )}
                          </span>

                          <div className="confidence-bar">
                            <div
                              className="confidence-fill"
                              style={{
                                width: `${Math.min(
                                  Number(
                                    item.confidence ||
                                      0
                                  ) * 100,
                                  100
                                )}%`,
                              }}
                            />
                          </div>
                        </div>
                      </td>

                      <td className="rationale-cell">
                        {item.rationale ||
                          "—"}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        )}

        {!loading &&
          filteredItems.length > 0 && (
            <div className="reconciliation-pagination">
              <button
                type="button"
                disabled={
                  currentPage === 1
                }
                onClick={
                  goToPreviousPage
                }
              >
                Previous
              </button>

              <span>
                Page{" "}
                {currentPage} of{" "}
                {totalPages}
              </span>

              <button
                type="button"
                disabled={
                  currentPage ===
                  totalPages
                }
                onClick={
                  goToNextPage
                }
              >
                Next
              </button>
            </div>
          )}
      </div>

      {selectedItem && (
        <div
          className="reconciliation-overlay"
          onClick={closeDetails}
        >
          <div
            className="reconciliation-detail-panel"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="reconciliation-detail-header">
              <div>
                <span className="detail-eyebrow">
                  RECONCILIATION DETAILS
                </span>

                <h2>
                  {selectedItem.invoice_id ||
                    "Reconciliation Record"}
                </h2>
              </div>

              <button
                type="button"
                className="detail-close-button"
                onClick={closeDetails}
                aria-label="Close details"
              >
                ×
              </button>
            </div>

            <div className="reconciliation-detail-match-section">
              <div>
                <span className="detail-label">
                  MATCH TYPE
                </span>

                <span
                  className={getDetailMatchClass(
                    selectedItem.match_type
                  )}
                >
                  {selectedItem.match_type}
                </span>
              </div>

              <div className="detail-confidence">
                <span className="detail-label">
                  CONFIDENCE
                </span>

                <strong>
                  {formatConfidence(
                    selectedItem.confidence
                  )}
                </strong>

                <div className="detail-confidence-bar">
                  <div
                    style={{
                      width: `${Math.min(
                        Number(
                          selectedItem.confidence ||
                            0
                        ) * 100,
                        100
                      )}%`,
                    }}
                  />
                </div>
              </div>
            </div>

            <div className="reconciliation-flow">
              <div className="reconciliation-flow-card">
                <span className="flow-step">
                  01
                </span>

                <div>
                  <span className="flow-type">
                    INVOICE
                  </span>

                  <strong>
                    {selectedItem.invoice_id ||
                      "—"}
                  </strong>

                  <span>
                    {formatAmount(
                      selectedItem.invoice_amount,
                      selectedItem.invoice_currency
                    )}
                  </span>

                  <small>
                    Date:{" "}
                    {selectedItem.invoice_date ||
                      "—"}
                  </small>
                </div>
              </div>

              <div className="reconciliation-flow-arrow">
                ↓
              </div>

              <div className="reconciliation-flow-card">
                <span className="flow-step">
                  02
                </span>

                <div>
                  <span className="flow-type">
                    PAYMENT
                  </span>

                  <strong>
                    {selectedItem.payment_id ||
                      "—"}
                  </strong>

                  <span>
                    {formatAmount(
                      selectedItem.payment_amount,
                      selectedItem.payment_currency
                    )}
                  </span>

                  <small>
                    Date:{" "}
                    {selectedItem.payment_date ||
                      "—"}
                  </small>
                </div>
              </div>

              <div className="reconciliation-flow-arrow">
                ↓
              </div>

              <div className="reconciliation-flow-card">
                <span className="flow-step">
                  03
                </span>

                <div>
                  <span className="flow-type">
                    BANK TRANSACTION
                  </span>

                  <strong>
                    {selectedItem.bank_transaction_id ||
                      "—"}
                  </strong>

                  <span>
                    {formatAmount(
                      selectedItem.bank_amount,
                      selectedItem.bank_currency
                    )}
                  </span>

                  <small>
                    Date:{" "}
                    {selectedItem.bank_date ||
                      "—"}
                  </small>
                </div>
              </div>
            </div>

            <div className="reconciliation-detail-metrics">
              <div className="detail-metric">
                <span>
                  PAYMENT COVERAGE
                </span>

                <strong>
                  {selectedItem.payment_coverage_percent ===
                  null
                    ? "—"
                    : `${Number(
                        selectedItem.payment_coverage_percent
                      ).toFixed(1)}%`}
                </strong>
              </div>

              <div className="detail-metric">
                <span>
                  PAYMENT − INVOICE
                </span>

                <strong>
                  {formatDifference(
                    selectedItem.payment_invoice_difference,
                    selectedItem.invoice_currency
                  )}
                </strong>
              </div>

              <div className="detail-metric">
                <span>
                  BANK − PAYMENT
                </span>

                <strong>
                  {formatDifference(
                    selectedItem.bank_payment_difference,
                    selectedItem.payment_currency
                  )}
                </strong>
              </div>

              <div className="detail-metric">
                <span>
                  RECONCILIATION PASS
                </span>

                <strong>
                  PASS{" "}
                  {selectedItem.pass_status}
                </strong>
              </div>
            </div>

            <div className="reconciliation-rationale-box">
              <span className="detail-label">
                RATIONALE
              </span>

              <p>
                {selectedItem.rationale ||
                  "No rationale available."}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Reconciliation;