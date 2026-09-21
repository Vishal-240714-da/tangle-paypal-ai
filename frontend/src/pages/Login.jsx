import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  CheckCircle2,
  LockKeyhole,
  ShieldCheck,
} from "lucide-react";

import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import api from "../services/api";

const features = [
  "Automated anomaly detection",
  "Explainable investigation workflows",
  "Human-controlled decisions",
  "Complete auditability",
];

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
    <div className="login-v2-page">
      {/* Brand panel */}
      <section className="login-v2-brand">
        <div className="login-v2-brand-inner">
          <div className="login-v2-brand-header">
            <div className="login-v2-brand-mark">T</div>

            <div>
              <div className="login-v2-brand-name">TANGLE</div>
              <div className="login-v2-brand-subtitle">
                Finance Intelligence
              </div>
            </div>
          </div>

          <div className="login-v2-brand-content">
            <div className="login-v2-eyebrow">
              TRANSACTION GOVERNANCE PLATFORM
            </div>

            <h1>
              Intelligence for
              <br />
              every transaction.
            </h1>

            <p>
              Detect anomalies, investigate risk, and maintain
              human-controlled governance across your financial
              operations.
            </p>

            <div className="login-v2-feature-list">
              {features.map((feature) => (
                <div className="login-v2-feature" key={feature}>
                  <CheckCircle2 size={17} strokeWidth={2} />
                  <span>{feature}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="login-v2-brand-footer">
            <ShieldCheck size={15} strokeWidth={1.9} />
            <span>Enterprise governance and auditability</span>
          </div>
        </div>
      </section>

      {/* Login panel */}
      <section className="login-v2-form-panel">
        <div className="login-v2-form-wrapper">
          <div className="login-v2-mobile-brand">
            <div className="login-v2-brand-mark">T</div>

            <div>
              <div className="login-v2-brand-name">TANGLE</div>
              <div className="login-v2-brand-subtitle">
                Finance Intelligence
              </div>
            </div>
          </div>

          <Card className="login-v2-card">
            <CardContent className="login-v2-card-content">
              <div className="login-v2-header">
                <div className="login-v2-security-icon">
                  <LockKeyhole size={20} strokeWidth={1.9} />
                </div>

                <div className="login-v2-header-text">
                  <span className="login-v2-header-eyebrow">
                    SECURE ACCESS
                  </span>

                  <h2>Welcome back</h2>

                  <p>
                    Sign in to access your TANGLE workspace.
                  </p>
                </div>
              </div>

              <form
                className="login-v2-form"
                onSubmit={handleLogin}
              >
                <div className="login-v2-field">
                  <Label htmlFor="email">Email address</Label>

                  <Input
                    id="email"
                    type="email"
                    placeholder="you@company.com"
                    value={email}
                    onChange={(event) =>
                      setEmail(event.target.value)
                    }
                    autoComplete="email"
                    required
                  />
                </div>

                <div className="login-v2-field">
                  <div className="login-v2-label-row">
                    <Label htmlFor="password">Password</Label>

                    <span>Secure login</span>
                  </div>

                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(event) =>
                      setPassword(event.target.value)
                    }
                    autoComplete="current-password"
                    required
                  />
                </div>

                {error && (
                  <div
                    className="login-v2-error"
                    role="alert"
                  >
                    <div className="login-v2-error-icon">
                      !
                    </div>

                    <span>{error}</span>
                  </div>
                )}

                <Button
                  type="submit"
                  size="lg"
                  disabled={loading}
                  className="login-v2-submit"
                >
                  {loading ? (
                    <>
                      <span className="login-v2-spinner"></span>
                      Signing in...
                    </>
                  ) : (
                    <>
                      Sign in
                      <ArrowRight
                        size={17}
                        strokeWidth={2}
                      />
                    </>
                  )}
                </Button>
              </form>

              <div className="login-v2-security-note">
                <ShieldCheck size={16} strokeWidth={1.9} />

                <span>
                  Your session is protected by token-based
                  authentication.
                </span>
              </div>
            </CardContent>
          </Card>

          <div className="login-v2-footer">
            <span>© 2026 TANGLE</span>
            <span>•</span>
            <span>Transaction Governance Platform</span>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Login;