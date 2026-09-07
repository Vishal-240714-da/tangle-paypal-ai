"""
TANGLE Case Lifecycle Manager

Controls valid case status transitions throughout the
financial investigation workflow.
"""

VALID_STATUSES = {
    "OPEN",
    "INVESTIGATING",
    "PENDING_REVIEW",
    "APPROVED",
    "REJECTED",
    "ESCALATED",
    "RESOLVED",
}


ALLOWED_TRANSITIONS = {
    "OPEN": {
        "INVESTIGATING",
    },

    "INVESTIGATING": {
        "PENDING_REVIEW",
    },

    "PENDING_REVIEW": {
        "APPROVED",
        "REJECTED",
        "ESCALATED",
    },

    "APPROVED": {
        "RESOLVED",
    },

    "REJECTED": {
        "RESOLVED",
    },

    "ESCALATED": {
        "INVESTIGATING",
        "RESOLVED",
    },

    "RESOLVED": set(),
}


def is_valid_status(status):
    """
    Check whether a status is a recognized TANGLE lifecycle status.
    """
    if not isinstance(status, str):
        return False

    return status.upper().strip() in VALID_STATUSES


def can_transition(current_status, new_status):
    """
    Check whether a lifecycle transition is allowed.
    """

    if not is_valid_status(current_status):
        return False

    if not is_valid_status(new_status):
        return False

    current_status = current_status.upper().strip()
    new_status = new_status.upper().strip()

    if current_status == new_status:
        return True

    return new_status in ALLOWED_TRANSITIONS.get(current_status, set())


def transition_case(current_status, new_status):
    """
    Attempt to move a case from one lifecycle status to another.

    Returns a structured result instead of directly modifying files.
    """

    if not is_valid_status(current_status):
        return {
            "success": False,
            "current_status": current_status,
            "new_status": new_status,
            "message": f"Invalid current status: {current_status}",
        }

    if not is_valid_status(new_status):
        return {
            "success": False,
            "current_status": current_status,
            "new_status": new_status,
            "message": f"Invalid new status: {new_status}",
        }

    current_status = current_status.upper().strip()
    new_status = new_status.upper().strip()

    if current_status == new_status:
        return {
            "success": True,
            "current_status": current_status,
            "new_status": new_status,
            "message": "Case is already in this status.",
        }

    if not can_transition(current_status, new_status):
        return {
            "success": False,
            "current_status": current_status,
            "new_status": new_status,
            "message": (
                f"Invalid lifecycle transition: "
                f"{current_status} → {new_status}"
            ),
        }

    return {
        "success": True,
        "current_status": current_status,
        "new_status": new_status,
        "message": (
            f"Case successfully transitioned: "
            f"{current_status} → {new_status}"
        ),
    }


def get_next_statuses(current_status):
    """
    Return all valid next statuses for a case.
    """

    if not is_valid_status(current_status):
        return []

    current_status = current_status.upper().strip()

    return sorted(
        ALLOWED_TRANSITIONS.get(current_status, set())
    )


def get_lifecycle_description(status):
    """
    Human-readable description of a lifecycle state.
    """

    descriptions = {
        "OPEN":
            "Case has been detected and is waiting for investigation.",

        "INVESTIGATING":
            "The investigation agent is analyzing the case.",

        "PENDING_REVIEW":
            "Investigation is complete and the case requires human review.",

        "APPROVED":
            "Analyst approved the proposed case resolution.",

        "REJECTED":
            "Analyst rejected the proposed case resolution.",

        "ESCALATED":
            "Case requires additional investigation or higher-level review.",

        "RESOLVED":
            "Case has reached its final resolution.",
    }

    return descriptions.get(
        status,
        "Unknown lifecycle status."
    )


def run_self_test():
    """
    Test lifecycle rules.
    """

    print("=" * 60)
    print("TANGLE CASE LIFECYCLE MANAGER")
    print("=" * 60)

    test_cases = [
        ("OPEN", "INVESTIGATING", True),
        ("INVESTIGATING", "PENDING_REVIEW", True),
        ("PENDING_REVIEW", "APPROVED", True),
        ("PENDING_REVIEW", "REJECTED", True),
        ("PENDING_REVIEW", "ESCALATED", True),
        ("APPROVED", "RESOLVED", True),
        ("REJECTED", "RESOLVED", True),
        ("ESCALATED", "INVESTIGATING", True),
        ("ESCALATED", "RESOLVED", True),

        # Invalid transitions
        ("OPEN", "APPROVED", False),
        ("OPEN", "RESOLVED", False),
        ("APPROVED", "INVESTIGATING", False),
        ("REJECTED", "APPROVED", False),
        ("RESOLVED", "OPEN", False),
    ]

    passed = 0

    for current, new, expected in test_cases:

        result = transition_case(current, new)

        actual = result["success"]

        if actual == expected:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"

        print(
            f"{status}: "
            f"{current} → {new} "
            f"(expected={expected}, actual={actual})"
        )

    print()
    print(f"Lifecycle tests passed: {passed}/{len(test_cases)}")

    print()
    print("VALID STATUSES:")
    for status in sorted(VALID_STATUSES):
        print(f"- {status}")

    print()
    print("CASE LIFECYCLE MANAGER READY")


if __name__ == "__main__":
    run_self_test()