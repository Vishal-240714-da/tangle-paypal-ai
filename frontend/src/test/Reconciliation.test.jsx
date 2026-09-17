
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

import Reconciliation from "../pages/Reconciliation";
import api from "../services/api";

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockItems = [
  {
    invoice_id: "INV-001",
    payment_id: "PAY-001",
    bank_transaction_id: "BANK-001",

    invoice_amount: 10000,
    invoice_currency: "INR",

    payment_amount: 10000,
    payment_currency: "INR",

    bank_amount: 10000,
    bank_currency: "INR",

    invoice_date: "2026-09-01",
    payment_date: "2026-09-02",
    bank_date: "2026-09-02",

    match_type: "EXACT",
    confidence: 0.98,

    rationale:
      "Invoice, payment and bank transaction amounts match exactly.",

    payment_coverage_percent: 100,
    payment_invoice_difference: 0,
    bank_payment_difference: 0,

    pass_status: "PASS",
  },

  {
    invoice_id: "INV-002",
    payment_id: "PAY-002",
    bank_transaction_id: "BANK-002",

    invoice_amount: 20000,
    invoice_currency: "INR",

    payment_amount: 19800,
    payment_currency: "INR",

    bank_amount: 19800,
    bank_currency: "INR",

    invoice_date: "2026-09-03",
    payment_date: "2026-09-04",
    bank_date: "2026-09-04",

    match_type: "FUZZY",
    confidence: 0.87,

    rationale:
      "Payment amount differs slightly from invoice amount.",

    payment_coverage_percent: 99,
    payment_invoice_difference: -200,
    bank_payment_difference: 0,

    pass_status: "PASS",
  },

  {
    invoice_id: "INV-003",
    payment_id: "PAY-003",
    bank_transaction_id: "BANK-003",

    invoice_amount: 30000,
    invoice_currency: "INR",

    payment_amount: 15000,
    payment_currency: "INR",

    bank_amount: 15000,
    bank_currency: "INR",

    invoice_date: "2026-09-05",
    payment_date: "2026-09-06",
    bank_date: "2026-09-06",

    match_type: "MERGED_PAYMENT",
    confidence: 0.76,

    rationale:
      "Multiple payment records were merged to reconcile the invoice.",

    payment_coverage_percent: 50,
    payment_invoice_difference: -15000,
    bank_payment_difference: 0,

    pass_status: "REVIEW",
  },

  {
    invoice_id: "INV-004",
    payment_id: "PAY-004",
    bank_transaction_id: "BANK-004",

    invoice_amount: 40000,
    invoice_currency: "INR",

    payment_amount: 40000,
    payment_currency: "INR",

    bank_amount: 40000,
    bank_currency: "INR",

    invoice_date: "2026-09-07",
    payment_date: "2026-09-08",
    bank_date: "2026-09-08",

    match_type: "EXACT",
    confidence: 0.95,

    rationale:
      "All transaction references and amounts match.",

    payment_coverage_percent: 100,
    payment_invoice_difference: 0,
    bank_payment_difference: 0,

    pass_status: "PASS",
  },
];

const mockSummary = {
  total: 4,
  exact: 2,
  fuzzy: 1,
  merged_payment: 1,
  failed: 0,
  average_confidence: 0.89,
};

const mockReconciliationResponse = {
  items: mockItems,
  summary: mockSummary,
};

function renderReconciliation() {
  return render(<Reconciliation />);
}

