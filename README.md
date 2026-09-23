# 🎓 Python Software Engineering Internship Deliverables & Proof Portfolio

![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg)
![Build Status](https://img.shields.io/badge/All%20Test%20Suites-56%20Passed%20(100%25)-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

This repository contains the complete, production-grade solutions, automated test suites, sample reports, and verification proofs for the **RabTech Python Software Engineering Internship Tasks (02 to 06)**.

---

## 📌 Deliverables & Submission Index

| Task # | Project Title | Key Technologies | Test Coverage | Deliverables & Proofs | Directory Link |
| :---: | :--- | :--- | :---: | :--- | :---: |
| **02** | **Packaged CLI Diagnostics Tool** | Python CLI, `psutil`, `rich`, `pyproject.toml` | **100% (17 tests)** | Distributable CLI package, Deterministic exit codes, JSON & text reports, Starter events analysis | [`02-packaged-cli-diagnostics`](./02-packaged-cli-diagnostics) |
| **03** | **Core Algorithms & OOP Ledger** | OOP, Inheritance, Polymorphism, SHA-256, `bisect` | **87%+ (17 tests)** | Class hierarchy, Custom exceptions, Atomic JSON/CSV persistence, Balance reconciliation | [`03-core-algorithms-oop-ledger`](./03-core-algorithms-oop-ledger) |
| **04** | **Automated Web Scraping Pipeline** | `BeautifulSoup4`, `requests`, `urllib3.Retry`, Pydantic | **87%+ (7 tests)** | Exponential backoff retries, Rate limiting & jitter, Clean CSV/JSON datasets, Executive analytical report | [`04-automated-web-scraping-pipeline`](./04-automated-web-scraping-pipeline) |
| **05** | **FastAPI JWT Microservice** | FastAPI, SQLAlchemy ORM, SQLite, `bcrypt`, `pyjwt` | **92%+ (11 tests)** | User registration/login, JWT bearer middleware, Full CRUD with ownership checks, Swagger UI, Postman collection | [`05-fastapi-jwt-microservice`](./05-fastapi-jwt-microservice) |
| **06** | **Enterprise Automation Capstone** | `ReportLab`, CLI subcommands, Daemon scheduler | **93%+ (11 tests)** | End-to-end multi-source collector, Anomaly detection, Automated PDF report generator, Webhook/Console alerts | [`06-enterprise-automation-capstone`](./06-enterprise-automation-capstone) |

---

## 🚀 Master Verification & Quickstart

### 1. Run Master Test Suite (All 5 Projects)
Execute the root test runner to automatically verify that all 5 projects pass 100% of their test suites:

```bash
python run_all_tests.py
```

### 2. GitHub Submission Setup
You can submit either as a **single unified monorepo** or **5 independent task repositories**:

#### Option A: Submit as a Unified Monorepo (Recommended)
```bash
python setup_git_repos.py
git remote add origin https://github.com/<your-username>/python-internship-portfolio.git
git branch -M main
git push -u origin main
```
*Submit the GitHub repo link for each task.*

#### Option B: Split into 5 Independent Repositories
```bash
python setup_git_repos.py --individual
```
*Creates individual Git commits inside each folder so you can push each to its own GitHub repository.*

---

## 🛠️ Task Summaries

### 02. Packaged CLI Diagnostics Tool (`devdiag`)
- Inspects host Python runtime, virtualenv, memory, CPU, disk, and configured developer toolchain (`git`, `python`, `pip`, `docker`, `node`, etc.).
- Redacts secrets in environment variables (`*_KEY`, `*_TOKEN`, `*_PASS`).
- Analyzes RabTech diagnostic event logs to compute service-level error rates and latency percentiles.
- Command: `devdiag --events sample_data/diagnostic-events.json`

### 03. Core Algorithms, OOP Structures & Robust Error Handling
- Domain: Enterprise Financial Ledger & Multi-Type Account Management Engine.
- Implements `SavingsAccount`, `CheckingAccount`, `InvestmentAccount`, and `BusinessAccount` with polymorphic business rules.
- Cryptographic SHA-256 transaction integrity and binary search timestamp querying.
- Two-way atomic JSON snapshot and CSV export persistence.

### 04. Automated Web Scraping & Data Extraction Pipeline
- Production ETL scraper for technical market intelligence.
- Features exponential backoff retry adapters, polite rate limiting with jitter, and User-Agent rotation.
- Extracts, cleans, and normalizes unstructured HTML data into validated Pydantic schemas.
- Produces analytical summary report with compensation distributions and in-demand skills breakdown.

### 05. FastAPI Microservice with JWT Authentication
- High-throughput REST API with interactive Swagger OpenAPI documentation at `/docs`.
- Passwords hashed securely using `bcrypt` with salt rounds.
- JWT Bearer tokens with expiration claims and role-based access control.
- Cross-user resource isolation and ownership validation.
- Ready-to-import Postman collection included (`postman_collection.json`).

### 06. Enterprise Python Automation Capstone Project (`sentinel`)
- End-to-end infrastructure sentinel collecting host telemetry and probing remote endpoints.
- Evaluates operational SLA thresholds to compute real-time Health Scores and grades.
- Compiles publication-grade executive PDF reports with ReportLab tables and metrics.
- Background daemon runner with interval scheduling and webhook alert dispatching.
- Command: `sentinel run-once`

---

## 📜 License
This project is licensed under the MIT License - open for evaluation and educational review.
