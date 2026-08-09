# Wealth, Education and PISA. Interactive Visualisation

Interactive Streamlit dashboard that crosses GDP per capita (PPP, constant 2021 USD), mean years of schooling, PISA scores, World Bank governance indicators and the World Bank income Gini index for more than 200 countries. The aim is not to estimate causal relationships between wealth, governance and learning, since that would require sub-national data and identification designs stronger than cross-country regressions allow. The aim is to give a non-specialist reader a visual, interactive entry point to those data, in line with the literature on democratic data visualisation (Tang, Wu and Li, 2019; Silva, 2019).

The dashboard ships in Portuguese and English, with light and dark theme and URL-persisted state.

## What the project does

1. Combines public, free official datasets (World Bank, UNDP, OECD) into a longitudinal cross-country panel covering 1990 to 2024.
2. Presents four elementary readings as interactive Plotly charts. Each tab provides country-group filters, country highlighting and CSV downloads.
   1. GDP versus mean years of schooling. Animated bubble chart, 1990 to 2024, bubbles scaled to total population, in the Gapminder style.
   2. GDP versus PISA score. 2022 cross-section and historical line chart for countries with longitudinal coverage (three or more PISA waves).
   3. Map. Choropleth layers for the panel's indicators on a flat projection or a rotatable 3D globe.
   4. PISA versus context. Scatter of PISA 2022 against a selectable context indicator: Government Effectiveness or Control of Corruption from the World Bank Worldwide Governance Indicators (WGI), or the World Bank income Gini index (`SI.POV.GINI`, latest available year per country). WGI Control of Corruption is widely used as a free public alternative to Transparency International's CPI, with which it correlates strongly in the series compared by the WGI methodology.

## Repository layout

```
.
├── README.md                                   # this file
├── app.py                                      # Streamlit dashboard
├── lab_geo.py                                  # map laboratory (px.choropleth / px.line_geo)
├── requirements.txt                            # Python dependencies
├── install.cmd                                 # Windows installer (creates .venv, installs deps)
├── data/                                       # working datasets consumed by the app
│   ├── API_NY.GDP.PCAP.PP.KD.csv               # WB GDP per capita PPP, constant 2021 USD
│   ├── API_SP.POP.TOTL_*.csv                   # WB Population (bulk download)
│   ├── hdr-data.xlsx                           # UNDP HDR, mean years of schooling
│   ├── _wb_wgi_ge.json                         # WB API. WGI Government Effectiveness
│   ├── _wb_wgi_cc.json                         # WB API. WGI Control of Corruption
│   ├── _wb_gini.json                           # WB API. Gini index (SI.POV.GINI)
│   ├── pisa_master_dataset.csv                 # PISA panel (output of build_pisa_panel.py)
│   ├── country_meta.csv                        # capital coordinates, region, income group
│   ├── build_pisa_panel.py                     # rebuilds pisa_master_dataset.csv
│   ├── build_country_meta.py                   # rebuilds country_meta.csv from the WB API
│   └── build_external_indicators.py            # refetches GDP and WGI from the WB API
└── knowledge/                                  # reference papers (PDFs)
```

## Data sources

Every dataset comes from an official statistical authority (World Bank, UNDP or OECD). No third-party aggregator is used.

| Variable | Provider | Indicator | Authoritative URL |
|---|---|---|---|
| GDP per capita PPP (constant 2021 international USD) | World Bank | `NY.GDP.PCAP.PP.KD` | https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.KD |
| Total population | World Bank | `SP.POP.TOTL` | https://data.worldbank.org/indicator/SP.POP.TOTL |
| Mean years of schooling | UNDP HDR | indicator `mys` | https://hdr.undp.org/data-center/documentation-and-downloads |
| Government Effectiveness (WGI) | World Bank | `GOV_WGI_GE.EST` | https://www.worldbank.org/en/publication/worldwide-governance-indicators |
| Control of Corruption (WGI) | World Bank | `GOV_WGI_CC.EST` | https://www.worldbank.org/en/publication/worldwide-governance-indicators |
| Gini index (income, 0–100) | World Bank | `SI.POV.GINI` | https://data.worldbank.org/indicator/SI.POV.GINI |
| PISA 2000 to 2018 (math, reading, science) | World Bank (ingests OECD PISA) | `LO.PISA.MAT`, `LO.PISA.REA`, `LO.PISA.SCI` | https://data.worldbank.org/indicator/LO.PISA.MAT |
| PISA 2022 (math, reading, science) | OECD | PISA 2022 Results, Vol. I, Annex B1 | https://doi.org/10.1787/53f23881-en |
| Capital coordinates, region, income group | World Bank | country endpoint | https://api.worldbank.org/v2/country |

