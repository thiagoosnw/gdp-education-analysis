import json
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# Constants
# ============================================================

DATA_DIR = "data"
PISA_YEARS_FALLBACK = [2000, 2003, 2006, 2009, 2012, 2015, 2018, 2022]

GROUPS_BASE = {
    "G20": ["ARG", "AUS", "BRA", "CAN", "CHN", "FRA", "DEU", "IND", "IDN", "ITA", "JPN", "KOR", "MEX", "RUS", "SAU", "ZAF", "TUR", "GBR", "USA", "ESP"],
    "G7": ["CAN", "FRA", "DEU", "ITA", "JPN", "GBR", "USA"],
    "BRICS+": ["BRA", "RUS", "IND", "CHN", "ZAF", "EGY", "ETH", "IRN", "ARE", "SAU"],
    "European Union": ["AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD", "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE"],
    "South America": ["ARG", "BOL", "BRA", "CHL", "COL", "ECU", "GUY", "PRY", "PER", "SUR", "URY", "VEN"],
    "Latin America & Caribbean": ["ARG", "BHS", "BRB", "BLZ", "BOL", "BRA", "CHL", "COL", "CRI", "CUB", "DOM", "ECU", "SLV", "GTM", "GUY", "HTI", "HND", "JAM", "MEX", "NIC", "PAN", "PRY", "PER", "SUR", "TTO", "URY", "VEN"],
    "East & Southeast Asia": ["CHN", "JPN", "IND", "KOR", "IDN", "THA", "MYS", "VNM", "PHL", "SGP", "BGD", "PAK", "HKG", "TWN"],
    "Lusophone": ["BRA", "PRT", "AGO", "MOZ", "CPV", "GNB", "STP", "TLS"],
    "Asian Tigers": ["KOR", "SGP", "HKG", "TWN", "MYS", "THA", "VNM", "IDN"],
    "OPEC": ["DZA", "COG", "GNQ", "GAB", "IRN", "IRQ", "KWT", "LBY", "NGA", "SAU", "ARE", "VEN"],
}

GROUP_LABELS_PT = {
    "G20": "G20",
    "G7": "G7",
    "BRICS+": "BRICS+",
    "European Union": "União Europeia",
    "South America": "América do Sul",
    "Latin America & Caribbean": "América Latina e Caribe",
    "East & Southeast Asia": "Leste e Sudeste Asiático",
    "Lusophone": "Lusófonos",
    "Asian Tigers": "Tigres Asiáticos",
    "OPEC": "OPEP",
}


# ============================================================
# Internationalisation
# ============================================================

