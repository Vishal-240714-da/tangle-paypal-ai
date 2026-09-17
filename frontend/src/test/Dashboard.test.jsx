import { describe, expect, test, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

import Dashboard from "../pages/Dashboard";
import api from "../services/api";

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("Dashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("shows loading state while dashboard data is loading", () => {
    api.get.mockReturnValue(new Promise(() => {}));

    render(<Dashboard />);

    expect(
      screen.getByText("Loading dashboard...")
    ).toBeInTheDocument();
  });

  test("displays dashboard data after successful API response", async () => {
    api.get.mockResolvedValue({
      data: {
        total_cases: 202,
        critical_cases: 25,
        high_risk_cases: 40,
        human_review: 197,
        outstanding_balance: 125000,
        average_payment_coverage: 82.5,
        resolved_or_approved: 150,
      },
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(
        screen.getByText("TANGLE Dashboard")
      ).toBeInTheDocument();
    });

    expect(screen.getByText("202")).toBeInTheDocument();
    expect(screen.getByText("25")).toBeInTheDocument();
    expect(screen.getByText("40")).toBeInTheDocument();
    expect(screen.getByText("197")).toBeInTheDocument();

    expect(
    screen.getByText("Outstanding Balance")
    ).toBeInTheDocument();

    expect(
    screen.getByText("Outstanding Balance")
        .parentElement
    ).toHaveTextContent("$1,25,000");

    expect(
    screen.getByText("Payment Coverage")
        .parentElement
    ).toHaveTextContent("82.5%");

    expect(screen.getByText("150")).toBeInTheDocument();

    expect(api.get).toHaveBeenCalledWith(
      "/api/dashboard/summary"
    );
  });

  test("shows error message when dashboard API fails", async () => {
    api.get.mockRejectedValue(
        new Error("API request failed")
        );

    const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

        render(<Dashboard />);

    await waitFor(() => {
        expect(
            screen.getByText("Unable to load dashboard data.")
        ).toBeInTheDocument();
        });

    expect(consoleErrorSpy).toHaveBeenCalled();

    consoleErrorSpy.mockRestore();
  });
});