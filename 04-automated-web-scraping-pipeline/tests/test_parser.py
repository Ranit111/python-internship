"""
Unit tests for HTMLJobParser and data extraction models.
"""

from scraper.parser import HTMLJobParser


def test_parse_salary_range():
    min_s, max_s = HTMLJobParser.parse_salary_range("$120,000 - $160,000")
    assert min_s == 120000.0
    assert max_s == 160000.0

    min_s2, max_s2 = HTMLJobParser.parse_salary_range("140k-180k USD")
    assert min_s2 == 140000.0
    assert max_s2 == 180000.0

    min_s3, max_s3 = HTMLJobParser.parse_salary_range(None)
    assert min_s3 is None and max_s3 is None


def test_parse_html_page():
    sample_html = """
    <div>
      <article class="job-listing" data-job-id="test-1">
        <h2 class="title">Senior AI Engineer</h2>
        <span class="company">OpenTech</span>
        <span class="location">Remote</span>
        <span class="salary">$160k - $210k</span>
        <div class="tags"><span class="tag">python</span><span class="tag">pytorch</span></div>
        <a href="https://example.com/apply/1">Apply</a>
      </article>
    </div>
    """
    items = HTMLJobParser.parse_html_page(sample_html)
    assert len(items) == 1
    job = items[0]
    assert job.job_id == "test-1"
    assert job.title == "Senior AI Engineer"
    assert job.company == "OpenTech"
    assert job.seniority == "Senior"
    assert job.salary_min == 160000.0
    assert job.salary_max == 210000.0
    assert job.salary_average == 185000.0
    assert "python" in job.tags
