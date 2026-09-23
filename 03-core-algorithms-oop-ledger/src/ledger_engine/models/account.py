"""
Account hierarchy demonstrating encapsulation, inheritance, and polymorphic monthly rules.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ledger_engine.exceptions import (
    AccountLockedError,
    InsufficientFundsError,
    InvalidPayloadError,
    ReconciliationError,
    TransactionLimitExceededError,
)
from ledger_engine.models.transaction import (
    DepositTransaction,
    FeeTransaction,
    InterestTransaction,
    Transaction,
    TransferTransaction,
    WithdrawalTransaction,
)


class Account(ABC):
    """
    Abstract Base Class for bank/ledger accounts.
    Encapsulates balance and transaction logs with protected state mutation.
    """

    def __init__(
        self,
        account_id: str,
        holder_name: str,
        initial_balance: float = 0.0,
        is_active: bool = True,
        created_at: Optional[str] = None,
    ) -> None:
        if not account_id or not isinstance(account_id, str):
            raise InvalidPayloadError("account_id", "Account ID must be a non-empty string")
        if not holder_name or not isinstance(holder_name, str):
            raise InvalidPayloadError("holder_name", "Holder name must be a non-empty string")
        if initial_balance < 0:
            raise InvalidPayloadError("initial_balance", "Initial balance cannot be negative")

        self._account_id = account_id.strip()
        self._holder_name = holder_name.strip()
        self._balance = round(float(initial_balance), 2)
        self._is_active = is_active
        self._created_at = created_at or datetime.now(timezone.utc).isoformat()
        self._transactions: List[Transaction] = []

        if initial_balance > 0:
            init_tx = DepositTransaction(
                account_id=self._account_id,
                amount=initial_balance,
                description="Initial Account Opening Deposit",
                timestamp=self._created_at,
            )
            self._transactions.append(init_tx)

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def holder_name(self) -> str:
        return self._holder_name

    @holder_name.setter
    def holder_name(self, value: str) -> None:
        if not value or not isinstance(value, str):
            raise InvalidPayloadError("holder_name", "Name must be a valid string")
        self._holder_name = value.strip()

    @property
    def balance(self) -> float:
        return round(self._balance, 2)

    @property
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, status: bool) -> None:
        self._is_active = bool(status)

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def transactions(self) -> List[Transaction]:
        return list(self._transactions)

    @property
    @abstractmethod
    def account_type(self) -> str:
        """Returns string name of account subtype."""
        pass

    def _ensure_active(self) -> None:
        if not self._is_active:
            raise AccountLockedError(self._account_id, "Account is deactivated or frozen")

    def deposit(self, amount: float, description: str = "Deposit") -> DepositTransaction:
        """Deposits funds into the account."""
        self._ensure_active()
        tx = DepositTransaction(account_id=self._account_id, amount=amount, description=description)
        self._balance = round(self._balance + tx.net_balance_impact(), 2)
        self._transactions.append(tx)
        return tx

    @abstractmethod
    def withdraw(self, amount: float, description: str = "Withdrawal") -> WithdrawalTransaction:
        """Withdraws funds following account-specific limits and rules."""
        pass

    @abstractmethod
    def calculate_interest_or_fees(self) -> float:
        """Calculates expected interest (positive) or monthly fee (negative)."""
        pass

    def apply_monthly_rules(self) -> Optional[Transaction]:
        """Polymorphic monthly rule execution (applies interest or deducts monthly fee)."""
        self._ensure_active()
        amount = self.calculate_interest_or_fees()
        if amount > 0:
            tx = InterestTransaction(self._account_id, amount, f"Monthly Interest Credit for {self.account_type}")
            self._balance = round(self._balance + tx.net_balance_impact(), 2)
            self._transactions.append(tx)
            return tx
        elif amount < 0:
            fee_amount = abs(amount)
            tx = FeeTransaction(self._account_id, fee_amount, f"Monthly Maintenance Fee for {self.account_type}")
            self._balance = round(self._balance + tx.net_balance_impact(), 2)
            self._transactions.append(tx)
            return tx
        return None

    def reconcile_balance(self) -> bool:
        """
        Reconciliation algorithm: verifies that recorded balance strictly equals
        the sum of net transaction impacts from creation to date.
        """
        calculated_balance = sum(tx.net_balance_impact() for tx in self._transactions)
        calculated_balance = round(calculated_balance, 2)
        if abs(calculated_balance - self._balance) > 0.001:
            raise ReconciliationError(self._account_id, calculated_balance, self._balance)
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serializes account details and full transaction ledger."""
        return {
            "account_id": self._account_id,
            "holder_name": self._holder_name,
            "account_type": self.account_type,
            "balance": self.balance,
            "is_active": self._is_active,
            "created_at": self._created_at,
            "transactions": [tx.to_dict() for tx in self._transactions],
        }


