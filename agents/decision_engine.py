
# ============================================================
# TANGLE DECISION ENGINE
# ============================================================

"""
Business Decision Engine for TANGLE.

This module converts the Investigation Agent's findings
into a business-level decision.

Decision hierarchy:

    RECONCILE
        ↓
    Known transaction is safely reconciled.

    INVESTIGATE
        ↓
    Known exception requires human investigation.

    ESCALATE
        ↓
    System cannot confidently determine what happened.
"""


# ============================================================
# DECISION RULES
# ============================================================

DECISION_RULES = {

    # --------------------------------------------------------
    # SUCCESSFUL RECONCILIATION
    # --------------------------------------------------------

    "FULL_RECONCILIATION": {
        "decision": "RECONCILE",
        "reason":
            "Invoice, payment and bank transaction amounts match.",
        "next_action":
            "Close the reconciliation case."
    },

    "FEE_ADJUSTED_RECONCILIATION": {
        "decision": "RECONCILE",
        "reason":
            "Payment plus applicable transaction fee reconciles with the invoice amount.",
        "next_action":
            "Close the reconciliation case after recording the transaction fee."
    },

    # --------------------------------------------------------
    # KNOWN EXCEPTIONS REQUIRING INVESTIGATION
    # --------------------------------------------------------

    "PARTIAL_PAYMENT": {
        "decision": "INVESTIGATE",
        "reason":
            "The received payment is lower than the invoice amount.",
        "next_action":
            "Review the outstanding balance and payment status."
    },

    "OVERPAYMENT": {
        "decision": "INVESTIGATE",
        "reason":
            "The received payment is higher than the invoice amount.",
        "next_action":
            "Review the overpayment and determine whether a refund or adjustment is required."
    },

    "MISSING_PAYMENT": {
        "decision": "INVESTIGATE",
        "reason":
            "An expected payment could not be matched to the invoice.",
        "next_action":
            "Search payment records and verify the customer's payment status."
    },

    "MISSING_BANK_TRANSACTION": {
        "decision": "INVESTIGATE",
        "reason":
            "A payment exists but the corresponding bank transaction could not be matched.",
        "next_action":
            "Verify the bank statement and investigate the missing deposit."
    },

    "BANK_PAYMENT_MISMATCH": {
        "decision": "INVESTIGATE",
        "reason":
            "The bank transaction amount does not match the payment amount.",
        "next_action":
            "Investigate the payment and bank transaction discrepancy."
    },

    "INCOMPLETE_RECONCILIATION": {
        "decision": "INVESTIGATE",
        "reason":
            "The financial chain is incomplete and cannot be fully reconciled.",
        "next_action":
            "Locate the missing financial record."
    },

    # --------------------------------------------------------
    # MULTI-INVOICE PAYMENT
    # --------------------------------------------------------

    "MULTI_INVOICE_PAYMENT": {
        "decision": "INVESTIGATE",
        "reason":
            "A single payment references multiple invoices and requires allocation review.",
        "next_action":
            "Review payment allocation across the referenced invoices before reconciliation."
    },

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    "UNKNOWN": {
        "decision": "ESCALATE",
        "reason":
            "The system could not determine a reliable reconciliation pattern.",
        "next_action":
            "Escalate the case to a finance analyst for manual review."
    }
}


# ============================================================
# MAKE BUSINESS DECISION
# ============================================================

def make_decision(investigation_result):
    """
    Convert an investigation result into a business decision.

    Parameters
    ----------
    investigation_result : dict
        Result returned by the investigation agent.

    Returns
    -------
    dict
        Business decision containing:

            decision
            reason
            next_action
            confidence
    """

    if investigation_result is None:
        investigation_result = {}

    category = investigation_result.get(
        "category",
        "UNKNOWN"
    )

    investigation_confidence = investigation_result.get(
        "confidence",
        0.0
    )

    # --------------------------------------------------------
    # FIND BUSINESS RULE
    # --------------------------------------------------------

    rule = DECISION_RULES.get(
        category,
        DECISION_RULES["UNKNOWN"]
    )

    # --------------------------------------------------------
    # BUILD DECISION
    # --------------------------------------------------------

    return {
        "decision": rule["decision"],

        "reason": rule["reason"],

        "next_action": rule["next_action"],

        "confidence": investigation_confidence
    }


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":

    print("\n====================================")
    print("TANGLE DECISION ENGINE TEST")
    print("====================================")

    test_cases = [

        # ----------------------------------------------------
        # FULL RECONCILIATION
        # ----------------------------------------------------

        {
            "category":
                "FULL_RECONCILIATION",

            "confidence":
                0.98
        },

        # ----------------------------------------------------
        # FEE ADJUSTED
        # ----------------------------------------------------

        {
            "category":
                "FEE_ADJUSTED_RECONCILIATION",

            "confidence":
                0.98
        },

        # ----------------------------------------------------
        # PARTIAL PAYMENT
        # ----------------------------------------------------

        {
            "category":
                "PARTIAL_PAYMENT",

            "confidence":
                0.97
        },

        # ----------------------------------------------------
        # OVERPAYMENT
        # ----------------------------------------------------

        {
            "category":
                "OVERPAYMENT",

            "confidence":
                0.97
        },

        # ----------------------------------------------------
        # MISSING PAYMENT
        # ----------------------------------------------------

        {
            "category":
                "MISSING_PAYMENT",

            "confidence":
                0.90
        },

        # ----------------------------------------------------
        # MISSING BANK
        # ----------------------------------------------------

        {
            "category":
                "MISSING_BANK_TRANSACTION",

            "confidence":
                0.90
        },

        # ----------------------------------------------------
        # BANK PAYMENT MISMATCH
        # ----------------------------------------------------

        {
            "category":
                "BANK_PAYMENT_MISMATCH",

            "confidence":
                0.95
        },

        # ----------------------------------------------------
        # INCOMPLETE RECONCILIATION
        # ----------------------------------------------------

        {
            "category":
                "INCOMPLETE_RECONCILIATION",

            "confidence":
                0.85
        },

        # ----------------------------------------------------
        # MULTI-INVOICE PAYMENT
        # ----------------------------------------------------

        {
            "category":
                "MULTI_INVOICE_PAYMENT",

            "confidence":
                0.95
        },

        # ----------------------------------------------------
        # UNKNOWN
        # ----------------------------------------------------

        {
            "category":
                "UNKNOWN",

            "confidence":
                0.50
        }
    ]

    # ========================================================
    # RUN TESTS
    # ========================================================

    for number, test_case in enumerate(
        test_cases,
        start=1
    ):

        result = make_decision(
            test_case
        )

        print(
            f"\nTest {number}"
        )

        print(
            f"Category: "
            f"{test_case['category']}"
        )

        print(
            f"Decision: "
            f"{result['decision']}"
        )

        print(
            f"Reason: "
            f"{result['reason']}"
        )

        print(
            f"Next Action: "
            f"{result['next_action']}"
        )

        print(
            f"Confidence: "
            f"{result['confidence']}"
        )

    print(
        "\n===================================="
    )

    print(
        "DECISION ENGINE TEST COMPLETE"
    )

    print(
        "===================================="
    )
