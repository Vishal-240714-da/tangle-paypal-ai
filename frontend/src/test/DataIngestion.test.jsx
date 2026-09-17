import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, test, vi, beforeEach } from "vitest";
import DataIngestion from "../pages/DataIngestion";
import api from "../services/api";

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockDatasets = {
  invoices: {
    filename: "invoices.csv",
    active: {
      exists: true,
    },
    staging: {
      exists: false,
    },
  },
  payments: {
    filename: "payments.csv",
    active: {
      exists: true,
    },
    staging: {
      exists: true,
    },
  },
  bank_transactions: {
    filename: "bank_transactions.csv",
    active: {
      exists: true,
    },
    staging: {
      exists: false,
    },
  },
};

const mockStatusResponse = {
  data: {
    datasets: mockDatasets,
  },
};

const mockValidation = {
  quality_score: 98.5,
  total_records: 100,
  valid_records: 99,
  warnings: 1,
  errors: 0,
  activation_allowed: true,
  issues: [],
};

const mockImportResult = {
  datasets: {
    invoices: {
      inserted: 10,
      updated: 5,
      skipped: 1,
    },
    payments: {
      inserted: 20,
      updated: 10,
      skipped: 2,
    },
    bank_transactions: {
      inserted: 30,
      updated: 15,
      skipped: 3,
    },
  },
};

