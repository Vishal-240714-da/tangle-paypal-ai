# ============================================================
# TANGLE AI
# Exception Detection Engine
# ============================================================

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

AMOUNT_TOLERANCE = 0.01




# ============================================================
# HELPER FUNCTIONS
# ============================================================

def to_float(value):
    """
    Safely convert a value to float.
    """

    try:
        if value is None:
            return None

        if pd.isna(value):
            return None

        return float(value)

    except (ValueError, TypeError):
        return None


def get_value(record, *keys, default=None):
    """
    Get the first available value from a record.

    Supports both:
        - normalized field names
        - raw CSV field names
    """

    if record is None:
        return default

    for key in keys:

        if key in record:

            value = record.get(key)

            if value is not None:
                return value

    return default


def amounts_match(amount1, amount2):
    """
    Check whether two financial amounts match
    within the allowed tolerance.
    """

    amount1 = to_float(amount1)
    amount2 = to_float(amount2)

    if amount1 is None or amount2 is None:
        return False

    return abs(amount1 - amount2) <= AMOUNT_TOLERANCE


# ============================================================
# EXCEPTION DETECTION
# ============================================================

def detect_exception(invoice=None, payment=None, bank=None):
    """
    Analyze invoice, payment and bank records.

    Returns:

        {
            "category": "...",
            "confidence": 0.0,
            "suggested_action": "..."
        }
    """

    # ========================================================
    # EXTRACT INVOICE INFORMATION
    # ========================================================

    invoice_amount = None
    invoice_id = None

    if invoice is not None:

        invoice_amount = to_float(
            get_value(
                invoice,
                "invoice_amount",
                "amount"
            )
        )

        invoice_id = get_value(
            invoice,
            "invoice_id",
            "id"
        )

    # ========================================================
    # EXTRACT PAYMENT INFORMATION
    # ========================================================

    payment_amount = None
    payment_fee = 0.0
    payment_id = None

    if payment is not None:

        payment_amount = to_float(
            get_value(
                payment,
                "payment_amount",
                "amount"
            )
        )

        payment_fee = to_float(
            get_value(
                payment,
                "payment_fee",
                "fee",
                default=0.0
            )
        )

        if payment_fee is None:
            payment_fee = 0.0

        payment_id = get_value(
            payment,
            "payment_id",
            "id"
        )

    # ========================================================
    # EXTRACT BANK INFORMATION
    # ========================================================

    bank_amount = None
    bank_id = None

    if bank is not None:

        bank_amount = to_float(
            get_value(
                bank,
                "bank_amount",
                "amount"
            )
        )

        bank_id = get_value(
            bank,
            "bank_transaction_id",
            "bank_id",
            "id"
        )

    # ========================================================
    # RULE 1
    # Invoice exists but payment is missing
    # ========================================================

    if invoice is not None and payment is None:

        return {
            "category": "MISSING_PAYMENT",
            "confidence": 0.90,
            "suggested_action": "INVESTIGATE"
        }

    # ========================================================
    # RULE 2
    # Payment exists but bank transaction is missing
    # ========================================================

    if payment is not None and bank is None:

        return {
            "category": "MISSING_BANK_TRANSACTION",
            "confidence": 0.90,
            "suggested_action": "INVESTIGATE"
        }

    # ========================================================
    # RULE 3
    # Bank exists but payment is missing
    # ========================================================

    if bank is not None and payment is None:

        return {
            "category": "MISSING_PAYMENT",
            "confidence": 0.90,
            "suggested_action": "INVESTIGATE"
        }

    # ========================================================
    # RULE 4
    # Bank and payment amounts do not match
    # ========================================================

    if (
        payment_amount is not None
        and bank_amount is not None
    ):

        if not amounts_match(
            payment_amount,
            bank_amount
        ):

            return {
                "category": "BANK_PAYMENT_MISMATCH",
                "confidence": 0.95,
                "suggested_action": "INVESTIGATE"
            }

    # ========================================================
    # RULE 5
    # Payment and bank match
    # ========================================================

    if (
        payment_amount is not None
        and bank_amount is not None
        and amounts_match(
            payment_amount,
            bank_amount
        )
    ):

        # ----------------------------------------------------
        # No invoice available
        # ----------------------------------------------------

        if invoice_amount is None:

            return {
                "category": "INCOMPLETE_RECONCILIATION",
                "confidence": 0.85,
                "suggested_action": "INVESTIGATE"
            }

        # ----------------------------------------------------
        # Full reconciliation
        # ----------------------------------------------------

        if amounts_match(
            payment_amount,
            invoice_amount
        ):

            return {
                "category": "FULL_RECONCILIATION",
                "confidence": 0.98,
                "suggested_action": "RECONCILE"
            }

        # ----------------------------------------------------
        # Fee-adjusted reconciliation
        #
        # Example:
        #
        # Invoice = 1000
        # Payment = 972.39
        # Fee = 27.61
        #
        # 972.39 + 27.61 = 1000
        # ----------------------------------------------------

        if amounts_match(
            payment_amount + payment_fee,
            invoice_amount
        ):

            return {
                "category": "FEE_ADJUSTED_RECONCILIATION",
                "confidence": 0.98,
                "suggested_action": "RECONCILE"
            }

        # ----------------------------------------------------
        # Partial payment
        # ----------------------------------------------------

        if payment_amount < invoice_amount:

            return {
                "category": "PARTIAL_PAYMENT",
                "confidence": 0.97,
                "suggested_action": "INVESTIGATE"
            }

        # ----------------------------------------------------
        # Overpayment
        # ----------------------------------------------------

        if payment_amount > invoice_amount:

            return {
                "category": "OVERPAYMENT",
                "confidence": 0.97,
                "suggested_action": "INVESTIGATE"
            }

    # ========================================================
    # RULE 6
    # No recognizable pattern
    # ========================================================

    return {
        "category": "UNKNOWN",
        "confidence": 0.50,
        "suggested_action": "ESCALATE"
    }