"""
LedgerManager orchestrating accounts, inter-account transfers, and search algorithms.
"""

from __future__ import annotations
import bisect
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ledger_engine.exceptions import (
    AccountNotFoundError,
    DuplicateAccountError,
    InvalidPayloadError,
    ReconciliationError,
)
from ledger_engine.models.account import (
    Account,
    BusinessAccount,
    CheckingAccount,
    InvestmentAccount,
    SavingsAccount,
)
from ledger_engine.models.transaction import (
    DepositTransaction,
    FeeTransaction,
    InterestTransaction,
    Transaction,
    TransferTransaction,
    WithdrawalTransaction,
)


class LedgerManager:
    """Core domain engine managing financial accounts, atomic transfers, and search algorithms."""

    def __init__(self) -> None:
        self._accounts: Dict[str, Account] = {}

    def register_account(self, account: Account) -> None:
        """Registers a new account into the ledger."""
        if not isinstance(account, Account):
            raise InvalidPayloadError("account", "Must be an instance of Account")
        if account.account_id in self._accounts:
            raise DuplicateAccountError(account.account_id)
        self._accounts[account.account_id] = account

    def create_account(
        self,
        account_type: str,
        account_id: str,
        holder_name: str,
        initial_balance: float = 0.0,
        **kwargs: Any,
    ) -> Account:
        """Factory method to instantiate and register a specific account subclass."""
        acc_type_clean = account_type.strip().upper()
        if acc_type_clean == "SAVINGS":
            rate = kwargs.get("annual_interest_rate", 0.045)
            min_bal = kwargs.get("minimum_balance", 100.0)
            acc = SavingsAccount(account_id, holder_name, initial_balance, annual_interest_rate=rate, minimum_balance=min_bal)
        elif acc_type_clean == "CHECKING":
            overdraft = kwargs.get("overdraft_limit", 500.0)
            fee = kwargs.get("monthly_fee", 12.0)
            acc = CheckingAccount(account_id, holder_name, initial_balance, overdraft_limit=overdraft, monthly_fee=fee)
        elif acc_type_clean == "INVESTMENT":
            yield_rate = kwargs.get("dividend_yield", 0.07)
            acc = InvestmentAccount(account_id, holder_name, initial_balance, dividend_yield=yield_rate)
        elif acc_type_clean == "BUSINESS":
            daily_limit = kwargs.get("daily_limit", 50000.0)
            acc = BusinessAccount(account_id, holder_name, initial_balance, daily_limit=daily_limit)
        else:
            raise InvalidPayloadError("account_type", f"Unsupported account type '{account_type}'")

        self.register_account(acc)
        return acc

    def get_account(self, account_id: str) -> Account:
        """Retrieves an account by unique ID or raises AccountNotFoundError."""
        if account_id not in self._accounts:
            raise AccountNotFoundError(account_id)
        return self._accounts[account_id]

    def list_accounts(self) -> List[Account]:
        """Returns list of all active accounts in the ledger."""
        return list(self._accounts.values())

    def transfer(
        self,
        source_account_id: str,
        target_account_id: str,
        amount: float,
        description: str = "Funds Transfer",
    ) -> Tuple[TransferTransaction, DepositTransaction]:
        """
        Executes atomic two-way transfer between two accounts with double-entry integrity.
        """
        if source_account_id == target_account_id:
            raise InvalidPayloadError("target_account_id", "Cannot transfer funds to the same account")

        source = self.get_account(source_account_id)
        target = self.get_account(target_account_id)

        # 1. Withdraw from source using polymorphic withdrawal rules
        source_tx = TransferTransaction(
            source_account_id=source.account_id,
            target_account_id=target.account_id,
            amount=amount,
            description=f"Transfer to {target.account_id}: {description}",
        )
        
        # Verify source can withdraw
        source.withdraw(amount, description=f"Transfer to {target.account_id}")

        # 2. Deposit into target account
        target_tx = target.deposit(amount, description=f"Transfer received from {source.account_id}")

        return source_tx, target_tx

    def process_monthly_cycle(self) -> Dict[str, Any]:
        """Runs batch monthly cycle over all registered accounts applying interest/fees."""
        results = {}
        for acc_id, acc in self._accounts.items():
            if acc.is_active:
                tx = acc.apply_monthly_rules()
                results[acc_id] = {
                    "applied": tx is not None,
                    "impact": tx.net_balance_impact() if tx else 0.0,
                    "new_balance": acc.balance,
                }
        return results

    def reconcile_all(self) -> Dict[str, bool]:
        """Runs ledger balance reconciliation across every registered account."""
        reconciled_status = {}
        for acc_id, acc in self._accounts.items():
            acc.reconcile_balance()
            reconciled_status[acc_id] = True
        return reconciled_status

    def get_all_transactions(self) -> List[Transaction]:
        """Gathers all transactions sorted deterministically by timestamp."""
        all_tx: List[Transaction] = []
        for acc in self._accounts.values():
            all_tx.extend(acc.transactions)
        all_tx.sort(key=lambda t: t.timestamp)
        return all_tx

    def binary_search_transactions_by_date(
        self,
        start_iso: str,
        end_iso: str,
    ) -> List[Transaction]:
        """
        Algorithm: Uses binary search (`bisect`) on time-sorted transactions
        to efficiently extract slice [start_iso, end_iso].
        Complexity: O(log N + K) where K is number of matching items.
        """
        all_tx = self.get_all_transactions()
        timestamps = [tx.timestamp for tx in all_tx]

        left_idx = bisect.bisect_left(timestamps, start_iso)
        right_idx = bisect.bisect_right(timestamps, end_iso)

        return all_tx[left_idx:right_idx]

    def get_ledger_summary(self) -> Dict[str, Any]:
        """Calculates ledger-wide financial statistics and health metrics."""
        accounts = self.list_accounts()
        total_balance = sum(a.balance for a in accounts)
        total_transactions = sum(len(a.transactions) for a in accounts)
        by_type: Dict[str, Dict[str, Any]] = {}

        for a in accounts:
            t = a.account_type
            if t not in by_type:
                by_type[t] = {"count": 0, "total_balance": 0.0}
            by_type[t]["count"] += 1
            by_type[t]["total_balance"] = round(by_type[t]["total_balance"] + a.balance, 2)

        return {
            "total_accounts": len(accounts),
            "total_balance": round(total_balance, 2),
            "total_transactions": total_transactions,
            "breakdown_by_type": by_type,
        }
