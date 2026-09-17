import { describe, expect, test, vi, beforeEach } from "vitest";
import {
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import Cases from "../pages/Cases";
import api from "../services/api";

const mockNavigate = vi.fn();

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");

  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("Cases", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("shows loading state while cases are loading", () => {
    api.get.mockReturnValue(new Promise(() => {}));

    render(<Cases />);

    expect(
      screen.getByText("Loading TANGLE cases...")
    ).toBeInTheDocument();
  });

  test("displays cases after successful API response", async () => {
    api.get.mockResolvedValue({
      data: {
        items: [
          {
            case_id: "CASE-001",
            category: "Financial",
            record_type: "Invoice",
            invoice_id: "INV-001",
            record_id: "REC-001",
            financial_status: "Outstanding",
            outstanding_amount: 125000,
            payment_coverage_percent: 82.5,
            decision: "REVIEW",
          },
          {
            case_id: "CASE-002",
            category: "Duplicate",
            record_type: "Payment",
            invoice_id: "INV-002",
            record_id: "REC-002",
            financial_status: "Paid",
            outstanding_amount: 5000,
            payment_coverage_percent: 100,
            decision: "APPROVE",
          },
        ],
      },
    });

    render(<Cases />);

    await waitFor(() => {
      expect(
        screen.getByText("CASE-001")
      ).toBeInTheDocument();
    });

    expect(
      screen.getByText("CASE-002")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Financial")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Duplicate")
    ).toBeInTheDocument();
    const casesCount = document.querySelector(".cases-count");

    expect(casesCount).toBeInTheDocument();
    expect(casesCount).toHaveTextContent("Showing 2 of 2 cases");

    expect(
      api.get
    ).toHaveBeenCalledWith("/api/cases");
  });

  test("filters cases using the search box", async () => {
    const user = userEvent.setup();

    api.get.mockResolvedValue({
      data: {
        items: [
          {
            case_id: "CASE-001",
            category: "Financial",
            record_type: "Invoice",
            invoice_id: "INV-001",
            record_id: "REC-001",
            financial_status: "Outstanding",
            outstanding_amount: 125000,
            payment_coverage_percent: 82.5,
            decision: "REVIEW",
          },
          {
            case_id: "CASE-002",
            category: "Duplicate",
            record_type: "Payment",
            invoice_id: "INV-002",
            record_id: "REC-002",
            financial_status: "Paid",
            outstanding_amount: 5000,
            payment_coverage_percent: 100,
            decision: "APPROVE",
          },
        ],
      },
    });

    render(<Cases />);

    await waitFor(() => {
      expect(
        screen.getByText("CASE-001")
      ).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(
      "Search by case, invoice, record, category..."
    );

    await user.type(searchInput, "CASE-002");

    expect(
      screen.getByText("CASE-002")
    ).toBeInTheDocument();

    expect(
      screen.queryByText("CASE-001")
    ).not.toBeInTheDocument();
  });

  test("shows error message when cases API fails", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    api.get.mockRejectedValue(
      new Error("API request failed")
    );

    render(<Cases />);

    await waitFor(() => {
      expect(
        screen.getByText(
          "Unable to load cases. Please make sure the FastAPI backend is running."
        )
      ).toBeInTheDocument();
    });

    expect(
      consoleErrorSpy
    ).toHaveBeenCalled();

    consoleErrorSpy.mockRestore();
  });

  test("navigates to investigation when Investigate is clicked", async () => {
    const user = userEvent.setup();

    api.get.mockResolvedValue({
      data: {
        items: [
          {
            case_id: "CASE-001",
            category: "Financial",
            record_type: "Invoice",
            invoice_id: "INV-001",
            record_id: "REC-001",
            financial_status: "Outstanding",
            outstanding_amount: 125000,
            payment_coverage_percent: 82.5,
            decision: "REVIEW",
          },
        ],
      },
    });

    render(<Cases />);

    await waitFor(() => {
      expect(
        screen.getByText("CASE-001")
      ).toBeInTheDocument();
    });

    const investigateButton =
      screen.getByRole("button", {
        name: "Investigate",
      });

    await user.click(investigateButton);

    expect(mockNavigate).toHaveBeenCalledWith(
      "/investigation/CASE-001"
    );
  });
});