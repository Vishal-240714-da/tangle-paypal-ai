import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

import Review from "../pages/Review";
import api from "../services/api";

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockPendingReviews = [
  {
    case_id: "CASE-001",
    risk_level: "HIGH",
    category: "PAYMENT_MISMATCH",
    priority: null,
    record_id: "PAY-001",
    record_type: "PAYMENT",
    status: "OPEN",
    invoice_id: "INV-001",
    financial_status: "MISMATCH",
    outstanding_amount: 25000,
    payment_coverage: 75,

    ai_investigation: {
      summary: "Invoice payment mismatch detected.",
      reasoning: [
        "Payment amount does not match invoice amount.",
        "Transaction requires human review.",
      ],
      evidence: [
        "Invoice INV-001",
        "Payment PAY-001",
      ],
      confidence: 0.91,
    },

    risk: {
      risk_level: "HIGH",
      human_review_required: true,
      risk_score: 82,
    },

    reviewer_decision: null,
    reviewer_comment: null,
  },

  {
    case_id: "CASE-002",
    risk_level: "MEDIUM",
    category: "UNMATCHED_TRANSACTION",
    priority: null,
    record_id: "BANK-002",
    record_type: "BANK_TRANSACTION",
    status: "OPEN",
    invoice_id: "INV-002",
    financial_status: "UNMATCHED",
    outstanding_amount: 10000,
    payment_coverage: 50,

    ai_investigation: {
      summary: "Unmatched bank transaction detected.",
      reasoning: [
        "Bank transaction could not be reconciled.",
      ],
      evidence: [
        "Bank transaction BANK-002",
      ],
      confidence: 0.78,
    },

    risk: {
      risk_level: "MEDIUM",
      human_review_required: true,
      risk_score: 60,
    },

    reviewer_decision: null,
    reviewer_comment: null,
  },
];

const mockSummary = {
  pending: 2,
  completed: 10,
  approved: 7,
  escalated: 3,
};

function renderReview() {
  return render(
    <MemoryRouter>
      <Review />
    </MemoryRouter>
  );
}

describe("Review", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    api.get.mockImplementation((url) => {
      if (url === "/api/reviews/pending") {
        return Promise.resolve({
          data: mockPendingReviews,
        });
      }

      if (url === "/api/reviews/summary") {
        return Promise.resolve({
          data: mockSummary,
        });
      }

      return Promise.reject(
        new Error(`Unexpected GET request: ${url}`)
      );
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("shows loading state while review data is loading", async () => {
    api.get.mockImplementation(
      () =>
        new Promise(() => {
          // Keep request pending.
        })
    );

    renderReview();

    expect(
      screen.getByText("Loading human review workspace...")
    ).toBeInTheDocument();
  });

  test("displays human review workspace after successful API response", async () => {
    renderReview();

    expect(
      await screen.findByText("Human Review Workspace")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Pending Review")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Completed")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Approved")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Escalated")
    ).toBeInTheDocument();

    /*
     * Check the summary cards directly instead of searching
     * globally for numeric text such as "2".
     */
    const metricValues = document.querySelectorAll(
      ".review-summary-grid .review-metric-value"
    );

    expect(metricValues).toHaveLength(4);

    expect(metricValues[0]).toHaveTextContent("2");
    expect(metricValues[1]).toHaveTextContent("10");
    expect(metricValues[2]).toHaveTextContent("7");
    expect(metricValues[3]).toHaveTextContent("3");

    expect(
      screen.getByRole("button", {
        name: /CASE-001/,
      })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: /CASE-002/,
      })
    ).toBeInTheDocument();
  });

  test("selects another case from the review queue", async () => {
    const user = userEvent.setup();

    renderReview();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /CASE-001/,
        })
      ).toBeInTheDocument();
    });

    const caseTwoButton = screen.getByRole("button", {
      name: /CASE-002/,
    });

    await user.click(caseTwoButton);

    /*
     * "Unmatched Transaction" appears in both the queue
     * and the selected case heading, so use the heading.
     */
    expect(
      screen.getByRole("heading", {
        name: "Unmatched Transaction",
      })
    ).toBeInTheDocument();

    expect(
        screen.getByRole("heading", {
            name: "Unmatched Transaction",
        }).parentElement
    ).toHaveTextContent("BANK-002");
  });

  test("changes reviewer decision", async () => {
    const user = userEvent.setup();

    renderReview();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /CASE-001/,
        })
      ).toBeInTheDocument();
    });

    const rejectButton = screen.getByRole("button", {
      name: /Reject/,
    });

    await user.click(rejectButton);

    expect(
      rejectButton
    ).toBeInTheDocument();

    expect(
      screen.getByText("REJECT")
    ).toBeInTheDocument();
  });

  test("updates analyst comment", async () => {
    const user = userEvent.setup();

    renderReview();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /CASE-001/,
        })
      ).toBeInTheDocument();
    });

    const commentBox = screen.getByLabelText(
      "Analyst Comment"
    );

    await user.clear(commentBox);

    await user.type(
      commentBox,
      "Payment details verified and approved."
    );

    expect(commentBox).toHaveValue(
      "Payment details verified and approved."
    );
  });

  test("submits human decision successfully", async () => {
    const user = userEvent.setup();

    api.post.mockResolvedValue({
      data: {
        case_id: "CASE-001",
        reviewer_decision: "APPROVE",
        reviewer_comment:
          "Payment details verified and approved.",
      },
    });

    renderReview();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /CASE-001/,
        })
      ).toBeInTheDocument();
    });

    const commentBox = screen.getByLabelText(
      "Analyst Comment"
    );

    await user.clear(commentBox);

    await user.type(
      commentBox,
      "Payment details verified and approved."
    );

    const submitButton = screen.getByRole("button", {
      name: /Submit Human Decision/,
    });

    await user.click(submitButton);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith(
        "/api/reviews/CASE-001",
        {
          reviewer_decision: "APPROVE",
          reviewer_comment:
            "Payment details verified and approved.",
        }
      );
    });

    expect(
      await screen.findByText("Decision Recorded")
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Decision recorded successfully for CASE-001."
      )
    ).toBeInTheDocument();
  });

  test("opens full investigation for selected case", async () => {
    const user = userEvent.setup();

    renderReview();

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /CASE-001/,
        })
      ).toBeInTheDocument();
    });

    const investigationButton = screen.getByRole(
      "button",
      {
        name: /Open Full Investigation/,
      }
    );

    expect(
      investigationButton
    ).toBeInTheDocument();

    await user.click(investigationButton);

    expect(
      investigationButton
    ).toBeInTheDocument();
  });

  test("shows error message when review API fails", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    api.get.mockRejectedValue(
      new Error("Review API request failed")
    );

    renderReview();

    expect(
      await screen.findByText("Review Error")
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Unable to load human review data."
      )
    ).toBeInTheDocument();

    expect(
      consoleErrorSpy
    ).toHaveBeenCalled();

    consoleErrorSpy.mockRestore();
  });
});