# GDP Lab — Wealth, Education and PISA

Cross-country empirical study of the relationship between national income, schooling, institutional quality and student achievement (PISA 2022), with a country-level **Education Efficiency Index** built on the production-function framework of Hanushek (2020) and Dee (2005), augmented with a governance proxy following Acemoglu, Johnson and Robinson (2024 Nobel laureate). The log-linear specification is benchmarked against non-linear alternatives (Ridge polynomial regression and a small MLP) by 5-fold cross-validation.

Delivered as an interactive Streamlit dashboard (Portuguese / English) backed by a reproducible Jupyter notebook.

> Para um resumo do projeto em português (≈ 500 palavras), veja [`RESUMO.md`](RESUMO.md).

## What the project does

1. Combines six official datasets (World Bank, UNDP, OECD) into a longitudinal cross-country panel covering 1990–2023.
2. Estimates an **education production function** by OLS (preferred) and 2SLS (robustness), with spending, GDP per capita, mean years of schooling and Government Effectiveness as drivers, on 57 countries with PISA 2022 data.
3. Compares the log-linear OLS to non-linear alternatives — Ridge polynomial regression (degree 2) and an MLP regressor — under matched 5-fold cross-validation, to test whether non-linear interactions add out-of-sample explanatory power.
4. Presents the analysis through a five-tab Streamlit dashboard: historical evolution, country-level efficiency ranking, driver correlations, a what-if simulator, and methodology.

## Repository layout

```
gdp_lab/
├── README.md                          # this file
├── RESUMO.md                          # 500-word PT abstract
├── app.py                             # Streamlit dashboard
├── efficiency_index.ipynb             # statistical pipeline (notebook)
├── requirements.txt                   # Python dependencies
├── install.cmd                        # Windows installer (creates .venv, installs deps)
├── .streamlit/config.toml             # Streamlit primary colour and server flags
├── .devcontainer/devcontainer.json    # GitHub Codespaces / VS Code Remote container
├── .gitignore
├── data/                              # working datasets consumed by the app
│   ├── API_NY.GDP.PCAP.PP.CD_*.csv    # World Bank GDP per capita PPP (bulk download)
│   ├── API_SP.POP.TOTL_*.csv          # World Bank Population (bulk download)
│   ├── hdr-data.xlsx                  # UNDP Human Development Report — mean years of schooling
│   ├── _wb_xpd_seco.json              # WB API: SE.XPD.SECO.PC.ZS, latest 2015–2018
│   ├── _wb_xpd_seco_lag.json          # WB API: SE.XPD.SECO.PC.ZS, lagged 2005–2014 (instrument)
│   ├── _wb_xpd_totl_gdp.json          # WB API: SE.XPD.TOTL.GD.ZS, total ed exp (% of GDP)
│   ├── _wb_wgi_ge.json                # WB API: GOV_WGI_GE.EST, Government Effectiveness
│   ├── build_pisa_panel.py            # rebuilds pisa_master_dataset.csv from WB API + OECD 2022
│   ├── pisa_master_dataset.csv        # PISA panel (output of build_pisa_panel.py)
│   └── efficiency_index.csv           # output of efficiency_index.ipynb
└── knowledge/                         # reference papers (PDFs)
    ├── Hanushek 2020 Education Production Functions_0 (1).pdf
    ├── Hanushek 1986 JEL 24(3).pdf
    ├── Expense_Preference_and_Student_Achievement_in_Scho.pdf
    ├── Education and Economic Growth.pdf
    ├── How Does Education Quality Affect Economic Growth.pdf
    ├── The Effect of Education Expenditure on Per Capita GDP.pdf
    └── Qualidade das instituições e PIB per capita dos municipios.pdf
```

## Data sources

Every dataset in this repository comes from an official statistical authority — World Bank, UNDP or OECD. No third-party aggregator or scraped page is used.

| Variable | Provider | Indicator / source | Authoritative URL |
|---|---|---|---|
| GDP per capita PPP (current international USD) | World Bank | `NY.GDP.PCAP.PP.CD` | https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD |
| Total population | World Bank | `SP.POP.TOTL` | https://data.worldbank.org/indicator/SP.POP.TOTL |
| Government expenditure per secondary student (% of GDP per capita) | World Bank (UNESCO UIS) | `SE.XPD.SECO.PC.ZS` | https://data.worldbank.org/indicator/SE.XPD.SECO.PC.ZS |
| Total government expenditure on education (% of GDP) | World Bank (UNESCO UIS) | `SE.XPD.TOTL.GD.ZS` | https://data.worldbank.org/indicator/SE.XPD.TOTL.GD.ZS |
| Government Effectiveness (WGI) | World Bank | `GOV_WGI_GE.EST` | https://www.worldbank.org/en/publication/worldwide-governance-indicators |
| Mean years of schooling | UNDP Human Development Report | indicator `mys` | https://hdr.undp.org/data-center/documentation-and-downloads |
| PISA scores 2000–2018 (math, reading, science) | World Bank (ingests OECD PISA) | `LO.PISA.MAT`, `LO.PISA.REA`, `LO.PISA.SCI` | https://data.worldbank.org/indicator/LO.PISA.MAT |
| PISA scores 2022 (math, reading, science) | OECD | PISA 2022 Results, Vol. I, Annex B1 (Tables I.B1.5.1, I.B1.6.1, I.B1.7.1) | https://doi.org/10.1787/53f23881-en |

