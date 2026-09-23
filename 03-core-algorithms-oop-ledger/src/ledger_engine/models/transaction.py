"""
Transaction data models demonstrating OOP inheritance and encapsulation.
"""

from __future__ import annotations
import hashlib
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from ledger_engine.exceptions import InvalidPayloadError


class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    FEE = "FEE"
    INTEREST = "INTEREST"


class Transaction(ABC):
    """
    Abstract Base Class representing a financial transaction.
    Demonstrates encapsulation with private/protected attributes and property interfaces.
    """

    def __init__(
        self,
        account_id: str,
        amount: float,
        description: str,
        tx_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not account_id or not isinstance(account_id, str):
            raise InvalidPayloadError("account_id", "Must be a non-empty string")
        if amount <= 0:
            raise InvalidPayloadError("amount", "Transaction amount must be strictly greater than 0")

        self._tx_id = tx_id or f"TXN-{uuid.uuid4().hex[:10].upper()}"
        self._account_id = account_id.strip()
        self._amount = round(float(amount), 2)
        self._description = description.strip()
        self._timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self._metadata = metadata or {}
        self._hash = self._generate_hash()

    @property
    def tx_id(self) -> str:
        return self._tx_id

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def description(self) -> str:
        return self._description

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    @property
    def hash(self) -> str:
        return self._hash

    @property
    @abstractmethod
    def transaction_type(self) -> TransactionType:
        """Returns the specific enum type for this transaction."""
        pass

    @abstractmethod
    def net_balance_impact(self) -> float:
        """Returns positive or negative impact on ledger balance."""
        pass

    def _generate_hash(self) -> str:
        """Generates deterministic cryptographic hash ensuring tamper resistance."""
        payload = f"{self._tx_id}:{self._account_id}:{self._amount:.2f}:{self._timestamp}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes transaction to dictionary representation."""
        return {
            "tx_id": self._tx_id,
            "account_id": self._account_id,
            "type": self.transaction_type.value,
            "amount": self._amount,
            "impact": self.net_balance_impact(),
            "description": self._description,
            "timestamp": self._timestamp,
            "hash": self._hash,
            "metadata": self._metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Transaction:
        """Factory method to deserialize polymorphic transaction instances."""
        tx_type = data.get("type")
        account_id = data["account_id"]
        amount = float(data["amount"])
        description = data.get("description", "")
        tx_id = data.get("tx_id")
        timestamp = data.get("timestamp")
        metadata = data.get("metadata", {})

        if tx_type == TransactionType.DEPOSIT.value:
            return DepositTransaction(account_id, amount, description, tx_id, timestamp, metadata)
        elif tx_type == TransactionType.WITHDRAWAL.value:
            return WithdrawalTransaction(account_id, amount, description, tx_id, timestamp, metadata)
        elif tx_type == TransactionType.TRANSFER.value:
            target_account = metadata.get("target_account_id", "UNKNOWN")
            return TransferTransaction(account_id, target_account, amount, description, tx_id, timestamp, metadata)
        elif tx_type == TransactionType.FEE.value:
            return FeeTransaction(account_id, amount, description, tx_id, timestamp, metadata)
        elif tx_type == TransactionType.INTEREST.value:
            return InterestTransaction(account_id, amount, description, tx_id, timestamp, metadata)
        else:
            raise InvalidPayloadError("type", f"Unknown transaction type '{tx_type}'")


class DepositTransaction(Transaction):
    """Credit transaction depositing funds into an account."""

    @property
    def transaction_type(self) -> TransactionType:
        return TransactionType.DEPOSIT

    def net_balance_impact(self) -> float:
        return self._amount


class WithdrawalTransaction(Transaction):
    """Debit transaction withdrawing funds from an account."""

    @property
    def transaction_type(self) -> TransactionType:
        return TransactionType.WITHDRAWAL

    def net_balance_impact(self) -> float:
        return -self._amount


class TransferTransaction(Transaction):
    """Debit transfer transaction sending funds to a destination account."""

    def __init__(
        self,
        source_account_id: str,
        target_account_id: str,
        amount: float,
        description: str = "Account Transfer",
        tx_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        meta = metadata or {}
        meta["target_account_id"] = target_account_id
        super().__init__(source_account_id, amount, description, tx_id, timestamp, meta)
        self._target_account_id = target_account_id

    @property
    def target_account_id(self) -> str:
        return self._target_account_id

    @property
    def transaction_type(self) -> TransactionType:
        return TransactionType.TRANSFER

    def net_balance_impact(self) -> float:
        return -self._amount


class FeeTransaction(Transaction):
    """Debit fee transaction charged by system/ledger."""

    @property
    def transaction_type(self) -> TransactionType:
        return TransactionType.FEE

    def net_balance_impact(self) -> float:
        return -self._amount


class InterestTransaction(Transaction):
    """Credit interest payment earned by account."""

    @property
    def transaction_type(self) -> TransactionType:
        return TransactionType.INTEREST

    def net_balance_impact(self) -> float:
        return self._amount
