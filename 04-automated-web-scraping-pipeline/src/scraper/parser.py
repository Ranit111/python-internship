"""
HTML parser and text transformation engine using BeautifulSoup4.
"""

from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup

from scraper.models import TechJobItem


class HTMLJobParser:
    """Parses raw HTML job board markups into validated Pydantic domain models."""

    @staticmethod
    def parse_salary_range(salary_text: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
        """
        Parses salary strings such as '$120,000 - $160,000', '130k-180k', '$95,000/yr'.
        Returns (min_salary, max_salary) in USD float.
        """
        if not salary_text:
            return None, None

        cleaned = salary_text.replace(",", "").replace("$", "").lower()
        # Look for numbers with optional 'k'
        matches = re.findall(r"(\d+(?:\.\d+)?)\s*(k)?", cleaned)
        if not matches:
            return None, None

        parsed_values = []
        for val_str, has_k in matches:
            val = float(val_str)
            if has_k or val < 1000:
                val *= 1000
            parsed_values.append(val)

        if len(parsed_values) >= 2:
            return min(parsed_values), max(parsed_values)
        elif len(parsed_values) == 1:
            return parsed_values[0], parsed_values[0]
        return None, None

    @classmethod
    def parse_html_page(cls, html_content: str, base_url: str = "https://example-jobs.com") -> List[TechJobItem]:
        """Parses HTML document extracting structured job items."""
        soup = BeautifulSoup(html_content, "html.parser")
        job_elements = soup.find_all(attrs={"data-job-id": True})
        if not job_elements:
            job_elements = soup.find_all("article", class_=re.compile(r"job|listing|post", re.I))
        if not job_elements:
            job_elements = soup.find_all("tr", class_=re.compile(r"job|row", re.I))

        extracted_jobs: List[TechJobItem] = []

        for idx, el in enumerate(job_elements):
            job_id = el.get("data-job-id") or f"job-{idx+1:04d}"
            
            # Title
            title_el = el.find(["h2", "h3", "h4", "a"], class_=re.compile(r"title|role|position", re.I)) or el.find(["h2", "h3", "h4"])
            title = title_el.get_text(strip=True) if title_el else "Software Engineer"

            # Company
            company_el = el.find(class_=re.compile(r"company|employer|brand", re.I))
            company = company_el.get_text(strip=True) if company_el else "Tech Innovations Inc"

            # Location
            location_el = el.find(class_=re.compile(r"location|remote|geo", re.I))
            location = location_el.get_text(strip=True) if location_el else "Remote"

            # Salary
            salary_el = el.find(class_=re.compile(r"salary|compensation|pay", re.I))
            salary_text = salary_el.get_text(strip=True) if salary_el else None
            s_min, s_max = cls.parse_salary_range(salary_text)

            # Tags
            tag_elements = el.find_all(class_=re.compile(r"tag|skill|pill|badge", re.I))
            tags = [t.get_text(strip=True) for t in tag_elements]
            if not tags:
                # Infer tags from title
                lower_title = title.lower()
                for tech in ["python", "fastapi", "django", "react", "golang", "aws", "docker", "kubernetes", "sql", "ai"]:
                    if tech in lower_title:
                        tags.append(tech)

            # URL
            link_el = el.find("a", href=True)
            job_url = link_el["href"] if link_el else f"{base_url}/jobs/{job_id}"
            if not job_url.startswith("http"):
                job_url = f"{base_url.rstrip('/')}/{job_url.lstrip('/')}"

            # Seniority
            seniority = "Mid-Level"
            t_low = title.lower()
            if "senior" in t_low or "sr" in t_low or "lead" in t_low or "principal" in t_low:
                seniority = "Senior"
            elif "junior" in t_low or "jr" in t_low or "intern" in t_low or "associate" in t_low:
                seniority = "Junior"
            elif "staff" in t_low or "architect" in t_low:
                seniority = "Staff/Architect"

            job_item = TechJobItem(
                job_id=str(job_id),
                title=title,
                company=company,
                location=location,
                salary_min=s_min,
                salary_max=s_max,
                tags=tags,
                url=job_url,
                date_posted=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                seniority=seniority,
            )
            extracted_jobs.append(job_item)

        return extracted_jobs