The lagged spending observations (2005–2014) used as the 2SLS instrument come from the same World Bank indicator queried for an earlier date range. The PISA 2022 country mean scores are reproduced verbatim from the OECD's Volume I publication tables in [`data/build_pisa_panel.py`](data/build_pisa_panel.py); the script also pulls 2000–2018 directly from the World Bank API and writes `data/pisa_master_dataset.csv`.

## Methodology

### Production function (preferred specification, M3)

$$\ln(\text{PISA}_i) = \theta\,\ln(\text{Spend}_i) + \beta\,\ln(\text{GDP}_i) + \gamma\,\ln(\text{MYS}_i) + \eta\,\text{GovEff}_i + \delta + \varepsilon_i$$

- $\text{Spend}_i$ — per-secondary-student expenditure, USD PPP, computed as `(SE.XPD.SECO.PC.ZS / 100) × GDP per capita PPP`.
- $\text{GDP}_i$ — GDP per capita PPP, 2022.
- $\text{MYS}_i$ — mean years of schooling, 2022.
- $\text{GovEff}_i$ — Government Effectiveness from the WGI (≈ −2.5 to +2.5).

Estimated by **OLS** with HC1-robust standard errors.

### Why governance is in the model

Following supervisor guidance and Acemoglu, Johnson & Robinson (Nobel Memorial Prize 2024 — *Why Nations Fail*), the **institutional environment** is a first-order determinant of long-run economic outcomes. Government Effectiveness proxies the public sector's capacity to translate budgets into services. Including it improves the model fit and reduces omitted-variable bias on the spending and schooling coefficients.

### Specification search

| Spec | Variables | Adj R² | N |
|---|---|---|---|
| M1 | Spend + GDP + MYS                            | 0.711 | 56 |
| M2 | + Total ed exp (% GDP)                        | 0.708 | 56 |
| **M3 (preferred)** | + Government Effectiveness | **0.720** | 56 |
| M4 | + Total ed exp + Government Effectiveness     | 0.718 | 56 |

`xpd_pct_gdp` (total education expenditure as a percentage of GDP) is **not statistically significant** in any specification — consistent with Hanushek's central finding that *how much* a country spends on education is a poor predictor of student achievement once other inputs are accounted for.

### 2SLS robustness check

The notebook also estimates the M3 model by 2SLS using lagged per-student spending (2005–2014) as instrument for current spending. Diagnostics:

| Diagnostic | Value | Interpretation |
|---|---|---|
| First-stage F-statistic | 128 | Strong instrument (>> threshold of 10) |
| Partial R² of instrument | 0.74 | Lagged spending explains 74% of current-spending variance after controls |
| Order condition | just-identified | Single endogenous regressor, single instrument |

The 2SLS spending coefficient is moderately higher than OLS, consistent with the downward bias predicted by Dee (2005). The dashboard reports the OLS predictions; 2SLS is kept in the notebook as a sensitivity check.

### Comparison with non-linear methods

The log-linear M3 specification is benchmarked against three alternatives that match exactly the same input set, reporting **5-fold cross-validated R²**:

| Model | Functional form | CV R² |
|---|---|---|
| M3 — OLS log-linear | linear in logs | 0.52 |
| M3+ — OLS + Spend × GovEff | linear with single interaction | 0.45 |
| **M5 — Ridge polynomial (deg 2, α=5)** | polynomial in scaled inputs, L2-regularised | **0.65** |
| M6 — MLP (1 layer, 4 units, tanh, α=1) | small neural network | 0.62 |

Ridge polynomial regression delivers the best out-of-sample fit; the MLP reaches similar performance with much higher specification cost. With *N = 57*, all CV estimates carry a standard deviation of roughly 0.2, so the 13-pp gap between OLS and ridge polynomial is consistent in sign but not large in magnitude. The published efficiency index keeps the OLS specification because (i) coefficients have direct elasticity interpretation, (ii) HC1-robust standard errors and the 2SLS robustness check are well-established for it, and (iii) the non-linear models do not produce reportable elasticities. The non-linear comparison is documented in the dashboard's *Methodology* tab as a methodological complement, not as the published estimator.

### Efficiency Index

$$\text{EI}_i = \frac{\hat\varepsilon_i - \bar{\hat\varepsilon}}{\hat\sigma_{\hat\varepsilon}}$$

The country efficiency score is the **standardised regression residual** (z-score). Reported directly as the z-score (range ≈ −3 to +2). Positive ⇒ produces more PISA points than its measurable inputs predict; negative ⇒ underperformance.

### Top-of-ranking sample

