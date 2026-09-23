"""
File I/O operations supporting robust JSON and CSV data persistence with validation.
"""

from __future__ import annotations
import csv
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Union

from ledger_engine.engine import LedgerManager
from ledger_engine.exceptions import InvalidPayloadError
from ledger_engine.models.account import (
    BusinessAccount,
    CheckingAccount,
    InvestmentAccount,
    SavingsAccount,
)
from ledger_engine.models.transaction import Transaction


class LedgerPersistence:
    """Handles serialization and deserialization of the ledger state in JSON and CSV formats."""

    @staticmethod
    def save_to_json(manager: LedgerManager, file_path: Union[str, Path]) -> None:
        """Atomically saves the complete ledger (accounts + transactions) to a JSON file."""
        target_path = Path(file_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "version": "1.0.0",
            "summary": manager.get_ledger_summary(),
            "accounts": [acc.to_dict() for acc in manager.list_accounts()],
        }

        # Atomic file write using temporary file
        temp_dir = target_path.parent
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
            json.dump(payload, tf, indent=2)
            temp_name = tf.name

        os.replace(temp_name, target_path)

    @staticmethod
    def load_from_json(file_path: Union[str, Path]) -> LedgerManager:
        """Loads and reconstructs accounts and transaction histories from a JSON file."""
        target_path = Path(file_path)
        if not target_path.exists():
            raise FileNotFoundError(f"JSON ledger file not found at: {target_path}")

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidPayloadError("json_payload", f"Malformed JSON: {e}") from e

        manager = LedgerManager()
        accounts_data = data.get("accounts", [])
        if not isinstance(accounts_data, list):
            raise InvalidPayloadError("accounts", "Expected list of accounts in JSON payload")

        for acc_dict in accounts_data:
            acc_id = acc_dict["account_id"]
            holder_name = acc_dict["holder_name"]
            acc_type = acc_dict["account_type"]
            is_active = acc_dict.get("is_active", True)
            created_at = acc_dict.get("created_at")

            if acc_type == "SAVINGS":
                account = SavingsAccount(acc_id, holder_name, initial_balance=0.0, is_active=is_active, created_at=created_at)
            elif acc_type == "CHECKING":
                account = CheckingAccount(acc_id, holder_name, initial_balance=0.0, is_active=is_active, created_at=created_at)
            elif acc_type == "INVESTMENT":
                account = InvestmentAccount(acc_id, holder_name, initial_balance=0.0, is_active=is_active, created_at=created_at)
            elif acc_type == "BUSINESS":
                account = BusinessAccount(acc_id, holder_name, initial_balance=0.0, is_active=is_active, created_at=created_at)
            else:
                raise InvalidPayloadError("account_type", f"Unknown type '{acc_type}'")

            # Restore transactions
            account._transactions = []
            running_balance = 0.0
            for tx_data in acc_dict.get("transactions", []):
                tx = Transaction.from_dict(tx_data)
                account._transactions.append(tx)
                running_balance += tx.net_balance_impact()

            account._balance = round(running_balance, 2)
            manager.register_account(account)

        return manager

    @staticmethod
    def export_transactions_to_csv(manager: LedgerManager, file_path: Union[str, Path]) -> None:
        """Exports all ledger transactions into a standardized CSV dataset."""
        target_path = Path(file_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        transactions = manager.get_all_transactions()
        fieldnames = ["tx_id", "account_id", "type", "amount", "impact", "description", "timestamp", "hash"]

        with open(target_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for tx in transactions:
                d = tx.to_dict()
                row = {k: d.get(k, "") for k in fieldnames}
                writer.writerow(row)

    @staticmethod
    def import_transactions_from_csv(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Imports and validates transaction rows from a CSV dataset."""
        target_path = Path(file_path)
        if not target_path.exists():
            raise FileNotFoundError(f"CSV file not found at: {target_path}")

        rows: List[Dict[str, Any]] = []
        with open(target_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("tx_id") or not row.get("account_id"):
                    continue
                rows.append({
                    "tx_id": row["tx_id"],
                    "account_id": row["account_id"],
                    "type": row["type"],
                    "amount": float(row["amount"]),
                    "impact": float(row.get("impact", 0.0)),
                    "description": row.get("description", ""),
                    "timestamp": row.get("timestamp", ""),
                    "hash": row.get("hash", ""),
                })
        return rows
