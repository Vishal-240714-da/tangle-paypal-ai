import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await api.post("/auth/login", {
        email,
        password,
      });

      const token = response.data.access_token;

      localStorage.setItem("tangle_token", token);

      navigate("/");
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Invalid email or password."
        );
      } else {
        setError("Unable to connect to TANGLE backend.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* Left branding panel */}
      <div className="login-brand-panel">
        <div className="login-brand-content">
          <div className="login-brand-logo">
            T
          </div>

          <div className="login-brand-name">
            TANGLE
          </div>

          <div className="login-brand-subtitle">
            Finance Intelligence
          </div>

          <div className="login-brand-line"></div>

          <h2>
            Transaction Anomaly
            <br />
            & Governance Engine
          </h2>

          <p>
            Intelligent transaction monitoring, investigation,
            risk assessment and human governance in one platform.
          </p>

          <div className="login-feature-list">
            <div className="login-feature">
              <span>✓</span>
              <span>Automated anomaly detection</span>
            </div>

            <div className="login-feature">
              <span>✓</span>
              <span>Explainable investigation workflows</span>
            </div>

            <div className="login-feature">
              <span>✓</span>
              <span>Human-controlled decisions</span>
            </div>

            <div className="login-feature">
              <span>✓</span>
              <span>Complete auditability</span>
            </div>
          </div>
        </div>

        <div className="login-brand-footer">
          TANGLE Enterprise • Secure Governance Platform
        </div>
      </div>

      {/* Login panel */}
      <div className="login-form-panel">
        <div className="login-card">
          <div className="login-header">
            <div className="login-mobile-logo">T</div>

            <span className="login-eyebrow">
              SECURE ACCESS
            </span>

            <h1>
              Welcome back
            </h1>

            <p>
              Sign in to access your TANGLE workspace.
            </p>
          </div>

          <form onSubmit={handleLogin}>
            <div className="login-field">
              <label htmlFor="email">
                Email address
              </label>

              <input
                id="email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <div className="login-field">
              <div className="login-label-row">
                <label htmlFor="password">
                  Password
                </label>

                <span className="login-secure-label">
                  Secure login
                </span>
              </div>

              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
              />
            </div>

            {error && (
              <div className="login-error">
                <span className="login-error-icon">!</span>
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              className="login-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="login-spinner"></span>
                  Signing in...
                </>
              ) : (
                <>
                  Sign in
                  <span className="login-arrow">→</span>
                </>
              )}
            </button>
          </form>

          <div className="login-security-note">
            <span className="security-lock">◈</span>

            <span>
              Your session is protected by token-based
              authentication.
            </span>
          </div>

          <div className="login-footer">
            <span>© 2026 TANGLE</span>
            <span>•</span>
            <span>Transaction Governance Platform</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;