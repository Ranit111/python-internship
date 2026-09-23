"""
Unit tests for custom exception hierarchy.
"""

from ledger_engine.exceptions import (
    AccountLockedError,
    AccountNotFoundError,
    DuplicateAccountError,
    InsufficientFundsError,
    InvalidPayloadError,
    LedgerException,
    ReconciliationError,
    TransactionLimitExceededError,
)


def test_exception_serialization():
    err1 = InsufficientFundsError("ACC-001", available_balance=50.0, requested_amount=100.0)
    d1 = err1.to_dict()
    assert d1["code"] == "ERR_INSUFFICIENT_FUNDS"
    assert "ACC-001" in d1["message"]
    assert d1["details"]["available_balance"] == 50.0

    err2 = AccountLockedError("ACC-002", "Suspicious activity")
    assert err2.error_code == "ERR_ACCOUNT_LOCKED"

    err3 = TransactionLimitExceededError("ACC-003", 5000.0, 1000.0)
    assert err3.error_code == "ERR_LIMIT_EXCEEDED"

    err4 = ReconciliationError("ACC-004", 100.0, 80.0)
    assert err4.details["delta"] == 20.0
