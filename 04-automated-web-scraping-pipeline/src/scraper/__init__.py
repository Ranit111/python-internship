"""
Automated Web Scraping & Data Extraction Pipeline.
"""

from scraper.client import ResilientHTTPClient
from scraper.models import TechJobItem, ScrapingJobBatch
from scraper.parser import HTMLJobParser
from scraper.analytics import JobMarketAnalytics
from scraper.pipeline import ScrapingPipeline

__version__ = "1.0.0"
__all__ = [
    "ResilientHTTPClient",
    "TechJobItem",
    "ScrapingJobBatch",
    "HTMLJobParser",
    "JobMarketAnalytics",
    "ScrapingPipeline",
]
