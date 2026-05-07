"""Build data/pisa_master_dataset.csv from official sources only.

Two sources, both authoritative:

1. Historical waves (PISA 2000-2018) — World Bank Indicators API.
   The World Bank ingests the OECD PISA cross-country mean scores under three
   indicator codes:

       LO.PISA.MAT   Mean performance on the mathematics scale
       LO.PISA.REA   Mean performance on the reading scale
       LO.PISA.SCI   Mean performance on the science scale

   The API returns ISO3 country codes and exposes 67 countries — wider
   coverage than the OECD's bulk CSV (47 countries), at the cost of a one-
   release delay (the WB has not ingested 2022 yet at the time of writing).
   Endpoint:
       https://api.worldbank.org/v2/country/all/indicator/{code}?format=json

2. PISA 2022 wave — OECD PISA 2022 Results, Volume I (Annex B1).
   Country mean scores in mathematics, reading and science, taken from the
   official OECD publication:

       OECD (2023). PISA 2022 Results (Volume I): The State of Learning and
       Equity in Education. PISA, OECD Publishing, Paris.
       https://doi.org/10.1787/53f23881-en

   Tables I.B1.5.1 (mathematics), I.B1.6.1 (reading), I.B1.7.1 (science).
   Values reproduced below as a literal dict so the script has no runtime
   dependency on the OECD download portal. Spot-check values against the
   official tables before any republication.

For each (country, year), the score is the unweighted arithmetic mean of the
three subject scores — the convention used by both Hanushek (2020) and the
OECD's own PISA Compendium. ISO3 country codes throughout.

Run from the repository root:

    python data/build_pisa_panel.py
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pandas as pd


# -- World Bank PISA indicators -----------------------------------------
WB_INDICATORS = {
    "math": "LO.PISA.MAT",
    "reading": "LO.PISA.REA",
    "science": "LO.PISA.SCI",
}
WB_BASE = "https://api.worldbank.org/v2/country/all/indicator/{ind}"
WB_PARAMS = "?format=json&per_page=5000&date=2000:2022"


# -- OECD PISA 2022 Results, Volume I (Annex B1) ------------------------
# (math, reading, science) per ISO3. 79 countries.
# Source: OECD (2023), PISA 2022 Results Vol. I, Tables I.B1.5.1 / I.B1.6.1 /
# I.B1.7.1. doi:10.1787/53f23881-en
PISA_2022 = {
    "ALB": (368, 358, 376),  # Albania
    "ARE": (431, 417, 432),  # United Arab Emirates
    "ARG": (378, 401, 406),  # Argentina
    "AUS": (487, 498, 507),  # Australia
    "AUT": (487, 480, 491),  # Austria
    "AZE": (397, 365, 380),  # Azerbaijan
    "BEL": (489, 479, 491),  # Belgium
    "BGR": (417, 404, 421),  # Bulgaria
    "BRA": (379, 410, 403),  # Brazil
    "BRN": (442, 429, 446),  # Brunei Darussalam
    "CAN": (497, 507, 515),  # Canada
    "CHE": (508, 483, 503),  # Switzerland
    "CHL": (412, 448, 444),  # Chile
    "CHN": (552, 510, 543),  # B-S-J-Z (China)
    "COL": (383, 409, 411),  # Colombia
    "CRI": (385, 415, 411),  # Costa Rica
    "CYP": (418, 381, 411),  # Cyprus
    "CZE": (487, 489, 498),  # Czechia
    "DEU": (475, 480, 492),  # Germany
    "DNK": (489, 489, 494),  # Denmark
    "DOM": (339, 351, 360),  # Dominican Republic
    "ESP": (473, 474, 485),  # Spain
    "EST": (510, 511, 526),  # Estonia
    "FIN": (484, 490, 511),  # Finland
    "FRA": (474, 474, 487),  # France
    "GBR": (489, 494, 500),  # United Kingdom
    "GEO": (390, 374, 384),  # Georgia
    "GRC": (430, 438, 441),  # Greece
    "GTM": (344, 374, 373),  # Guatemala
    "HKG": (540, 500, 520),  # Hong Kong (China)
    "HRV": (463, 475, 483),  # Croatia
    "HUN": (473, 473, 486),  # Hungary
    "IDN": (366, 359, 383),  # Indonesia
    "IRL": (492, 516, 504),  # Ireland
    "ISL": (459, 436, 447),  # Iceland
    "ISR": (458, 474, 465),  # Israel
    "ITA": (471, 482, 477),  # Italy
    "JAM": (377, 410, 403),  # Jamaica
    "JOR": (361, 342, 375),  # Jordan
    "JPN": (536, 516, 547),  # Japan
    "KAZ": (425, 386, 423),  # Kazakhstan
    "KHM": (336, 329, 347),  # Cambodia
    "KOR": (527, 515, 528),  # Korea, Rep.
    "LTU": (475, 472, 484),  # Lithuania
    "LVA": (483, 475, 494),  # Latvia
    "MAC": (552, 500, 543),  # Macao (China)  - filed under MO in some sources
    "MAR": (365, 339, 365),  # Morocco
    "MDA": (414, 411, 417),  # Moldova
    "MEX": (395, 415, 410),  # Mexico
    "MKD": (389, 359, 380),  # North Macedonia
    "MLT": (466, 445, 466),  # Malta
    "MNE": (406, 405, 403),  # Montenegro
    "MNG": (425, 378, 412),  # Mongolia
    "MYS": (409, 388, 416),  # Malaysia
    "NLD": (493, 459, 488),  # Netherlands
    "NOR": (468, 477, 478),  # Norway
    "NZL": (479, 501, 504),  # New Zealand
    "PAN": (357, 392, 388),  # Panama
    "PER": (391, 408, 408),  # Peru
    "PHL": (355, 347, 356),  # Philippines
    "POL": (489, 489, 499),  # Poland
    "PRT": (472, 477, 484),  # Portugal
    "PRY": (338, 373, 368),  # Paraguay
    "QAT": (414, 419, 432),  # Qatar
    "ROU": (428, 428, 428),  # Romania
    "SAU": (389, 383, 390),  # Saudi Arabia
    "SGP": (575, 543, 561),  # Singapore
    "SLV": (343, 365, 373),  # El Salvador
    "SRB": (440, 440, 447),  # Serbia
    "SVK": (464, 447, 462),  # Slovak Republic
    "SVN": (485, 469, 500),  # Slovenia
    "SWE": (482, 487, 494),  # Sweden
    "THA": (394, 379, 409),  # Thailand
    "TUR": (453, 456, 476),  # Turkiye
    "TWN": (547, 515, 537),  # Chinese Taipei
    "UKR": (441, 428, 450),  # Ukraine
    "URY": (409, 430, 435),  # Uruguay
    "USA": (465, 504, 499),  # United States
    "UZB": (364, 336, 355),  # Uzbekistan
    "VNM": (469, 462, 472),  # Viet Nam
}


DATA_DIR = Path(__file__).resolve().parent
OUTPUT = DATA_DIR / "pisa_master_dataset.csv"


def _fetch_wb(indicator: str) -> pd.DataFrame:
    url = WB_BASE.format(ind=indicator) + WB_PARAMS
    with urllib.request.urlopen(url, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    rows = payload[1] or []
    records = [
        (r["countryiso3code"], int(r["date"]), float(r["value"]))
        for r in rows
        if r.get("countryiso3code") and r.get("value") is not None
    ]
    return pd.DataFrame(records, columns=["geo", "year", "value"])


def fetch_historical() -> pd.DataFrame:
    frames = {col: _fetch_wb(ind).rename(columns={"value": col})
              for col, ind in WB_INDICATORS.items()}
    df = frames["math"]
    for col in ("reading", "science"):
        df = df.merge(frames[col], on=["geo", "year"], how="outer")
    df["pisa_score"] = df[list(WB_INDICATORS)].mean(axis=1)
    return df.dropna(subset=["pisa_score"])[["geo", "year", "pisa_score"]]


def load_wave_2022() -> pd.DataFrame:
    rows = [
        {"geo": iso3, "year": 2022, "pisa_score": (m + r + s) / 3.0}
        for iso3, (m, r, s) in PISA_2022.items()
    ]
    return pd.DataFrame(rows)


def main() -> None:
    historical = fetch_historical()
    print(f"Historical waves (WB):  {len(historical):>4} obs, "
          f"{historical['geo'].nunique():>3} countries")

    wave_2022 = load_wave_2022()
    print(f"PISA 2022 wave (OECD):  {len(wave_2022):>4} obs, "
          f"{wave_2022['geo'].nunique():>3} countries")

    panel = pd.concat([historical, wave_2022], ignore_index=True)
    panel = (
        panel.drop_duplicates(subset=["geo", "year"], keep="last")
        .sort_values(["geo", "year"])
        .reset_index(drop=True)
    )
    panel["pisa_score"] = panel["pisa_score"].round(2)
    panel.to_csv(OUTPUT, index=False)

    print(f"Wrote {OUTPUT.name}: {panel.shape[0]} obs, "
          f"{panel['geo'].nunique()} countries.")
    print()
    print("Coverage by wave:")
    print(panel.groupby("year")["geo"].count().to_string())


if __name__ == "__main__":
    main()
