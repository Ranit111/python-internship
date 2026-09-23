"""
Job Market Statistical Analytics and Automated Report Generator.
"""

from __future__ import annotations
import collections
import statistics
from typing import Any, Dict, List
from scraper.models import TechJobItem


class JobMarketAnalytics:
    """Calculates statistics, skill frequencies, salary percentiles, and generates analytical reports."""

    def __init__(self, jobs: List[TechJobItem]) -> None:
        self.jobs = jobs

    def compute_summary_statistics(self) -> Dict[str, Any]:
        """Calculates comprehensive quantitative metrics from the scraped job dataset."""
        total_jobs = len(self.jobs)
        if total_jobs == 0:
            return {"total_jobs": 0, "status": "EMPTY"}

        companies = set(j.company for j in self.jobs)
        salaries = [j.salary_average for j in self.jobs if j.salary_average is not None]

        if salaries:
            sorted_sal = sorted(salaries)
            salary_metrics = {
                "records_with_salary": len(salaries),
                "coverage_pct": round((len(salaries) / total_jobs) * 100, 1),
                "min_usd": round(min(salaries), 2),
                "max_usd": round(max(salaries), 2),
                "mean_usd": round(statistics.mean(salaries), 2),
                "median_usd": round(statistics.median(salaries), 2),
                "p75_usd": round(sorted_sal[int(len(sorted_sal) * 0.75)], 2),
                "p90_usd": round(sorted_sal[int(len(sorted_sal) * 0.9)], 2),
            }
        else:
            salary_metrics = {"records_with_salary": 0, "coverage_pct": 0.0}

        # Tag / Skill frequency
        tag_counter: collections.Counter = collections.Counter()
        for j in self.jobs:
            for t in j.tags:
                tag_counter[t] += 1
        
        top_skills = [
            {"skill": skill, "count": count, "frequency_pct": round((count / total_jobs) * 100, 1)}
            for skill, count in tag_counter.most_common(10)
        ]

        # Seniority distribution
        seniority_counter = collections.Counter(j.seniority for j in self.jobs)
        
        # Location distribution
        location_counter = collections.Counter(
            "Remote" if "remote" in j.location.lower() else "Onsite/Hybrid" for j in self.jobs
        )

        return {
            "total_jobs": total_jobs,
            "unique_companies": len(companies),
            "salary_metrics": salary_metrics,
            "top_skills": top_skills,
            "seniority_breakdown": dict(seniority_counter),
            "workplace_type": dict(location_counter),
        }

    def generate_markdown_report(self) -> str:
        """Generates an executive analytical report in Markdown format."""
        stats = self.compute_summary_statistics()
        if stats.get("total_jobs", 0) == 0:
            return "# Tech Job Market Intelligence Report\n\nNo records available to analyze."

        sal = stats.get("salary_metrics", {})
        skills = stats.get("top_skills", [])
        seniority = stats.get("seniority_breakdown", {})
        workplace = stats.get("workplace_type", {})

        md = []
        md.append("# 📊 Tech Job Market Intelligence & ETL Scraping Report")
        md.append(f"\n*Automated analytical pipeline report generated from {stats['total_jobs']} extracted postings across {stats['unique_companies']} hiring organizations.*\n")
        
        md.append("## 1. Executive Summary & Key KPIs\n")
        md.append("| Metric | Value | Description |")
        md.append("| :--- | :--- | :--- |")
        md.append(f"| **Total Job Listings** | `{stats['total_jobs']}` | Extracted & validated records |")
        md.append(f"| **Unique Companies** | `{stats['unique_companies']}` | Active hiring employers |")
        if sal.get("records_with_salary", 0) > 0:
            md.append(f"| **Average Market Salary** | `${sal['mean_usd']:,.2f}` | Mean annualized compensation |")
            md.append(f"| **Median Salary (P50)** | `${sal['median_usd']:,.2f}` | 50th percentile baseline |")
            md.append(f"| **Top Tier Salary (P90)** | `${sal['p90_usd']:,.2f}` | 90th percentile top bracket |")
            md.append(f"| **Salary Transparency** | `{sal['coverage_pct']}%` | Postings with explicit pay |")
        md.append("")

        md.append("## 2. In-Demand Skills & Technology Frequency\n")
        md.append("| Rank | Technology / Skill | Job Count | Market Demand Share |")
        md.append("| :---: | :--- | :---: | :--- |")
        for rank, s in enumerate(skills, 1):
            bar = "█" * int(s["frequency_pct"] // 5)
            md.append(f"| {rank} | **{s['skill'].upper()}** | `{s['count']}` | `{bar}` {s['frequency_pct']}% |")
        md.append("")

        md.append("## 3. Seniority & Experience Level Distribution\n")
        md.append("| Seniority Level | Number of Openings | Share |")
        md.append("| :--- | :---: | :--- |")
        for level, count in seniority.items():
            pct = round((count / stats["total_jobs"]) * 100, 1)
            md.append(f"| **{level}** | `{count}` | {pct}% |")
        md.append("")

        md.append("## 4. Workplace Flexibility\n")
        for w_type, count in workplace.items():
            pct = round((count / stats["total_jobs"]) * 100, 1)
            md.append(f"- **{w_type}**: `{count}` positions ({pct}%)")
        md.append("")

        md.append("## 5. Pipeline Data Governance\n")
        md.append("- **Extraction Method**: Resilient HTTP GET with rate limiting & User-Agent rotation.")
        md.append("- **Validation**: Pydantic models verifying schemas, salary ranges, and tag normalization.")
        md.append("- **Exports Generated**: `data/tech_jobs_dataset.json` and `data/tech_jobs_dataset.csv`.")
        md.append("\n---\n*Report generated deterministically by the ETL Web Scraping Pipeline.*")

        return "\n".join(md)
