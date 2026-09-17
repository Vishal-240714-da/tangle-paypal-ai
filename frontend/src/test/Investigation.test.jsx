import { describe, expect, test, vi, beforeEach } from "vitest";
import {
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import Investigation from "../pages/Investigation";
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
    useParams: () => ({
      caseId: "CASE-001",
    }),
    useNavigate: () => mockNavigate,
  };
});

describe("Investigation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("shows loading state while investigation is loading", () => {
    api.get.mockReturnValue(new Promise(() => {}));

    render(<Investigation />);

    expect(
      screen.getByText(
        "Loading investigation for CASE-001..."
      )
    ).toBeInTheDocument();
  });

  test("displays investigation data after successful API response", async () => {
    api.get.mockResolvedValue({
      data: {
        case: {
          case_id: "CASE-001",
          record_type: "Invoice",
          record_id: "REC-001",
          invoice_id: "INV-001",
          payment_id: "PAY-001",
          category: "Financial",
          status: "OPEN",
          decision: "REVIEW",
          confidence: 0.92,
        },

        financial: {
          currency: "INR",
          invoice_amount: 125000,
          payment_amount: 100000,
          bank_amount: 100000,
          outstanding_amount: 25000,
          payment_coverage_percent: 80,
          invoice_payment_difference: 25000,
          bank_payment_difference: 0,
          payment_fee: 500,
          financial_status: "Outstanding",
          financial_impact: "HIGH",
        },

        ai_investigation: {
          confidence: 0.92,
          finding: "Invoice payment mismatch detected.",
          rationale: "Invoice amount exceeds payment amount.",
          likely_cause: "Partial payment.",
          recommendation: "Send case for human review.",
          reasoning: [
            "Invoice amount was identified.",
            "Payment amount was compared.",
            "Outstanding balance was calculated.",
          ],
          evidence: [
            {
              source: "Invoice",
              label: "Invoice Amount",
              value: "₹1,25,000",
            },
            {
              source: "Payment",
              label: "Payment Amount",
              value: "₹1,00,000",
            },
          ],
          evidence_summary:
            "Financial records indicate a payment mismatch.",
        },

        risk: {
          risk_level: "HIGH",
          risk_score: 85,
          priority_score: 90,
          human_review_required: true,
          risk_reason: "Significant payment mismatch.",
        },

        review: {
          case_status: "OPEN",
          review_status: "PENDING",
          reviewer: "TANGLE Reviewer",
          reviewer_decision: "PENDING",
          final_status: "PENDING",
          comment: "Awaiting human review.",
        },
      },
    });

    render(<Investigation />);

    await waitFor(() => {
      expect(
        screen.getByText("CASE-001")
      ).toBeInTheDocument();
    });

    expect(
      screen.getByText("Transaction Information")
    ).toBeInTheDocument();

    expect(
      screen.getByText("REC-001")
    ).toBeInTheDocument();

    expect(
      screen.getByText("INV-001")
    ).toBeInTheDocument();

    expect(
      screen.getByText("PAY-001")
    ).toBeInTheDocument();

    expect(
        screen.getAllByText("Financial").length
    ).toBeGreaterThan(0);

    expect(
      screen.getByText("Financial Analysis")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Outstanding")
    ).toBeInTheDocument();

    expect(
      screen.getByText("AI Investigation")
    ).toBeInTheDocument();

    expect(
        screen.getAllByText(
            "Invoice payment mismatch detected."
        ).length
    ).toBeGreaterThan(0);

    expect(
        screen.getAllByText(
            "Send case for human review."
        ).length
    ).toBeGreaterThan(0);

    expect(
      screen.getByText(
        "Invoice amount was identified."
      )
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Payment amount was compared."
      )
    ).toBeInTheDocument();

    expect(
      screen.getByText("Evidence Used")
    ).toBeInTheDocument();

    expect(
      screen.getByText("₹1,25,000")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Risk Assessment")
    ).toBeInTheDocument();

    expect(
        screen.getAllByText("HIGH").length
    ).toBeGreaterThan(0);

    expect(
      screen.getByText("Governance & Review")
    ).toBeInTheDocument();

    expect(
      screen.getByText("TANGLE Reviewer")
    ).toBeInTheDocument();

    expect(
      api.get
    ).toHaveBeenCalledWith(
      "/api/investigation/CASE-001"
    );
  });

  test("shows error message when investigation API fails", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    api.get.mockRejectedValue(
      new Error("API request failed")
    );

    render(<Investigation />);

    await waitFor(() => {
      expect(
        screen.getByText(
          "Unable to load investigation data."
        )
      ).toBeInTheDocument();
    });

    expect(
      screen.getByRole("button", {
        name: "← Back to Cases",
      })
    ).toBeInTheDocument();

    expect(
      consoleErrorSpy
    ).toHaveBeenCalled();

    consoleErrorSpy.mockRestore();
  });

  test("navigates back to cases from the error state", async () => {
    const user = userEvent.setup();

    api.get.mockRejectedValue(
      new Error("API request failed")
    );

    render(<Investigation />);

    const backButton = await screen.findByRole(
      "button",
      {
        name: "← Back to Cases",
      }
    );

    await user.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith(
      "/cases"
    );
  });
});