"""
Unit tests for LedgerPersistence (JSON and CSV serialization/deserialization).
"""

from pathlib import Path
import pytest
from ledger_engine.engine import LedgerManager
from ledger_engine.exceptions import InvalidPayloadError
from ledger_engine.persistence import LedgerPersistence


def test_json_roundtrip(tmp_path):
    mgr = LedgerManager()
    sav = mgr.create_account("SAVINGS", "SAV-888", "Diana Prince", 5000.0)
    chk = mgr.create_account("CHECKING", "CHK-888", "Bruce Wayne", 10000.0)
    sav.deposit(1200.0, "Consulting Fee")
    chk.withdraw(2500.0, "Equipment Purchase")

    json_file = tmp_path / "ledger_test.json"
    LedgerPersistence.save_to_json(mgr, json_file)
    assert json_file.exists()

    restored_mgr = LedgerPersistence.load_from_json(json_file)
    assert len(restored_mgr.list_accounts()) == 2
    r_sav = restored_mgr.get_account("SAV-888")
    assert r_sav.balance == 6200.0
    assert len(r_sav.transactions) == 2


def test_csv_export_and_import(tmp_path):
    mgr = LedgerManager()
    sav = mgr.create_account("SAVINGS", "SAV-999", "Clark Kent", 3000.0)
    sav.deposit(500.0, "Bonus")

    csv_file = tmp_path / "transactions_test.csv"
    LedgerPersistence.export_transactions_to_csv(mgr, csv_file)
    assert csv_file.exists()

    rows = LedgerPersistence.import_transactions_from_csv(csv_file)
    assert len(rows) == 2
    assert rows[0]["account_id"] == "SAV-999"
    assert rows[1]["amount"] == 500.0


def test_persistence_missing_file():
    with pytest.raises(FileNotFoundError):
        LedgerPersistence.load_from_json("non_existent_file.json")

    with pytest.raises(FileNotFoundError):
        LedgerPersistence.import_transactions_from_csv("non_existent_file.csv")


def test_persistence_corrupted_json(tmp_path):
    corrupted_file = tmp_path / "bad.json"
    corrupted_file.write_text("{ invalid json payload", encoding="utf-8")
    with pytest.raises(InvalidPayloadError):
        LedgerPersistence.load_from_json(corrupted_file)
