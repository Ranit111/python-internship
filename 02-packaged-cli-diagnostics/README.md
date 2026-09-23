# Task 02: Packaged CLI Diagnostics Tool (`devdiag`)

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Build Status](https://img.shields.io/badge/tests-17%20passed-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A production-ready, distributable command-line diagnostics tool that inspects a host machine and produces deterministic developer-environment health reports in both formatted human-readable text and structured JSON.

---

## 📌 Features & Capabilities

- **Python Runtime Inspection**: Checks Python version compatibility ($\ge 3.9$), virtual environment status (`VIRTUAL_ENV`), executable paths, and compiler information.
- **Hardware & OS Auditing**: Measures primary disk capacity/usage, virtual memory (RAM) allocation, CPU core counts, and platform architecture.
- **Developer Toolchain Verification**: Scans `PATH` for essential and optional developer binaries (`git`, `python`, `pip`, `pytest`, `node`, `npm`, `docker`, `rustc`, `go`, `sqlite3`), reporting operational status and versions.
- **Environment Security Audit**: Inspects system environment variables with automatic masking of secrets (`*_KEY`, `*_SECRET`, `*_TOKEN`, `*_PASS`).
- **Telemetry Event Log Analysis**: Analyzes machine and service diagnostic events (e.g. `diagnostic-events.json` starter dataset), computing error rates, latency percentiles (min, max, mean, median, P90), and service-level health.
- **Deterministic Exit Codes**:
  - `0`: Environment is **HEALTHY** (all required tools and metrics pass).
  - `1`: Environment is **DEGRADED / WARNING** (optional tools missing or resource threshold warning).
  - `2`: Environment has **CRITICAL ERRORS** (missing required tools, high error rate, or malformed input paths).

---

## 🚀 Installation & Quickstart

### 1. Install in editable mode
```bash
cd 02-packaged-cli-diagnostics
pip install -e .
```

### 2. Run Diagnostics

#### Standard Terminal Health Report:
```bash
devdiag
```

#### Analyze Service Event Log:
```bash
devdiag --events sample_data/diagnostic-events.json
```

#### Export Structured JSON Report:
```bash
devdiag --events sample_data/diagnostic-events.json --json -o reports/sample_health_report.json
```

#### Save Human-Readable Report to File:
```bash
devdiag --events sample_data/diagnostic-events.json -o reports/sample_health_report.txt
```

---

## 📊 Sample Output (Human-Readable)

```text
========================================================================
             DEVELOPER ENVIRONMENT HEALTH REPORT
========================================================================
 Timestamp    : 2026-09-23T06:18:20+00:00
 Overall Status: [WARNING] (Exit Code: 1)
------------------------------------------------------------------------

[1] PYTHON RUNTIME & ENVIRONMENT
  * Python Version  : 3.11.9 (HEALTHY)
  * Executable Path : C:\Python311\python.exe
  * Virtualenv Active: YES
  * Virtualenv Path : C:\projects\dev-environment\.venv
  * Compiler/Impl   : CPython / MSC v.1938 64 bit (AMD64)

[2] OPERATING SYSTEM & HARDWARE RESOURCES
  * OS Platform     : Windows 10 (64bit)
  * CPU Cores       : 8 Physical, 12 Logical (12.5% utilized)
  * Memory (RAM)    : 11.58 / 15.7 GB (73.7%) [HEALTHY]
  * Primary Disk    : 58.67 GB free of 474.71 GB (87.6%) [WARNING]

[3] CONFIGURED DEVELOPER TOOLCHAIN
  * Tools Checked   : 10 (Healthy: 5, Warn: 5, Fail: 0)
    - git        [HEALTHY] (Required) : git version 2.52.0.windows.1
    - python     [HEALTHY] (Required) : Python 3.11.9
    - pip        [HEALTHY] (Required) : pip 26.2.1
    - pytest     [HEALTHY] (Optional) : pytest 9.1.1
    - node       [HEALTHY] (Optional) : v26.7.0

[4] DIAGNOSTIC EVENT LOG ANALYSIS
  * Total Events    : 5
  * Overall Status  : [ERROR] (Error Rate: 40.0%)
  * Event Levels    : INFO=2, WARN=1, ERROR=2
  * Latency Metrics : Mean=620.75ms | Median=562.5ms | Max=1210.0ms | P90=1210.0ms
  * Service Breakdown:
      * billing-api   : 3 reqs, 1 errs (33.33%), avg 534.0ms [ERROR]
      * profile-api   : 2 reqs, 1 errs (50.0%), avg 707.5ms [ERROR]
========================================================================
```

---

## 🧪 Running Unit Tests

```bash
pytest tests/ -v --cov=src
```

### Test Coverage Breakdown
- `test_system_inspector.py`: Python runtime, hardware metrics, OS properties, and secret masking.
- `test_toolchain_checker.py`: Tool discovery, binary execution, optional vs required tools.
- `test_event_analyzer.py`: Official starter events dataset, latency stats, error calculations, malformed JSON handling.
- `test_cli.py`: CLI arguments, exit code propagation, JSON output export, and quiet mode.

---

## 📂 Project Structure

```
02-packaged-cli-diagnostics/
├── pyproject.toml
├── README.md
├── reports/
│   ├── sample_health_report.json
│   └── sample_health_report.txt
├── sample_data/
│   └── diagnostic-events.json
├── src/
│   └── devdiag/
│       ├── __init__.py
│       ├── cli.py
│       ├── event_analyzer.py
│       ├── reporter.py
│       ├── system_inspector.py
│       └── toolchain_checker.py
└── tests/
    ├── test_cli.py
    ├── test_event_analyzer.py
    ├── test_system_inspector.py
    └── test_toolchain_checker.py
```