describe("Reconciliation", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    api.get.mockResolvedValue({
      data: mockReconciliationResponse,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("shows loading state while reconciliation data is loading", async () => {
    api.get.mockImplementation(
      () =>
        new Promise(() => {
          // Keep request pending.
        })
    );

    renderReconciliation();

    expect(
      screen.getByRole("heading", {
        name: "Reconciliation",
      })
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Loading reconciliation data..."
      )
    ).toBeInTheDocument();

    expect(api.get).toHaveBeenCalledWith(
      "/api/reconciliation"
    );
  });

  test("displays reconciliation summary and records after successful API response", async () => {
    renderReconciliation();

    expect(
      await screen.findByText("INV-001")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Total Records")
    ).toBeInTheDocument();

    expect(
    screen.getByText("Exact", {
        selector: ".stat-label",
    })
    ).toBeInTheDocument();

    expect(
    screen.getByText("Fuzzy", {
        selector: ".stat-label",
    })
    ).toBeInTheDocument();
    expect(
      screen.getByText("Merged Payment", {
        selector: ".stat-label",
      })
    ).toBeInTheDocument();

    expect(
      screen.getByText("Avg Confidence")
    ).toBeInTheDocument();

    expect(
      screen.getByText("4")
    ).toBeInTheDocument();

    expect(
      screen.getByText("2")
    ).toBeInTheDocument();

    expect(
    screen
        .getByText("Fuzzy", {
        selector: ".stat-label",
        })
        .parentElement
    ).toHaveTextContent("1");

    expect(
      screen.getByText("89.0%")
    ).toBeInTheDocument();

    expect(
      screen.getByText("INV-002")
    ).toBeInTheDocument();

    expect(
      screen.getByText("INV-003")
    ).toBeInTheDocument();

    expect(
      screen.getByText("INV-004")
    ).toBeInTheDocument();
  });

  test("displays match types and confidence values correctly", async () => {
    renderReconciliation();

    expect(
      await screen.findByText("INV-001")
    ).toBeInTheDocument();

    expect(
      screen.getAllByText("EXACT").length
    ).toBeGreaterThan(0);

    expect(
      screen.getByText("FUZZY")
    ).toBeInTheDocument();

    expect(
      screen.getByText("MERGED_PAYMENT")
    ).toBeInTheDocument();

    expect(
      screen.getByText("98.0%")
    ).toBeInTheDocument();

    expect(
      screen.getByText("87.0%")
    ).toBeInTheDocument();

    expect(
      screen.getByText("76.0%")
    ).toBeInTheDocument();
  });

  test("filters reconciliation records by match type", async () => {
    const user = userEvent.setup();

    renderReconciliation();

    expect(
      await screen.findByText("INV-001")
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: "Exact",
      })
    );

    expect(
      screen.getByText("INV-001")
    ).toBeInTheDocument();

    expect(
      screen.getByText("INV-004")
    ).toBeInTheDocument();

    expect(
      screen.queryByText("INV-002")
    ).not.toBeInTheDocument();

    expect(
      screen.queryByText("INV-003")
    ).not.toBeInTheDocument();

    const count = document.querySelector(
      ".reconciliation-count"
    );

    expect(count).toHaveTextContent(
      "Showing 1–2 of 2"
    );
  });

  test("filters reconciliation records using the search box", async () => {
    const user = userEvent.setup();

    renderReconciliation();

    expect(
      await screen.findByText("INV-001")
    ).toBeInTheDocument();

    const searchInput = screen.getByRole(
      "textbox",
      {
        name: "Search reconciliation records",
      }
    );

    await user.type(searchInput, "PAY-002");

    expect(
      screen.getByText("INV-002")
    ).toBeInTheDocument();

    expect(
      screen.queryByText("INV-001")
    ).not.toBeInTheDocument();

    expect(
      screen.queryByText("INV-003")
    ).not.toBeInTheDocument();

    expect(
      screen.queryByText("INV-004")
    ).not.toBeInTheDocument();
  });

  test("opens reconciliation details when a row is clicked", async () => {
    const user = userEvent.setup();

    renderReconciliation();

    const invoice = await screen.findByText(
      "INV-001"
    );

    const row = invoice.closest("tr");

    expect(row).toBeInTheDocument();

    await user.click(row);

    expect(
      screen.getByText(
        "RECONCILIATION DETAILS"
      )
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: "INV-001",
      })
    ).toBeInTheDocument();

    expect(
      screen.getByText("MATCH TYPE")
    ).toBeInTheDocument();

    expect(
      screen.getByText("CONFIDENCE")
    ).toBeInTheDocument();

    expect(
      screen.getByText("INVOICE")
    ).toBeInTheDocument();

    expect(
      screen.getByText("PAYMENT")
    ).toBeInTheDocument();

    expect(
      screen.getByText("BANK TRANSACTION")
    ).toBeInTheDocument();

    expect(
    screen.getAllByText(
        "Invoice, payment and bank transaction amounts match exactly."
    ).length
    ).toBeGreaterThan(0);
  });

  test("opens reconciliation details using Enter on a focused row", async () => {
    const user = userEvent.setup();

    renderReconciliation();

    const invoice = await screen.findByText(
      "INV-002"
    );

    const row = invoice.closest("tr");

    expect(row).toBeInTheDocument();

    row.focus();

    await user.keyboard("{Enter}");

    expect(
      screen.getByText(
        "RECONCILIATION DETAILS"
      )
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: "INV-002",
      })
    ).toBeInTheDocument();

    expect(
    screen.getAllByText(
        "Payment amount differs slightly from invoice amount."
    ).length
    ).toBeGreaterThan(0);
  });

  test("displays reconciliation detail metrics correctly", async () => {
    const user = userEvent.setup();

    renderReconciliation();

    const invoice = await screen.findByText(
      "INV-003"
    );

    await user.click(invoice.closest("tr"));

    expect(
      screen.getByText("PAYMENT COVERAGE")
    ).toBeInTheDocument();

    expect(
      screen.getByText("50.0%")
    ).toBeInTheDocument();

    expect(
      screen.getByText("PAYMENT − INVOICE")
    ).toBeInTheDocument();

    expect(
      screen.getByText("-INR 15,000")
    ).toBeInTheDocument();

    expect(
      screen.getByText("BANK − PAYMENT")
    ).toBeInTheDocument();

    expect(
      screen.getByText("INR 0.00")
    ).toBeInTheDocument();

    expect(
      screen.getByText("RECONCILIATION PASS")
    ).toBeInTheDocument();

    expect(
      screen.getByText("PASS REVIEW")
    ).toBeInTheDocument();
  });

  test("closes reconciliation details using the close button", async () => {
    const user = userEvent.setup();

    renderReconciliation();

    const invoice = await screen.findByText(
      "INV-001"
    );

    await user.click(invoice.closest("tr"));

    expect(
      screen.getByText(
        "RECONCILIATION DETAILS"
      )
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: "Close details",
      })
    );

    expect(
      screen.queryByText(
        "RECONCILIATION DETAILS"
      )
    ).not.toBeInTheDocument();
  });

  test("shows error message when reconciliation API fails", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    api.get.mockRejectedValue(
      new Error(
        "Reconciliation API request failed"
      )
    );

    renderReconciliation();

    expect(
      await screen.findByText(
        "Unable to load reconciliation data."
      )
    ).toBeInTheDocument();

    expect(
      consoleErrorSpy
    ).toHaveBeenCalled();

    expect(
      screen.queryByText(
        "INV-001"
      )
    ).not.toBeInTheDocument();

    consoleErrorSpy.mockRestore();
  });
});
