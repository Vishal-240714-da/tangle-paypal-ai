
import {
  describe,
  expect,
  test,
  vi,
  beforeEach,
  afterEach,
} from "vitest";

import {
  render,
  screen,
  waitFor,
} from "@testing-library/react";

import userEvent from "@testing-library/user-event";

import DataQuality from "../pages/DataQuality";
import api from "../services/api";

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockDataQuality = {
  quality_score: 92.5,

  total_records: 1000,
  valid_records: 920,
  warnings: 60,
  errors: 20,

  issue_summary: {
    DUPLICATE_RECORD: 2,
    MISSING_ID: 1,
    INVALID_AMOUNT: 0,
    INVALID_DATE: 3,
    MISSING_RELATIONSHIP: 0,
    NEGATIVE_VALUE: 4,
    CURRENCY_PROBLEM: 0,
    MALFORMED_RECORD: 1,
  },

  datasets: {
    invoices: {
      total_records: 500,
      valid_records: 480,
      warnings: 15,
      errors: 5,
    },

    payments: {
      total_records: 300,
      valid_records: 270,
      warnings: 20,
      errors: 10,
    },

    bank_transactions: {
      total_records: 200,
      valid_records: 170,
      warnings: 25,
      errors: 5,
    },
  },

  issues: [
    {
      dataset: "invoices",
      record_id: "INV-001",
      severity: "ERROR",
      issue_type: "INVALID_AMOUNT",
      message: "Invoice amount is invalid.",
    },
    {
      dataset: "payments",
      record_id: "PAY-002",
      severity: "WARNING",
      issue_type: "MISSING_ID",
      message: "Payment ID is missing.",
    },
  ],
};

function renderDataQuality() {
  return render(<DataQuality />);
}

