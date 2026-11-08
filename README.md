# Databricks energy prices

Automatic daily download of fuel and electricity prices for the group project of the course
*Analyzing Big Data* (NOVA IMS, 2026/2027): a Data Lakehouse on Databricks about new passenger cars registered
in Germany, Spain, France, Italy and Portugal.

## Why this repository

Databricks Free Edition can only reach a short list of internet domains, and the two sources below are not on it.
GitHub is, so this repository works as a bridge:

1. Every day at 05:00 UTC a GitHub Action runs `fetch_prices.py`, downloads the files from the sources and commits
   the ones that changed in `data/`, together with `data/manifest.json` (download date, size and checksum of each
   changed file). Ember changes every day, the Oil Bulletin once a week; if nothing changed, nothing is committed.
2. Every day at 08:00 (Lisbon) a Databricks job reads `manifest.json` from this repository, copies the changed files
   to the Volume `automotive_analytics.raw.energy_prices_files/<download_date>/` and appends them to the Bronze tables.

Each download is a new read of the sources, so the Bronze layer keeps the full read history.

## Sources

| File | Source | Updated | Licence |
|---|---|---|---|
| `Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx` | [EU Weekly Oil Bulletin](https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en) – European Commission, DG Energy. Consumer prices of petrol, diesel, LPG and heating oil by EU country, weekly since 2005 | weekly | reuse with acknowledgement of the source |
| `european_wholesale_electricity_price_data_daily.csv` | [Ember – European Wholesale Electricity Price Data](https://ember-energy.org/data/european-wholesale-electricity-price-data), based on ENTSO-E. Daily day-ahead wholesale prices by country since 2015 | daily | CC-BY-4.0 |

The Oil Bulletin link has a document id that can change, so the script finds it on the bulletin page with
BeautifulSoup. The Ember file has a fixed URL.

## Repository structure

```
├── fetch_prices.py                       # downloads the files and writes the manifest of the changed ones
├── requirements.txt                      # requests, beautifulsoup4
├── .github/workflows/fetch_prices.yml    # daily schedule (05:00 UTC) + manual run
└── data/                                 # latest version of each file (git history keeps the old ones)
    ├── Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx
    ├── european_wholesale_electricity_price_data_daily.csv
    └── manifest.json
```

`manifest.json` tells Databricks when the files were downloaded and lets it check that they were copied correctly:

```json
{
  "download_date": "2026-11-12",
  "files": [
    {"file": "Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx", "url": "https://energy.ec.europa.eu/...", "size_bytes": 4502019, "sha256": "b55d86c3..."},
    {"file": "european_wholesale_electricity_price_data_daily.csv", "url": "https://files.ember-energy.org/...", "size_bytes": 3651892, "sha256": "480c25ab..."}
  ]
}
```

## Run it manually

```bash
pip install -r requirements.txt
python fetch_prices.py
```

Or from GitHub: **Actions → Fetch energy prices → Run workflow**.
