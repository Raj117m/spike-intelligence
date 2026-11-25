from pathlib import Path

import requests

url = "https://mausam.imd.gov.in/responsive/rainfallinformation_swd.php"

html = requests.get(url, timeout=60)

html.raise_for_status()

Path(
    "data_lake/raw/imd"
).mkdir(
    parents=True,
    exist_ok=True,
)

outfile = Path(
    "data_lake/raw/imd/rainfall_page.html"
)

outfile.write_text(
    html.text,
    encoding="utf-8",
)

print(outfile)
print(len(html.text))