| Rank | Country | PISA actual | PISA predicted | GovEff | z-score |
|---|---|---|---|---|---|
| 1 | Türkiye    | 462 | 413 | −0.11 | +1.84 |
| 2 | Ukraine    | 440 | 396 | −0.58 | +1.75 |
| 3 | Japan      | 533 | 483 | +1.99 | +1.63 |
| 4 | Korea      | 523 | 480 | +1.50 | +1.45 |
| 5 | Estonia    | 516 | 474 | +1.27 | +1.42 |

### Limitations

1. Cross-section of 57 countries — limited statistical power.
2. PISA captures one cohort and three subjects only.
3. Spending observations span 2015–2018 (latest WB availability), not 2022.
4. Sociodemographic controls $W$ are limited to GDP, MYS and GovEff.
5. The WGI Government Effectiveness indicator is itself a perception-based composite.
6. Strict causal identification would require panel data with within-country variation (not available for PISA at the country level) or stronger instruments.

## How the app is structured

`app.py` exposes five tabs and ships with PT/EN translation, a light/dark theme toggle, and URL-persisted state for language, theme and country group.

1. **Historical Panel** — animated bubble chart of GDP per capita versus the chosen y-axis metric, 1990–2023. Bubbles sized by population, with thin contrasting borders (Gapminder style). The default metric is **mean years of schooling**, which has continuous coverage. When the user switches to PISA, the panel renders a static **2022 cross-section** plus a separate longitudinal line chart for the subset of countries with three or more PISA waves — this avoids the misleading "spawning bubbles" effect produced when 38 of 84 countries only joined PISA in 2022.
2. **Education Efficiency Index** — country ranking by efficiency z-score, with an alternative ranking by PISA-per-1 000-USD-spent. A bootstrap (B = 300) confidence-interval toggle estimates the stability of the ranking and is critical for reading high-z surprises (Türkiye, Ukraine). Includes a spending-vs-achievement scatter and a country-level table with all model inputs and outputs.
3. **Drivers Correlations** — bivariate scatters of PISA versus each driver (spending, GDP, MYS, Government Effectiveness) with Pearson correlations and OLS-fit lines.
4. **Simulator** — what-if interface backed by the M3 OLS coefficients. The user picks a baseline country and four sliders (Spend, GDP, MYS, GovEff). The dashboard reports actual PISA, predicted PISA at the baseline, predicted PISA under the scenario, and a per-driver decomposition of the change. A **Reset** button restores all sliders to the baseline country's actual values.
5. **Methodology** — full theoretical framework, empirical specification, specification search, OLS vs 2SLS, comparison with non-linear methods, model diagnostics (predicted vs actual, residual histogram, residuals vs fitted), limitations and references.

The sidebar carries language/theme toggles, a country-group filter (G7, G20, EU, BRICS+, South America, Latin America, etc.) shared by all tabs, the y-axis selector, an optional "highlight countries" multiselect, a collapsible data-sources block, and the author block. When a selected group has fewer than three countries with efficiency data, the app falls back to the full sample with an informational banner.

## Reproducing the analysis

### Setup

Linux / macOS:

```bash
pip install -r requirements.txt
```

Windows (creates a local `.venv` and installs everything):

```cmd
install.cmd
```

### Re-build the PISA panel

```bash
python data/build_pisa_panel.py
```

Pulls historical PISA waves (2000–2018) directly from the **World Bank** indicators `LO.PISA.MAT`, `LO.PISA.REA` and `LO.PISA.SCI` — which ingest the official OECD cross-country mean scores under clean ISO3 codes — and combines them with the 2022 wave reproduced verbatim from **OECD PISA 2022 Results, Volume I (Annex B1)**, embedded as a Python dict in the script with the exact OECD table reference. The output `data/pisa_master_dataset.csv` covers 91 countries across eight PISA waves.

### Re-build the efficiency index

```bash
jupyter nbconvert --to notebook --execute efficiency_index.ipynb
```

Reads from `data/`, runs OLS (M3 preferred) and 2SLS (robustness), and writes `data/efficiency_index.csv`.

### Run the dashboard

```bash
streamlit run app.py
```

The browser opens at `http://localhost:8501`. Language and theme can be switched at the top of the sidebar; both are persisted in the URL so views are shareable.

## References

- Hanushek, E. A. (2020). *Education production functions*. The Economics of Education, 2nd ed., Elsevier.
- Hanushek, E. A. (1986). The economics of schooling: Production and efficiency in public schools. *Journal of Economic Literature*, 24(3).
- Dee, T. S. (2005). Expense preference and student achievement in school districts. *Eastern Economic Journal*, 31(1).
- Acemoglu, D., Johnson, S., & Robinson, J. A. (2012). *Why Nations Fail*. Crown Business.
- Kaufmann, D., & Kraay, A. (2024). *Worldwide Governance Indicators — 2024 Methodology Update*. World Bank.

## Author and supervision

**Thiago Alcebíades Rodrigues** — [thiago.alcebiades@unifesp.br](mailto:thiago.alcebiades@unifesp.br) · [LinkedIn](https://www.linkedin.com/in/thiago-alcebiades-rodrigues-95446621b/)

Supervisor: **Profa. Martha Bianchi**, Departamento de Ciências Atuariais, UNIFESP/EPPEN
