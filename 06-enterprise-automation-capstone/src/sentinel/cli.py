"""
Command-line interface (CLI) for the Sentinel Enterprise Automation platform.
"""

from __future__ import annotations
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from sentinel import __version__
from sentinel.scheduler import AutomatedScheduler


def load_config(config_path: Optional[str] = None) -> tuple[Dict[str, Any], Path]:
    """Loads and validates configuration JSON."""
    c_path = Path(config_path) if config_path else (Path.cwd() / "config.json")
    if not c_path.exists():
        # Fallback to defaults
        c_path = Path(__file__).parent.parent.parent / "config.json"

    if not c_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {c_path}")

    with open(c_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config, c_path.parent


def build_parser() -> argparse.ArgumentParser:
    """Builds CLI argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="sentinel",
        description="Enterprise Automated Sentinel: Telemetry, PDF Executive Reporting & Alerts",
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-c", "--config", type=str, default=None, help="Path to config.json file")

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # Subcommand: run-once
    subparsers.add_parser("run-once", help="Executes one complete health inspection and PDF generation")

    # Subcommand: schedule
    sched_p = subparsers.add_parser("schedule", help="Starts continuous automated background monitoring daemon")
    sched_p.add_argument("-i", "--interval", type=int, default=60, help="Interval between runs in seconds (default: 60)")
    sched_p.add_argument("-m", "--max-cycles", type=int, default=None, help="Maximum cycles to execute before exiting")

    # Subcommand: generate-report
    rep_p = subparsers.add_parser("generate-report", help="Generates an executive PDF report immediately")
    rep_p.add_argument("-o", "--output", type=str, default=None, help="Custom output PDF path")

    # Subcommand: verify-config
    subparsers.add_parser("verify-config", help="Validates syntax and thresholds in config.json")

    return parser


def main(args: Optional[list[str]] = None) -> int:
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.subcommand:
        # Default to run-once if no subcommand provided
        parsed_args.subcommand = "run-once"

    try:
        config, config_dir = load_config(parsed_args.config)
    except Exception as e:
        sys.stderr.write(f"Configuration Error: {e}\n")
        return 1

    if parsed_args.subcommand == "verify-config":
        print(f"[OK] Configuration at {config_dir / 'config.json'} is valid!")
        print(f"  * App Name: {config.get('app_name')}")
        print(f"  * Endpoints Configured: {len(config.get('endpoints', []))}")
        print(f"  * Thresholds: {config.get('thresholds')}")
        return 0

    scheduler = AutomatedScheduler(config, config_dir=config_dir)

    if parsed_args.subcommand == "run-once":
        print("[*] Running Sentinel Health Inspection & Report Generation...")
        result = scheduler.run_single_cycle()
        print(f"\n[OK] Health Inspection Complete!")
        print(f"  * Overall Status : {result['evaluation']['overall_status']}")
        print(f"  * Health Score   : {result['evaluation']['health_score']}/100")
        print(f"  * Executive Grade: {result['evaluation']['grade']}")
        print(f"  * PDF Report     : {result['pdf_path']}")
        return 0

    elif parsed_args.subcommand == "generate-report":
        if hasattr(parsed_args, "output") and parsed_args.output:
            scheduler.pdf_generator.output_path = Path(parsed_args.output)
        result = scheduler.run_single_cycle()
        print(f"[OK] PDF Report successfully generated at: {result['pdf_path']}")
        return 0

    elif parsed_args.subcommand == "schedule":
        scheduler.start_loop(
            interval_seconds=parsed_args.interval,
            max_cycles=parsed_args.max_cycles,
        )
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
