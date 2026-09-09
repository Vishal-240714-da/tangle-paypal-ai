import { useEffect, useState } from "react";
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
      const response = await api.get(
        "/api/ingestion/status"
      );

      setDatasets(
        response.data.datasets || {}
      );
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

  const handleFileChange = (event) => {
    const file =
      event.target.files?.[0] || null;

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

      formData.append(
        "file",
        selectedFile
      );

      const response = await api.post(
        `/api/ingestion/upload/${selectedDataset}`,
        formData,
        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },
        }
      );

      setMessage(
        response.data.message ||
          "Dataset uploaded successfully."
      );

      setSelectedFile(null);

      const fileInput =
        document.getElementById(
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

      setValidation(
        response.data.quality
      );

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
        response.data.activation?.validation ||
          null
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

  const selectedStatus =
    datasets[selectedDataset];

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

  return (
    <div className="page ingestion-page">

      {/* PAGE HEADER */}

      <div className="page-header">
        <div>
          <h1>Data Ingestion</h1>

          <p>
            Upload, validate, activate, and
            import TANGLE source datasets safely.
          </p>
        </div>
      </div>

      {/* GLOBAL SUCCESS MESSAGE */}

      {message && (
        <div className="ingestion-message success">
          {message}
        </div>
      )}

      {/* GLOBAL ERROR MESSAGE */}

      {error && (
        <div className="ingestion-message error">
          {error}
        </div>
      )}

      {/* DATASET + UPLOAD */}

      <div className="ingestion-grid">

        {/* DATASET STATUS */}

        <section className="ingestion-card">

          <div className="ingestion-card-header">
            <div>
              <h2>Dataset Status</h2>

              <p>
                Current active and staged
                source datasets.
              </p>
            </div>
          </div>

          <div className="ingestion-dataset-list">

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
                    className={
                      `ingestion-dataset-row ${
                        isSelected
                          ? "selected"
                          : ""
                      }`
                    }
                    onClick={() => {
                      setSelectedDataset(name);
                      setValidation(null);
                      setImportResult(null);
                      setMessage("");
                      setError("");
                    }}
                  >

                    <div className="ingestion-dataset-main">

                      <strong>
                        {name ===
                        "bank_transactions"
                          ? "Bank Transactions"
                          : name
                              .charAt(0)
                              .toUpperCase() +
                            name.slice(1)}
                      </strong>

                      <span>
                        {dataset.filename}
                      </span>

                    </div>

                    <div className="ingestion-status-badges">

                      <span
                        className={
                          active
                            ? "status-badge active"
                            : "status-badge inactive"
                        }
                      >
                        {active
                          ? "ACTIVE"
                          : "INACTIVE"}
                      </span>

                      {staged && (
                        <span className="status-badge staged">
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

            <div>
              <h2>Upload Dataset</h2>

              <p>
                Upload a CSV into the staging
                area before activation.
              </p>
            </div>

          </div>

          <div className="ingestion-form">

            <label htmlFor="dataset-select">
              Dataset
            </label>

            <select
              id="dataset-select"
              value={selectedDataset}
              onChange={(event) => {
                setSelectedDataset(
                  event.target.value
                );
                setValidation(null);
                setImportResult(null);
                setMessage("");
                setError("");
              }}
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

            <input
              id="ingestion-file-input"
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
            />


            {selectedFile && (
              <div className="selected-file">
                <strong>
                  Selected:
                </strong>{" "}
                {selectedFile.name}
              </div>
            )}


            <button
              type="button"
              className="primary-button"
              onClick={handleUpload}
              disabled={
                uploading ||
                !selectedFile
              }
            >
              {uploading
                ? "Uploading..."
                : "Upload to Staging"}
            </button>

          </div>

        </section>

      </div>


      {/* PIPELINE */}

      <section className="ingestion-card ingestion-pipeline-card">

        <div className="ingestion-card-header">

          <div>
            <h2>Ingestion Pipeline</h2>

            <p>
              The selected dataset follows
              TANGLE's controlled ingestion flow.
            </p>
          </div>

        </div>


        <div className="ingestion-pipeline">

          <div className="pipeline-step complete">

            <span className="pipeline-number">
              1
            </span>

            <div>
              <strong>Upload</strong>

              <span>
                CSV → staging
              </span>
            </div>

          </div>


          <div className="pipeline-arrow">
            →
          </div>


          <div
            className={
              `pipeline-step ${
                hasStagedDataset
                  ? "complete"
                  : ""
              }`
            }
          >

            <span className="pipeline-number">
              2
            </span>

            <div>
              <strong>Validate</strong>

              <span>
                Structural + Data Quality
              </span>
            </div>

          </div>


          <div className="pipeline-arrow">
            →
          </div>


          <div
            className={
              `pipeline-step ${
                activationAllowed
                  ? "complete"
                  : ""
              }`
            }
          >

            <span className="pipeline-number">
              3
            </span>

            <div>
              <strong>Activate</strong>

              <span>
                Safe active dataset
              </span>
            </div>

          </div>


          <div className="pipeline-arrow">
            →
          </div>


          <div
            className={
              `pipeline-step ${
                importResult
                  ? "complete"
                  : ""
              }`
            }
          >

            <span className="pipeline-number">
              4
            </span>

            <div>
              <strong>Import</strong>

              <span>
                PostgreSQL
              </span>
            </div>

          </div>

        </div>

      </section>


      {/* VALIDATION */}

      <section className="ingestion-card">

        <div className="ingestion-card-header">

          <div>
            <h2>Data Quality Validation</h2>

            <p>
              Run the complete Data Quality
              Engine against the staged dataset.
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
            {validating
              ? "Validating..."
              : "Run Validation"}
          </button>

        </div>


        {!hasStagedDataset && (
          <div className="ingestion-empty">
            Upload a dataset to staging before
            running validation.
          </div>
        )}


        {validation && (
          <div className="ingestion-validation">

            <div className="validation-metrics">

              <div className="validation-metric">
                <span>
                  Quality Score
                </span>

                <strong>
                  {validation.quality_score}%
                </strong>
              </div>


              <div className="validation-metric">
                <span>
                  Total Records
                </span>

                <strong>
                  {validation.total_records}
                </strong>
              </div>


              <div className="validation-metric">
                <span>
                  Valid Records
                </span>

                <strong>
                  {validation.valid_records}
                </strong>
              </div>


              <div className="validation-metric">
                <span>
                  Warnings
                </span>

                <strong>
                  {validation.warnings}
                </strong>
              </div>


              <div className="validation-metric">
                <span>
                  Errors
                </span>

                <strong
                  className={
                    hasErrors
                      ? "metric-error"
                      : "metric-success"
                  }
                >
                  {validation.errors}
                </strong>
              </div>

            </div>


            <div className="validation-decision">

              <div>
                <span>
                  Activation Decision
                </span>

                <strong
                  className={
                    activationAllowed
                      ? "decision-allowed"
                      : "decision-blocked"
                  }
                >
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
                  {activating
                    ? "Activating..."
                    : "Activate Dataset"}
                </button>
              )}

            </div>


            {validation.issues?.length > 0 && (
              <div className="validation-issues">

                <h3>
                  Validation Issues
                </h3>

                {validation.issues.map(
                  (issue, index) => (
                    <div
                      key={`${issue.record_id}-${index}`}
                      className={
                        `validation-issue ${
                          issue.severity ===
                          "ERROR"
                            ? "error"
                            : "warning"
                        }`
                      }
                    >

                      <div>
                        <strong>
                          {issue.issue_type}
                        </strong>

                        {issue.record_id && (
                          <span>
                            {" "}
                            · {issue.record_id}
                          </span>
                        )}
                      </div>

                      <p>
                        {issue.message}
                      </p>

                    </div>
                  )
                )}

              </div>
            )}

          </div>
        )}

      </section>


      {/* POSTGRESQL IMPORT */}

      <section className="ingestion-card">

        <div className="ingestion-card-header">

          <div>
            <h2>PostgreSQL Import</h2>

            <p>
              Import the currently active source
              datasets into TANGLE's database.
            </p>
          </div>


          <button
            type="button"
            className="secondary-button"
            onClick={handleImport}
            disabled={importing}
          >
            {importing
              ? "Importing..."
              : "Import Active Data"}
          </button>

        </div>


        <div className="ingestion-import-note">
          Import affects only invoices, payments,
          and bank transactions. Existing cases,
          investigations, risk assessments, and
          reviews are not modified.
        </div>


        {/* IMPORT SUMMARY */}

        {importResult?.datasets && (
          <div className="ingestion-import-summary">

            <div className="ingestion-import-summary-header">

              <div>
                <h3>
                  Import Summary
                </h3>

                <p>
                  Active source datasets were
                  successfully synchronized
                  with PostgreSQL.
                </p>
              </div>

              <span className="import-success-badge">
                IMPORT SUCCESS
              </span>

            </div>


            <div className="ingestion-import-stats">

              <div className="import-stat">

                <span>
                  Invoices
                </span>

                <strong>
                  {invoiceImport?.updated ?? 0}
                </strong>

                <small>
                  updated
                </small>

              </div>


              <div className="import-stat">

                <span>
                  Payments
                </span>

                <strong>
                  {paymentImport?.updated ?? 0}
                </strong>

                <small>
                  updated
                </small>

              </div>


              <div className="import-stat">

                <span>
                  Bank Transactions
                </span>

                <strong>
                  {bankImport?.updated ?? 0}
                </strong>

                <small>
                  updated
                </small>

              </div>

            </div>


            <div className="ingestion-import-detail">

              <div>
                <span>
                  Inserted
                </span>

                <strong>
                  {totalInserted}
                </strong>
              </div>


              <div>
                <span>
                  Updated
                </span>

                <strong>
                  {totalUpdated}
                </strong>
              </div>


              <div>
                <span>
                  Skipped
                </span>

                <strong>
                  {totalSkipped}
                </strong>
              </div>

            </div>

          </div>
        )}

      </section>

    </div>
  );
}

export default DataIngestion;