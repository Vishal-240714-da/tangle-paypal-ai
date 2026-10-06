import { useEffect, useState } from "react";
import {
  Upload,
  Database,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ArrowRight,
  RefreshCw,
  ShieldCheck,
  Activity,
  Server,
  CircleDot,
} from "lucide-react";

import api from "../services/api";

function DataIngestion() {
  const [datasets, setDatasets] = useState({});
  const [selectedDataset, setSelectedDataset] = useState("invoices");
  const [selectedFile, setSelectedFile] = useState(null);

  const [validation, setValidation] = useState(null);
  const [importResult, setImportResult] = useState(null);

  const [uploading, setUploading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [activating, setActivating] = useState(false);
  const [importing, setImporting] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadStatus = async () => {
    try {
      const response = await api.get("/api/ingestion/status");

      setDatasets(response.data.datasets || {});
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load ingestion status."
      );
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleDatasetChange = (name) => {
    setSelectedDataset(name);
    setSelectedFile(null);
    setValidation(null);
    setImportResult(null);
    setMessage("");
    setError("");

    const fileInput = document.getElementById(
      "ingestion-file-input"
    );

    if (fileInput) {
      fileInput.value = "";
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] || null;

    setSelectedFile(file);
    setValidation(null);
    setImportResult(null);
    setMessage("");
    setError("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a CSV file first.");
      return;
    }

    setUploading(true);
    setMessage("");
    setError("");
    setValidation(null);
    setImportResult(null);

    try {
      const formData = new FormData();

      formData.append("file", selectedFile);

      const response = await api.post(
        `/api/ingestion/upload/${selectedDataset}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setMessage(
        response.data.message ||
          "Dataset uploaded successfully."
      );

      setSelectedFile(null);

      const fileInput = document.getElementById(
        "ingestion-file-input"
      );

      if (fileInput) {
        fileInput.value = "";
      }

      await loadStatus();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Dataset upload failed."
      );
    } finally {
      setUploading(false);
    }
  };

  const handleValidate = async () => {
    setValidating(true);
    setMessage("");
    setError("");

    try {
      const response = await api.post(
        `/api/ingestion/validate/${selectedDataset}`
      );

      setValidation(response.data.quality);

      setMessage(
        "Full Data Quality validation completed."
      );
    } catch (err) {
      setValidation(null);

      setError(
        err.response?.data?.detail ||
          "Dataset validation failed."
      );
    } finally {
      setValidating(false);
    }
  };

  const handleActivate = async () => {
    setActivating(true);
    setMessage("");
    setError("");

    try {
      const response = await api.post(
        `/api/ingestion/activate/${selectedDataset}`
      );

      setMessage(
        response.data.message ||
          "Dataset activated successfully."
      );

      setValidation(
        response.data.activation?.validation || null
      );

      setSelectedFile(null);

      await loadStatus();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Dataset activation failed."
      );
    } finally {
      setActivating(false);
    }
  };

  const handleImport = async () => {
    setImporting(true);
    setMessage("");
    setError("");
    setImportResult(null);

    try {
      const response = await api.post(
        "/api/ingestion/import"
      );

      setMessage(
        response.data.message ||
          "Active datasets imported successfully."
      );

      setImportResult(
        response.data.import || null
      );

      await loadStatus();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Dataset import failed."
      );
    } finally {
      setImporting(false);
    }
  };

  const selectedStatus = datasets[selectedDataset];

  const hasStagedDataset =
    selectedStatus?.staging?.exists === true;

  const hasErrors =
    validation?.errors > 0;

  const activationAllowed =
    validation?.activation_allowed === true;

  const invoiceImport =
    importResult?.datasets?.invoices;

  const paymentImport =
    importResult?.datasets?.payments;

  const bankImport =
    importResult?.datasets?.bank_transactions;

  const totalInserted =
    (invoiceImport?.inserted ?? 0) +
    (paymentImport?.inserted ?? 0) +
    (bankImport?.inserted ?? 0);

  const totalUpdated =
    (invoiceImport?.updated ?? 0) +
    (paymentImport?.updated ?? 0) +
    (bankImport?.updated ?? 0);

  const totalSkipped =
    (invoiceImport?.skipped ?? 0) +
    (paymentImport?.skipped ?? 0) +
    (bankImport?.skipped ?? 0);

  const datasetLabel = (name) => {
    if (name === "bank_transactions") {
      return "Bank Transactions";
    }

    return (
      name.charAt(0).toUpperCase() +
      name.slice(1)
    );
  };

  return (
    <div className="page ingestion-page">

      {/* HEADER */}
      <div className="ingestion-hero">
        <div>
          <div className="section-eyebrow">
            TANGLE CONTROL LAYER
          </div>

          <h1>Data Ingestion</h1>

          <p>
            Upload, validate, activate, and import
            TANGLE source datasets safely.
          </p>
        </div>

        <button
          type="button"
          className="ingestion-refresh-button"
          onClick={loadStatus}
        >
          <RefreshCw size={15} />
          Refresh Status
        </button>
      </div>

      {/* GLOBAL MESSAGES */}
      {message && (
        <div className="ingestion-alert success">
          <CheckCircle2 size={18} />

          <div>
            <strong>Operation successful</strong>
            <span>{message}</span>
          </div>
        </div>
      )}

      {error && (
        <div className="ingestion-alert error">
          <XCircle size={18} />

          <div>
            <strong>Operation failed</strong>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* PIPELINE */}
      <section className="ingestion-card ingestion-pipeline-card">

        <div className="ingestion-section-heading">
          <div>
            <div className="section-eyebrow">
              CONTROLLED WORKFLOW
            </div>

            <h2>Ingestion Pipeline</h2>

            <p>
              Every source dataset passes through a
              controlled validation and activation flow.
            </p>
          </div>
        </div>

        <div className="modern-pipeline">

          <div className="pipeline-node active">
            <div className="pipeline-icon">
              <Upload size={17} />
            </div>

            <div>
              <strong>Upload</strong>
              <span>CSV → staging</span>
            </div>
          </div>

          <ArrowRight className="pipeline-connector" size={18} />

          <div
            className={`pipeline-node ${
              hasStagedDataset ? "active" : ""
            }`}
          >
            <div className="pipeline-icon">
              <ShieldCheck size={17} />
            </div>

            <div>
              <strong>Validate</strong>
              <span>Quality checks</span>
            </div>
          </div>

          <ArrowRight className="pipeline-connector" size={18} />

          <div
            className={`pipeline-node ${
              activationAllowed ? "active" : ""
            }`}
          >
            <div className="pipeline-icon">
              <CheckCircle2 size={17} />
            </div>

            <div>
              <strong>Activate</strong>
              <span>Safe dataset</span>
            </div>
          </div>

          <ArrowRight className="pipeline-connector" size={18} />

          <div
            className={`pipeline-node ${
              importResult ? "active" : ""
            }`}
          >
            <div className="pipeline-icon">
              <Database size={17} />
            </div>

            <div>
              <strong>Import</strong>
              <span>PostgreSQL</span>
            </div>
          </div>

        </div>
      </section>

      {/* DATASET + UPLOAD */}
      <div className="ingestion-main-grid">

        {/* DATASET STATUS */}
        <section className="ingestion-card">

          <div className="ingestion-card-header">

            <div className="ingestion-heading-icon blue">
              <Database size={18} />
            </div>

            <div>
              <h2>Dataset Status</h2>

              <p>
                Active and staged source datasets.
              </p>
            </div>

          </div>

          <div className="dataset-list">

            {Object.entries(datasets).map(
              ([name, dataset]) => {

                const isSelected =
                  selectedDataset === name;

                const active =
                  dataset.active?.exists;

                const staged =
                  dataset.staging?.exists;

                return (
                  <button
                    key={name}
                    type="button"
                    className={`dataset-row ${
                      isSelected ? "selected" : ""
                    }`}
                    onClick={() =>
                      handleDatasetChange(name)
                    }
                  >

                    <div className="dataset-row-icon">
                      <FileSpreadsheet size={17} />
                    </div>

                    <div className="dataset-main">

                      <strong>
                        {datasetLabel(name)}
                      </strong>

                      <span>
                        {dataset.filename ||
                          "No dataset file"}
                      </span>

                    </div>

                    <div className="dataset-status">

                      <span
                        className={`status-pill ${
                          active
                            ? "active"
                            : "inactive"
                        }`}
                      >
                        <CircleDot size={10} />
                        {active
                          ? "ACTIVE"
                          : "INACTIVE"}
                      </span>

                      {staged && (
                        <span className="status-pill staged">
                          STAGED
                        </span>
                      )}

                    </div>

                  </button>
                );
              }
            )}

          </div>
        </section>

        {/* UPLOAD */}
        <section className="ingestion-card">

          <div className="ingestion-card-header">

            <div className="ingestion-heading-icon purple">
              <Upload size={18} />
            </div>

            <div>
              <h2>Upload Dataset</h2>

              <p>
                Upload a CSV into the staging area.
              </p>
            </div>

          </div>

          <div className="ingestion-upload-area">

            <label htmlFor="dataset-select">
              Dataset
            </label>

            <select
              id="dataset-select"
              value={selectedDataset}
              onChange={(event) =>
                handleDatasetChange(
                  event.target.value
                )
              }
            >
              <option value="invoices">
                Invoices
              </option>

              <option value="payments">
                Payments
              </option>

              <option value="bank_transactions">
                Bank Transactions
              </option>
            </select>

            <label htmlFor="ingestion-file-input">
              CSV File
            </label>

            <label
              htmlFor="ingestion-file-input"
              className={`upload-dropzone ${
                selectedFile ? "has-file" : ""
              }`}
            >
              <div className="upload-dropzone-icon">
                <Upload size={22} />
              </div>

              <strong>
                {selectedFile
                  ? selectedFile.name
                  : "Choose a CSV file"}
              </strong>

              <span>
                {selectedFile
                  ? `${(
                      selectedFile.size / 1024
                    ).toFixed(1)} KB selected`
                  : "CSV files only"}
              </span>
            </label>

            <input
              id="ingestion-file-input"
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
            />

            <button
              type="button"
              className="primary-button ingestion-primary-button"
              onClick={handleUpload}
              disabled={
                uploading || !selectedFile
              }
            >
              <Upload size={16} />

              {uploading
                ? "Uploading..."
                : "Upload to Staging"}
            </button>

          </div>
        </section>

      </div>

      {/* VALIDATION */}
      <section className="ingestion-card">

        <div className="ingestion-card-header">

          <div className="ingestion-heading-icon green">
            <ShieldCheck size={18} />
          </div>

          <div>
            <h2>Data Quality Validation</h2>

            <p>
              Run the complete Data Quality Engine
              against the staged dataset.
            </p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={handleValidate}
            disabled={
              validating ||
              !hasStagedDataset
            }
          >
            <Activity size={15} />

            {validating
              ? "Validating..."
              : "Run Validation"}
          </button>

        </div>

        {!hasStagedDataset && (
          <div className="ingestion-empty-state">
            <AlertTriangle size={17} />

            <div>
              <strong>
                Dataset not ready for validation
              </strong>

              <span>
                Upload a dataset to staging before
                running validation.
              </span>
            </div>
          </div>
        )}

        {validation && (
          <div className="validation-panel">

            <div className="validation-metrics">

              <div className="validation-stat">
                <span>Quality Score</span>
                <strong className="quality-score">
                  {validation.quality_score}%
                </strong>
              </div>

              <div className="validation-stat">
                <span>Total Records</span>
                <strong>
                  {validation.total_records}
                </strong>
              </div>

              <div className="validation-stat">
                <span>Valid Records</span>
                <strong>
                  {validation.valid_records}
                </strong>
              </div>

              <div className="validation-stat">
                <span>Warnings</span>
                <strong className="warning-number">
                  {validation.warnings}
                </strong>
              </div>

              <div className="validation-stat">
                <span>Errors</span>
                <strong
                  className={
                    hasErrors
                      ? "error-number"
                      : "success-number"
                  }
                >
                  {validation.errors}
                </strong>
              </div>

            </div>

            <div
              className={`activation-panel ${
                activationAllowed
                  ? "allowed"
                  : "blocked"
              }`}
            >
              <div>

                <span>
                  Activation Decision
                </span>

                <strong>
                  {activationAllowed
                    ? "ALLOWED"
                    : "BLOCKED"}
                </strong>

              </div>

              {activationAllowed && (
                <button
                  type="button"
                  className="primary-button"
                  onClick={handleActivate}
                  disabled={activating}
                >
                  <CheckCircle2 size={16} />

                  {activating
                    ? "Activating..."
                    : "Activate Dataset"}
                </button>
              )}

            </div>

            {validation.issues?.length > 0 && (
              <div className="validation-issues">

                <div className="validation-issues-header">
                  <div>
                    <h3>Validation Issues</h3>
                    <p>
                      Problems detected during
                      quality validation.
                    </p>
                  </div>

                  <span>
                    {validation.issues.length} issue
                    {validation.issues.length !== 1
                      ? "s"
                      : ""}
                  </span>
                </div>

                <div className="issue-list">

                  {validation.issues.map(
                    (issue, index) => (
                      <div
                        key={`${issue.record_id}-${index}`}
                        className={`issue-row ${
                          issue.severity === "ERROR"
                            ? "error"
                            : "warning"
                        }`}
                      >

                        <div className="issue-icon">
                          {issue.severity ===
                          "ERROR" ? (
                            <XCircle size={17} />
                          ) : (
                            <AlertTriangle size={17} />
                          )}
                        </div>

                        <div className="issue-content">

                          <strong>
                            {issue.issue_type}
                          </strong>

                          {issue.record_id && (
                            <span className="issue-record">
                              {issue.record_id}
                            </span>
                          )}

                          <p>
                            {issue.message}
                          </p>

                        </div>

                      </div>
                    )
                  )}

                </div>
              </div>
            )}

          </div>
        )}

      </section>

      {/* POSTGRES IMPORT */}
      <section className="ingestion-card">

        <div className="ingestion-card-header">

          <div className="ingestion-heading-icon blue">
            <Server size={18} />
          </div>

          <div>
            <h2>PostgreSQL Import</h2>

            <p>
              Import currently active source datasets
              into TANGLE's database.
            </p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={handleImport}
            disabled={importing}
          >
            <Database size={15} />

            {importing
              ? "Importing..."
              : "Import Active Data"}
          </button>

        </div>

        <div className="import-note">
          <ShieldCheck size={17} />

          <span>
            Import affects only invoices, payments,
            and bank transactions. Existing cases,
            investigations, risk assessments, and
            reviews are not modified.
          </span>
        </div>

        {importResult?.datasets && (
          <div className="import-result">

            <div className="import-result-header">

              <div>
                <h3>Import Summary</h3>

                <p>
                  Active source datasets were
                  successfully synchronized
                  with PostgreSQL.
                </p>
              </div>

              <span className="import-success">
                <CheckCircle2 size={14} />
                IMPORT SUCCESS
              </span>

            </div>

            <div className="import-dataset-stats">

              <div>
                <span>Invoices</span>
                <strong>
                  {invoiceImport?.updated ?? 0}
                </strong>
                <small>updated</small>
              </div>

              <div>
                <span>Payments</span>
                <strong>
                  {paymentImport?.updated ?? 0}
                </strong>
                <small>updated</small>
              </div>

              <div>
                <span>Bank Transactions</span>
                <strong>
                  {bankImport?.updated ?? 0}
                </strong>
                <small>updated</small>
              </div>

            </div>

            <div className="import-total-row">

              <div>
                <span>Inserted</span>
                <strong>{totalInserted}</strong>
              </div>

              <div>
                <span>Updated</span>
                <strong>{totalUpdated}</strong>
              </div>

              <div>
                <span>Skipped</span>
                <strong>{totalSkipped}</strong>
              </div>

            </div>

          </div>
        )}

      </section>

    </div>
  );
}

export default DataIngestion;