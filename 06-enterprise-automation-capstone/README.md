# Task 06: Enterprise Python Automation Capstone Project

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Tests](https://img.shields.io/badge/pytest-11%20passed-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen.svg)
![ReportLab](https://img.shields.io/badge/PDF_Engine-ReportLab-red.svg)

**Enterprise Automated Sentinel** is an end-to-end production Python application providing automated infrastructure telemetry collection, SLA anomaly detection, automated PDF executive health report compilation, real-time alert dispatching (Webhook/Slack/Console), and background daemon scheduling.

---

## 🏗️ Architecture & Pipeline Flow

```mermaid
flowchart TD
    subgraph Data Ingestion
        A[Host System Telemetry<br/>CPU, Memory, Disk, OS] --> D[Sentinel Collector]
        B[Remote API Health Checks<br/>Latency & Status Codes] --> D
    end

    subgraph Evaluation & Decision
        D --> E[HealthAnalyzer<br/>- Threshold Matrix<br/>- Health Score 0-100<br/>- SLA Incident Anomaly Log]
    end

    subgraph Reporting & Dispatch
        E --> F[PDFReportGenerator<br/>(ReportLab Engine)<br/>executive_health_report.pdf]
        E --> G[AlertNotifier<br/>- Webhook / Slack JSON<br/>- Rich Terminal Summary]
    end

    subgraph Automation Engine
        H[AutomatedScheduler CLI Daemon] --> D
    end
```

---

## 🌟 Key Features

1. **Multi-Source Telemetry Collector**:
   - Host metrics: CPU core usage %, physical/virtual memory breakdown (total/used/available), primary disk partition usage, OS platform parameters.
   - Remote endpoints: Concurrent HTTP probing of critical APIs (payment gateways, authentication servers, external partners) with latency tracking and status verification.
2. **SLA Anomaly Detection & Health Scoring**:
   - Compares metrics against configurable thresholds (`config.json`).
   - Computes weighted **Health Score (0-100)** and letter grade (`GRADE A+ (Optimal)`, `GRADE B (Degraded)`, `GRADE D (Critical)`, `GRADE F (Major Outage)`).
3. **Automated PDF Executive Report Generator**:
   - Generates publication-grade styled PDFs using `ReportLab Platypus`.
   - Formatted executive summary banner, status cards, host hardware resource table, API health matrix, and actionable incident log.
4. **Multi-Channel Alert Dispatcher**:
   - Rich terminal display with formatted tables and color-coded status badges.
   - Webhook & Slack POST alert payloads dispatched on warning/critical incidents.
5. **CLI & Background Daemon Scheduling**:
   - CLI subcommands: `run-once`, `schedule`, `generate-report`, `verify-config`.
   - Continuous interval-based execution loop.

---

## 🚀 Installation & Usage

### 1. Install Application
```bash
cd 06-enterprise-automation-capstone
pip install -r requirements.txt
pip install -e .
```

### 2. CLI Commands

#### One-Shot Health Audit & PDF Generation:
```bash
sentinel run-once
```

#### Generate Custom Output PDF Report:
```bash
sentinel generate-report -o output/custom_executive_report.pdf
```

#### Validate System Configuration:
```bash
sentinel verify-config
```

#### Start Background Automation Daemon (every 60 seconds):
```bash
sentinel schedule --interval 60
```

---

## 📄 Sample Generated Deliverables

- **Executive PDF Health Report**: [`output/executive_health_report.pdf`](file:///output/executive_health_report.pdf)
- **Configuration File**: [`config.json`](file:///config.json)

---

## 🧪 Unit & Integration Testing

```bash
cd 06-enterprise-automation-capstone
pytest tests/ -v --cov=sentinel --cov-report=term-missing
```

### Test Suite Highlights
- ✅ **11 passed test cases** achieving **93% test coverage**.
- ✅ Validated end-to-end CLI arguments, background scheduler loop, mock HTTP probes, anomaly scoring, and binary PDF creation.
