"""Download the latest fuel and electricity prices for the ABD group project.

Sources:
- EU Weekly Oil Bulletin (European Commission): weekly consumer prices of petroleum products, history since 2005
- Ember: daily European wholesale electricity prices, history since 2015

The files are saved in data/ with the names used by the source, together with a manifest.json
that Databricks reads to know when the data was downloaded.
"""
import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

OIL_BULLETIN_PAGE = "https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en"
OIL_BULLETIN_FILE = "Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx"
EMBER_URL = ("https://files.ember-energy.org/public-downloads/price/outputs/"
             "european_wholesale_electricity_price_data_daily.csv")
EMBER_FILE = "european_wholesale_electricity_price_data_daily.csv"
DATA_DIR = Path("data")

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (databricks-energy-prices; university project)"


def find_oil_bulletin_link():
    """The download link of the price history has a document id that can change, so we read it from the page."""
    page = session.get(OIL_BULLETIN_PAGE, timeout=60)
    page.raise_for_status()
    for link in BeautifulSoup(page.text, "html.parser").find_all("a", href=True):
        if "Prices_History" in link["href"]:
            return urljoin(OIL_BULLETIN_PAGE, link["href"])
    raise RuntimeError("Price history link not found on the Oil Bulletin page")


def download(url, filename):
    response = session.get(url, timeout=300)
    response.raise_for_status()
    (DATA_DIR / filename).write_bytes(response.content)
    return {"file": filename, "url": url, "size_bytes": len(response.content),
            "sha256": hashlib.sha256(response.content).hexdigest()}


def main():
    DATA_DIR.mkdir(exist_ok=True)
    files = [download(find_oil_bulletin_link(), OIL_BULLETIN_FILE),
             download(EMBER_URL, EMBER_FILE)]
    manifest = {"download_date": date.today().isoformat(), "files": files}
    (DATA_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
