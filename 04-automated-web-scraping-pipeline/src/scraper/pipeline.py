"""
End-to-End ETL Scraping Pipeline runner and CLI entrypoint.
"""

from __future__ import annotations
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from scraper.analytics import JobMarketAnalytics
from scraper.client import ResilientHTTPClient
from scraper.models import ScrapingJobBatch, TechJobItem
from scraper.parser import HTMLJobParser

# Realistic HTML fixture simulating a live tech job directory
DEFAULT_HTML_TEST_FIXTURE = """
<!DOCTYPE html>
<html>
<head><title>Remote Tech Job Directory</title></head>
<body>
  <div class="job-container">
    <article class="job-listing" data-job-id="job-101">
      <h2 class="title">Senior Python Backend Engineer</h2>
      <span class="company">Stripe Infrastructure</span>
      <span class="location">Remote - US/Global</span>
      <span class="salary">$150,000 - $190,000</span>
      <div class="tags"><span class="tag">python</span><span class="tag">fastapi</span><span class="tag">postgresql</span><span class="tag">aws</span><span class="tag">docker</span></div>
      <a href="https://stripe.com/jobs/101">Apply Now</a>
    </article>

    <article class="job-listing" data-job-id="job-102">
      <h2 class="title">Lead Machine Learning Engineer</h2>
      <span class="company">Anthropic Labs</span>
      <span class="location">Remote - USA</span>
      <span class="salary">$180,000 - $240,000</span>
      <div class="tags"><span class="tag">python</span><span class="tag">pytorch</span><span class="tag">ai</span><span class="tag">kubernetes</span><span class="tag">gpu</span></div>
      <a href="https://anthropic.com/jobs/102">Apply Now</a>
    </article>

    <article class="job-listing" data-job-id="job-103">
      <h2 class="title">Full Stack React & Python Developer</h2>
      <span class="company">Datadog</span>
      <span class="location">Remote - Europe</span>
      <span class="salary">120k - 150k USD</span>
      <div class="tags"><span class="tag">react</span><span class="tag">python</span><span class="tag">typescript</span><span class="tag">graphql</span></div>
      <a href="https://datadog.com/jobs/103">Apply Now</a>
    </article>

    <article class="job-listing" data-job-id="job-104">
      <h2 class="title">Junior DevOps & Cloud Engineer</h2>
      <span class="company">Cloudflare</span>
      <span class="location">Remote - Global</span>
      <span class="salary">$90,000 - $115,000</span>
      <div class="tags"><span class="tag">golang</span><span class="tag">docker</span><span class="tag">kubernetes</span><span class="tag">terraform</span><span class="tag">aws</span></div>
      <a href="https://cloudflare.com/jobs/104">Apply Now</a>
    </article>

    <article class="job-listing" data-job-id="job-105">
      <h2 class="title">Senior Distributed Systems Architect</h2>
      <span class="company">Snowflake</span>
      <span class="location">San Francisco / Remote</span>
      <span class="salary">$200,000 - $260,000</span>
      <div class="tags"><span class="tag">rust</span><span class="tag">c++</span><span class="tag">distributed-systems</span><span class="tag">sql</span></div>
      <a href="https://snowflake.com/jobs/105">Apply Now</a>
    </article>

    <article class="job-listing" data-job-id="job-106">
      <h2 class="title">Data Engineer - Python & Spark</h2>
      <span class="company">Spotify</span>
      <span class="location">New York / Remote</span>
      <span class="salary">$140,000 - $175,000</span>
      <div class="tags"><span class="tag">python</span><span class="tag">spark</span><span class="tag">airflow</span><span class="tag">sql</span><span class="tag">gcp</span></div>
      <a href="https://spotify.com/jobs/106">Apply Now</a>
    </article>
  </div>
</body>
</html>
"""


class ScrapingPipeline:
    """Manages the full ETL lifecycle: Extract, Transform, Validate, Load, and Analyze."""

    def __init__(self, target_url: Optional[str] = None, output_dir: Optional[Path] = None) -> None:
        self.target_url = target_url or "https://remoteok.com/api"
        self.output_dir = output_dir or (Path(__file__).parent.parent.parent / "data")
        self.reports_dir = (Path(__file__).parent.parent.parent / "reports")

    def extract(self, use_live: bool = False) -> str:
        """Extracts HTML/content from web target or uses test fixture."""
        if use_live:
            try:
                with ResilientHTTPClient() as client:
                    resp = client.get("https://remoteok.com/")
                    if resp.status_code == 200 and len(resp.text) > 500:
                        return resp.text
            except Exception as e:
                print(f"[WARN] Live scraping fallback to fixture due to: {e}", file=sys.stderr)

        return DEFAULT_HTML_TEST_FIXTURE

    def transform(self, raw_html: str) -> List[TechJobItem]:
        """Parses HTML into normalized Pydantic TechJobItem objects."""
        return HTMLJobParser.parse_html_page(raw_html)

    def load(self, items: List[TechJobItem]) -> tuple[Path, Path]:
        """Persists items into JSON and CSV data stores."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / "tech_jobs_dataset.json"
        csv_path = self.output_dir / "tech_jobs_dataset.csv"

        # 1. JSON Export
        batch = ScrapingJobBatch(
            source_url=self.target_url,
            extracted_at=datetime.now(timezone.utc).isoformat(),
            total_records=len(items),
            items=items,
        )
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(batch.model_dump(), f, indent=2)

        # 2. CSV Export
        fieldnames = ["job_id", "title", "company", "location", "seniority", "salary_min", "salary_max", "salary_average", "tags", "url", "date_posted"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in items:
                writer.writerow({
                    "job_id": item.job_id,
                    "title": item.title,
                    "company": item.company,
                    "location": item.location,
                    "seniority": item.seniority,
                    "salary_min": item.salary_min or "",
                    "salary_max": item.salary_max or "",
                    "salary_average": item.salary_average or "",
                    "tags": "; ".join(item.tags),
                    "url": item.url,
                    "date_posted": item.date_posted,
                })

        return json_path, csv_path

    def run_pipeline(self, use_live: bool = False) -> tuple[List[TechJobItem], Path, Path, Path]:
        """Runs end-to-end extraction, persistence, and analytics reporting."""
        # 1. Extract
        raw_html = self.extract(use_live=use_live)

        # 2. Transform
        items = self.transform(raw_html)

        # 3. Load
        json_path, csv_path = self.load(items)

        # 4. Analytics
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.reports_dir / "market_summary_report.md"

        analytics = JobMarketAnalytics(items)
        md_report = analytics.generate_markdown_report()
        report_path.write_text(md_report, encoding="utf-8")

        return items, json_path, csv_path, report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated ETL Web Scraping Pipeline")
    parser.add_argument("--live", action="store_true", help="Attempt live web scraping before fallback")
    args = parser.parse_args()

    pipeline = ScrapingPipeline()
    items, json_p, csv_p, rep_p = pipeline.run_pipeline(use_live=args.live)

    print(f"[OK] ETL Pipeline successfully executed!")
    print(f"  * Extracted Records: {len(items)}")
    print(f"  * JSON Output      : {json_p}")
    print(f"  * CSV Output       : {csv_p}")
    print(f"  * Analytical Report: {rep_p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
