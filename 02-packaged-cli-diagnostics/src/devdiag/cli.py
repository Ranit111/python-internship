"""
CLI entry point for the devdiag command-line application.
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import Optional

from devdiag import __version__
from devdiag.event_analyzer import EventAnalyzer, MalformedEventFileError
from devdiag.reporter import DiagnosticReporter
from devdiag.system_inspector import SystemInspector
from devdiag.toolchain_checker import ToolchainChecker


def build_parser() -> argparse.ArgumentParser:
    """Builds and returns command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="devdiag",
        description="Deterministic Developer Environment & Machine Diagnostics CLI Tool",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON instead of human-readable text",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Write diagnostic report to specified file path",
    )
    parser.add_argument(
        "--events",
        type=str,
        default=None,
        help="Path to machine/service diagnostic events JSON file to analyze",
    )
    parser.add_argument(
        "--disk-path",
        type=str,
        default=None,
        help="Custom disk partition mount point to inspect (defaults to root)",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress console output (useful for CI scripts evaluating exit codes)",
    )
    return parser


def run_diagnostics(
    events_path: Optional[str] = None,
    disk_path: Optional[str] = None,
) -> tuple[dict, int]:
    """
    Executes full diagnostic suite and returns aggregated data and exit code.
    Exit codes:
      0 = HEALTHY
      1 = WARNING / DEGRADED
      2 = ERROR / CRITICAL FAILURE
    """
    system_inspector = SystemInspector(disk_path=disk_path)
    system_data = system_inspector.run_full_inspection()

    toolchain_checker = ToolchainChecker()
    toolchain_data = toolchain_checker.check_all()

    events_data = None
    events_status = "HEALTHY"
    if events_path:
        analyzer = EventAnalyzer(events_path)
        events_data = analyzer.analyze()
        events_status = events_data.get("status", "HEALTHY")

    # Determine overall status and exit code
    statuses = [
        system_data["python"]["status"],
        system_data["resources"]["disk"]["status"],
        system_data["resources"]["memory"]["status"],
        toolchain_data["status"],
    ]
    if events_data:
        statuses.append(events_status)

    if "ERROR" in statuses:
        overall_status = "ERROR"
        exit_code = 2
    elif "WARNING" in statuses:
        overall_status = "WARNING"
        exit_code = 1
    else:
        overall_status = "HEALTHY"
        exit_code = 0

    report_payload = {
        "overall_status": overall_status,
        "exit_code": exit_code,
        "system": system_data,
        "toolchain": toolchain_data,
    }
    if events_data:
        report_payload["events"] = events_data

    return report_payload, exit_code


def main(args: Optional[list[str]] = None) -> int:
    """Main CLI entry point."""
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    try:
        data, exit_code = run_diagnostics(
            events_path=parsed_args.events,
            disk_path=parsed_args.disk_path,
        )
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: {e}\n")
        return 2
    except MalformedEventFileError as e:
        sys.stderr.write(f"Error: Malformed diagnostic event file: {e}\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"Fatal Diagnostic Error: {e}\n")
        return 2

    reporter = DiagnosticReporter(data)

    if parsed_args.json:
        output_text = reporter.generate_json()
    else:
        output_text = reporter.generate_human_readable()

    if parsed_args.output:
        out_path = Path(parsed_args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_text, encoding="utf-8")

    if not parsed_args.quiet:
        print(output_text)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
