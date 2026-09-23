# 📊 Tech Job Market Intelligence & ETL Scraping Report

*Automated analytical pipeline report generated from 6 extracted postings across 6 hiring organizations.*

## 1. Executive Summary & Key KPIs

| Metric | Value | Description |
| :--- | :--- | :--- |
| **Total Job Listings** | `6` | Extracted & validated records |
| **Unique Companies** | `6` | Active hiring employers |
| **Average Market Salary** | `\$167,500.00` | Mean annualized compensation |
| **Median Salary (P50)** | `\$163,750.00` | 50th percentile baseline |
| **Top Tier Salary (P90)** | `\$230,000.00` | 90th percentile top bracket |
| **Salary Transparency** | `100.0%` | Postings with explicit pay |

## 2. In-Demand Skills & Technology Frequency

| Rank | Technology / Skill | Job Count | Market Demand Share |
| :---: | :--- | :---: | :--- |
| 1 | **PYTHON** | `4` | `█████████████` 66.7% |
| 2 | **AWS** | `2` | `██████` 33.3% |
| 3 | **DOCKER** | `2` | `██████` 33.3% |
| 4 | **KUBERNETES** | `2` | `██████` 33.3% |
| 5 | **SQL** | `2` | `██████` 33.3% |
| 6 | **PYTHONFASTAPIPOSTGRESQLAWSDOCKER** | `1` | `███` 16.7% |
| 7 | **FASTAPI** | `1` | `███` 16.7% |
| 8 | **POSTGRESQL** | `1` | `███` 16.7% |
| 9 | **PYTHONPYTORCHAIKUBERNETESGPU** | `1` | `███` 16.7% |
| 10 | **PYTORCH** | `1` | `███` 16.7% |

## 3. Seniority & Experience Level Distribution

| Seniority Level | Number of Openings | Share |
| :--- | :---: | :--- |
| **Senior** | `3` | 50.0% |
| **Mid-Level** | `2` | 33.3% |
| **Junior** | `1` | 16.7% |

## 4. Workplace Flexibility

- **Remote**: `6` positions (100.0%)

## 5. Pipeline Data Governance

- **Extraction Method**: Resilient HTTP GET with rate limiting & User-Agent rotation.
- **Validation**: Pydantic models verifying schemas, salary ranges, and tag normalization.
- **Exports Generated**: `data/tech_jobs_dataset.json` and `data/tech_jobs_dataset.csv`.

---
*Report generated deterministically by the ETL Web Scraping Pipeline.*