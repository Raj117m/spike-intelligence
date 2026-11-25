from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://mausam.imd.gov.in"

URLS = [

    "/responsive/rainfallinformation.php",

    "/responsive/rainfallinformation_state.php",

    "/responsive/rainfallinformation_msd.php",

    "/responsive/rainfall_statistics.php",

    "/responsive/rainfall_page_station_rainfall.php",

]

for page in URLS:

    url = BASE + page

    print("\n", "=" * 80)

    print(url)

    r = requests.get(url, timeout=60)

    print("Status:", r.status_code)

    Path("data_lake/raw/imd").mkdir(parents=True, exist_ok=True)

    filename = page.split("/")[-1]

    Path(f"data_lake/raw/imd/{filename}.html").write_text(
        r.text,
        encoding="utf-8",
    )

    soup = BeautifulSoup(r.text, "html.parser")

    print("Title:", soup.title.text if soup.title else "None")

    print("Tables:", len(soup.find_all("table")))

    print("Links:", len(soup.find_all("a")))

    print("Forms:", len(soup.find_all("form")))

    print("\nPossible downloadable files:\n")

    seen = set()

    for a in soup.find_all("a", href=True):

        href = urljoin(url, a["href"])

        if href in seen:
            continue

        seen.add(href)

        if any(
            x in href.lower()
            for x in [
                ".csv",
                ".xls",
                ".xlsx",
                ".pdf",
                ".json",
                ".xml",
                ".zip",
            ]
        ):

            print(href)
