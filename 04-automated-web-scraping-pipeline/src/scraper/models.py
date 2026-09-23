"""
Pydantic data models for validated web extraction records.
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class TechJobItem(BaseModel):
    """Normalized and validated technological job listing record."""

    job_id: str = Field(..., description="Unique job listing identifier")
    title: str = Field(..., description="Job role or title")
    company: str = Field(..., description="Hiring organization")
    location: str = Field(default="Remote", description="Job location or remote status")
    salary_min: Optional[float] = Field(default=None, description="Minimum annualized salary USD")
    salary_max: Optional[float] = Field(default=None, description="Maximum annualized salary USD")
    tags: List[str] = Field(default_factory=list, description="Associated tech stacks and tags")
    url: str = Field(..., description="Direct job application URL")
    date_posted: str = Field(..., description="Posting date ISO string")
    seniority: str = Field(default="Mid-Level", description="Seniority classification")

    @field_validator("title", "company", mode="before")
    @classmethod
    def clean_text(cls, v: str) -> str:
        if isinstance(v, str):
            return " ".join(v.split())
        return str(v)

    @field_validator("tags", mode="before")
    @classmethod
    def clean_tags(cls, v: List[str]) -> List[str]:
        if isinstance(v, list):
            cleaned = []
            for item in v:
                c = str(item).strip().lower()
                if c and c not in cleaned:
                    cleaned.append(c)
            return cleaned
        return []

    @property
    def salary_average(self) -> Optional[float]:
        """Returns average salary if range is present."""
        if self.salary_min is not None and self.salary_max is not None:
            return round((self.salary_min + self.salary_max) / 2.0, 2)
        elif self.salary_min is not None:
            return self.salary_min
        elif self.salary_max is not None:
            return self.salary_max
        return None


class ScrapingJobBatch(BaseModel):
    """Collection wrapper for scraped dataset with metadata."""

    source_url: str
    extracted_at: str
    total_records: int
    items: List[TechJobItem]
