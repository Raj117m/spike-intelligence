from pathlib import Path

from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://mausam.imd.gov.in/responsive/"

html = Path(
    "data_lake/raw/imd/rainfall_page.html"
).read_text(
    encoding="utf-8",
    errors="ignore",
)

soup = BeautifulSoup(html, "html.parser")

print("\n=== POSSIBLE DATA FILES ===\n")

seen = set()

for a in soup.find_all("a", href=True):

    href = a["href"].strip()

    if not href:
        continue

    url = urljoin(BASE, href)

    text = " ".join(a.get_text(" ", strip=True).split())

    if any(
        x in url.lower()
        for x in [
            ".csv",
            ".xls",
            ".xlsx",
            ".zip",
            ".json",
            ".xml",
            ".pdf",
            "rain",
            "district",
            "state",
            "subdivision",
            "daily",
            "weekly",
            "monthly",
            "cumulative",
        ]
    ):

        if url not in seen:
            seen.add(url)
            print(text)
            print(url)
            print()
