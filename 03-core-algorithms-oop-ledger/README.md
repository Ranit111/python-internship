# Task 03: Core Algorithms, OOP Structures & Robust Error Handling

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Coverage](https://img.shields.io/badge/coverage-%3E85%25-brightgreen.svg)
![Tests](https://img.shields.io/badge/pytest-17%20passed-brightgreen.svg)

An enterprise-grade Object-Oriented Financial Ledger & Account Management Engine showcasing encapsulation, class inheritance, polymorphism, custom exception hierarchies, and data persistence in JSON and CSV.

---

## 🏛️ System Architecture & Class Hierarchy

```mermaid
classDiagram
    class Account {
        <<abstract>>
        -_account_id: str
        -_holder_name: str
        -_balance: float
        -_is_active: bool
        -_transactions: List~Transaction~
        +account_id: str
        +holder_name: str
        +balance: float
        +is_active: bool
        +deposit(amount, desc)
        +withdraw(amount, desc)*
        +apply_monthly_rules()*
        +reconcile_balance() bool
    }

    class SavingsAccount {
        -_annual_interest_rate: float
        -_minimum_balance: float
        +withdraw(amount, desc)
        +calculate_interest_or_fees()
    }

    class CheckingAccount {
        -_overdraft_limit: float
        -_monthly_fee: float
        +withdraw(amount, desc)
        +calculate_interest_or_fees()
    }

    class InvestmentAccount {
        -_dividend_yield: float
        +withdraw(amount, desc)
        +calculate_interest_or_fees()
    }

    class BusinessAccount {
        -_daily_limit: float
        +withdraw(amount, desc)
        +calculate_interest_or_fees()
    }

    Account <|-- SavingsAccount
    Account <|-- CheckingAccount
    Account <|-- InvestmentAccount
    Account <|-- BusinessAccount

    class Transaction {
        <<abstract>>
        -_tx_id: str
        -_account_id: str
        -_amount: float
        -_timestamp: str
        -_hash: str
        +net_balance_impact()*
        +to_dict()
    }

    class DepositTransaction {
        +net_balance_impact() float
    }
    class WithdrawalTransaction {
        +net_balance_impact() float
    }
    class TransferTransaction {
        -_target_account_id: str
        +net_balance_impact() float
    }
    class FeeTransaction {
        +net_balance_impact() float
    }
    class InterestTransaction {
        +net_balance_impact() float
    }

    Transaction <|-- DepositTransaction
    Transaction <|-- WithdrawalTransaction
    Transaction <|-- TransferTransaction
    Transaction <|-- FeeTransaction
    Transaction <|-- InterestTransaction
```

---

## 🔑 OOP Principles Demonstrated

1. **Encapsulation**:
   - Internal state (`_balance`, `_transactions`, `_is_active`) is protected.
   - Access and mutations are governed via `@property` getters, setters with validation, and business rule methods.
2. **Inheritance & Abstraction**:
   - Abstract Base Classes `Account` and `Transaction` enforce contracts via `@abstractmethod`.
   - Four distinct account types (`SavingsAccount`, `CheckingAccount`, `InvestmentAccount`, `BusinessAccount`) inherit core ledger features while implementing customized business logic.
3. **Polymorphism**:
   - `withdraw()` applies account-specific constraints (e.g., minimum balance floor in Savings vs. overdraft allowances in Checking vs. daily transaction limits in Business).
   - `apply_monthly_rules()` dynamically credits compounded interest to Savings/Investment accounts while debiting maintenance fees from Checking/Business accounts.
4. **Custom Exception Hierarchy**:
   - `LedgerException` base class with JSON error code serialization.
   - Specific sub-exceptions: `InsufficientFundsError`, `AccountLockedError`, `TransactionLimitExceededError`, `InvalidPayloadError`, `AccountNotFoundError`, `DuplicateAccountError`, and `ReconciliationError`.

---

## ⚡ Core Algorithms

1. **Deterministic Ledger Balance Reconciliation**:
   $$\text{Balance} = \sum_{i=1}^{N} \text{Impact}(T_i)$$
   Verifies ledger integrity by ensuring the current account balance strictly matches the sum of historical net transaction impacts.
2. **Binary Search Timestamp Extraction**:
   Uses `bisect` over chronologically sorted transaction logs to perform $O(\log N + K)$ slice lookups over date ranges.
3. **Tamper-Evident Cryptographic Hashing**:
   Computes a SHA-256 integrity hash for each transaction event:
   $$\text{Hash} = \text{SHA256}(\text{tx\_id} : \text{account\_id} : \text{amount} : \text{timestamp})$$

---

## 💾 Data Persistence (JSON & CSV)

- **JSON Storage (`data/sample_ledger.json`)**: Complete ledger snapshot with account schemas, transaction histories, and ledger summary. Uses atomic write operations via temporary files to avoid partial state corruption.
- **CSV Storage (`data/sample_transactions.csv`)**: Standardized tabular export of all transaction events with cryptographic hashes.

---

## 🧪 Unit Testing & Coverage

```bash
cd 03-core-algorithms-oop-ledger
pytest tests/ -v --cov=ledger_engine --cov-report=term-missing
```

### Test Coverage Highlights
- ✅ 17 comprehensive unit tests with **87%+ code coverage**.
- ✅ Boundary test cases for overdrafts, minimum balances, withdrawal limits, locked accounts, and reconciliation mismatches.
- ✅ Two-way JSON serialization and CSV export/import integrity validation.