I18N = {
    "pt": {
        "page_title": "Riqueza, Educação e PISA — Visualização Interativa",
        "app_title": "Riqueza, Educação e PISA",
        "app_subtitle": (
            "Painel interativo que cruza PIB per capita (em paridade de poder de compra, "
            "dólares constantes de 2021), anos médios de escolaridade, pontuação no PISA "
            "e indicadores de governança do Banco Mundial. O objetivo é tornar visíveis, "
            "em poucos cliques, relações que normalmente exigem horas em planilhas, "
            "democratizando o acesso a dados sobre educação e desenvolvimento."
        ),
        "ui_language": "Idioma",
        "ui_theme": "Tema",
        "theme_dark": "Escuro",
        "theme_light": "Claro",
        "filters": "Filtros",
        "country_group": "Grupo de países",
        "group_all": "Todos os países",
        "view_options": "Opções de visualização",
        "highlight_label": "Países em destaque (opcional)",
        "highlight_help": "Países selecionados ficam em cor saturada; os demais ficam translúcidos.",
        "data_sources": "Fontes de dados",
        "data_sources_md": (
            "- PIB per capita PPC, dólares constantes de 2021. World Bank `NY.GDP.PCAP.PP.KD`. "
            "https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.KD\n"
            "- População. World Bank `SP.POP.TOTL`. "
            "https://data.worldbank.org/indicator/SP.POP.TOTL\n"
            "- Anos médios de escolaridade. UNDP HDR, indicador `mys`. "
            "https://hdr.undp.org/data-center/documentation-and-downloads\n"
            "- Pontuação PISA. OECD e WB Education Statistics. "
            "https://www.oecd.org/pisa/\n"
            "- Eficácia governamental (WGI). World Bank. "
            "https://www.worldbank.org/en/publication/worldwide-governance-indicators\n"
            "- Controle de corrupção (WGI). World Bank. "
            "https://www.worldbank.org/en/publication/worldwide-governance-indicators\n"
            "- Coeficiente de Gini (renda). World Bank `SI.POV.GINI`. "
            "https://data.worldbank.org/indicator/SI.POV.GINI"
        ),
        "author": "Autor",
        "tab_mys": "PIB × Escolaridade",
        "tab_pisa": "PIB × PISA",
        "tab_map": "Mapa",
        "tab_gov": "PISA × Contexto",
        "tab_about": "Sobre",
        "subtitle_mys": "PIB per capita versus anos médios de escolaridade. {group}",
        "subtitle_pisa": "PIB per capita versus pontuação PISA. {group}",
        "subtitle_map": "Distribuição geográfica dos indicadores do painel. {group}",
        "subtitle_gov": "Pontuação PISA versus indicadores de contexto institucional e de desigualdade. {group}",
        "panel_pisa_note": (
            "Apresentado como recorte transversal da onda mais recente do PISA (2022, 81 países). "
            "Como 38 dos 84 países só ingressaram no PISA em 2022, uma animação contínua "
            "induziria leitura equivocada. O painel de tendências cobre apenas os países com "
            "três ou mais aplicações."
        ),
        "panel_pisa_trend_title": "Trajetórias por país (três ou mais aplicações)",
        "panel_pisa_trend_note": (
            "{n} países do grupo selecionado têm três ou mais aplicações do PISA. "
            "Cada linha conecta as ondas reais sem interpolação."
        ),
        "no_data_warning": "Sem dados disponíveis para {metric} em {group}.",
        "m_countries": "Países na visualização",
        "m_years": "Anos de dados",
        "m_median_gdp": "Mediana do PIB per capita ({year})",
        "m_median_y": "Mediana de {metric} ({year})",
        "x_label": "PIB per capita (USD PPC, dólares constantes de 2021, escala logarítmica)",
        "x_label_short": "PIB per capita (USD PPC, dólares constantes de 2021)",
        "y_mys": "Anos médios de escolaridade",
        "y_pisa": "Pontuação PISA",
        "year": "Ano",
        "country": "País",
        "population": "População",
        "footnote_bubble": "As bolhas têm tamanho proporcional à população total. Eixo X em escala logarítmica.",
        "download_csv": "Baixar dados (CSV)",
        "gov_description": (
            "Cada ponto é um país. O eixo X mostra um indicador de contexto. Você pode "
            "escolher entre dois indicadores de qualidade institucional do Banco Mundial — "
            "Eficácia Governamental e Controle de Corrupção — ou o coeficiente de Gini de "
            "renda, que mede desigualdade. Os dois primeiros vão de aproximadamente −2,5 a "
            "+2,5: valores mais altos indicam instituições de melhor qualidade. O Gini vai "
            "de 0 a 100: valores mais altos indicam mais desigualdade. O eixo Y mostra a "
            "pontuação média no PISA 2022. O Controle de Corrupção do Banco Mundial é "
            "frequentemente usado como alternativa pública e gratuita ao índice de "
            "percepção de corrupção da Transparency International."
        ),
        "map_description": (
            "Os indicadores das abas anteriores distribuídos no globo. A leitura geográfica "
            "não substitui os cruzamentos, mas revela agrupamentos regionais que um gráfico "
            "de dispersão embaralha."
        ),
        "map_layer": "Camada",
        "map_l_gdp": "PIB per capita",
        "map_l_mys": "Anos médios de escolaridade",
        "map_l_pisa": "Pontuação PISA",
        "map_projection": "Projeção",
        "map_globe": "Globo 3D",
        "map_flat": "Planisfério",
        "map_rotation": "Girar o globo (longitude)",
        "map_log": "Escala logarítmica de cor",
        "map_pisa_wave": "Camada fixada na onda mais recente do PISA ({year}).",
        "map_footnote": (
            "Países em cinza não têm observação para a camada e o ano escolhidos. Ausência de "
            "dado não é zero. O mapa também pinta área, não população. Rússia, Canadá e "
            "Austrália ocupam muito espaço com poucos habitantes, enquanto países pequenos e "
            "populosos quase desaparecem. Para leitura ponderada por população, use as bolhas "
            "das duas primeiras abas."
        ),
        "map_no_data": "Sem dados para {metric} em {group}.",
        "map_code": "Código do gráfico",
        "map_code_note": (
            "O painel inteiro é software livre. Este é o trecho que gera o mapa acima, pronto "
            "para colar em um script com pandas e plotly."
        ),
        "gov_indicator": "Indicador de contexto",
        "gov_ge": "Eficácia Governamental (WGI)",
        "gov_cc": "Controle de Corrupção (WGI)",
        "gov_gini": "Coeficiente de Gini (renda)",
        "gov_year": "Ano de referência",
        "gov_correlation": "Correlação (grupo)",
        "gov_correlation_global": "Correlação (global)",
        "gov_correlation_global_help": "Calculada sobre todos os países com PISA 2022 e o indicador escolhido ({n} países). Serve como referência para comparar com o valor do grupo filtrado.",
        "gov_axis_ge": "Eficácia Governamental (≈ −2,5 a +2,5)",
        "gov_axis_cc": "Controle de Corrupção (≈ −2,5 a +2,5)",
        "gov_axis_gini": "Coeficiente de Gini (0–100, maior = mais desigual)",
        "gov_n_countries": "{n} países (PISA 2022 + indicador)",
        "ols_fit": "Ajuste OLS",
        "about_md": (
            "Este painel é um exercício de democratização de dados sobre educação e "
            "desenvolvimento econômico. Foi construído integralmente em Python, com "
            "Streamlit e Plotly, a partir de fontes públicas e gratuitas:\n\n"
            "1. World Bank Open Data (PIB, população, governança).\n"
            "2. UNDP Human Development Report (anos médios de escolaridade).\n"
            "3. OECD Programme for International Student Assessment (PISA 2022).\n\n"
            "A intenção não é estimar uma relação causal entre riqueza, governança e "
            "aprendizagem. Esse é um problema reconhecidamente difícil que demanda dados "
            "regionalizados e desenhos de identificação mais fortes do que cortes transversais "
            "entre países permitem. A intenção é dar ao leitor não especialista uma porta de "
            "entrada visual e interativa para esses dados, no espírito da literatura sobre "
            "visualização democrática (Tang, Wu e Li, 2019; Silva, 2019).\n\n"
            "Cada aba apresenta uma leitura elementar dos dados:\n\n"
            "1. PIB versus anos médios de escolaridade. Animação histórica de 1990 a 2024, "
            "com bolhas proporcionais à população.\n"
            "2. PIB versus pontuação no PISA. Recorte transversal de 2022 e trajetórias dos "
            "países com cobertura longitudinal (três ou mais aplicações).\n"
            "3. Mapa. Os mesmos indicadores distribuídos geograficamente, em planisfério ou "
            "globo, com filtro de grupo, destaque de países e download em CSV.\n"
            "4. PISA versus contexto. Relação entre desempenho educacional e dois "
            "tipos de variáveis estruturais: qualidade institucional (Eficácia Governamental "
            "e Controle de Corrupção do WGI) e desigualdade de renda (coeficiente de Gini "
            "do Banco Mundial).\n\n"
            "Todos os dados podem ser baixados em CSV diretamente no painel."
        ),
        "about_refs": "Referências",
        "about_refs_md": (
            "- Tang, N., Wu, E., & Li, G. (2019). *Towards Democratizing Relational Data "
            "Visualization*. SIGMOD '19, ACM. https://doi.org/10.1145/3299869.3314029\n"
            "- Silva, F. C. C. (2019). Visualização de dados: passado, presente e futuro. "
            "*Liinc em Revista*, 15(2), 205–223. https://doi.org/10.18617/liinc.v15i2.4812\n"
            "- Kaufmann, D., & Kraay, A. (2024). *Worldwide Governance Indicators — 2024 "
            "Methodology Update*. World Bank.\n"
            "- OECD (2023). *PISA 2022 Results (Volume I): The State of Learning and Equity in "
            "Education*. OECD Publishing. https://doi.org/10.1787/53f23881-en\n"
            "- UNDP (2024). *Human Development Report 2023/24*. United Nations Development "
            "Programme."
        ),
    },
    "en": {
        "page_title": "Wealth, Education & PISA — Interactive Visualisation",
        "app_title": "Wealth, Education and PISA",
        "app_subtitle": (
            "Interactive dashboard that crosses GDP per capita (PPP, constant 2021 USD), "
            "mean years of schooling, PISA scores and World Bank governance indicators. "
            "The aim is to make visible, in a few clicks, relationships that usually require "
            "hours in spreadsheets, democratising access to data on education and development."
        ),
        "ui_language": "Language",
        "ui_theme": "Theme",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "filters": "Filters",
        "country_group": "Country group",
        "group_all": "All countries",
        "view_options": "View options",
        "highlight_label": "Highlight countries (optional)",
        "highlight_help": "Selected countries appear in saturated colour; others are dimmed.",
        "data_sources": "Data sources",
        "data_sources_md": (
            "- GDP per capita PPP, constant 2021 USD. World Bank `NY.GDP.PCAP.PP.KD`. "
            "https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.KD\n"
            "- Population. World Bank `SP.POP.TOTL`. "
            "https://data.worldbank.org/indicator/SP.POP.TOTL\n"
            "- Mean years of schooling. UNDP HDR, indicator `mys`. "
            "https://hdr.undp.org/data-center/documentation-and-downloads\n"
            "- PISA scores. OECD and WB Education Statistics. "
            "https://www.oecd.org/pisa/\n"
            "- Government Effectiveness (WGI). World Bank. "
            "https://www.worldbank.org/en/publication/worldwide-governance-indicators\n"
            "- Control of Corruption (WGI). World Bank. "
            "https://www.worldbank.org/en/publication/worldwide-governance-indicators\n"
            "- Gini index (income). World Bank `SI.POV.GINI`. "
            "https://data.worldbank.org/indicator/SI.POV.GINI"
        ),
        "author": "Author",
        "tab_mys": "GDP × Schooling",
        "tab_pisa": "GDP × PISA",
        "tab_map": "Map",
        "tab_gov": "PISA × Context",
        "tab_about": "About",
        "subtitle_mys": "GDP per capita versus mean years of schooling. {group}",
        "subtitle_pisa": "GDP per capita versus PISA score. {group}",
        "subtitle_map": "Geographic distribution of the dashboard's indicators. {group}",
        "subtitle_gov": "PISA score versus institutional quality and income-inequality indicators. {group}",
        "panel_pisa_note": (
            "Shown as the cross-section of the latest PISA wave (2022, 81 countries). "
            "Since 38 of the 84 countries joined PISA only in 2022, a continuous animation "
            "would be misleading. The trends panel covers only countries with three or more "
            "assessments."
        ),
        "panel_pisa_trend_title": "Country trajectories (three or more assessments)",
        "panel_pisa_trend_note": (
            "{n} countries in the selected group have three or more PISA assessments. "
            "Each line connects actual waves with no interpolation."
        ),
        "no_data_warning": "No data available for {metric} within {group}.",
        "m_countries": "Countries in view",
        "m_years": "Years of data",
        "m_median_gdp": "Median GDP per capita ({year})",
        "m_median_y": "Median {metric} ({year})",
        "x_label": "GDP per capita (USD PPP, constant 2021, log scale)",
        "x_label_short": "GDP per capita (USD PPP, constant 2021)",
        "y_mys": "Mean years of schooling",
        "y_pisa": "PISA score",
        "year": "Year",
        "country": "Country",
        "population": "Population",
        "footnote_bubble": "Bubble size scales with total population. X-axis is logarithmic.",
        "download_csv": "Download data (CSV)",
        "gov_description": (
            "Each point is a country. The X-axis shows a context indicator. You can pick "
            "between two World Bank institutional-quality measures — Government "
            "Effectiveness and Control of Corruption — or the income Gini index, which "
            "measures inequality. The first two range from about −2.5 to +2.5: higher "
            "values mean better-perceived institutional quality. The Gini ranges from 0 to "
            "100: higher values mean greater inequality. The Y-axis shows the average PISA "
            "2022 score. World Bank Control of Corruption is widely used as a free public "
            "alternative to Transparency International's corruption perceptions index."
        ),
        "map_description": (
            "The indicators from the previous tabs spread over the globe. Reading them "
            "geographically does not replace the crossings, but it exposes regional clusters "
            "that a scatter plot scrambles."
        ),
        "map_layer": "Layer",
        "map_l_gdp": "GDP per capita",
        "map_l_mys": "Mean years of schooling",
        "map_l_pisa": "PISA score",
        "map_projection": "Projection",
        "map_globe": "3D globe",
        "map_flat": "Flat map",
        "map_rotation": "Spin the globe (longitude)",
        "map_log": "Logarithmic colour scale",
        "map_pisa_wave": "Layer pinned to the latest PISA wave ({year}).",
        "map_footnote": (
            "Countries in grey have no observation for the chosen layer and year. Missing "
            "data is not zero. A map also colours area, not population. Russia, Canada and "
            "Australia take up much space with few inhabitants, while small populous "
            "countries nearly vanish. For a population-weighted reading, use the bubbles in "
            "the first two tabs."
        ),
        "map_no_data": "No data available for {metric} within {group}.",
        "map_code": "Chart source code",
        "map_code_note": (
            "The whole dashboard is free software. This is the snippet that produces the map "
            "above, ready to paste into a script with pandas and plotly."
        ),
        "gov_indicator": "Context indicator",
        "gov_ge": "Government Effectiveness (WGI)",
        "gov_cc": "Control of Corruption (WGI)",
        "gov_gini": "Gini index (income)",
        "gov_year": "Reference year",
        "gov_correlation": "Correlation (group)",
        "gov_correlation_global": "Correlation (full sample)",
        "gov_correlation_global_help": "Computed over every country with PISA 2022 and the selected indicator ({n} countries). Use it as a reference against the value for the filtered group.",
        "gov_axis_ge": "Government Effectiveness (≈ −2.5 to +2.5)",
        "gov_axis_cc": "Control of Corruption (≈ −2.5 to +2.5)",
        "gov_axis_gini": "Gini index (0–100, higher = more unequal)",
        "gov_n_countries": "{n} countries (PISA 2022 + indicator)",
        "ols_fit": "OLS fit",
        "about_md": (
            "This dashboard is an exercise in democratising data on education and economic "
            "development. It is built end-to-end in Python with Streamlit and Plotly, drawing "
            "only on free public sources:\n\n"
            "1. World Bank Open Data (GDP, population, governance).\n"
            "2. UNDP Human Development Report (mean years of schooling).\n"
            "3. OECD Programme for International Student Assessment (PISA 2022).\n\n"
            "The goal is not to estimate a causal relationship between wealth, governance and "
            "learning. That is a hard problem requiring sub-national data and identification "
            "designs stronger than cross-country regressions allow. The goal is to give a "
            "non-specialist reader a visual, interactive entry point to these data, in line "
            "with the literature on democratic data visualisation (Tang, Wu and Li, 2019; "
            "Silva, 2019).\n\n"
            "Each tab presents a single elementary reading of the data:\n\n"
            "1. GDP versus mean years of schooling. Historical animation from 1990 to 2024, "
            "with bubbles scaled to total population.\n"
            "2. GDP versus PISA score. 2022 cross-section and trajectories of countries with "
            "longitudinal coverage (three or more assessments).\n"
            "3. Map. The same indicators spread geographically, on a flat map or a globe, "
            "with the group filter, country highlighting and CSV download.\n"
            "4. PISA versus context. Relationship between educational performance and two "
            "kinds of structural variables: institutional quality (WGI Government "
            "Effectiveness and Control of Corruption) and income inequality (World Bank "
            "Gini index).\n\n"
            "All data can be downloaded as CSV directly from the dashboard."
        ),
        "about_refs": "References",
        "about_refs_md": (
            "- Tang, N., Wu, E., & Li, G. (2019). *Towards Democratizing Relational Data "
            "Visualization*. SIGMOD '19, ACM. https://doi.org/10.1145/3299869.3314029\n"
            "- Silva, F. C. C. (2019). Visualização de dados: passado, presente e futuro. "
            "*Liinc em Revista*, 15(2), 205–223. https://doi.org/10.18617/liinc.v15i2.4812\n"
            "- Kaufmann, D., & Kraay, A. (2024). *Worldwide Governance Indicators — 2024 "
            "Methodology Update*. World Bank.\n"
            "- OECD (2023). *PISA 2022 Results (Volume I): The State of Learning and Equity in "
            "Education*. OECD Publishing. https://doi.org/10.1787/53f23881-en\n"
            "- UNDP (2024). *Human Development Report 2023/24*. United Nations Development "
            "Programme."
        ),
    },
}


