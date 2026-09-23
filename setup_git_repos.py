"""
Helper utility to initialize and publish Git repositories for internship submissions.
"""

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
TASK_DIRS = [
    ("02-packaged-cli-diagnostics", "feat: complete Task 02 Packaged CLI Diagnostics Tool"),
    ("03-core-algorithms-oop-ledger", "feat: complete Task 03 Core Algorithms & OOP Ledger Engine"),
    ("04-automated-web-scraping-pipeline", "feat: complete Task 04 Automated Web Scraping & ETL Pipeline"),
    ("05-fastapi-jwt-microservice", "feat: complete Task 05 FastAPI Microservice with JWT Auth"),
    ("06-enterprise-automation-capstone", "feat: complete Task 06 Enterprise Automation Sentinel Capstone"),
]


def run_cmd(cmd: list[str], cwd: Path) -> None:
    print(f"[{cwd.name}] Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0 and "already exists" not in res.stderr.lower():
        print(f"  Note: {res.stderr.strip()}")
    elif res.stdout.strip():
        print(f"  {res.stdout.strip()[:100]}...")


def init_monorepo() -> None:
    """Initializes the entire portfolio as a single unified Git repository."""
    print("\n--- Initializing Unified Master Portfolio Repository ---")
    run_cmd(["git", "init"], ROOT_DIR)
    run_cmd(["git", "add", "."], ROOT_DIR)
    run_cmd(["git", "commit", "-m", "feat: complete all 5 Python Software Engineering internship deliverables (Tasks 02-06)"], ROOT_DIR)
    print("\n[SUCCESS] Master portfolio initialized and committed!")
    print("To push to GitHub:")
    print("  git remote add origin <your-github-repo-url>")
    print("  git branch -M main")
    print("  git push -u origin main")


def init_individual_repos() -> None:
    """Initializes independent Git repositories in each task subdirectory."""
    print("\n--- Initializing 5 Independent Git Repositories ---")
    for d_name, msg in TASK_DIRS:
        sub_dir = ROOT_DIR / d_name
        if sub_dir.exists():
            print(f"\nSetting up repository for: {d_name}")
            run_cmd(["git", "init"], sub_dir)
            run_cmd(["git", "add", "."], sub_dir)
            run_cmd(["git", "commit", "-m", msg], sub_dir)
    print("\n[SUCCESS] All 5 task repositories initialized!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--individual":
        init_individual_repos()
    else:
        init_monorepo()
