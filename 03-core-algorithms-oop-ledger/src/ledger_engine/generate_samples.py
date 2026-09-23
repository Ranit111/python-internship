"""
Script to populate sample data files for Task 03 deliverables.
"""

from pathlib import Path
from ledger_engine.engine import LedgerManager
from ledger_engine.persistence import LedgerPersistence


def generate_sample_data():
    mgr = LedgerManager()

    # 1. Create multiple diverse accounts
    sav = mgr.create_account("SAVINGS", "SAV-1001", "Emma Watson", 15000.0, annual_interest_rate=0.05, minimum_balance=250.0)
    chk = mgr.create_account("CHECKING", "CHK-2001", "John Doe", 3500.0, overdraft_limit=1000.0, monthly_fee=15.0)
    inv = mgr.create_account("INVESTMENT", "INV-3001", "Alex Rivera", 75000.0, dividend_yield=0.08)
    biz = mgr.create_account("BUSINESS", "BIZ-4001", "Apex Logistics LLC", 125000.0, daily_limit=75000.0)

    # 2. Perform transactions
    sav.deposit(2500.0, "Consulting Retainer")
    sav.withdraw(1200.0, "Hardware Purchase")
    
    chk.deposit(4200.0, "Direct Deposit Payroll")
    chk.withdraw(1800.0, "Office Lease")

    # 3. Inter-account transfer
    mgr.transfer("SAV-1001", "CHK-2001", 3000.0, "Inter-Account Liquidity Rebalance")

    # 4. Investment & Business activity
    inv.deposit(10000.0, "Portfolio Re-investment")
    biz.withdraw(22000.0, "Fleet Fuel Invoices")

    # 5. Process monthly cycle
    mgr.process_monthly_cycle()

    # 6. Verify reconciliation
    mgr.reconcile_all()

    # 7. Persist to data/
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = out_dir / "sample_ledger.json"
    csv_path = out_dir / "sample_transactions.csv"

    LedgerPersistence.save_to_json(mgr, json_path)
    LedgerPersistence.export_transactions_to_csv(mgr, csv_path)
    print(f"Generated {json_path} and {csv_path}")


if __name__ == "__main__":
    generate_sample_data()
