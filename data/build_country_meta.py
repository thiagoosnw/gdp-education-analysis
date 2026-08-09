"""Fetch country metadata (capital coordinates, region, income group) from the
World Bank API.

Run from the repository root:

    python data/build_country_meta.py

Output:
    data/country_meta.csv  — one row per economy (aggregates excluded)

The capital-city latitude/longitude published by the World Bank is what makes
`px.line_geo` usable in this project: choropleths only need the ISO3 code, but
any line/flow layer needs a point per country. Region and income group come
from the same endpoint and are handy as ready-made grouping columns.

Source: https://api.worldbank.org/v2/country
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent

WB_COUNTRY_API = "https://api.worldbank.org/v2/country"


def _fetch_countries(per_page: int = 400) -> list[dict]:
    rows: list[dict] = []
    page = 1
    while True:
        url = f"{WB_COUNTRY_API}?format=json&per_page={per_page}&page={page}"
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=120) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                break
            except (TimeoutError, OSError) as exc:
                if attempt == 2:
                    raise
                print(f"  retry {attempt + 1} for page {page}: {exc}")
        meta, batch = payload[0], (payload[1] or [])
        rows.extend(batch)
        if page >= int(meta.get("pages", 1)):
            break
        page += 1
    return rows


def build_country_meta() -> Path:
    rows = _fetch_countries()

    records = []
    for r in rows:
        region = (r.get("region") or {}).get("id") or ""
        # Aggregates (world, income groups, regional totals) carry region id "NA".
        if region in ("", "NA"):
            continue
        lat, lon = r.get("latitude"), r.get("longitude")
        records.append({
            "geo": (r.get("id") or "").upper(),
            "iso2": r.get("iso2Code") or "",
            "name": r.get("name") or "",
            "region_id": region,
            "region": (r.get("region") or {}).get("value") or "",
            "income_id": (r.get("incomeLevel") or {}).get("id") or "",
            "income": (r.get("incomeLevel") or {}).get("value") or "",
            "capital": r.get("capitalCity") or "",
            "lat": float(lat) if lat not in (None, "") else None,
            "lon": float(lon) if lon not in (None, "") else None,
        })

    df = pd.DataFrame(records).sort_values("geo").reset_index(drop=True)
    out = DATA_DIR / "country_meta.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    n_coords = int(df[["lat", "lon"]].notna().all(axis=1).sum())
    print(f"Wrote {out.name}: {len(df)} economies, {n_coords} with capital coordinates")
    return out


if __name__ == "__main__":
    build_country_meta()
