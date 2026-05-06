import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Wealth, Education & PISA — Efficiency Lab",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1300px; }
    h1, h2, h3 { letter-spacing: -0.01em; }
    [data-testid="stMetric"] {
        background: var(--secondary-background-color, #262730);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 14px 18px;
        border-radius: 10px;
    }
    [data-testid="stMetricValue"] { color: var(--text-color, #FAFAFA); }
    [data-testid="stMetricLabel"] { color: var(--text-color, #FAFAFA); opacity: 0.85; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: var(--secondary-background-color, #262730);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 8px 18px;
    }
    .footnote { color: rgba(140,140,140,0.95); font-size: 0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_DIR = "data"
PISA_YEARS = [2000, 2003, 2006, 2009, 2012, 2015, 2018, 2022]

GROUPS = {
    "G20": ["ARG", "AUS", "BRA", "CAN", "CHN", "FRA", "DEU", "IND", "IDN", "ITA", "JPN", "KOR", "MEX", "RUS", "SAU", "ZAF", "TUR", "GBR", "USA", "ESP"],
    "G7": ["CAN", "FRA", "DEU", "ITA", "JPN", "GBR", "USA"],
    "BRICS+": ["BRA", "RUS", "IND", "CHN", "ZAF", "EGY", "ETH", "IRN", "ARE", "SAU"],
    "European Union": ["AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD", "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE"],
    "South America": ["ARG", "BOL", "BRA", "CHL", "COL", "ECU", "GUY", "PRY", "PER", "SUR", "URY", "VEN"],
    "Latin America & Caribbean": ["ARG", "BHS", "BRB", "BLZ", "BOL", "BRA", "CHL", "COL", "CRI", "CUB", "DOM", "ECU", "SLV", "GTM", "GUY", "HTI", "HND", "JAM", "MEX", "NIC", "PAN", "PRY", "PER", "SUR", "TTO", "URY", "VEN"],
    "East & Southeast Asia": ["CHN", "JPN", "IND", "KOR", "IDN", "THA", "MYS", "VNM", "PHL", "SGP", "BGD", "PAK", "HKG", "TWN"],
    "Lusophone": ["BRA", "PRT", "AGO", "MOZ", "CPV", "GNB", "STP", "TLS"],
    "Asian Tigers": ["KOR", "SGP", "HKG", "TWN", "MYS", "THA", "VNM", "IDN"],
}


def _mtime(*paths):
    return tuple(os.path.getmtime(p) if os.path.exists(p) else 0 for p in paths)


@st.cache_data(show_spinner=False)
def load_panel(_mtime_key):
    fixed = ["Country Code", "Country Name"]
    years = [str(y) for y in range(1990, 2024)]

    df_gdp = pd.read_csv(f"{DATA_DIR}/API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_216039.csv", skiprows=4)
    df_gdp = df_gdp[[c for c in fixed + years if c in df_gdp.columns]].melt(
        id_vars=fixed, var_name="year", value_name="gdp_per_capita"
    )
    df_gdp = df_gdp.rename(columns={"Country Code": "geo", "Country Name": "name"})
    df_gdp["year"] = pd.to_numeric(df_gdp["year"])
    df_gdp["geo"] = df_gdp["geo"].str.upper()

    df_pop = pd.read_csv(f"{DATA_DIR}/API_SP.POP.TOTL_DS2_en_csv_v2_246068.csv", skiprows=4)
    df_pop = df_pop[[c for c in fixed + years if c in df_pop.columns]].melt(
        id_vars=fixed, var_name="year", value_name="population"
    )
    df_pop = df_pop.rename(columns={"Country Code": "geo", "Country Name": "name"})
    df_pop["year"] = pd.to_numeric(df_pop["year"])
    df_pop["geo"] = df_pop["geo"].str.upper()

    df_edu = pd.read_excel(f"{DATA_DIR}/hdr-data.xlsx")
    df_edu.columns = df_edu.columns.str.strip()
    df_edu["year"] = pd.to_numeric(df_edu["year"], errors="coerce")
    df_edu = df_edu[(df_edu["year"] >= 1990) & (df_edu["year"] <= 2023)]
    df_edu = df_edu[["countryIsoCode", "year", "value"]].rename(
        columns={"countryIsoCode": "geo", "value": "years_schooling"}
    )
    df_edu["geo"] = df_edu["geo"].str.upper()
    df_edu["years_schooling"] = pd.to_numeric(df_edu["years_schooling"], errors="coerce")

    df_pisa = pd.read_csv(f"{DATA_DIR}/pisa_master_dataset.csv")
    df_pisa["geo"] = df_pisa["geo"].str.upper()
    df_pisa["year"] = pd.to_numeric(df_pisa["year"])

    panel = (
        df_gdp.merge(df_edu, on=["geo", "year"], how="inner")
        .merge(df_pop[["geo", "year", "population"]], on=["geo", "year"], how="left")
        .merge(df_pisa, on=["geo", "year"], how="left")
    )
    panel["population_str"] = panel["population"].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) else "N/A"
    )
    return panel


@st.cache_data(show_spinner=False)
def load_efficiency(_mtime_key):
    return pd.read_csv(f"{DATA_DIR}/efficiency_index.csv")


try:
    panel_files = (
        f"{DATA_DIR}/API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_216039.csv",
        f"{DATA_DIR}/API_SP.POP.TOTL_DS2_en_csv_v2_246068.csv",
        f"{DATA_DIR}/hdr-data.xlsx",
        f"{DATA_DIR}/pisa_master_dataset.csv",
    )
    panel = load_panel(_mtime(*panel_files))
    eff = load_efficiency(_mtime(f"{DATA_DIR}/efficiency_index.csv"))
except Exception as exc:
    st.error(f"Data loading failed: {exc}")
    st.stop()


with st.sidebar:
    st.markdown("### Filters")
    GROUPS["All countries"] = sorted(panel["geo"].dropna().unique().tolist())
    selected_group = st.selectbox("Country group", list(GROUPS.keys()))
    country_list = GROUPS[selected_group]

    st.markdown("### View options")
    y_axis_choice = st.radio(
        "Y-axis metric",
        ["PISA Score", "Mean Years of Schooling"],
        index=0,
    )

    st.divider()
    st.markdown("### Data sources")
    st.markdown(
        """
        - **GDP per capita PPP** — [World Bank `NY.GDP.PCAP.PP.CD`](https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD)
        - **Population** — [World Bank `SP.POP.TOTL`](https://data.worldbank.org/indicator/SP.POP.TOTL)
        - **Mean Years of Schooling** — [UNDP HDR](https://hdr.undp.org/data-center/documentation-and-downloads)
        - **PISA scores** — [OECD](https://www.oecd.org/pisa/)
        - **Per-secondary-student spending** — [WB `SE.XPD.SECO.PC.ZS`](https://data.worldbank.org/indicator/SE.XPD.SECO.PC.ZS)
        - **Total ed spending (% GDP)** — [WB `SE.XPD.TOTL.GD.ZS`](https://data.worldbank.org/indicator/SE.XPD.TOTL.GD.ZS)
        - **Government Effectiveness (WGI)** — [WB Worldwide Governance Indicators](https://www.worldbank.org/en/publication/worldwide-governance-indicators)
        """
    )

    st.divider()
    st.markdown("### Author")
    st.info(
        "**Thiago Alcebíades Rodrigues**  \n"
        "[thiago.alcebiades@unifesp.br](mailto:thiago.alcebiades@unifesp.br)  \n"
        "[LinkedIn](https://www.linkedin.com/in/thiago-alcebiades-rodrigues-95446621b/)"
    )


st.title("Wealth, Education and PISA")
st.markdown(
    "Study of the relationship between national income, schooling, institutional quality and student achievement"
)
st.divider()

if y_axis_choice == "Mean Years of Schooling":
    y_col, y_label = "years_schooling", "Years of Schooling"
    panel_for_view = panel
else:
    y_col, y_label = "pisa_score", "PISA Score"
    panel_for_view = panel[panel["year"].isin(PISA_YEARS)]

view_panel = panel_for_view[panel_for_view["geo"].isin(country_list)].dropna(
    subset=["gdp_per_capita", y_col]
).copy()
view_panel["population_for_size"] = view_panel["population"].fillna(1)

tab_panel, tab_efficiency, tab_drivers, tab_methodology = st.tabs(
    ["Historical Panel", "Education Efficiency Index", "Drivers Correlations", "Methodology"]
)


with tab_panel:
    st.subheader(f"Historical evolution — {selected_group} ({y_label})")

    if y_col == "pisa_score":
        st.markdown(
            "<span class='footnote'>PISA is administered every three years. "
            "The animation iterates only over wave years.</span>",
            unsafe_allow_html=True,
        )

    if view_panel.empty:
        st.warning(f"No data available for {y_label} within {selected_group}.")
    else:
        latest_year = int(view_panel["year"].max())
        latest = view_panel[view_panel["year"] == latest_year]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Countries in view", f"{view_panel['geo'].nunique()}")
        c2.metric("Years of data", f"{int(view_panel['year'].min())} – {latest_year}")
        c3.metric(
            f"Median GDP per capita ({latest_year})",
            f"${latest['gdp_per_capita'].median():,.0f}" if not latest.empty else "—",
        )
        c4.metric(
            f"Median {y_label} ({latest_year})",
            f"{latest[y_col].median():.1f}" if not latest.empty else "—",
        )

        min_x = view_panel["gdp_per_capita"].min() * 0.8
        max_x = view_panel["gdp_per_capita"].max() * 1.2
        min_y = view_panel[y_col].min() * 0.95
        max_y = view_panel[y_col].max() * 1.05

        fig = px.scatter(
            view_panel,
            x="gdp_per_capita",
            y=y_col,
            animation_frame="year",
            animation_group="name",
            size="population_for_size",
            color="name",
            hover_name="name",
            custom_data=["gdp_per_capita", "population", "population_str", y_col],
            log_x=True,
            size_max=55,
            range_x=[min_x, max_x],
            range_y=[min_y, max_y],
            labels={
                "gdp_per_capita": "GDP per capita (USD PPP, log scale)",
                y_col: y_label,
                "name": "Country",
                "year": "Year",
            },
            template="plotly_dark",
        )
        fig.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "GDP per capita (USD PPP): %{customdata[0]:,.0f}<br>"
                "Population: %{customdata[2]}<br>"
                + y_label + ": %{customdata[3]:.2f}<extra></extra>"
            )
        )
        fig.update_layout(height=620, legend_title_text="Country")
        if y_col == "pisa_score" and fig.layout.updatemenus:
            for menu in fig.layout.updatemenus:
                for button in menu.buttons:
                    if button.label == "▶":
                        button.args[1]["frame"]["duration"] = 1200
                        button.args[1]["transition"]["duration"] = 600
        st.plotly_chart(fig, width="stretch")

        st.markdown(
            "<span class='footnote'>Bubble size scales with total population. "
            "X-axis is logarithmic.</span>",
            unsafe_allow_html=True,
        )


with tab_efficiency:
    st.subheader("Education Efficiency Index")
    st.markdown(
        "Standardised residual (z-score) of the production function "
        r"$\ln(\text{PISA})=\theta\ln(\text{Spend})+\beta\ln(\text{GDP})+\gamma\ln(\text{MYS})+\eta\,\text{GovEff}+\delta+\varepsilon$, "
        "estimated by **OLS** with HC1-robust standard errors. "
        "$\\text{Spend}$ is per-secondary-student government expenditure (USD PPP), "
        "$\\text{MYS}$ is mean years of schooling, "
        "$\\text{GovEff}$ is the World Bank Government Effectiveness score (≈ −2.5 to +2.5). "
        "Positive z ⇒ country produces more PISA points than its measurable inputs predict."
    )

    eff_filtered = eff[eff["geo"].isin(country_list)].copy()
    if len(eff_filtered) < 3:
        match_count = len(eff_filtered)
        eff_filtered = eff.copy()
        st.info(
            f"Only {match_count} country in **{selected_group}** has efficiency data. "
            f"Showing the full sample of {len(eff_filtered)} countries instead."
        )

    sort_choice = st.radio(
        "Rank by",
        ["Efficiency z-score", "PISA per 1 000 USD spent"],
        horizontal=True,
    )
    sort_col = {"Efficiency z-score": "efficiency_z",
                "PISA per 1 000 USD spent": "pisa_per_1k_usd"}[sort_choice]
    eff_filtered = eff_filtered.sort_values(sort_col, ascending=True).reset_index(drop=True)
    best = eff_filtered.iloc[-1]
    worst = eff_filtered.iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Most efficient",  f"{best['name']}",  f"z = {best['efficiency_z']:+.2f}")
    c2.metric("Least efficient", f"{worst['name']}", f"z = {worst['efficiency_z']:+.2f}")
    c3.metric("Sample size", f"{len(eff_filtered)} countries")

    bar = px.bar(
        eff_filtered,
        x=sort_col,
        y="name",
        orientation="h",
        color="efficiency_z",
        color_continuous_scale=["#C73E1D", "#F4F1DE", "#2E86AB"],
        color_continuous_midpoint=0,
        category_orders={"name": eff_filtered["name"].tolist()},
        hover_data={
            "pisa_score": ":.0f",
            "pisa_pred": ":.0f",
            "spend_per_student": ":,.0f",
            "spend_year": True,
            "gdp_per_capita": ":,.0f",
            "years_schooling": ":.1f",
            "gov_eff": ":+.2f",
            "efficiency_z": ":+.2f",
        },
        labels={
            "efficiency_z": "Efficiency z-score",
            "pisa_per_1k_usd": "PISA points per 1 000 USD",
            "name": "",
        },
        template="plotly_dark",
    )
    bar.update_layout(
        height=max(420, 18 * len(eff_filtered)),
        coloraxis_colorbar_title="z-score",
    )
    bar.add_vline(x=0, line_color="white", line_width=0.5, opacity=0.5)
    st.plotly_chart(bar, width="stretch")

    st.markdown("#### Spending vs achievement")
    fit = eff_filtered.dropna(subset=["spend_per_student", "pisa_score"]).copy()
    scatter = px.scatter(
        fit,
        x="spend_per_student",
        y="pisa_score",
        size="spend_per_student",
        color="efficiency_z",
        color_continuous_scale=["#C73E1D", "#F4F1DE", "#2E86AB"],
        color_continuous_midpoint=0,
        text="geo",
        hover_data={
            "name": True,
            "spend_per_student": ":,.0f",
            "pisa_score": ":.0f",
            "pisa_pred": ":.0f",
            "years_schooling": ":.1f",
            "gov_eff": ":+.2f",
            "spend_year": True,
            "geo": False,
        },
        labels={
            "spend_per_student": "Per-student spending (USD PPP, log scale)",
            "pisa_score": "PISA score (2022)",
            "efficiency_z": "Efficiency z-score",
        },
        log_x=True,
        template="plotly_dark",
    )
    scatter.update_traces(textposition="top center")
    if len(fit) >= 5:
        ln_x = np.log(fit["spend_per_student"])
        slope, intercept = np.polyfit(ln_x, fit["pisa_score"], 1)
        x_grid = np.linspace(fit["spend_per_student"].min(), fit["spend_per_student"].max(), 80)
        scatter.add_trace(
            go.Scatter(
                x=x_grid,
                y=intercept + slope * np.log(x_grid),
                mode="lines",
                line=dict(color="#888", dash="dash"),
                name="Empirical fit",
                showlegend=True,
            )
        )
    scatter.update_layout(height=560)
    st.plotly_chart(scatter, width="stretch")

    with st.expander("Country-level table"):
        display = eff_filtered[
            ["name", "geo", "pisa_score", "pisa_pred", "spend_per_student", "spend_year",
             "years_schooling", "gdp_per_capita", "gov_eff", "xpd_pct_gdp", "efficiency_z"]
        ].rename(
            columns={
                "name": "Country", "geo": "ISO3",
                "pisa_score": "PISA (actual)", "pisa_pred": "PISA (predicted)",
                "spend_per_student": "Spend / student (USD PPP)",
                "spend_year": "Spending year",
                "years_schooling": "Mean years of schooling",
                "gdp_per_capita": "GDP per capita (USD PPP)",
                "gov_eff": "Govt Effectiveness",
                "xpd_pct_gdp": "Total ed exp (% GDP)",
                "efficiency_z": "Efficiency z",
            }
        )
        st.dataframe(
            display.style.format({
                "PISA (actual)": "{:.0f}",
                "PISA (predicted)": "{:.0f}",
                "Spend / student (USD PPP)": "{:,.0f}",
                "Spending year": "{:.0f}",
                "Mean years of schooling": "{:.1f}",
                "GDP per capita (USD PPP)": "{:,.0f}",
                "Govt Effectiveness": "{:+.2f}",
                "Total ed exp (% GDP)": "{:.1f}",
                "Efficiency z": "{:+.2f}",
            }),
            width="stretch",
            hide_index=True,
        )


with tab_drivers:
    st.subheader("How each driver correlates with PISA")
    st.markdown(
        "Bivariate associations between PISA 2022 score and the four candidate drivers used "
        "in the efficiency model. Each panel includes an OLS-fit line; the headline number "
        "is the simple Pearson correlation."
    )

    drivers = [
        ("spend_per_student",  "Spending / student",   "Per-student spending (USD PPP, log scale)", True),
        ("gdp_per_capita",     "GDP per capita",       "GDP per capita (USD PPP, log scale)",       True),
        ("years_schooling",    "Years of schooling",   "Mean years of schooling",                   False),
        ("gov_eff",            "Govt Effectiveness",   "Government Effectiveness (-2.5 to +2.5)",   False),
    ]

    for col, short_label, axis_label, log_x in drivers:
        sub = eff.dropna(subset=[col, "pisa_score"])
        r = sub[col].corr(sub["pisa_score"])

        c1, c2 = st.columns([1, 3])
        c1.metric(short_label, f"r = {r:+.2f}",
                  help=f"Pearson correlation between PISA 2022 and {short_label.lower()} across {len(sub)} countries.")
        with c2:
            scat = px.scatter(
                sub,
                x=col, y="pisa_score",
                text="geo",
                color="efficiency_z",
                color_continuous_scale=["#C73E1D", "#F4F1DE", "#2E86AB"],
                color_continuous_midpoint=0,
                hover_data={"name": True, col: ":,.2f", "pisa_score": ":.0f", "geo": False},
                log_x=log_x,
                template="plotly_dark",
                labels={col: axis_label, "pisa_score": "PISA 2022 score"},
            )
            scat.update_traces(textposition="top center")
            xs = sub[col].to_numpy()
            ys = sub["pisa_score"].to_numpy()
            if log_x:
                z = np.polyfit(np.log(xs), ys, 1)
                xline = np.linspace(xs.min(), xs.max(), 60)
                yline = np.polyval(z, np.log(xline))
            else:
                z = np.polyfit(xs, ys, 1)
                xline = np.linspace(xs.min(), xs.max(), 60)
                yline = np.polyval(z, xline)
            scat.add_trace(go.Scatter(x=xline, y=yline, mode="lines",
                                       line=dict(color="#888", dash="dash"),
                                       name="OLS fit", showlegend=False))
            scat.update_layout(height=380, margin=dict(t=20, b=20))
            st.plotly_chart(scat, width="stretch")


with tab_methodology:
    st.subheader("Methodology")

    st.markdown("### Specification")
    st.markdown(
        r"""
$$\ln(\text{PISA}_i) = \theta\,\ln(\text{Spend}_i) + \beta\,\ln(\text{GDP}_i) + \gamma\,\ln(\text{MYS}_i) + \eta\,\text{GovEff}_i + \delta + \varepsilon_i$$

Estimated by OLS with HC1-robust standard errors on the cross-section of 57 countries with a PISA 2022 score. The Education Efficiency Index is the standardised residual:

$$\text{EI}_i = \frac{\hat\varepsilon_i - \bar{\hat\varepsilon}}{\hat\sigma_{\hat\varepsilon}}$$

Reported directly as the z-score. Positive values indicate that a country produces more PISA points than its measurable inputs predict; negative values indicate underperformance.
        """
    )

    st.markdown("### Variables and sources")
    st.markdown(
        """
| Variable | Source | Indicator | Year |
|---|---|---|---|
| PISA score | OECD | mean of math, reading, science (TOT) | 2022 |
| Per-secondary-student spending | World Bank (UNESCO UIS) | `SE.XPD.SECO.PC.ZS` × GDP per capita PPP | 2015–2018 |
| GDP per capita PPP | World Bank | `NY.GDP.PCAP.PP.CD` | 2022 |
| Mean years of schooling | UNDP HDR | `mys` | 2022 |
| Government Effectiveness | World Bank WGI | `GOV_WGI_GE.EST` | 2018–2023 |
| Total education expenditure (% GDP) | World Bank (UNESCO UIS) | `SE.XPD.TOTL.GD.ZS` | 2018–2023 |
        """
    )

    st.markdown("### Specification search")
    st.markdown(
        """
| Spec | Variables | adj R² | N |
|---|---|---|---|
| M1 | Spend, GDP, MYS                            | 0.711 | 56 |
| M2 | M1 + Total ed exp (% GDP)                   | 0.708 | 56 |
| **M3 (preferred)** | M1 + Government Effectiveness | **0.720** | 56 |
| M4 | M1 + Total ed exp + Government Effectiveness | 0.718 | 56 |

Total education expenditure as a percentage of GDP is not statistically significant in any specification, consistent with Hanushek's finding that the size of the fiscal effort does not predict achievement once other inputs are controlled for. Government Effectiveness contributes positively and is retained in the preferred specification.
        """
    )

    st.markdown("### 2SLS robustness check")
    st.markdown(
        r"""
The notebook re-estimates M3 by 2SLS using lagged per-student spending (2005–2014) as instrument for current spending. First-stage F-statistic is 128, well above the conventional threshold of 10. The 2SLS coefficient on $\ln(\text{Spend})$ is moderately higher than OLS, consistent with downward bias in OLS. The dashboard index is built from OLS predictions; 2SLS is reported in the notebook as a sensitivity check.
        """
    )

    st.markdown("### Prediction versus causal identification")
    st.markdown(
        "OLS is appropriate because the objective is prediction of PISA given inputs, "
        "not recovery of causal elasticities. Causal identification would require panel "
        "data with within-country variation or stronger instruments, which is left for "
        "follow-up work."
    )

    st.markdown("### Limitations")
    st.markdown(
        """
1. Cross-section of 57 countries — limited statistical power.
2. PISA captures one cohort and three subjects.
3. Spending observations span 2015–2018, not 2022.
4. Sociodemographic controls limited to GDP, MYS and GovEff.
5. Government Effectiveness is a perception-based composite.
        """
    )

    st.markdown("### References")
    st.markdown(
        """
- Hanushek, E. A. (2020). *Education production functions*. The Economics of Education, 2nd ed., Elsevier.
- Hanushek, E. A. (1986). The economics of schooling: Production and efficiency in public schools. *Journal of Economic Literature*, 24(3).
- Dee, T. S. (2005). Expense preference and student achievement in school districts. *Eastern Economic Journal*, 31(1).
- Acemoglu, D., Johnson, S., & Robinson, J. A. (2012). *Why Nations Fail*. Crown Business.
- Kaufmann, D., & Kraay, A. (2024). *Worldwide Governance Indicators — 2024 Methodology Update*. World Bank.
        """
    )
