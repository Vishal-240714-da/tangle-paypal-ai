import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";


function Cases() {
  const [cases, setCases] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();


  // ============================================================
  // LOAD CASES FROM FASTAPI
  // ============================================================

  useEffect(() => {
    const loadCases = async () => {
      try {
        const response = await api.get("/api/cases");

        setCases(response.data);
      } catch (error) {
        console.error("Failed to load cases:", error);

        setError(
          "Unable to load cases. Please make sure the FastAPI backend is running."
        );
      } finally {
        setLoading(false);
      }
    };

    loadCases();
  }, []);


  // ============================================================
  // SEARCH / FILTER
  // ============================================================

  const filteredCases = cases.filter((item) => {
    const searchText = search.trim().toLowerCase();

    if (!searchText) {
      return true;
    }

    return (
      item.case_id?.toLowerCase().includes(searchText) ||
      item.record_id?.toLowerCase().includes(searchText) ||
      item.invoice_id?.toLowerCase().includes(searchText) ||
      item.category?.toLowerCase().includes(searchText) ||
      item.record_type?.toLowerCase().includes(searchText) ||
      item.financial_status?.toLowerCase().includes(searchText) ||
      item.decision?.toLowerCase().includes(searchText)
    );
  });


  // ============================================================
  // LOADING STATE
  // ============================================================

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Cases</h1>
          <p>Loading TANGLE cases...</p>
        </div>
      </div>
    );
  }


  // ============================================================
  // ERROR STATE
  // ============================================================

  if (error) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Cases</h1>
          <p>{error}</p>
        </div>
      </div>
    );
  }


  // ============================================================
  // MAIN PAGE
  // ============================================================

  return (
    <div className="page">

      {/* ======================================================
          PAGE HEADER
          ====================================================== */}

      <div className="page-header">

        <h1>Cases</h1>

        <p>
          Review and investigate transaction
          anomalies detected by TANGLE.
        </p>

      </div>


      {/* ======================================================
          SEARCH
          ====================================================== */}

      <div className="cases-controls">

        <input
          type="text"
          className="search-input"
          placeholder="Search by case, invoice, record, category..."
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
          }}
        />

      </div>


      {/* ======================================================
          CASE COUNT
          ====================================================== */}

      <div className="cases-count">

        Showing{" "}
        <strong>
          {filteredCases.length}
        </strong>{" "}

        of{" "}

        <strong>
          {cases.length}
        </strong>{" "}

        cases

      </div>


      {/* ======================================================
          CASE TABLE
          ====================================================== */}

      <div className="table-container">

        <table className="cases-table">

          <thead>

            <tr>

              <th>
                Case ID
              </th>

              <th>
                Category
              </th>

              <th>
                Type
              </th>

              <th>
                Invoice
              </th>

              <th>
                Record
              </th>

              <th>
                Financial Status
              </th>

              <th>
                Outstanding
              </th>

              <th>
                Coverage
              </th>

              <th>
                Decision
              </th>

              <th>
                Action
              </th>

            </tr>

          </thead>


          <tbody>

            {filteredCases.map((item) => (

              <tr key={item.case_id}>

                {/* CASE ID */}

                <td>

                  <strong>
                    {item.case_id}
                  </strong>

                </td>


                {/* CATEGORY */}

                <td>

                  <span className="category-badge">

                    {item.category || "N/A"}

                  </span>

                </td>


                {/* RECORD TYPE */}

                <td>
                  {item.record_type || "—"}
                </td>


                {/* INVOICE */}

                <td>
                  {item.invoice_id || "—"}
                </td>


                {/* RECORD */}

                <td>
                  {item.record_id || "—"}
                </td>


                {/* FINANCIAL STATUS */}

                <td>
                  {item.financial_status || "—"}
                </td>


                {/* OUTSTANDING */}

                <td>

                  $
                  {Number(
                    item.outstanding_amount || 0
                  ).toLocaleString(
                    undefined,
                    {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    }
                  )}

                </td>


                {/* PAYMENT COVERAGE */}

                <td>

                  {item.payment_coverage_percent !== null &&
                  item.payment_coverage_percent !== undefined
                    ? `${Number(
                        item.payment_coverage_percent
                      ).toFixed(2)}%`
                    : "—"}

                </td>


                {/* AI DECISION */}

                <td>

                  <span className="decision-badge">

                    {item.decision || "—"}

                  </span>

                </td>


                {/* INVESTIGATION BUTTON */}

                <td>

                  <button
                    className="view-button"
                    onClick={() => {
                      navigate(
                        `/investigation/${item.case_id}`
                      );
                    }}
                  >
                    Investigate
                  </button>

                </td>

              </tr>

            ))}

          </tbody>

        </table>


        {/* ==================================================
            NO RESULTS
            ================================================== */}

        {filteredCases.length === 0 && (

          <div className="empty-state">

            No cases found.

          </div>

        )}

      </div>

    </div>
  );
}


export default Cases;