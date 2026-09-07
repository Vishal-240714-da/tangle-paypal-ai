import { useEffect, useState } from "react";

import api from "../services/api";


function Analytics() {
  const [summary, setSummary] = useState(null);
  const [riskData, setRiskData] = useState([]);
  const [exceptionData, setExceptionData] = useState([]);
  const [lifecycleData, setLifecycleData] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  // ============================================================
  // LOAD ANALYTICS DATA
  // ============================================================

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoading(true);
        setError("");

        const [
          summaryResponse,
          riskResponse,
          exceptionResponse,
          lifecycleResponse,
        ] = await Promise.all([
          api.get("/api/analytics/summary"),
          api.get("/api/analytics/risk"),
          api.get("/api/analytics/exceptions"),
          api.get("/api/analytics/lifecycle"),
        ]);


        setSummary(summaryResponse.data);


        // Backend returns objects such as:
        //
        // {
        //   "HIGH": 132,
        //   "CRITICAL": 65,
        //   "MEDIUM": 5
        // }
        //
        // Convert them into arrays for the UI.

        const riskObject = riskResponse.data || {};

        setRiskData(
          Object.entries(riskObject).map(
            ([level, count]) => ({
              level,
              count,
            })
          )
        );


        const exceptionObject =
          exceptionResponse.data || {};

        setExceptionData(
          Object.entries(exceptionObject).map(
            ([category, count]) => ({
              category,
              count,
            })
          )
        );


        const lifecycleObject =
          lifecycleResponse.data || {};

        setLifecycleData(
          Object.entries(lifecycleObject).map(
            ([status, count]) => ({
              status,
              count,
            })
          )
        );

      } catch (error) {
        console.error(
          "Failed to load analytics:",
          error
        );

        setError(
          "Unable to load analytics data. Please make sure the FastAPI backend is running."
        );

      } finally {
        setLoading(false);
      }
    };


    loadAnalytics();

  }, []);


  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Analytics</h1>

          <p>
            Loading TANGLE analytics...
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
          <h1>Analytics</h1>

          <p>{error}</p>
        </div>
      </div>
    );
  }


  // ============================================================
  // HUMAN REVIEW
  // ============================================================

  const humanReview =
    summary?.human_review || {};

  const humanReviewRequired =
    typeof humanReview === "object"
      ? humanReview.required ?? 0
      : humanReview ?? 0;

  const humanReviewRate =
    typeof humanReview === "object"
      ? humanReview.rate ?? 0
      : 0;


  // ============================================================
  // FINANCIAL DATA
  // ============================================================

  const financial =
    summary?.financial || {};

  const outstandingBalance =
    financial.outstanding_balance ?? 0;

  const averagePaymentCoverage =
    financial.average_payment_coverage ?? 0;

  const totalInvoiceAmount =
    financial.total_invoice_amount ?? 0;

  const totalPaymentAmount =
    financial.total_payment_amount ?? 0;

  const totalBankAmount =
    financial.total_bank_amount ?? 0;


  // ============================================================
  // PRIORITY DATA
  // ============================================================

  const priority =
    summary?.priority || {};

  const averagePriority =
    priority.average ?? 0;

  const maximumPriority =
    priority.maximum ?? 0;

  const minimumPriority =
    priority.minimum ?? 0;


  // ============================================================
  // SUMMARY DISTRIBUTIONS
  // ============================================================

  const decisionDistribution =
    summary?.decision_distribution || {};

  const totalCases =
    Object.values(
      summary?.risk_distribution || {}
    ).reduce(
      (total, count) =>
        total + Number(count || 0),
      0
    );


  // ============================================================
  // MAIN PAGE
  // ============================================================

  return (
    <div className="page">


      {/* ======================================================
          PAGE HEADER
      ====================================================== */}

      <div className="page-header">

        <h1>
          Analytics
        </h1>

        <p>
          Operational and risk analytics for the
          TANGLE reconciliation engine.
        </p>

      </div>


      {/* ======================================================
          SUMMARY
      ====================================================== */}

      <div className="analytics-summary-grid">


        {/* TOTAL CASES */}

        <div className="analytics-card">

          <span>
            Total Cases
          </span>

          <strong>
            {totalCases}
          </strong>

        </div>


        {/* CRITICAL CASES */}

        <div className="analytics-card">

          <span>
            Critical Cases
          </span>

          <strong>
            {summary?.risk_distribution
              ?.CRITICAL ?? 0}
          </strong>

        </div>


        {/* HUMAN REVIEW */}

        <div className="analytics-card">

          <span>
            Human Review
          </span>

          <strong>
            {humanReviewRequired}
          </strong>

          <small>
            {Number(
              humanReviewRate
            ).toFixed(2)}
            % review rate
          </small>

        </div>


        {/* OUTSTANDING BALANCE */}

        <div className="analytics-card">

          <span>
            Outstanding Balance
          </span>

          <strong>

            $
            {Number(
              outstandingBalance
            ).toLocaleString(
              undefined,
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }
            )}

          </strong>

        </div>


        {/* PAYMENT COVERAGE */}

        <div className="analytics-card">

          <span>
            Payment Coverage
          </span>

          <strong>

            {Number(
              averagePaymentCoverage
            ).toFixed(2)}
            %

          </strong>

        </div>


        {/* AVERAGE PRIORITY */}

        <div className="analytics-card">

          <span>
            Average Priority
          </span>

          <strong>
            {Number(
              averagePriority
            ).toFixed(2)}
          </strong>

        </div>


      </div>


      {/* ======================================================
          ANALYTICS GRID
      ====================================================== */}

      <div className="analytics-grid">


        {/* ====================================================
            RISK DISTRIBUTION
        ==================================================== */}

        <div className="analytics-section">

          <div className="analytics-section-header">

            <div>

              <h2>
                Risk Distribution
              </h2>

              <p>
                Distribution of cases by risk level.
              </p>

            </div>

          </div>


          <div className="analytics-list">

            {riskData.length === 0 ? (

              <div className="analytics-empty">
                No risk data available.
              </div>

            ) : (

              riskData.map(
                (item, index) => (

                  <div
                    className="analytics-row"
                    key={`${item.level}-${index}`}
                  >

                    <div className="analytics-row-label">

                      <span
                        className={
                          `analytics-risk-badge ${
                            String(
                              item.level
                            ).toLowerCase()
                          }`
                        }
                      >
                        {item.level}
                      </span>

                    </div>

                    <strong>
                      {item.count}
                    </strong>

                  </div>

                )
              )

            )}

          </div>

        </div>


        {/* ====================================================
            EXCEPTION DISTRIBUTION
        ==================================================== */}

        <div className="analytics-section">

          <div className="analytics-section-header">

            <div>

              <h2>
                Exception Distribution
              </h2>

              <p>
                Types of transaction anomalies detected.
              </p>

            </div>

          </div>


          <div className="analytics-list">

            {exceptionData.length === 0 ? (

              <div className="analytics-empty">
                No exception data available.
              </div>

            ) : (

              exceptionData.map(
                (item, index) => (

                  <div
                    className="analytics-row"
                    key={`${item.category}-${index}`}
                  >

                    <span>
                      {item.category}
                    </span>

                    <strong>
                      {item.count}
                    </strong>

                  </div>

                )
              )

            )}

          </div>

        </div>


        {/* ====================================================
            CASE LIFECYCLE
        ==================================================== */}

        <div className="analytics-section">

          <div className="analytics-section-header">

            <div>

              <h2>
                Case Lifecycle
              </h2>

              <p>
                Current distribution of case statuses.
              </p>

            </div>

          </div>


          <div className="analytics-list">

            {lifecycleData.length === 0 ? (

              <div className="analytics-empty">
                No lifecycle data available.
              </div>

            ) : (

              lifecycleData.map(
                (item, index) => (

                  <div
                    className="analytics-row"
                    key={`${item.status}-${index}`}
                  >

                    <span>
                      {item.status}
                    </span>

                    <strong>
                      {item.count}
                    </strong>

                  </div>

                )
              )

            )}

          </div>

        </div>


        {/* ====================================================
            FINANCIAL ANALYSIS
        ==================================================== */}

        <div className="analytics-section">

          <div className="analytics-section-header">

            <div>

              <h2>
                Financial Analysis
              </h2>

              <p>
                Financial exposure across TANGLE cases.
              </p>

            </div>

          </div>


          <div className="analytics-list">

            <div className="analytics-row">

              <span>
                Invoice Amount
              </span>

              <strong>
                $
                {Number(
                  totalInvoiceAmount
                ).toLocaleString(
                  undefined,
                  {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  }
                )}
              </strong>

            </div>


            <div className="analytics-row">

              <span>
                Payment Amount
              </span>

              <strong>
                $
                {Number(
                  totalPaymentAmount
                ).toLocaleString(
                  undefined,
                  {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  }
                )}
              </strong>

            </div>


            <div className="analytics-row">

              <span>
                Bank Amount
              </span>

              <strong>
                $
                {Number(
                  totalBankAmount
                ).toLocaleString(
                  undefined,
                  {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  }
                )}
              </strong>

            </div>


            <div className="analytics-row">

              <span>
                Outstanding Balance
              </span>

              <strong>
                $
                {Number(
                  outstandingBalance
                ).toLocaleString(
                  undefined,
                  {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  }
                )}
              </strong>

            </div>

          </div>

        </div>


        {/* ====================================================
            PRIORITY ANALYSIS
        ==================================================== */}

        <div className="analytics-section">

          <div className="analytics-section-header">

            <div>

              <h2>
                Priority Analysis
              </h2>

              <p>
                Priority score distribution across investigations.
              </p>

            </div>

          </div>


          <div className="analytics-list">

            <div className="analytics-row">

              <span>
                Average Priority
              </span>

              <strong>
                {Number(
                  averagePriority
                ).toFixed(2)}
              </strong>

            </div>


            <div className="analytics-row">

              <span>
                Maximum Priority
              </span>

              <strong>
                {Number(
                  maximumPriority
                ).toFixed(2)}
              </strong>

            </div>


            <div className="analytics-row">

              <span>
                Minimum Priority
              </span>

              <strong>
                {Number(
                  minimumPriority
                ).toFixed(2)}
              </strong>

            </div>


            <div className="analytics-row">

              <span>
                AI Decision
              </span>

              <strong>
                {decisionDistribution.INVESTIGATE ?? 0}
              </strong>

            </div>

          </div>

        </div>


        {/* ====================================================
            TANGLE INSIGHTS
        ==================================================== */}

        <div className="analytics-section analytics-insight">

          <div className="analytics-section-header">

            <div>

              <h2>
                TANGLE Insights
              </h2>

              <p>
                What these analytics represent.
              </p>

            </div>

          </div>


          <div className="analytics-insight-list">


            <div>

              <strong>
                Risk
              </strong>

              <p>
                Shows how detected exceptions are
                distributed across TANGLE risk levels.
              </p>

            </div>


            <div>

              <strong>
                Exceptions
              </strong>

              <p>
                Shows which types of reconciliation
                anomalies are occurring most frequently.
              </p>

            </div>


            <div>

              <strong>
                Lifecycle
              </strong>

              <p>
                Shows where cases currently stand in
                the human governance workflow.
              </p>

            </div>


            <div>

              <strong>
                Financial Exposure
              </strong>

              <p>
                Outstanding balance indicates the
                financial value associated with unresolved
                reconciliation exceptions.
              </p>

            </div>


          </div>

        </div>


      </div>

    </div>
  );
}


export default Analytics;