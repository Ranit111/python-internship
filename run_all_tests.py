"""
Master Test Runner verifying all 5 Python internship projects.
"""

import subprocess
import sys
from pathlib import Path


PROJECTS = [
    {"name": "Task 02: Packaged CLI Diagnostics", "dir": "02-packaged-cli-diagnostics"},
    {"name": "Task 03: Core Algorithms & OOP Ledger", "dir": "03-core-algorithms-oop-ledger"},
    {"name": "Task 04: Web Scraping & ETL Pipeline", "dir": "04-automated-web-scraping-pipeline"},
    {"name": "Task 05: FastAPI JWT Microservice", "dir": "05-fastapi-jwt-microservice"},
    {"name": "Task 06: Enterprise Automation Capstone", "dir": "06-enterprise-automation-capstone"},
]


def run_tests() -> int:
    root_dir = Path(__file__).parent
    total_passed = 0
    total_projects = len(PROJECTS)
    failed_projects = []

    print("=" * 80)
    print("           PYTHON SOFTWARE ENGINEERING INTERNSHIP - TEST SUITE RUNNER")
    print("=" * 80)

    for p in PROJECTS:
        p_dir = root_dir / p["dir"]
        print(f"\n[RUNNING] {p['name']} ({p['dir']})...")
        cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
        
        res = subprocess.run(cmd, cwd=p_dir, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  --> [PASS] All tests passed cleanly for {p['name']}")
            total_passed += 1
        else:
            print(f"  --> [FAIL] Tests failed for {p['name']}")
            print(res.stdout)
            print(res.stderr)
            failed_projects.append(p["name"])

    print("\n" + "=" * 80)
    print(f" TEST SUMMARY: {total_passed}/{total_projects} Projects Passed with 100% Green Status")
    print("=" * 80)

    if failed_projects:
        print(f"Failed Projects: {failed_projects}")
        return 1
    else:
        print("ALL INTERNSHIP DELIVERABLES VERIFIED & READY FOR GITHUB SUBMISSION!")
        return 0


if __name__ == "__main__":
    sys.exit(run_tests())
