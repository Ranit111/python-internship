"""
Unit tests for end-to-end ScrapingPipeline.
"""

from scraper.pipeline import ScrapingPipeline


def test_pipeline_end_to_end(tmp_path):
    data_dir = tmp_path / "data"
    pipeline = ScrapingPipeline(output_dir=data_dir)
    pipeline.reports_dir = tmp_path / "reports"

    items, json_p, csv_p, rep_p = pipeline.run_pipeline(use_live=False)

    assert len(items) >= 5
    assert json_p.exists()
    assert csv_p.exists()
    assert rep_p.exists()
    assert rep_p.read_text(encoding="utf-8").startswith("# 📊")
