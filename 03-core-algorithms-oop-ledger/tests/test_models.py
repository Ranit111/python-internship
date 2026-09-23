"""
Unit tests for Account and Transaction OOP hierarchies.
"""

import pytest
from ledger_engine.exceptions import (
    AccountLockedError,
    InsufficientFundsError,
    InvalidPayloadError,
    ReconciliationError,
    TransactionLimitExceededError,
)
from ledger_engine.models.account import (
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
    TransactionType,
    TransferTransaction,
    WithdrawalTransaction,
)


def test_savings_account_deposit_and_withdrawal():
    acc = SavingsAccount(account_id="SAV-001", holder_name="Alice Smith", initial_balance=500.0, minimum_balance=100.0)
    assert acc.balance == 500.0
    assert acc.account_type == "SAVINGS"

    # Deposit
    dep_tx = acc.deposit(200.0, "Salary Deposit")
    assert dep_tx.net_balance_impact() == 200.0
    assert acc.balance == 700.0
    assert len(acc.transactions) == 2

    # Normal withdrawal
    with_tx = acc.withdraw(300.0, "Rent Payment")
    assert with_tx.net_balance_impact() == -300.0
    assert acc.balance == 400.0

    # Withdrawal violating minimum balance floor
    with pytest.raises(InsufficientFundsError):
        acc.withdraw(350.0)  # would leave $50, below min $100

    # Withdrawal violating max limit
    with pytest.raises(TransactionLimitExceededError):
        acc.withdraw(6000.0)


def test_checking_account_overdraft():
    acc = CheckingAccount(account_id="CHK-001", holder_name="Bob Jones", initial_balance=200.0, overdraft_limit=300.0)
    assert acc.balance == 200.0

    # Withdraw into overdraft
    acc.withdraw(400.0)  # balance becomes -200.0
    assert acc.balance == -200.0

    # Exceed overdraft
    with pytest.raises(InsufficientFundsError):
        acc.withdraw(200.0)  # total -400 > overdraft 300


def test_investment_and_business_accounts():
    inv = InvestmentAccount(account_id="INV-001", holder_name="Charlie", initial_balance=1000.0, dividend_yield=0.12)
    assert inv.calculate_interest_or_fees() == 10.0  # 1000 * 0.12 / 12 = 10.0

    biz = BusinessAccount(account_id="BIZ-001", holder_name="Acme Corp", initial_balance=50000.0, daily_limit=10000.0)
    with pytest.raises(TransactionLimitExceededError):
        biz.withdraw(15000.0)


def test_polymorphic_monthly_rules():
    sav = SavingsAccount(account_id="SAV-002", holder_name="Dave", initial_balance=1200.0, annual_interest_rate=0.06)
    rule_tx = sav.apply_monthly_rules()
    assert isinstance(rule_tx, InterestTransaction)
    assert sav.balance == 1206.0  # +6.0 interest

    chk = CheckingAccount(account_id="CHK-002", holder_name="Dave", initial_balance=500.0, monthly_fee=15.0)
    fee_tx = chk.apply_monthly_rules()
    assert isinstance(fee_tx, FeeTransaction)
    assert chk.balance == 485.0


def test_locked_account_operations():
    acc = SavingsAccount(account_id="SAV-003", holder_name="Eve", initial_balance=300.0, is_active=False)
    with pytest.raises(AccountLockedError):
        acc.deposit(50.0)
    with pytest.raises(AccountLockedError):
        acc.withdraw(50.0)
    with pytest.raises(AccountLockedError):
        acc.apply_monthly_rules()


def test_reconciliation_check():
    acc = SavingsAccount(account_id="SAV-004", holder_name="Frank", initial_balance=1000.0)
    acc.deposit(500.0)
    acc.withdraw(200.0)
    assert acc.reconcile_balance() is True

    # Tamper with internal balance directly
    acc._balance = 9999.0
    with pytest.raises(ReconciliationError):
        acc.reconcile_balance()


def test_transaction_hash_integrity():
    tx1 = DepositTransaction(account_id="SAV-001", amount=150.0, description="Test")
    assert len(tx1.hash) == 64  # sha256
    d = tx1.to_dict()
    assert d["type"] == TransactionType.DEPOSIT.value
    assert d["impact"] == 150.0

    restored = Transaction.from_dict(d)
    assert restored.tx_id == tx1.tx_id
    assert restored.amount == tx1.amount
