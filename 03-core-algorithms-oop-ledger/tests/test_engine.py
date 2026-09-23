"""
Unit tests for LedgerManager and core search & reconciliation algorithms.
"""

import pytest
from ledger_engine.engine import LedgerManager
from ledger_engine.exceptions import (
    AccountNotFoundError,
    DuplicateAccountError,
    InvalidPayloadError,
)
from ledger_engine.models.account import SavingsAccount


def test_ledger_manager_crud_and_registration():
    mgr = LedgerManager()
    acc = mgr.create_account("SAVINGS", "SAV-101", "Alice", 1000.0)
    assert acc.balance == 1000.0
    assert mgr.get_account("SAV-101") == acc
    assert len(mgr.list_accounts()) == 1

    with pytest.raises(DuplicateAccountError):
        mgr.create_account("SAVINGS", "SAV-101", "Alice Duplicate", 500.0)

    with pytest.raises(AccountNotFoundError):
        mgr.get_account("NON-EXISTENT")

    with pytest.raises(InvalidPayloadError):
        mgr.create_account("INVALID_TYPE", "ACC-999", "Name")


def test_inter_account_transfer():
    mgr = LedgerManager()
    src = mgr.create_account("SAVINGS", "SRC-001", "Sender", 2000.0, minimum_balance=100.0)
    dst = mgr.create_account("CHECKING", "DST-001", "Receiver", 500.0)

    s_tx, d_tx = mgr.transfer("SRC-001", "DST-001", 600.0, "Bill Split")
    assert src.balance == 1400.0
    assert dst.balance == 1100.0
    assert s_tx.amount == 600.0
    assert d_tx.amount == 600.0

    with pytest.raises(InvalidPayloadError):
        mgr.transfer("SRC-001", "SRC-001", 100.0)


def test_batch_monthly_cycle_and_reconciliation():
    mgr = LedgerManager()
    mgr.create_account("SAVINGS", "SAV-201", "User1", 1200.0, annual_interest_rate=0.06)
    mgr.create_account("CHECKING", "CHK-201", "User2", 400.0, monthly_fee=10.0)

    results = mgr.process_monthly_cycle()
    assert results["SAV-201"]["applied"] is True
    assert results["CHK-201"]["applied"] is True

    recon = mgr.reconcile_all()
    assert recon["SAV-201"] is True
    assert recon["CHK-201"] is True


def test_binary_search_transactions():
    mgr = LedgerManager()
    acc1 = mgr.create_account("SAVINGS", "ACC-1", "User", 100.0)
    acc1.deposit(50.0)
    acc1.deposit(75.0)

    all_tx = mgr.get_all_transactions()
    assert len(all_tx) == 3

    t_start = all_tx[0].timestamp
    t_end = all_tx[-1].timestamp
    matched = mgr.binary_search_transactions_by_date(t_start, t_end)
    assert len(matched) == 3


def test_ledger_summary():
    mgr = LedgerManager()
    mgr.create_account("SAVINGS", "S1", "User A", 1000.0)
    mgr.create_account("CHECKING", "C1", "User B", 500.0)
    summary = mgr.get_ledger_summary()

    assert summary["total_accounts"] == 2
    assert summary["total_balance"] == 1500.0
    assert "SAVINGS" in summary["breakdown_by_type"]
    assert "CHECKING" in summary["breakdown_by_type"]
