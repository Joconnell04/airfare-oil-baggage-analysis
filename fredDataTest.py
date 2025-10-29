import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_fred_series(url_or_path: str) -> pd.DataFrame:
    # Load HTML from web or local file
    if url_or_path.startswith("http"):
        resp = requests.get(url_or_path, timeout=30)
        resp.raise_for_status()
        html = resp.text
    else:
        with open(url_or_path, "r", encoding="utf-8") as f:
            html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Find the observations table and parse rows
    table = soup.find("table", id="data-table-observations")
    if table is None:
        raise ValueError("Could not find observations table")

    records = []
    tbody = table.find("tbody") or table
    for tr in tbody.find_all("tr"):
        th = tr.find("th")
        td = tr.find("td")
        if not th or not td:
            continue
        date_str = th.get_text(strip=True)
        value_str = td.get_text(strip=True)
        records.append((date_str, value_str))

    # Build tidy DataFrame
    df = pd.DataFrame(records, columns=["date", "value"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=False)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"]).sort_values("date").reset_index(drop=True)
    return df

if __name__ == "__main__":
    url = "https://fred.stlouisfed.org/data/FPCPITOTLZGUSA"
    df = fetch_fred_series(url)
    print(df.head())
    print(df.tail())
    # df.to_csv("fred_cpi_series.csv", index=False)