# ============================================================
# Themes
# ============================================================

THEMES = {
    "dark": {
        "bg": "#0E1117",
        "secondary_bg": "#1B1E27",
        "text": "#FAFAFA",
        "muted": "rgba(200,200,200,0.85)",
        "border": "rgba(255,255,255,0.06)",
        "plotly": "plotly_dark",
        "diverging": ["#C73E1D", "#F4F1DE", "#2E86AB"],
        "geo_land": "#2A2F3A",
        "geo_ocean": "#11151C",
        "geo_coast": "rgba(255,255,255,0.25)",
        "geo_country_line": "rgba(255,255,255,0.18)",
        "fit_line": "#A0A0A0",
        "zero_line": "#FAFAFA",
        "table_header_bg": "#1B1E27",
        "input_bg": "rgba(255,255,255,0.04)",
        "code_bg": "rgba(46,134,171,0.18)",
        "code_color": "#7FC4DC",
        "popover_hover": "rgba(46,134,171,0.22)",
    },
    "light": {
        "bg": "#FFFFFF",
        "secondary_bg": "#F4F6FA",
        "text": "#0E1117",
        "muted": "rgba(60,60,60,0.85)",
        "border": "rgba(0,0,0,0.06)",
        "plotly": "plotly_white",
        "diverging": ["#B2182B", "#E0E0E0", "#2166AC"],
        "geo_land": "#E9ECF2",
        "geo_ocean": "#F7F9FC",
        "geo_coast": "rgba(0,0,0,0.25)",
        "geo_country_line": "rgba(0,0,0,0.18)",
        "fit_line": "#555555",
        "zero_line": "#262730",
        "table_header_bg": "#E8EAEF",
        "input_bg": "rgba(0,0,0,0.03)",
        "code_bg": "rgba(46,134,171,0.10)",
        "code_color": "#1F5C77",
        "popover_hover": "rgba(46,134,171,0.12)",
    },
}


