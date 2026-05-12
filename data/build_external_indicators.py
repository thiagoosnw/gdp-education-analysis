"""Fetch external indicators from the World Bank API and persist them locally.

Run from the repository root:

    python data/build_external_indicators.py

Outputs:
    data/API_NY.GDP.PCAP.PP.KD.csv   — GDP per capita, PPP (constant 2021 intl $)
    data/_wb_wgi_ge.json              — WGI Government Effectiveness (estimate)
    data/_wb_wgi_cc.json              — WGI Control of Corruption (estimate)
    data/_wb_gini.json                — World Bank Gini index (SI.POV.GINI)

The GDP CSV mirrors the layout of the World Bank bulk download (4 skip rows,
"Country Name", "Country Code" and one column per year) so the dashboard can
swap data sources without touching the loader.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent

WB_API = "https://api.worldbank.org/v2/country/all/indicator/{ind}"


def _fetch(ind: str, *, date: str, per_page: int = 5000) -> list[dict]:
    base = f"{WB_API.format(ind=ind)}?format=json&per_page={per_page}&date={date}"
    rows: list[dict] = []
    page = 1
    while True:
        url = f"{base}&page={page}"
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


def build_constant_gdp() -> Path:
    rows = _fetch("NY.GDP.PCAP.PP.KD", date="1990:2024", per_page=20000)
    df = pd.DataFrame([
        {
            "Country Name": r["country"]["value"],
            "Country Code": r["countryiso3code"],
            "year": int(r["date"]),
            "value": r["value"],
        }
        for r in rows
        if r.get("countryiso3code") and r.get("value") is not None
    ])
    wide = df.pivot_table(
        index=["Country Name", "Country Code"],
        columns="year",
        values="value",
        aggfunc="first",
    ).reset_index()
    wide.columns.name = None
    wide = wide[["Country Name", "Country Code"] + sorted(c for c in wide.columns if isinstance(c, int))]
    wide.columns = [str(c) for c in wide.columns]

    out = DATA_DIR / "API_NY.GDP.PCAP.PP.KD.csv"
    header = (
        '"Data Source","World Bank","",""\n'
        '"Last Updated Date","","",""\n'
        '"","","",""\n'
        '"","","",""\n'
    )
    with out.open("w", encoding="utf-8", newline="") as f:
        f.write(header)
        wide.to_csv(f, index=False)
    print(f"Wrote {out.name}: {wide.shape[0]} countries, {wide.shape[1] - 2} year cols")
    return out


def build_wgi(ind: str, name: str) -> Path:
    rows = _fetch(ind, date="2018:2023", per_page=20000)
    out = DATA_DIR / f"_wb_wgi_{name}.json"
    payload = [{"page": 1, "pages": 1, "per_page": 20000, "total": len(rows)}, rows]
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out.name}: {len(rows)} obs")
    return out


def build_gini() -> Path:
    """World Bank Gini index (SI.POV.GINI). Survey-based, reported irregularly
    per country; some only have a household survey every 5–10 years. We pull a
    wide date window and keep all non-null observations; the app selects the
    latest available value per country (with the survey year shown next to it)."""
    rows = _fetch("SI.POV.GINI", date="2005:2024", per_page=20000)
    out = DATA_DIR / "_wb_gini.json"
    payload = [{"page": 1, "pages": 1, "per_page": 20000, "total": len(rows)}, rows]
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out.name}: {len(rows)} obs")
    return out


def main() -> None:
    build_constant_gdp()
    build_wgi("GOV_WGI_GE.EST", "ge")
    build_wgi("GOV_WGI_CC.EST", "cc")
    build_gini()


if __name__ == "__main__":
    main()
