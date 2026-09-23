"""
Custom domain exception hierarchy for the Financial Ledger Engine.
"""

from typing import Any, Dict, Optional


class LedgerException(Exception):
    """Base exception for all domain-specific errors in the ledger engine."""

    def __init__(self, message: str, error_code: str = "ERR_GENERIC", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation of the error."""
        return {
            "error": self.__class__.__name__,
            "code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class InsufficientFundsError(LedgerException):
    """Raised when an account does not have sufficient funds for a withdrawal/transfer."""

    def __init__(self, account_id: str, available_balance: float, requested_amount: float) -> None:
        super().__init__(
            f"Account '{account_id}' has insufficient funds: available ${available_balance:.2f}, requested ${requested_amount:.2f}",
            error_code="ERR_INSUFFICIENT_FUNDS",
            details={
                "account_id": account_id,
                "available_balance": available_balance,
                "requested_amount": requested_amount,
            },
        )


class AccountLockedError(LedgerException):
    """Raised when attempting an operation on a suspended or frozen account."""

    def __init__(self, account_id: str, reason: str = "Account is frozen/inactive") -> None:
        super().__init__(
            f"Account '{account_id}' is locked: {reason}",
            error_code="ERR_ACCOUNT_LOCKED",
            details={"account_id": account_id, "reason": reason},
        )


class TransactionLimitExceededError(LedgerException):
    """Raised when a single transaction or daily volume exceeds allowable limits."""

    def __init__(self, account_id: str, amount: float, max_limit: float) -> None:
        super().__init__(
            f"Transaction of ${amount:.2f} exceeds limit of ${max_limit:.2f} for account '{account_id}'",
            error_code="ERR_LIMIT_EXCEEDED",
            details={"account_id": account_id, "amount": amount, "limit": max_limit},
        )


class InvalidPayloadError(LedgerException):
    """Raised when input parameters, amounts, or identifiers are invalid."""

    def __init__(self, field_name: str, reason: str) -> None:
        super().__init__(
            f"Invalid input for field '{field_name}': {reason}",
            error_code="ERR_INVALID_PAYLOAD",
            details={"field": field_name, "reason": reason},
        )


class AccountNotFoundError(LedgerException):
    """Raised when an account lookup fails."""

    def __init__(self, account_id: str) -> None:
        super().__init__(
            f"Account with ID '{account_id}' was not found in the ledger",
            error_code="ERR_ACCOUNT_NOT_FOUND",
            details={"account_id": account_id},
        )


class DuplicateAccountError(LedgerException):
    """Raised when creating an account that already exists."""

    def __init__(self, account_id: str) -> None:
        super().__init__(
            f"Account with ID '{account_id}' already exists",
            error_code="ERR_DUPLICATE_ACCOUNT",
            details={"account_id": account_id},
        )


class ReconciliationError(LedgerException):
    """Raised when calculated ledger integrity or hash verification fails."""

    def __init__(self, account_id: str, calculated_balance: float, recorded_balance: float) -> None:
        super().__init__(
            f"Ledger reconciliation mismatch for account '{account_id}': calculated ${calculated_balance:.2f} != recorded ${recorded_balance:.2f}",
            error_code="ERR_RECONCILIATION_MISMATCH",
            details={
                "account_id": account_id,
                "calculated_balance": calculated_balance,
                "recorded_balance": recorded_balance,
                "delta": round(calculated_balance - recorded_balance, 2),
            },
        )
