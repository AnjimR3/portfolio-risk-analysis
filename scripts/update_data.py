"""Download the latest public data into data/."""

from pathlib import Path
from urllib.request import urlopen

BASE = "https://raw.githubusercontent.com/datasets"
FILES = {
    "sp500.csv": f"{BASE}/s-and-p-500/main/data/data.csv",
    "us_10y_yield.csv": f"{BASE}/bond-yields-us-10y/main/data/monthly.csv",
    "gold.csv": f"{BASE}/gold-prices/main/data/monthly.csv",
}
DATA = Path(__file__).resolve().parents[1] / "data"

for name, url in FILES.items():
    with urlopen(url, timeout=60) as response:
        (DATA / name).write_bytes(response.read())
    print(f"Updated {name}")