# ============================================================
# Helpers
# ============================================================

def t(key, **kwargs):
    lang = st.session_state.get("lang", "pt")
    s = I18N.get(lang, I18N["pt"]).get(key)
    if s is None:
        s = I18N["en"].get(key, key)
    return s.format(**kwargs) if kwargs else s


def get_theme():
    return THEMES[st.session_state.get("theme", "dark")]


def init_state():
    qp = st.query_params
    if "lang" not in st.session_state:
        st.session_state.lang = qp.get("lang") if qp.get("lang") in ("pt", "en") else "pt"
    if "theme" not in st.session_state:
        st.session_state.theme = qp.get("theme") if qp.get("theme") in ("dark", "light") else "light"


def localised_groups():
    if st.session_state.get("lang", "pt") == "pt":
        return {GROUP_LABELS_PT.get(k, k): v for k, v in GROUPS_BASE.items()}
    return dict(GROUPS_BASE)


def _mtime(*paths):
    return tuple(os.path.getmtime(p) if os.path.exists(p) else 0 for p in paths)


# ============================================================
# Data loading (cached)
# ============================================================

@st.cache_data(show_spinner=False)
def load_panel(_mtime_key):
    fixed = ["Country Code", "Country Name"]
    years = [str(y) for y in range(1990, 2025)]

    df_gdp = pd.read_csv(f"{DATA_DIR}/API_NY.GDP.PCAP.PP.KD.csv", skiprows=4)
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
    df_edu = df_edu[(df_edu["year"] >= 1990) & (df_edu["year"] <= 2024)]
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


def _load_wgi_one(path: str, value_col: str) -> pd.DataFrame:
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        return pd.DataFrame(columns=["geo", "year", value_col])
    rows = []
    for r in payload[1]:
        iso = r.get("countryiso3code") or ""
        if len(iso) != 3:
            continue
        if r.get("value") is None:
            continue
        rows.append({"geo": iso.upper(), "year": int(r["date"]), value_col: float(r["value"])})
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def load_governance(_mtime_key):
    """Country-level WGI panel and a per-country latest cross-section."""
    ge = _load_wgi_one(f"{DATA_DIR}/_wb_wgi_ge.json", "gov_eff")
    cc = _load_wgi_one(f"{DATA_DIR}/_wb_wgi_cc.json", "control_corruption")
    panel = ge.merge(cc, on=["geo", "year"], how="outer").sort_values(["geo", "year"])

    latest = panel.dropna(subset=["gov_eff", "control_corruption"], how="all")
    latest = latest.sort_values("year").groupby("geo", as_index=False).last()
    latest = latest.rename(columns={"year": "wgi_year"})
    return panel, latest


@st.cache_data(show_spinner=False)
def load_gini(_mtime_key):
    """World Bank Gini index. Reported irregularly per country, so we keep the
    latest non-null observation per country within the fetched window."""
    path = f"{DATA_DIR}/_wb_gini.json"
    if not os.path.exists(path):
        return pd.DataFrame(columns=["geo", "gini", "gini_year"])
    raw = _load_wgi_one(path, "gini")
    if raw.empty:
        return pd.DataFrame(columns=["geo", "gini", "gini_year"])
    latest = raw.dropna(subset=["gini"]).sort_values("year").groupby("geo", as_index=False).last()
    return latest.rename(columns={"year": "gini_year"})


# ============================================================
# Page setup
# ============================================================

init_state()

st.set_page_config(
    page_title=t("page_title"),
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

T = get_theme()
TEMPLATE = T["plotly"]
DIVERGING = T["diverging"]


def show_chart(fig, **kwargs):
    """Render a plotly figure with transparent backgrounds so the page theme shows through.

    Charts inside st.tabs do not always get a correct width on the first paint
    (Plotly captures the width of a hidden, zero-sized container). Forcing
    autosize and Plotly's responsive config makes the chart re-measure on
    every tab switch, which keeps the layout from collapsing.
    """
    fig.update_layout(
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=T["text"]),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(color=T["text"]),
            title=dict(font=dict(color=T["text"])),
        ),
        xaxis=dict(
            gridcolor=T["border"], zerolinecolor=T["border"],
            tickfont=dict(color=T["text"]), title=dict(font=dict(color=T["text"])),
        ),
        yaxis=dict(
            gridcolor=T["border"], zerolinecolor=T["border"],
            tickfont=dict(color=T["text"]), title=dict(font=dict(color=T["text"])),
        ),
        coloraxis=dict(colorbar=dict(tickfont=dict(color=T["text"]),
                                       title=dict(font=dict(color=T["text"])))),
    )
    config = {"responsive": True, **kwargs.pop("config", {})}
    st.plotly_chart(fig, config=config, **kwargs)


def style_geo(fig, *, projection="natural earth", rotation_lon=0, height=620):
    """Apply the page theme to a geographic figure.

    Choropleths need land, ocean and coastline colours that plotly templates do
    not set, otherwise the map keeps plotly's own palette and clashes with the
    surrounding page in both themes.
    """
    fig.update_geos(
        projection_type=projection,
        projection_rotation=dict(lon=rotation_lon, lat=0, roll=0),
        showland=True, landcolor=T["geo_land"],
        showocean=True, oceancolor=T["geo_ocean"], lakecolor=T["geo_ocean"],
        showcoastlines=True, coastlinecolor=T["geo_coast"], coastlinewidth=0.5,
        showcountries=True, countrycolor=T["geo_country_line"],
        showframe=False,
        bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=10, b=0))
    return fig


