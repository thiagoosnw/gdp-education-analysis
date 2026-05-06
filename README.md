# Wealth, Education and PISA

Cross-country empirical study of the relationship between national income, schooling, institutional quality and student achievement (PISA 2022), with a country-level **Education Efficiency Index** built on the production-function framework of Hanushek (2020) and Dee (2005), augmented with a governance proxy following Acemoglu, Johnson and Robinson (2024 Nobel laureate).

Delivered as an interactive Streamlit dashboard backed by a reproducible Jupyter notebook.

## What the project does

1. Combines six official datasets (World Bank, UNDP, OECD) into a longitudinal cross-country panel covering 1990–2023.
2. Estimates an **education production function** by OLS (preferred) and 2SLS (robustness), with spending, GDP per capita, mean years of schooling and Government Effectiveness as drivers, on 57 countries with PISA 2022 data.
3. Presents the analysis through a dashboard with four tabs: historical panel evolution, country-level efficiency ranking, driver-level correlations, and methodology.

## Repository layout

```
gdp_lab/
├── README.md                          # this file
├── app.py                             # Streamlit dashboard
├── efficiency_index.ipynb             # statistical pipeline (notebook)
├── convert.ipynb                      # PISA data preparation (notebook)
├── requirements.txt                   # Python dependencies
├── install.cmd                        # Windows installer for venv + deps
├── .streamlit/config.toml             # forces dark theme for consistent contrast
├── OECD PISA data.csv                 # raw PISA historical waves  (input to convert.ipynb)
├── pisa-scores-by-country-2026.csv    # raw PISA 2022 wave         (input to convert.ipynb)
├── data/                              # working datasets consumed by the app
│   ├── API_NY.GDP.PCAP.PP.CD_*.csv    # World Bank GDP per capita PPP
│   ├── API_SP.POP.TOTL_*.csv          # World Bank population
│   ├── hdr-data.xlsx                  # UNDP HDR mean years of schooling
│   ├── pisa_master_dataset.csv        # cleaned PISA panel (output of convert.ipynb)
│   ├── _wb_xpd_seco.json              # WB SE.XPD.SECO.PC.ZS, latest 2015–2018
│   ├── _wb_xpd_seco_lag.json          # WB SE.XPD.SECO.PC.ZS, lagged 2005–2014 (instrument)
│   ├── _wb_xpd_totl_gdp.json          # WB SE.XPD.TOTL.GD.ZS, total ed exp (% of GDP)
│   ├── _wb_wgi_ge.json                # WB GOV_WGI_GE.EST, Government Effectiveness
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

All data come from official statistical authorities. No private or unverifiable source is used.

| Variable | Provider | Indicator code | URL |
|---|---|---|---|
| GDP per capita PPP (current international USD) | World Bank | `NY.GDP.PCAP.PP.CD` | https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD |
| Total population | World Bank | `SP.POP.TOTL` | https://data.worldbank.org/indicator/SP.POP.TOTL |
| Government expenditure per secondary student (% of GDP per capita) | World Bank (UNESCO UIS) | `SE.XPD.SECO.PC.ZS` | https://data.worldbank.org/indicator/SE.XPD.SECO.PC.ZS |
| Total government expenditure on education (% of GDP) | World Bank (UNESCO UIS) | `SE.XPD.TOTL.GD.ZS` | https://data.worldbank.org/indicator/SE.XPD.TOTL.GD.ZS |
| Government Effectiveness (WGI) | World Bank | `GOV_WGI_GE.EST` | https://www.worldbank.org/en/publication/worldwide-governance-indicators |
| PISA scores (math, reading, science) | OECD | direct download | https://www.oecd.org/pisa/ |
| Mean years of schooling | UNDP Human Development Report | `mys` | https://hdr.undp.org/data-center/documentation-and-downloads |

The lagged spending observations (2005–2014) used as the 2SLS instrument come from the same World Bank indicator queried for an earlier date range.

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
6. Strict causal identification would require panel data with within-country variation (not available for PISA at the country level) or stronger instruments. Time-series and neural-network extensions are deferred to follow-up work.

## How the app is structured

`app.py` exposes four tabs:

1. **Historical Panel** — animated bubble chart of GDP per capita versus PISA score (or mean years of schooling), 1990–2023. Bubbles sized by population. When the metric is PISA, the animation iterates only over the eight PISA wave years (2000, 2003, 2006, 2009, 2012, 2015, 2018, 2022) so bubbles do not "teleport" across off-years.
2. **Education Efficiency Index** — country ranking by efficiency z-score, with an alternative ranking by PISA-per-1 000-USD spent. Includes a scatter of spending versus achievement and a country-level table with all model inputs and outputs.
3. **Drivers Correlations** — bivariate scatters of PISA versus each driver (spending, GDP, MYS, Government Effectiveness) with Pearson correlations and OLS-fit lines. This view supports the supervisor's recommendation of presenting "data with easy correlation, visually presentable in the dashboard".
4. **Methodology** — full theoretical framework, empirical specification, specification search, OLS vs 2SLS, identification diagnostics, limitations and references.

The sidebar carries a single country-group filter (G7, G20, EU, BRICS+, South America, Latin America, etc.) that drives all tabs. When a selected group has fewer than three countries with efficiency data, the app falls back to the full sample with an informational banner.

## Reproducing the analysis

### Setup

```bash
pip install -r requirements.txt
```

### Re-build the PISA panel (if needed)

```bash
jupyter nbconvert --to notebook --execute convert.ipynb
```

This reads `OECD PISA data.csv` (historical waves) and `pisa-scores-by-country-2026.csv` (2022 wave) and produces `data/pisa_master_dataset.csv`.

### Re-build the efficiency index

```bash
jupyter nbconvert --to notebook --execute efficiency_index.ipynb
```

The notebook reads from `data/`, runs OLS (M3 preferred) and 2SLS (robustness), and writes `data/efficiency_index.csv`.

### Run the dashboard

```bash
streamlit run app.py
```

The browser opens at `http://localhost:8501`. The dark theme is forced via `.streamlit/config.toml` for consistent contrast across operating systems.

## References

- Hanushek, E. A. (2020). *Education production functions*. The Economics of Education, 2nd ed., Elsevier.
- Hanushek, E. A. (1986). The economics of schooling: Production and efficiency in public schools. *Journal of Economic Literature*, 24(3).
- Dee, T. S. (2005). Expense preference and student achievement in school districts. *Eastern Economic Journal*, 31(1).
- Acemoglu, D., Johnson, S., & Robinson, J. A. (2012). *Why Nations Fail*. Crown Business.
- Kaufmann, D., & Kraay, A. (2024). *Worldwide Governance Indicators — 2024 Methodology Update*. World Bank.

## Author and supervision

**Thiago Alcebíades Rodrigues** — [thiago.alcebiades@unifesp.br](mailto:thiago.alcebiades@unifesp.br) · [LinkedIn](https://www.linkedin.com/in/thiago-alcebiades-rodrigues-95446621b/)

Supervisor: **Profa. Martha Bianchi**, Departamento de Ciências Atuariais, UNIFESP/EPPEN
