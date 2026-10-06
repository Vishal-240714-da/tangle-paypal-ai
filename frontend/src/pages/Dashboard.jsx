import { useEffect, useState } from "react";
import {
  AlertCircle,
  ArrowUpRight,
  CheckCircle2,
  ClipboardCheck,
  DollarSign,
  FileSearch,
  RefreshCw,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";

import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";

import api from "../services/api";

function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDashboard = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/api/dashboard/summary");
      setData(response.data);
    } catch (error) {
      console.error(error);
      setError("Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-loading">
          <RefreshCw
            size={20}
            className="dashboard-loading-icon"
          />
          <span>Loading dashboard...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <Card className="dashboard-error-card">
          <CardContent className="dashboard-error-content">
            <div className="dashboard-error-icon">
              <AlertCircle size={20} />
            </div>

            <div>
              <h2>{error}</h2>
              <p>
                The dashboard service could not be reached.
                Please try again.
              </p>
            </div>

            <Button
              variant="outline"
              onClick={loadDashboard}
            >
              <RefreshCw size={15} />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const totalCases = Number(data?.total_cases || 0);
  const criticalCases = Number(data?.critical_cases || 0);
  const highRiskCases = Number(data?.high_risk_cases || 0);
  const humanReview = Number(data?.human_review || 0);

  const paymentCoverage = Number(
    data?.average_payment_coverage || 0
  );

  const outstandingBalance = Number(
    data?.outstanding_balance || 0
  );

  const resolvedOrApproved = Number(
    data?.resolved_or_approved || 0
  );

  const formattedOutstandingBalance =
    outstandingBalance.toLocaleString("en-US");

  return (
    <div className="dashboard-page">
      {/* =====================================================
          PAGE HEADER
          ===================================================== */}

      <div className="dashboard-header">
        <div>
          <div className="dashboard-eyebrow">
            RISK INTELLIGENCE
          </div>

          <h1>TANGLE Dashboard</h1>

          <p>
            Transaction anomaly and governance overview
          </p>
        </div>

        <Button
          variant="outline"
          className="dashboard-refresh-button"
          onClick={loadDashboard}
        >
          <RefreshCw size={15} />
          Refresh
        </Button>
      </div>

      {/* =====================================================
          KPI OVERVIEW
          ===================================================== */}

      <section className="dashboard-section">
        <div className="dashboard-section-heading">
          <div>
            <h2>Operational Overview</h2>

            <p>
              Current transaction risk and review workload
            </p>
          </div>

          <Badge variant="outline">
            Live data
          </Badge>
        </div>

        <div className="dashboard-kpi-grid">
          {/* Total Cases */}

          <Card className="dashboard-kpi-card">
            <CardContent className="dashboard-kpi-content">
              <div className="dashboard-kpi-top">
                <div className="dashboard-kpi-icon blue">
                  <FileSearch size={19} />
                </div>

                <Badge variant="outline">
                  Cases
                </Badge>
              </div>

              <div className="dashboard-kpi-label">
                Total Cases
              </div>

              <div className="dashboard-kpi-value">
                {totalCases}
              </div>

              <div className="dashboard-kpi-description">
                Active transaction exceptions
              </div>
            </CardContent>
          </Card>

          {/* Critical Cases */}

          <Card className="dashboard-kpi-card dashboard-kpi-critical">
            <CardContent className="dashboard-kpi-content">
              <div className="dashboard-kpi-top">
                <div className="dashboard-kpi-icon red">
                  <ShieldAlert size={19} />
                </div>

                <Badge variant="destructive">
                  Critical
                </Badge>
              </div>

              <div className="dashboard-kpi-label">
                Critical Cases
              </div>

              <div className="dashboard-kpi-value">
                {criticalCases}
              </div>

              <div className="dashboard-kpi-description">
                Cases requiring immediate attention
              </div>
            </CardContent>
          </Card>

          {/* High Risk */}

          <Card className="dashboard-kpi-card">
            <CardContent className="dashboard-kpi-content">
              <div className="dashboard-kpi-top">
                <div className="dashboard-kpi-icon orange">
                  <TrendingUp size={19} />
                </div>

                <Badge className="dashboard-warning-badge">
                  High risk
                </Badge>
              </div>

              <div className="dashboard-kpi-label">
                High Risk Cases
              </div>

              <div className="dashboard-kpi-value">
                {highRiskCases}
              </div>

              <div className="dashboard-kpi-description">
                Elevated transaction risk detected
              </div>
            </CardContent>
          </Card>

          {/* Human Review */}

          <Card className="dashboard-kpi-card">
            <CardContent className="dashboard-kpi-content">
              <div className="dashboard-kpi-top">
                <div className="dashboard-kpi-icon purple">
                  <ClipboardCheck size={19} />
                </div>

                <Badge variant="outline">
                  Review
                </Badge>
              </div>

              <div className="dashboard-kpi-label">
                Human Review
              </div>

              <div className="dashboard-kpi-value">
                {humanReview}
              </div>

              <div className="dashboard-kpi-description">
                Cases requiring analyst review
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* =====================================================
          FINANCIAL OVERVIEW
          ===================================================== */}

      <section className="dashboard-section">
        <div className="dashboard-section-heading">
          <div>
            <h2>Financial Overview</h2>

            <p>
              Exposure and payment reconciliation indicators
            </p>
          </div>
        </div>

        <div className="dashboard-financial-grid">
          {/* Outstanding Balance */}

          <Card className="dashboard-financial-card">
            <CardHeader className="dashboard-card-header">
              <div className="dashboard-card-title-group">
                <div className="dashboard-financial-icon">
                  <DollarSign size={19} />
                </div>

                <div>
                  <CardTitle>
                    Outstanding Balance
                  </CardTitle>

                  <p>
                    Current unresolved financial exposure
                  </p>
                </div>
              </div>

              <ArrowUpRight
                size={17}
                className="dashboard-muted-icon"
              />
            </CardHeader>

            <CardContent>
              <div
                className="dashboard-financial-value"
                data-testid="outstanding-balance"
              >
                {`$${formattedOutstandingBalance}`}
              </div>

              <div className="dashboard-financial-meta">
                <span>
                  Outstanding financial exposure
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Payment Coverage */}

          <Card className="dashboard-financial-card">
            <CardHeader className="dashboard-card-header">
              <div className="dashboard-card-title-group">
                <div className="dashboard-financial-icon green">
                  <CheckCircle2 size={19} />
                </div>

                <div>
                  <CardTitle>
                    Payment Coverage
                  </CardTitle>

                  <p>
                    Average payment coverage across cases
                  </p>
                </div>
              </div>

              <Badge variant="outline">
                {paymentCoverage >= 90
                  ? "Healthy"
                  : "Attention"}
              </Badge>
            </CardHeader>

            <CardContent>
              <div className="dashboard-financial-value">
                {paymentCoverage}%
              </div>

              <div className="dashboard-progress">
                <div
                  className="dashboard-progress-bar"
                  style={{
                    width: `${Math.min(
                      paymentCoverage,
                      100
                    )}%`,
                  }}
                />
              </div>

              <div className="dashboard-financial-meta">
                <span>
                  Average transaction payment coverage
                </span>

                <strong>
                  {paymentCoverage}%
                </strong>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* =====================================================
          RESOLUTION OVERVIEW
          ===================================================== */}

      <section className="dashboard-section">
        <div className="dashboard-section-heading">
          <div>
            <h2>Case Resolution</h2>

            <p>
              Governance progress across investigated cases
            </p>
          </div>
        </div>

        <Card className="dashboard-resolution-card">
          <CardContent className="dashboard-resolution-content">
            <div className="dashboard-resolution-icon">
              <CheckCircle2 size={20} />
            </div>

            <div className="dashboard-resolution-main">
              <div className="dashboard-resolution-label">
                Resolved / Approved
              </div>

              <div className="dashboard-resolution-value">
                {resolvedOrApproved}
              </div>

              <p>
                Cases that have reached an approved or
                resolved state.
              </p>
            </div>

            <div className="dashboard-resolution-status">
              <Badge variant="outline">
                Governance tracking
              </Badge>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}

export default Dashboard;