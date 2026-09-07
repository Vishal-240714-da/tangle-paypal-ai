
from agents.exception_detector import detect_exception


# ============================================================
# TEST 1: FULL RECONCILIATION
# Invoice = Payment = Bank
# ============================================================

invoice = {
    "invoice_id": "INV-TEST-001",
    "invoice_amount": 1000
}

payment = {
    "payment_id": "PAY-TEST-001",
    "payment_amount": 1000,
    "payment_fee": 0
}

bank = {
    "bank_transaction_id": "BANK-TEST-001",
    "bank_amount": 1000
}

print("TEST 1 - FULL RECONCILIATION")

result = detect_exception(
    invoice,
    payment,
    bank
)

print(result)


# ============================================================
# TEST 2: PARTIAL PAYMENT
# Invoice = 1500
# Payment = 800
# Bank = 800
# ============================================================

invoice = {
    "invoice_id": "INV-TEST-002",
    "invoice_amount": 1500
}

payment = {
    "payment_id": "PAY-TEST-002",
    "payment_amount": 800,
    "payment_fee": 0
}

bank = {
    "bank_transaction_id": "BANK-TEST-002",
    "bank_amount": 800
}

print("\nTEST 2 - PARTIAL PAYMENT")

result = detect_exception(
    invoice,
    payment,
    bank
)

print(result)


# ============================================================
# TEST 3: FEE-ADJUSTED RECONCILIATION
#
# Invoice = 1000
# Payment = 972.39
# Fee = 27.61
#
# 972.39 + 27.61 = 1000
# ============================================================

invoice = {
    "invoice_id": "INV-TEST-003",
    "invoice_amount": 1000
}

payment = {
    "payment_id": "PAY-TEST-003",
    "payment_amount": 972.39,
    "payment_fee": 27.61
}

bank = {
    "bank_transaction_id": "BANK-TEST-003",
    "bank_amount": 972.39
}

print("\nTEST 3 - FEE-ADJUSTED RECONCILIATION")

result = detect_exception(
    invoice,
    payment,
    bank
)

print(result)


# ============================================================
# TEST 4: BANK / PAYMENT MISMATCH
#
# Payment = 1000
# Bank = 950
# ============================================================

invoice = {
    "invoice_id": "INV-TEST-004",
    "invoice_amount": 1000
}

payment = {
    "payment_id": "PAY-TEST-004",
    "payment_amount": 1000,
    "payment_fee": 0
}

bank = {
    "bank_transaction_id": "BANK-TEST-004",
    "bank_amount": 950
}

print("\nTEST 4 - BANK PAYMENT MISMATCH")

result = detect_exception(
    invoice,
    payment,
    bank
)

print(result)


# ============================================================
# TEST 5: MISSING PAYMENT
#
# Invoice exists
# Payment does not exist
# Bank does not exist
# ============================================================

invoice = {
    "invoice_id": "INV-TEST-005",
    "invoice_amount": 2500
}

payment = None
bank = None

print("\nTEST 5 - MISSING PAYMENT")

result = detect_exception(
    invoice,
    payment,
    bank
)

print(result)


# ============================================================
# TEST 6: MISSING BANK TRANSACTION
#
# Invoice exists
# Payment exists
# Bank transaction missing
# ============================================================

invoice = {
    "invoice_id": "INV-TEST-006",
    "invoice_amount": 5000
}

payment = {
    "payment_id": "PAY-TEST-006",
    "payment_amount": 5000,
    "payment_fee": 0
}

bank = None

print("\nTEST 6 - MISSING BANK TRANSACTION")

result = detect_exception(
    invoice,
    payment,
    bank
)

print(result)


# ============================================================
# TEST 7: OVERPAYMENT
#
# Invoice = 1000
# Payment = 1200
# Bank = 1200
# ============================================================

invoice = {
    "invoice_id": "INV-TEST-007",
    "invoice_amount": 1000
}

payment = {
    "payment_id": "PAY-TEST-007",
    "payment_amount": 1200,
    "payment_fee": 0
}

bank = {
    "bank_transaction_id": "BANK-TEST-007",
    "bank_amount": 1200
}

print("\nTEST 7 - OVERPAYMENT")

result = detect_exception(
    invoice,
    payment,
    bank
)

print(result)
