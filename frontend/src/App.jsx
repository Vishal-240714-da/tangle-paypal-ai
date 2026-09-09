
import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Cases from "./pages/Cases";
import Investigation from "./pages/Investigation";
import Review from "./pages/Review";
import Analytics from "./pages/Analytics";
import DataQuality from "./pages/DataQuality";
import Reconciliation from "./pages/Reconciliation";
import AuditTrail from "./pages/AuditTrail";
import DataIngestion from "./pages/DataIngestion";

import Layout from "./components/Layout";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>

          {/* ==================================================
              DASHBOARD
              ================================================== */}

          <Route
            path="/"
            element={<Dashboard />}
          />

          {/* ==================================================
              CASES
              ================================================== */}

          <Route
            path="/cases"
            element={<Cases />}
          />

          {/* ==================================================
              DATA QUALITY
              ================================================== */}

          <Route
            path="/data-quality"
            element={<DataQuality />}
          />

          {/* ==================================================
              DATA INGESTION
              ================================================== */}

          <Route
            path="/data-ingestion"
            element={<DataIngestion />}
          />

          {/* ==================================================
              RECONCILIATION
              ================================================== */}

          <Route
            path="/reconciliation"
            element={<Reconciliation />}
          />

          {/* ==================================================
              INVESTIGATION
              ================================================== */}

          <Route
            path="/investigation/:caseId"
            element={<Investigation />}
          />

          {/* ==================================================
              HUMAN REVIEW
              ================================================== */}

          <Route
            path="/review"
            element={<Review />}
          />

          {/* ==================================================
              AUDIT TRAIL
              ================================================== */}

          <Route
            path="/audit"
            element={<AuditTrail />}
          />

          {/* ==================================================
              ANALYTICS
              ================================================== */}

          <Route
            path="/analytics"
            element={<Analytics />}
          />

          {/* ==================================================
              UNKNOWN ROUTE
              ================================================== */}

          <Route
            path="*"
            element={
              <div className="page">
                <div className="page-header">
                  <h1>
                    Page Not Found
                  </h1>

                  <p>
                    The requested TANGLE page does not exist.
                  </p>
                </div>
              </div>
            }
          />

        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
