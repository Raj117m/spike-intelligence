"""
Resolve the newest Wikimedia pageview dump automatically.
"""

from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup


class WikimediaResolver:

    ROOT = "https://dumps.wikimedia.org/other/pageview_complete/monthly/"

    def years(self):

        html = requests.get(
            self.ROOT,
            timeout=60,
            headers={
                "User-Agent": "DemandPhysicsResearchBot/1.0"
            },
        ).text

        soup = BeautifulSoup(html, "html.parser")

        years = []

        for link in soup.find_all("a"):

            href = link.get("href", "")

            if re.fullmatch(r"\d{4}/", href):

                years.append(href[:-1])

        return sorted(years)

    def newest_year(self):

        return self.years()[-1]