def log_tick_values(log_values):
    """Colour-bar ticks at 1, 2 and 5 times each power of ten in range.

    Whole decades alone leave a narrow range such as the G20, which spans a
    single decade of GDP per capita, with one labelled tick and an unreadable
    colour bar. Takes and returns values already in log10 space.
    """
    low, high = float(np.min(log_values)), float(np.max(log_values))
    ticks = []
    for exponent in range(int(np.floor(low)), int(np.ceil(high)) + 1):
        for mantissa in (1, 2, 5):
            candidate = exponent + np.log10(mantissa)
            if low - 1e-9 <= candidate <= high + 1e-9:
                ticks.append(candidate)
    return ticks if len(ticks) >= 2 else [low, high]


# ============================================================
# CSS injection (theme-aware)
# ============================================================

st.markdown(
    f"""
    <style>
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .main, .main .block-container {{
        background-color: {T['bg']};
    }}
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {{
        background-color: {T['secondary_bg']};
        border-right: 1px solid {T['border']};
    }}
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }}

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 0.55rem; }}
    [data-testid="stSidebar"] hr {{ display: none; }}
    [data-testid="stSidebar"] .stRadio > label,
    [data-testid="stSidebar"] .stSelectbox > label,
    [data-testid="stSidebar"] .stMultiSelect > label {{
        font-size: 0.8rem;
        opacity: 0.78;
        margin-bottom: 0.15rem;
    }}

    .stApp, .stApp p, .stApp span, .stApp li,
    .stApp label, .stApp .stMarkdown,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    [data-testid="stSidebar"] *, .stApp [data-baseweb="tab"] span,
    .stApp .stRadio label, .stApp .stCheckbox label,
    .stApp .stSelectbox label, .stApp .stMultiSelect label,
    .stApp .stSlider label, .stApp .stTextInput label,
    .stApp .stDownloadButton button, .stApp .stButton button {{
        color: {T['text']} !important;
    }}
    .stApp h1, .stApp h2, .stApp h3 {{ letter-spacing: -0.01em; }}

    .stApp code, [data-testid="stSidebar"] code {{
        background: {T['code_bg']} !important;
        color: {T['code_color']} !important;
        border: none !important;
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 0.86em;
    }}
    .stApp pre {{ background: {T['secondary_bg']} !important; }}
    .stApp pre code {{ background: transparent !important; }}

    /* Bare source URLs are longer than the sidebar is wide and have no spaces
       to break on, so without this they are simply clipped at the edge. */
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] code,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] p {{
        overflow-wrap: anywhere;
        word-break: break-word;
    }}

    [data-testid="stMetric"] {{
        background: {T['secondary_bg']};
        border: 1px solid {T['border']};
        padding: 14px 18px;
        border-radius: 10px;
    }}
    [data-testid="stMetricValue"] {{ color: {T['text']} !important; }}
    [data-testid="stMetricLabel"] {{ color: {T['text']} !important; opacity: 0.85; }}
    [data-testid="stMetricDelta"] {{ color: {T['text']} !important; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background: {T['secondary_bg']};
        border: 1px solid {T['border']};
        border-radius: 8px;
        padding: 8px 18px;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        border-color: #2E86AB;
    }}

    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {{
        background-color: {T['input_bg']} !important;
        color: {T['text']} !important;
        border-color: transparent !important;
    }}
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {{
        border: none !important;
    }}

    [data-baseweb="popover"] {{
        background: {T['secondary_bg']} !important;
        border: 1px solid {T['border']} !important;
    }}
    [data-baseweb="popover"] [role="listbox"],
    [data-baseweb="popover"] ul {{
        background: {T['secondary_bg']} !important;
    }}
    [data-baseweb="popover"] [role="option"],
    [data-baseweb="popover"] li {{
        background: {T['secondary_bg']} !important;
        color: {T['text']} !important;
    }}
    [data-baseweb="popover"] [role="option"][aria-selected="true"],
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] li:hover {{
        background: {T['popover_hover']} !important;
    }}

    .stDownloadButton button, .stButton button {{
        background: {T['secondary_bg']};
        border: 1px solid {T['border']};
        color: {T['text']};
    }}
    .stDownloadButton button:hover, .stButton button:hover {{
        border-color: #2E86AB;
    }}

    [data-testid="stDataFrame"] {{
        background: {T['bg']};
    }}
    .stApp table th {{
        background: {T['table_header_bg']} !important;
        color: {T['text']} !important;
    }}
    .stApp table td {{ color: {T['text']} !important; }}

    [data-testid="stExpander"] {{
        border: 1px solid {T['border']} !important;
        background: transparent !important;
    }}
    [data-testid="stExpander"] summary {{ color: {T['text']} !important; }}

    .footnote {{ color: {T['muted']}; font-size: 0.85rem; }}
    hr {{ border-color: {T['border']}; }}

    [data-testid="stNotification"] * {{ color: {T['text']} !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Load data
# ============================================================

try:
    panel_files = (
        f"{DATA_DIR}/API_NY.GDP.PCAP.PP.KD.csv",
        f"{DATA_DIR}/API_SP.POP.TOTL_DS2_en_csv_v2_246068.csv",
        f"{DATA_DIR}/hdr-data.xlsx",
        f"{DATA_DIR}/pisa_master_dataset.csv",
    )
    panel = load_panel(_mtime(*panel_files))
    wgi_files = (f"{DATA_DIR}/_wb_wgi_ge.json", f"{DATA_DIR}/_wb_wgi_cc.json")
    wgi_panel, wgi_latest = load_governance(_mtime(*wgi_files))
    gini_latest = load_gini(_mtime(f"{DATA_DIR}/_wb_gini.json"))
except Exception as exc:
    st.error(f"Data loading failed: {exc}")
    st.stop()

PISA_YEARS = sorted({int(y) for y in panel.dropna(subset=["pisa_score"])["year"].unique()})
if not PISA_YEARS:
    PISA_YEARS = PISA_YEARS_FALLBACK


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    col_lang, col_theme = st.columns(2)
    with col_lang:
        lang_choice = st.radio(
            t("ui_language"),
            options=["pt", "en"],
            format_func=lambda x: {"pt": "PT", "en": "EN"}[x],
            index=["pt", "en"].index(st.session_state.lang),
            horizontal=True,
            key="ui_lang_radio",
        )
    with col_theme:
        theme_choice = st.radio(
            t("ui_theme"),
            options=["light", "dark"],
            format_func=lambda x: t(f"theme_{x}"),
            index=["light", "dark"].index(st.session_state.theme),
            horizontal=True,
            key="ui_theme_radio",
        )

    if lang_choice != st.session_state.lang or theme_choice != st.session_state.theme:
        st.session_state.lang = lang_choice
        st.session_state.theme = theme_choice
        st.query_params["lang"] = lang_choice
        st.query_params["theme"] = theme_choice
        st.rerun()

    GROUPS_LOC = localised_groups()
    GROUPS_LOC[t("group_all")] = sorted(panel["geo"].dropna().unique().tolist())
    group_keys = list(GROUPS_LOC.keys())

    qp_group = st.query_params.get("group", group_keys[0])
    if qp_group not in group_keys:
        qp_group = group_keys[0]

    selected_group = st.selectbox(
        t("country_group"),
        options=group_keys,
        index=group_keys.index(qp_group),
        key="group_select",
    )
    if st.query_params.get("group") != selected_group:
        st.query_params["group"] = selected_group

    country_list = GROUPS_LOC[selected_group]

    available_for_highlight = sorted(
        panel.loc[panel["geo"].isin(country_list), "name"].dropna().unique().tolist()
    )
    highlight_names = st.multiselect(
        t("highlight_label"),
        options=available_for_highlight,
        help=t("highlight_help"),
    )

    with st.expander(t("data_sources"), expanded=False):
        st.markdown(t("data_sources_md"))

    st.markdown(
        f"<div class='footnote' style='margin-top: 0.6rem;'>"
        f"<b>{t('author')}</b> — Thiago Alcebíades Rodrigues<br>"
        "<a href='mailto:thiago.alcebiades@unifesp.br'>thiago.alcebiades@unifesp.br</a> · "
        "<a href='https://www.linkedin.com/in/thiago-alcebiades-rodrigues-95446621b/'>LinkedIn</a>"
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# Header
# ============================================================

st.title(t("app_title"))
st.markdown(t("app_subtitle"))
st.divider()


# ============================================================
# Shared state for the visualisation tabs
# ============================================================

bubble_line = "rgba(0,0,0,0.55)" if st.session_state.theme == "light" else "rgba(255,255,255,0.55)"
highlight_set = set(highlight_names) if highlight_names else set()


def _style_bubbles(fig, hover_template):
    for trace in fig.data:
        if hasattr(trace, "marker") and trace.marker is not None:
            trace.marker.line.color = bubble_line
            trace.marker.line.width = 0.7
        trace.hovertemplate = hover_template
        if highlight_set:
            trace.opacity = 1.0 if trace.name in highlight_set else 0.18
        else:
            trace.opacity = 0.85


def _apply_highlight(fig):
    if not highlight_set:
        return
    for trace in fig.data:
        trace.opacity = 1.0 if trace.name in highlight_set else 0.18


# ============================================================
# Tabs
# ============================================================

tab_mys, tab_pisa, tab_map, tab_gov, tab_about = st.tabs([
    t("tab_mys"),
    t("tab_pisa"),
    t("tab_map"),
    t("tab_gov"),
    t("tab_about"),
])


# ------------------------------------------------------------
# Tab: GDP × Mean Years of Schooling (animated bubble)
# ------------------------------------------------------------

with tab_mys:
    st.subheader(t("subtitle_mys", group=selected_group))

    view = panel[panel["geo"].isin(country_list)].dropna(
        subset=["gdp_per_capita", "years_schooling"]
    ).copy()
    view["population_for_size"] = view["population"].fillna(1)

    if view.empty:
        st.warning(t("no_data_warning", metric=t("y_mys"), group=selected_group))
    else:
        latest_year = int(view["year"].max())
        first_year = int(view["year"].min())
        latest = view[view["year"] == latest_year]
        years_text = f"{first_year}" if first_year == latest_year else f"{first_year} – {latest_year}"

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t("m_countries"), f"{view['geo'].nunique()}")
        c2.metric(t("m_years"), years_text)
        c3.metric(
            t("m_median_gdp", year=latest_year),
            f"${latest['gdp_per_capita'].median():,.0f}" if not latest.empty else "—",
        )
        c4.metric(
            t("m_median_y", metric=t("y_mys"), year=latest_year),
            f"{latest['years_schooling'].median():.1f}" if not latest.empty else "—",
        )

        min_x = view["gdp_per_capita"].min() * 0.8
        max_x = view["gdp_per_capita"].max() * 1.2
        min_y = view["years_schooling"].min() * 0.95
        max_y = view["years_schooling"].max() * 1.05

        hover_template = (
            "<b>%{hovertext}</b><br>"
            f"{t('x_label_short')}: %{{customdata[0]:,.0f}}<br>"
            f"{t('population')}: %{{customdata[2]}}<br>"
            + t("y_mys") + ": %{customdata[3]:.2f}<extra></extra>"
        )

        fig = px.scatter(
            view,
            x="gdp_per_capita", y="years_schooling",
            animation_frame="year", animation_group="name",
            size="population_for_size", color="name", hover_name="name",
            custom_data=["gdp_per_capita", "population", "population_str", "years_schooling"],
            log_x=True, size_max=55,
            range_x=[min_x, max_x], range_y=[min_y, max_y],
            labels={
                "gdp_per_capita": t("x_label"),
                "years_schooling": t("y_mys"),
                "name": t("country"),
                "year": t("year"),
            },
            template=TEMPLATE,
        )
        _style_bubbles(fig, hover_template)
        # Per-frame styling is only needed for highlight (which changes opacity
        # mid-animation). Base trace styling carries through otherwise — skipping
        # this loop is a large win for groups with hundreds of countries.
        if highlight_set:
            for frame in fig.frames or []:
                for trace in frame.data:
                    trace.opacity = 1.0 if trace.name in highlight_set else 0.18

        n_countries = view["geo"].nunique()
        fig.update_layout(
            height=620,
            legend_title_text=t("country"),
            showlegend=n_countries <= 30,
            transition=dict(duration=400, easing="cubic-in-out"),
        )
        if fig.layout.updatemenus:
            for menu in fig.layout.updatemenus:
                for button in menu.buttons:
                    if button.label == "▶":
                        button.args[1]["frame"]["duration"] = 200
                        button.args[1]["transition"]["duration"] = 200
        show_chart(fig, width="stretch", key=f"chart_mys_{selected_group}")

        st.markdown(
            f"<span class='footnote'>{t('footnote_bubble')}</span>",
            unsafe_allow_html=True,
        )

        view_csv = view.drop(columns=["population_for_size"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            t("download_csv"),
            data=view_csv,
            file_name=f"gdp_schooling_{selected_group}.csv",
            mime="text/csv",
        )


# ------------------------------------------------------------
# Tab: GDP × PISA (cross-section + trend)
# ------------------------------------------------------------

with tab_pisa:
    st.subheader(t("subtitle_pisa", group=selected_group))

    pisa_full = panel[panel["geo"].isin(country_list)].dropna(
        subset=["gdp_per_capita", "pisa_score"]
    ).copy()
    pisa_full["population_for_size"] = pisa_full["population"].fillna(1)

    if pisa_full.empty:
        st.warning(t("no_data_warning", metric=t("y_pisa"), group=selected_group))
    else:
        latest_pisa_year = int(pisa_full["year"].max())
        view = pisa_full[pisa_full["year"] == latest_pisa_year].copy()

        st.markdown(
            f"<span class='footnote'>{t('panel_pisa_note')}</span>",
            unsafe_allow_html=True,
        )

        first_year = int(pisa_full["year"].min())
        years_text = (
            f"{first_year}" if first_year == latest_pisa_year
            else f"{first_year} – {latest_pisa_year}"
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t("m_countries"), f"{view['geo'].nunique()}")
        c2.metric(t("m_years"), years_text)
        c3.metric(
            t("m_median_gdp", year=latest_pisa_year),
            f"${view['gdp_per_capita'].median():,.0f}" if not view.empty else "—",
        )
        c4.metric(
            t("m_median_y", metric=t("y_pisa"), year=latest_pisa_year),
            f"{view['pisa_score'].median():.0f}" if not view.empty else "—",
        )

        min_x = view["gdp_per_capita"].min() * 0.8
        max_x = view["gdp_per_capita"].max() * 1.2
        min_y = view["pisa_score"].min() * 0.95
        max_y = view["pisa_score"].max() * 1.05

        hover_template = (
            "<b>%{hovertext}</b><br>"
            f"{t('x_label_short')}: %{{customdata[0]:,.0f}}<br>"
            f"{t('population')}: %{{customdata[2]}}<br>"
            + t("y_pisa") + ": %{customdata[3]:.0f}<extra></extra>"
        )

        fig = px.scatter(
            view,
            x="gdp_per_capita", y="pisa_score",
            size="population_for_size", color="name", hover_name="name",
            custom_data=["gdp_per_capita", "population", "population_str", "pisa_score"],
            log_x=True, size_max=55,
            range_x=[min_x, max_x], range_y=[min_y, max_y],
            labels={
                "gdp_per_capita": t("x_label"),
                "pisa_score": t("y_pisa"),
                "name": t("country"),
            },
            template=TEMPLATE,
        )
        _style_bubbles(fig, hover_template)
        fig.update_layout(
            height=620,
            legend_title_text=t("country"),
            showlegend=view["geo"].nunique() <= 30,
        )
        show_chart(fig, width="stretch", key=f"chart_pisa_{selected_group}")

        # Historical trend chart for countries with ≥ 3 PISA waves
        wave_counts = pisa_full.groupby("geo")["year"].nunique()
        trend_geos = wave_counts[wave_counts >= 3].index
        trend_df = pisa_full[pisa_full["geo"].isin(trend_geos)].copy()
        if not trend_df.empty:
            st.markdown(f"#### {t('panel_pisa_trend_title')}")
            trend_fig = px.line(
                trend_df.sort_values(["name", "year"]),
                x="year", y="pisa_score", color="name",
                markers=True, hover_name="name",
                labels={"year": t("year"), "pisa_score": t("y_pisa"), "name": t("country")},
                template=TEMPLATE,
            )
            _apply_highlight(trend_fig)
            trend_fig.update_layout(
                height=440,
                legend_title_text=t("country"),
                showlegend=trend_df["geo"].nunique() <= 30,
            )
            show_chart(trend_fig, width="stretch", key=f"chart_pisa_trend_{selected_group}")
            st.markdown(
                f"<span class='footnote'>{t('panel_pisa_trend_note', n=len(trend_geos))}</span>",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"<span class='footnote'>{t('footnote_bubble')}</span>",
            unsafe_allow_html=True,
        )

        view_csv = view.drop(columns=["population_for_size"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            t("download_csv"),
            data=view_csv,
            file_name=f"gdp_pisa_{selected_group}.csv",
            mime="text/csv",
        )


# ------------------------------------------------------------
# Tab: Map
# ------------------------------------------------------------

with tab_map:
    st.subheader(t("subtitle_map", group=selected_group))
    st.markdown(t("map_description"))

    # `num` is the d3 format used in the hover and `prefix` the unit shown on the
    # colour bar. Counts of people carry neither a currency sign nor decimals.
    LAYERS = {
        t("map_l_gdp"): {"col": "gdp_per_capita", "log": True, "prefix": "$", "num": ",.0f"},
        t("map_l_mys"): {"col": "years_schooling", "log": False, "prefix": "", "num": ".1f"},
        t("map_l_pisa"): {"col": "pisa_score", "log": False, "prefix": "", "num": ".0f"},
    }
    layer_choice = st.radio(
        t("map_layer"), options=list(LAYERS), horizontal=True, key="map_layer_radio"
    )
    layer = LAYERS[layer_choice]

    col_proj, col_year = st.columns([1, 2])
    projection_choice = col_proj.radio(
        t("map_projection"),
        options=[t("map_flat"), t("map_globe")],
        horizontal=True,
        key="map_projection_radio",
    )
    is_globe = projection_choice == t("map_globe")

    # PISA is only measured on wave years, so that layer is pinned to the latest
    # wave instead of offering a year slider that would mostly land on gaps.
    if layer["col"] == "pisa_score":
        map_year = int(panel.dropna(subset=["pisa_score"])["year"].max())
        col_year.markdown(
            f"<span class='footnote'>{t('map_pisa_wave', year=map_year)}</span>",
            unsafe_allow_html=True,
        )
    else:
        years_available = sorted(
            panel.dropna(subset=[layer["col"]])["year"].unique().astype(int)
        )
        map_year = col_year.select_slider(
            t("year"), options=years_available, value=years_available[-1], key="map_year_slider"
        )

    rotation_lon = (
        st.slider(t("map_rotation"), -180, 180, -20, 5, key="map_rotation_slider")
        if is_globe else 0
    )

    map_view = panel[
        (panel["year"] == map_year) & (panel["geo"].isin(country_list))
    ].dropna(subset=[layer["col"]]).copy()

    if map_view.empty:
        st.warning(t("map_no_data", metric=layer_choice, group=selected_group))
    else:
        map_view["color_val"] = (
            np.log10(map_view[layer["col"]].clip(lower=1))
            if layer["log"] else map_view[layer["col"]]
        )

        fig = px.choropleth(
            map_view,
            locations="geo",
            locationmode="ISO-3",
            color="color_val",
            hover_name="name",
            custom_data=[layer["col"]],
            color_continuous_scale="Viridis",
            template=TEMPLATE,
        )
        fig.update_traces(
            marker_line_color=T["geo_country_line"],
            marker_line_width=0.3,
            hovertemplate=(
                "<b>%{hovertext}</b><br>" + layer_choice + ": "
                + layer["prefix"] + "%{customdata[0]:" + layer["num"] + "}<extra></extra>"
            ),
        )

        # A choropleth has a single trace, so the shared highlight mechanism
        # cannot dim it. Highlighted countries get a thick outline instead.
        if highlight_set:
            highlighted = map_view[map_view["name"].isin(highlight_set)]
            if not highlighted.empty:
                fig.add_trace(go.Choropleth(
                    locations=highlighted["geo"],
                    locationmode="ISO-3",
                    z=[0] * len(highlighted),
                    colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                    showscale=False,
                    marker_line_color=T["text"],
                    marker_line_width=1.8,
                    hoverinfo="skip",
                ))

        fig.update_layout(coloraxis_colorbar=dict(
            title=dict(text=layer_choice, side="right"), thickness=14, len=0.7,
        ))
        if layer["log"]:
            ticks = log_tick_values(map_view["color_val"])
            fig.update_layout(coloraxis_colorbar=dict(
                tickvals=ticks,
                ticktext=[f"{layer['prefix']}{10 ** v:,.0f}" for v in ticks],
            ))

        style_geo(
            fig,
            projection="orthographic" if is_globe else "natural earth",
            rotation_lon=rotation_lon,
        )
        show_chart(
            fig,
            width="stretch",
            key=f"chart_map_{layer['col']}_{map_year}_{selected_group}_{is_globe}",
        )

        st.markdown(
            f"<span class='footnote'>{t('map_footnote')}</span>",
            unsafe_allow_html=True,
        )

        map_csv = map_view.drop(columns=["color_val"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            t("download_csv"),
            data=map_csv,
            file_name=f"map_{layer['col']}_{map_year}_{selected_group}.csv",
            mime="text/csv",
        )

        with st.expander(t("map_code"), expanded=False):
            st.caption(t("map_code_note"))
            projection_name = "orthographic" if is_globe else "natural earth"
            color_line = (
                f'view["color_val"] = np.log10(view["{layer["col"]}"])\n'
                if layer["log"] else f'view["color_val"] = view["{layer["col"]}"]\n'
            )
            st.code(
                "import numpy as np\n"
                "import plotly.express as px\n\n"
                f'view = panel[panel["year"] == {map_year}].dropna(subset=["{layer["col"]}"]).copy()\n'
                + color_line
                + "\nfig = px.choropleth(\n"
                "    view,\n"
                '    locations="geo", locationmode="ISO-3",\n'
                '    color="color_val", hover_name="name",\n'
                '    color_continuous_scale="Viridis",\n'
                ")\n"
                f'fig.update_geos(projection_type="{projection_name}", showocean=True, showframe=False)\n'
                "fig.show()",
                language="python",
            )


# ------------------------------------------------------------
# Tab: PISA × Governance
# ------------------------------------------------------------

with tab_gov:
    st.subheader(t("subtitle_gov", group=selected_group))
    st.markdown(t("gov_description"))

    pisa_2022 = panel[panel["year"] == 2022][["geo", "name", "pisa_score", "population"]].dropna(
        subset=["pisa_score"]
    )
    gov_df_full = (
        pisa_2022
        .merge(wgi_latest[["geo", "wgi_year", "gov_eff", "control_corruption"]], on="geo", how="left")
        .merge(gini_latest[["geo", "gini_year", "gini"]], on="geo", how="left")
    )
    gov_df = gov_df_full[gov_df_full["geo"].isin(country_list)].copy()

    indicator_specs = {
        t("gov_ge"): {
            "col": "gov_eff", "axis": t("gov_axis_ge"), "year_col": "wgi_year",
            "hover_fmt": ":+.2f", "midpoint": 0, "show_zero_line": True,
            "color_reverse": False,
        },
        t("gov_cc"): {
            "col": "control_corruption", "axis": t("gov_axis_cc"), "year_col": "wgi_year",
            "hover_fmt": ":+.2f", "midpoint": 0, "show_zero_line": True,
            "color_reverse": False,
        },
        t("gov_gini"): {
            "col": "gini", "axis": t("gov_axis_gini"), "year_col": "gini_year",
            "hover_fmt": ":.1f", "midpoint": None, "show_zero_line": False,
            "color_reverse": True,
        },
    }
    indicator_choice = st.radio(
        t("gov_indicator"),
        options=list(indicator_specs.keys()),
        horizontal=True,
    )
    spec = indicator_specs[indicator_choice]
    x_col = spec["col"]
    x_label = spec["axis"]
    year_col = spec["year_col"]

    sub = gov_df.dropna(subset=[x_col, year_col]).copy()
    if sub.empty:
        st.warning(t("no_data_warning", metric=indicator_choice, group=selected_group))
    else:
        r = sub[x_col].corr(sub["pisa_score"])
        sub_global = gov_df_full.dropna(subset=[x_col, year_col])
        r_global = (
            sub_global[x_col].corr(sub_global["pisa_score"])
            if len(sub_global) >= 3 else float("nan")
        )
        midpoint = spec["midpoint"] if spec["midpoint"] is not None else float(sub[x_col].median())

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            t("gov_n_countries", n=len(sub)),
            f"{int(sub[year_col].max())}",
            help=t("gov_year"),
        )
        c2.metric(t("gov_correlation"), f"r = {r:+.2f}")
        c3.metric(
            t("gov_correlation_global"),
            f"r = {r_global:+.2f}" if not pd.isna(r_global) else "—",
            help=t("gov_correlation_global_help", n=len(sub_global)),
        )
        c4.metric(
            t("m_median_y", metric=t("y_pisa"), year=2022),
            f"{sub['pisa_score'].median():.0f}",
        )

        marker_opacity = (
            sub["name"].apply(lambda n: 1.0 if n in highlight_set else 0.25).tolist()
            if highlight_set else 0.85
        )

        color_scale = DIVERGING[::-1] if spec.get("color_reverse") else DIVERGING

        scatter = px.scatter(
            sub,
            x=x_col, y="pisa_score",
            text="geo",
            color=x_col,
            color_continuous_scale=color_scale,
            color_continuous_midpoint=midpoint,
            hover_data={
                "name": True,
                x_col: spec["hover_fmt"],
                "pisa_score": ":.0f",
                year_col: True,
                "geo": False,
            },
            labels={
                x_col: x_label,
                "pisa_score": t("y_pisa"),
                "name": t("country"),
                year_col: t("gov_year"),
            },
            template=TEMPLATE,
        )
        scatter.update_traces(
            textposition="top center",
            textfont=dict(size=12, color=T["text"], family="Arial"),
            marker=dict(
                size=14,
                opacity=marker_opacity,
                line=dict(color=T["text"], width=0.6),
            ),
            selector=dict(mode="markers+text"),
        )

        if len(sub) >= 5:
            xs = sub[x_col].to_numpy()
            ys = sub["pisa_score"].to_numpy()
            slope, intercept = np.polyfit(xs, ys, 1)
            x_grid = np.linspace(xs.min(), xs.max(), 80)
            scatter.add_trace(
                go.Scatter(
                    x=x_grid,
                    y=intercept + slope * x_grid,
                    mode="lines",
                    line=dict(color=T["fit_line"], dash="dash"),
                    name=t("ols_fit"),
                    showlegend=True,
                )
            )

        if spec["show_zero_line"]:
            scatter.add_vline(x=0, line_color=T["zero_line"], line_width=0.5, opacity=0.4)
        scatter.update_layout(height=580, coloraxis_showscale=False)
        show_chart(scatter, width="stretch", key=f"chart_gov_{selected_group}_{x_col}")

        export_cols = ["geo", "name", "pisa_score", x_col, year_col]
        gov_csv = sub[export_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            t("download_csv"),
            data=gov_csv,
            file_name=f"pisa_{x_col}_{selected_group}.csv",
            mime="text/csv",
        )


# ------------------------------------------------------------
# Tab: About
# ------------------------------------------------------------

with tab_about:
    st.markdown(t("about_md"))
    st.markdown(f"### {t('about_refs')}")
    st.markdown(t("about_refs_md"))