describe("DataQuality", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    api.get.mockResolvedValue({
      data: mockDataQuality,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("shows loading state while data quality is loading", async () => {
    api.get.mockImplementation(
      () =>
        new Promise(() => {
          // Keep request pending.
        })
    );

    renderDataQuality();

    expect(
      screen.getByText("Data Quality")
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Running data quality checks..."
      )
    ).toBeInTheDocument();

    expect(api.get).toHaveBeenCalledWith(
      "/api/data-quality"
    );
  });

  test("displays data quality information after successful API response", async () => {
    renderDataQuality();

    expect(
      await screen.findByText("92.5%")
    ).toBeInTheDocument();

    expect(
      screen.getByText("DATA QUALITY")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Total Records")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Valid Records")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Warnings")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Errors")
    ).toBeInTheDocument();

    expect(
      screen.getByText("1000")
    ).toBeInTheDocument();

    expect(
      screen.getByText("920")
    ).toBeInTheDocument();

    expect(
      screen.getByText("60")
    ).toBeInTheDocument();

    expect(
      screen.getByText("20")
    ).toBeInTheDocument();
  });

  test("displays quality checks with correct pass and review status", async () => {
    renderDataQuality();

    expect(
      await screen.findByText("Quality Checks")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Duplicate Records")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Missing IDs")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Invalid Amounts")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Invalid Dates")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Missing Relationships")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Negative Values")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Currency Problems")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Malformed Records")
    ).toBeInTheDocument();

    expect(
      screen.getAllByText("PASS").length
    ).toBeGreaterThan(0);

    expect(
      screen.getAllByText("REVIEW").length
    ).toBeGreaterThan(0);

    expect(
      screen.getByText("2 issues detected")
    ).toBeInTheDocument();

    expect(
        screen.getAllByText("1 issue detected").length
    ).toBe(2);
  });

  test("displays source datasets and calculated quality percentages", async () => {
    renderDataQuality();

    expect(
      await screen.findByText("Source Datasets")
    ).toBeInTheDocument();

    const invoicesCard = screen
      .getByRole("heading", {
        name: "Invoices",
      })
      .closest(".dq-dataset-card");

    const paymentsCard = screen
      .getByRole("heading", {
        name: "Payments",
      })
      .closest(".dq-dataset-card");

    const bankTransactionsCard = screen
      .getByRole("heading", {
        name: "Bank Transactions",
      })
      .closest(".dq-dataset-card");

    expect(invoicesCard).toBeInTheDocument();
    expect(paymentsCard).toBeInTheDocument();
    expect(bankTransactionsCard).toBeInTheDocument();

    /*
     * invoices:
     * 480 / 500 * 100 = 96%
     *
     * payments:
     * 270 / 300 * 100 = 90%
     *
     * bank transactions:
     * 170 / 200 * 100 = 85%
     */

    expect(
      screen.getByText("96.0%")
    ).toBeInTheDocument();

    expect(
      screen.getByText("90.0%")
    ).toBeInTheDocument();

    expect(
      screen.getByText("85.0%")
    ).toBeInTheDocument();

    expect(invoicesCard).toHaveTextContent("480");
    expect(invoicesCard).toHaveTextContent("valid");
    expect(invoicesCard).toHaveTextContent("500");
    expect(invoicesCard).toHaveTextContent("total");

    expect(paymentsCard).toHaveTextContent("270");
    expect(paymentsCard).toHaveTextContent("valid");
    expect(paymentsCard).toHaveTextContent("300");
    expect(paymentsCard).toHaveTextContent("total");

    expect(bankTransactionsCard).toHaveTextContent("170");
    expect(bankTransactionsCard).toHaveTextContent("valid");
    expect(bankTransactionsCard).toHaveTextContent("200");
    expect(bankTransactionsCard).toHaveTextContent("total");
  });

  test("displays detected issues", async () => {
    renderDataQuality();

    expect(
      await screen.findByText("Detected Issues")
    ).toBeInTheDocument();

    expect(
      screen.getByText("2 issues")
    ).toBeInTheDocument();

    expect(
      screen.getByText("INV-001")
    ).toBeInTheDocument();

    expect(
      screen.getByText("PAY-002")
    ).toBeInTheDocument();

    expect(
      screen.getByText("ERROR")
    ).toBeInTheDocument();

    expect(
      screen.getByText("WARNING")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Invoice amount is invalid.")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Payment ID is missing.")
    ).toBeInTheDocument();

    expect(
      screen.getByText("INVALID AMOUNT")
    ).toBeInTheDocument();

    expect(
      screen.getByText("MISSING ID")
    ).toBeInTheDocument();
  });

  test("refreshes data quality check when Refresh Check is clicked", async () => {
    const user = userEvent.setup();

    api.get
      .mockResolvedValueOnce({
        data: mockDataQuality,
      })
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                data: {
                  ...mockDataQuality,
                  quality_score: 95.5,
                },
              });
            }, 100);
          })
      );

    renderDataQuality();

    expect(
      await screen.findByText("92.5%")
    ).toBeInTheDocument();

    const refreshButton = screen.getByRole(
      "button",
      {
        name: "Refresh Check",
      }
    );

    await user.click(refreshButton);

    expect(
      screen.getByRole("button", {
        name: "Checking...",
      })
    ).toBeDisabled();

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledTimes(2);
    });

    expect(
      await screen.findByText("95.5%")
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: "Refresh Check",
      })
    ).not.toBeDisabled();
  });

  test("shows error message when data quality API fails", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    api.get.mockRejectedValue(
      new Error("Data quality API request failed")
    );

    renderDataQuality();

    expect(
      await screen.findByText(
        "Unable to load data quality information. Please make sure the FastAPI backend is running."
      )
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: "Try Again",
      })
    ).toBeInTheDocument();

    expect(
      consoleErrorSpy
    ).toHaveBeenCalled();

    consoleErrorSpy.mockRestore();
  });

    test("retries data quality check from the error state", async () => {
    const user = userEvent.setup();

    const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

    api.get
        .mockRejectedValueOnce(
        new Error("Initial request failed")
        )
        .mockResolvedValueOnce({
        data: mockDataQuality,
        });

    renderDataQuality();

    expect(
        await screen.findByRole("button", {
        name: "Try Again",
        })
    ).toBeInTheDocument();

    await user.click(
        screen.getByRole("button", {
        name: "Try Again",
        })
    );

    expect(
        await screen.findByText("92.5%")
    ).toBeInTheDocument();

    expect(api.get).toHaveBeenCalledTimes(2);

    expect(api.get).toHaveBeenNthCalledWith(
        1,
        "/api/data-quality"
    );

    expect(api.get).toHaveBeenNthCalledWith(
        2,
        "/api/data-quality"
    );

    consoleErrorSpy.mockRestore();
    });
});
