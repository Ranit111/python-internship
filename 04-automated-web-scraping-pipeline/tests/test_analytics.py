"""
Unit tests for JobMarketAnalytics and markdown report generator.
"""

from scraper.analytics import JobMarketAnalytics
from scraper.models import TechJobItem


def test_analytics_computation():
    jobs = [
        TechJobItem(
            job_id="j1",
            title="Senior Python Dev",
            company="Google",
            location="Remote",
            salary_min=150000,
            salary_max=200000,
            tags=["python", "fastapi"],
            url="https://google.com/1",
            date_posted="2026-09-01",
            seniority="Senior",
        ),
        TechJobItem(
            job_id="j2",
            title="Junior Dev",
            company="Amazon",
            location="Onsite",
            salary_min=90000,
            salary_max=110000,
            tags=["python", "aws"],
            url="https://amazon.com/2",
            date_posted="2026-09-01",
            seniority="Junior",
        ),
    ]

    analytics = JobMarketAnalytics(jobs)
    stats = analytics.compute_summary_statistics()

    assert stats["total_jobs"] == 2
    assert stats["unique_companies"] == 2
    assert stats["salary_metrics"]["mean_usd"] == 137500.0
    assert stats["top_skills"][0]["skill"] == "python"

    md = analytics.generate_markdown_report()
    assert "# 📊 Tech Job Market Intelligence" in md
    assert "Average Market Salary" in md