The PISA panel-building script ([`data/build_pisa_panel.py`](data/build_pisa_panel.py)) pulls historical waves directly from the World Bank API and combines them with the 2022 wave reproduced verbatim from the OECD's published tables. The external-indicators script ([`data/build_external_indicators.py`](data/build_external_indicators.py)) refreshes the constant-PPP GDP CSV and the two WGI JSONs.

## How the dashboard is structured

`app.py` exposes five tabs:

1. GDP versus schooling. Animated bubble chart, 1990 to 2024.
2. GDP versus PISA. 2022 cross-section with a historical-trajectories sub-chart for countries with three or more PISA waves.
3. Map. The panel's indicators as choropleth layers (GDP per capita, mean years of schooling, PISA score), on a flat projection or a rotatable 3D globe. GDP per capita carries a logarithmic colour scale with ticks at 1, 2 and 5 times each power of ten, so a narrow group such as the G7 still gets a readable colour bar. Each layer has an expander showing the Plotly call that produced it. The PISA layer is pinned to the latest wave, since PISA only exists on wave years.
4. PISA versus context. Scatter of PISA 2022 against the chosen context indicator (WGI Government Effectiveness, WGI Control of Corruption, or World Bank Gini index of income), with Pearson correlation, OLS fit line and country-level table.
5. About. Methodology notes, references, sources.

The sidebar carries language and theme toggles, a country-group filter (G7, G20, EU, BRICS+, South America, Latin America, Asian Tigers, Lusophone, etc.) shared by all tabs, an optional "highlight countries" multiselect, a collapsible data-sources block, and the author block.

## Reproducing the analysis

### Setup

Linux or macOS:

```bash
pip install -r requirements.txt
```

Windows (creates a local `.venv` and installs everything):

```cmd
install.cmd
```

### Re-fetch external indicators (optional)

```bash
python data/build_external_indicators.py
python data/build_pisa_panel.py
```

`build_external_indicators.py` queries the World Bank API for GDP per capita PPP (constant 2021 USD), the two WGI series (Government Effectiveness, Control of Corruption) and the Gini index (`SI.POV.GINI`), writing them to `data/`. `build_pisa_panel.py` rebuilds the PISA cross-country master dataset.

### Run the dashboard

```bash
streamlit run app.py
```

The browser opens at `http://localhost:8501`. Language and theme can be switched at the top of the sidebar. Both are persisted in the URL so views are shareable.

### Run the map laboratory

```bash
streamlit run lab_geo.py
```

`lab_geo.py` is a separate sandbox for geographic representations of the same panel, kept out of `app.py` so experiments cannot destabilise the published dashboard. It has six tabs:

1. Base choropleth. Any indicator, any year, switchable projection (orthographic globe, Natural Earth, Robinson, Mollweide, ...), rotation sliders and optional log colour scale.
2. Animated choropleth. Mean years of schooling or GDP per capita, one frame per year, colour scale locked across frames.
3. PISA residual. `PISA ~ log10(GDP per capita)` fitted on a chosen wave. The map shows the residual on a diverging scale, so countries that score above or below what their income predicts are legible at a glance. Kept in the laboratory only. Defending a cross-country residual is a heavier methodological commitment than the dashboard needs, so the published panel carries the descriptive layers alone.
4. `px.line_geo` peer network. Each country is linked to the country within a ±X% GDP-per-capita band that has the highest PISA score, i.e. its comparable-income benchmark.
5. `px.line_geo` ranking trail. The top-N countries connected in rank order, once by PISA and once by GDP per capita, so the divergence between the two rankings becomes a shape on the globe.
6. PISA coverage. Number of waves per country. A methodological note in map form: most of the world has never sat PISA.

Each tab carries an expander with the Plotly call that produced the chart, to make porting an experiment into `app.py` mechanical.

The line layers need one coordinate pair per country, which the choropleths do not. Those coordinates (plus region and income group) come from the World Bank country endpoint:

```bash
python data/build_country_meta.py
```

## References

- Tang, N., Wu, E., and Li, G. (2019). *Towards Democratizing Relational Data Visualization*. SIGMOD '19, ACM. https://doi.org/10.1145/3299869.3314029
- Silva, F. C. C. (2019). Visualização de dados: passado, presente e futuro. *Liinc em Revista*, 15(2), 205–223. https://doi.org/10.18617/liinc.v15i2.4812
- Kaufmann, D., and Kraay, A. (2024). *Worldwide Governance Indicators, 2024 Methodology Update*. World Bank.
- OECD (2023). *PISA 2022 Results (Volume I): The State of Learning and Equity in Education*. OECD Publishing. https://doi.org/10.1787/53f23881-en
- UNDP (2024). *Human Development Report 2023/24*. United Nations Development Programme.

## Author

Thiago Alcebíades Rodrigues. [thiago.alcebiades@unifesp.br](mailto:thiago.alcebiades@unifesp.br) · [LinkedIn](https://www.linkedin.com/in/thiago-alcebiades-rodrigues-95446621b/)