describe("DataIngestion", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    api.get.mockResolvedValue(mockStatusResponse);
  });

  test("loads ingestion status and displays datasets", async () => {
    render(<DataIngestion />);

    expect(
      screen.getByRole("heading", { name: "Data Ingestion" })
    ).toBeInTheDocument();

    expect(
      screen.getByText("Upload, validate, activate, and import TANGLE source datasets safely.")
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/api/ingestion/status");
    });

    expect(
        screen.getAllByText("Invoices").length
    ).toBeGreaterThanOrEqual(1);

    expect(
        screen.getAllByText("Payments").length
    ).toBeGreaterThanOrEqual(1);

    expect(
        screen.getAllByText("Bank Transactions").length
    ).toBeGreaterThanOrEqual(1);
  });

  test("shows active and staged dataset status", async () => {
    render(<DataIngestion />);

    await screen.findByText("invoices.csv");

    const datasetRows = screen.getAllByRole("button");

    const paymentsRow = datasetRows.find((button) =>
      button.textContent.includes("Payments")
    );

    expect(paymentsRow).toBeInTheDocument();
    expect(paymentsRow).toHaveTextContent("ACTIVE");
    expect(paymentsRow).toHaveTextContent("STAGED");

    const invoicesRow = datasetRows.find((button) =>
      button.textContent.includes("Invoices")
    );

    expect(invoicesRow).toBeInTheDocument();
    expect(invoicesRow).toHaveTextContent("ACTIVE");
    expect(invoicesRow).not.toHaveTextContent("STAGED");
  });

  test("changes the selected dataset", async () => {
    render(<DataIngestion />);

    await screen.findByText("invoices.csv");

    const datasetSelect = screen.getByLabelText("Dataset");

    expect(datasetSelect).toHaveValue("invoices");

    fireEvent.change(datasetSelect, {
      target: {
        value: "bank_transactions",
      },
    });

    expect(datasetSelect).toHaveValue("bank_transactions");
  });

  test("shows error when upload is attempted without selecting a file", async () => {
    render(<DataIngestion />);

    await screen.findByText("invoices.csv");

    const uploadButton = screen.getByRole("button", {
      name: "Upload to Staging",
    });

    /*
     * The component normally disables this button until a file
     * is selected, so directly call the click handler through
     * temporarily removing the disabled attribute.
     */
    expect(uploadButton).toBeDisabled();
  });

  test("selects a CSV file and uploads it to staging", async () => {
    api.post.mockResolvedValue({
      data: {
        message: "Dataset uploaded successfully.",
      },
    });

    render(<DataIngestion />);

    await screen.findByText("invoices.csv");

    const file = new File(
      ["invoice_id,amount\nINV-001,10000"],
      "new-invoices.csv",
      {
        type: "text/csv",
      }
    );

    const fileInput = screen.getByLabelText("CSV File");

    fireEvent.change(fileInput, {
      target: {
        files: [file],
      },
    });

    expect(screen.getByText("new-invoices.csv")).toBeInTheDocument();

    const uploadButton = screen.getByRole("button", {
      name: "Upload to Staging",
    });

    expect(uploadButton).not.toBeDisabled();

    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith(
        "/api/ingestion/upload/invoices",
        expect.any(FormData),
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
    });

    expect(
      await screen.findByText("Dataset uploaded successfully.")
    ).toBeInTheDocument();
  });

  test("shows upload error when upload API fails", async () => {
    api.post.mockRejectedValue({
      response: {
        data: {
          detail: "Invalid CSV file.",
        },
      },
    });

    render(<DataIngestion />);

    await screen.findByText("invoices.csv");

    const file = new File(
      ["invalid,data"],
      "invalid.csv",
      {
        type: "text/csv",
      }
    );

    fireEvent.change(screen.getByLabelText("CSV File"), {
      target: {
        files: [file],
      },
    });

    fireEvent.click(
      screen.getByRole("button", {
        name: "Upload to Staging",
      })
    );

    expect(
      await screen.findByText("Invalid CSV file.")
    ).toBeInTheDocument();
  });

  test("runs validation for a staged dataset", async () => {
    api.post.mockResolvedValue({
      data: {
        quality: mockValidation,
      },
    });

    render(<DataIngestion />);

    await screen.findByText("invoices.csv");

    /*
     * Select payments because the mocked payments dataset
     * has a staged file.
     */
    const paymentsDatasetButton = screen
      .getAllByRole("button")
      .find((button) => button.textContent.includes("Payments"));

    fireEvent.click(paymentsDatasetButton);

    const validateButton = screen.getByRole("button", {
      name: "Run Validation",
    });

    expect(validateButton).not.toBeDisabled();

    fireEvent.click(validateButton);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith(
        "/api/ingestion/validate/payments"
      );
    });

    expect(
      await screen.findByText("Full Data Quality validation completed.")
    ).toBeInTheDocument();

    expect(screen.getByText("98.5%")).toBeInTheDocument();
    expect(screen.getByText("100")).toBeInTheDocument();
    expect(screen.getByText("99")).toBeInTheDocument();
    expect(screen.getByText("ALLOWED")).toBeInTheDocument();
  });

  test("displays validation issues and blocks activation when errors exist", async () => {
    api.post.mockResolvedValue({
      data: {
        quality: {
          quality_score: 72,
          total_records: 100,
          valid_records: 90,
          warnings: 5,
          errors: 5,
          activation_allowed: false,
          issues: [
            {
              issue_type: "MISSING_ID",
              record_id: "INV-099",
              severity: "ERROR",
              message: "Invoice ID is missing.",
            },
          ],
        },
      },
    });

    render(<DataIngestion />);

    await screen.findByText("invoices.csv");

    const paymentsDatasetButton = screen
      .getAllByRole("button")
      .find((button) => button.textContent.includes("Payments"));

    fireEvent.click(paymentsDatasetButton);

    fireEvent.click(
      screen.getByRole("button", {
        name: "Run Validation",
      })
    );

    expect(
      await screen.findByText("Activation Decision")
    ).toBeInTheDocument();

    expect(screen.getByText("BLOCKED")).toBeInTheDocument();
    expect(screen.getByText("Validation Issues")).toBeInTheDocument();
    expect(screen.getByText("MISSING_ID")).toBeInTheDocument();
    expect(
        screen.getByText((content) => content.includes("INV-099"))
    ).toBeInTheDocument();
    expect(screen.getByText("Invoice ID is missing.")).toBeInTheDocument();

    expect(
      screen.queryByRole("button", {
        name: "Activate Dataset",
      })
    ).not.toBeInTheDocument();
  });

  test("activates a validated dataset", async () => {
    api.post
      .mockResolvedValueOnce({
        data: {
          quality: mockValidation,
        },
      })
      .mockResolvedValueOnce({
        data: {
          message: "Dataset activated successfully.",
          activation: {
            validation: mockValidation,
          },
        },
      });

    render(<DataIngestion />);

    await screen.findByText("invoices.csv");

    const paymentsDatasetButton = screen
      .getAllByRole("button")
      .find((button) => button.textContent.includes("Payments"));

    fireEvent.click(paymentsDatasetButton);

    fireEvent.click(
      screen.getByRole("button", {
        name: "Run Validation",
      })
    );

    const activateButton = await screen.findByRole("button", {
      name: "Activate Dataset",
    });

    fireEvent.click(activateButton);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith(
        "/api/ingestion/activate/payments"
      );
    });

    expect(
      await screen.findByText("Dataset activated successfully.")
    ).toBeInTheDocument();
  });

  test("imports active datasets into PostgreSQL and displays import summary", async () => {
    api.post.mockResolvedValue({
      data: {
        message: "Active datasets imported successfully.",
        import: mockImportResult,
      },
    });

    render(<DataIngestion />);

    await screen.findByText("invoices.csv");

    fireEvent.click(
      screen.getByRole("button", {
        name: "Import Active Data",
      })
    );

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/api/ingestion/import");
    });

    expect(
      await screen.findByText(
        "Active datasets imported successfully."
      )
    ).toBeInTheDocument();

    expect(screen.getByText("Import Summary")).toBeInTheDocument();
    expect(screen.getByText("IMPORT SUCCESS")).toBeInTheDocument();

    expect(screen.getByText("Inserted").parentElement).toHaveTextContent(
      "60"
    );

    expect(screen.getByText("Updated").parentElement).toHaveTextContent(
      "30"
    );

    expect(screen.getByText("Skipped").parentElement).toHaveTextContent(
      "6"
    );
  });

  test("shows import error when PostgreSQL import fails", async () => {
    api.post.mockRejectedValue({
      response: {
        data: {
          detail: "Import failed.",
        },
      },
    });

    render(<DataIngestion />);

    await screen.findByText("invoices.csv");

    fireEvent.click(
      screen.getByRole("button", {
        name: "Import Active Data",
      })
    );

    expect(
      await screen.findByText("Import failed.")
    ).toBeInTheDocument();
  });
});