class SavingsAccount(Account):
    """Savings Account with annual interest rate, minimum balance floor, and withdrawal limit."""

    def __init__(
        self,
        account_id: str,
        holder_name: str,
        initial_balance: float = 0.0,
        annual_interest_rate: float = 0.045, # 4.5% APY
        minimum_balance: float = 100.0,
        max_withdrawal_limit: float = 5000.0,
        is_active: bool = True,
        created_at: Optional[str] = None,
    ) -> None:
        super().__init__(account_id, holder_name, initial_balance, is_active, created_at)
        self._annual_interest_rate = annual_interest_rate
        self._minimum_balance = minimum_balance
        self._max_withdrawal_limit = max_withdrawal_limit

    @property
    def account_type(self) -> str:
        return "SAVINGS"

    @property
    def annual_interest_rate(self) -> float:
        return self._annual_interest_rate

    @property
    def minimum_balance(self) -> float:
        return self._minimum_balance

    def withdraw(self, amount: float, description: str = "Savings Withdrawal") -> WithdrawalTransaction:
        self._ensure_active()
        if amount > self._max_withdrawal_limit:
            raise TransactionLimitExceededError(self._account_id, amount, self._max_withdrawal_limit)
        
        if (self._balance - amount) < self._minimum_balance:
            raise InsufficientFundsError(
                self._account_id,
                available_balance=max(0.0, self._balance - self._minimum_balance),
                requested_amount=amount,
            )

        tx = WithdrawalTransaction(self._account_id, amount, description)
        self._balance = round(self._balance + tx.net_balance_impact(), 2)
        self._transactions.append(tx)
        return tx

    def calculate_interest_or_fees(self) -> float:
        """Calculates monthly interest compounded: (balance * rate) / 12."""
        monthly_rate = self._annual_interest_rate / 12.0
        return round(self._balance * monthly_rate, 2)


class CheckingAccount(Account):
    """Checking Account with overdraft protection and monthly maintenance fee."""

    def __init__(
        self,
        account_id: str,
        holder_name: str,
        initial_balance: float = 0.0,
        overdraft_limit: float = 500.0,
        monthly_fee: float = 12.0,
        is_active: bool = True,
        created_at: Optional[str] = None,
    ) -> None:
        super().__init__(account_id, holder_name, initial_balance, is_active, created_at)
        self._overdraft_limit = overdraft_limit
        self._monthly_fee = monthly_fee

    @property
    def account_type(self) -> str:
        return "CHECKING"

    @property
    def overdraft_limit(self) -> float:
        return self._overdraft_limit

    def withdraw(self, amount: float, description: str = "Checking Withdrawal") -> WithdrawalTransaction:
        self._ensure_active()
        max_available = self._balance + self._overdraft_limit
        if amount > max_available:
            raise InsufficientFundsError(self._account_id, max_available, amount)

        tx = WithdrawalTransaction(self._account_id, amount, description)
        self._balance = round(self._balance + tx.net_balance_impact(), 2)
        self._transactions.append(tx)
        return tx

    def calculate_interest_or_fees(self) -> float:
        """Returns negative monthly maintenance fee (waived if balance >= $2000)."""
        if self._balance >= 2000.0:
            return 0.0
        return -round(self._monthly_fee, 2)


class InvestmentAccount(Account):
    """Investment Account with variable dividend yield and capital appreciation rules."""

    def __init__(
        self,
        account_id: str,
        holder_name: str,
        initial_balance: float = 0.0,
        dividend_yield: float = 0.07, # 7%
        is_active: bool = True,
        created_at: Optional[str] = None,
    ) -> None:
        super().__init__(account_id, holder_name, initial_balance, is_active, created_at)
        self._dividend_yield = dividend_yield

    @property
    def account_type(self) -> str:
        return "INVESTMENT"

    def withdraw(self, amount: float, description: str = "Investment Liquidation") -> WithdrawalTransaction:
        self._ensure_active()
        if amount > self._balance:
            raise InsufficientFundsError(self._account_id, self._balance, amount)

        tx = WithdrawalTransaction(self._account_id, amount, description)
        self._balance = round(self._balance + tx.net_balance_impact(), 2)
        self._transactions.append(tx)
        return tx

    def calculate_interest_or_fees(self) -> float:
        """Monthly dividend yield calculation."""
        monthly_yield = self._dividend_yield / 12.0
        return round(self._balance * monthly_yield, 2)


class BusinessAccount(Account):
    """Commercial Business Account with high volume limits and tiered transaction fee."""

    def __init__(
        self,
        account_id: str,
        holder_name: str,
        initial_balance: float = 0.0,
        daily_limit: float = 50000.0,
        is_active: bool = True,
        created_at: Optional[str] = None,
    ) -> None:
        super().__init__(account_id, holder_name, initial_balance, is_active, created_at)
        self._daily_limit = daily_limit

    @property
    def account_type(self) -> str:
        return "BUSINESS"

    def withdraw(self, amount: float, description: str = "Business Outflow") -> WithdrawalTransaction:
        self._ensure_active()
        if amount > self._daily_limit:
            raise TransactionLimitExceededError(self._account_id, amount, self._daily_limit)
        if amount > self._balance:
            raise InsufficientFundsError(self._account_id, self._balance, amount)

        tx = WithdrawalTransaction(self._account_id, amount, description)
        self._balance = round(self._balance + tx.net_balance_impact(), 2)
        self._transactions.append(tx)
        return tx

    def calculate_interest_or_fees(self) -> float:
        """Flat business treasury maintenance fee."""
        return -25.0
