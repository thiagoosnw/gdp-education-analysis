"""Laboratorio de mapas. Experimentos com px.choropleth e px.line_geo.

Aplicativo Streamlit separado do painel principal (`app.py`). Serve para testar
representações geográficas dos mesmos dados antes de decidir o que vale a pena
levar para o painel definitivo.

Rodar a partir da raiz do repositório:

    streamlit run lab_geo.py

Nenhum arquivo de `app.py` é modificado. Os carregadores de dados aqui são
versoes enxutas dos que existem em `app.py`. Se algum experimento for promovido
para o painel, vale extrair os carregadores para um módulo compartilhado.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_DIR = "data"

GROUPS_BASE = {
    "G20": ["ARG", "AUS", "BRA", "CAN", "CHN", "FRA", "DEU", "IND", "IDN", "ITA", "JPN", "KOR", "MEX", "RUS", "SAU", "ZAF", "TUR", "GBR", "USA", "ESP"],
    "G7": ["CAN", "FRA", "DEU", "ITA", "JPN", "GBR", "USA"],
    "BRICS+": ["BRA", "RUS", "IND", "CHN", "ZAF", "EGY", "ETH", "IRN", "ARE", "SAU"],
    "União Europeia": ["AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD", "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE"],
    "América do Sul": ["ARG", "BOL", "BRA", "CHL", "COL", "ECU", "GUY", "PRY", "PER", "SUR", "URY", "VEN"],
    "América Latina e Caribe": ["ARG", "BHS", "BRB", "BLZ", "BOL", "BRA", "CHL", "COL", "CRI", "CUB", "DOM", "ECU", "SLV", "GTM", "GUY", "HTI", "HND", "JAM", "MEX", "NIC", "PAN", "PRY", "PER", "SUR", "TTO", "URY", "VEN"],
    "Leste e Sudeste Asiático": ["CHN", "JPN", "IND", "KOR", "IDN", "THA", "MYS", "VNM", "PHL", "SGP", "BGD", "PAK", "HKG", "TWN"],
    "Lusófonos": ["BRA", "PRT", "AGO", "MOZ", "CPV", "GNB", "STP", "TLS"],
    "Tigres Asiáticos": ["KOR", "SGP", "HKG", "TWN", "MYS", "THA", "VNM", "IDN"],
    "OPEP": ["DZA", "COG", "GNQ", "GAB", "IRN", "IRQ", "KWT", "LBY", "NGA", "SAU", "ARE", "VEN"],
}

THEMES = {
    "dark": {
        "text": "#FAFAFA",
        "border": "rgba(255,255,255,0.06)",
        "plotly": "plotly_dark",
        "land": "#2A2F3A",
        "ocean": "#11151C",
        "coast": "rgba(255,255,255,0.25)",
        "country_line": "rgba(255,255,255,0.18)",
        "diverging": ["#C73E1D", "#F4F1DE", "#2E86AB"],
    },
    "light": {
        "text": "#0E1117",
        "border": "rgba(0,0,0,0.06)",
        "plotly": "plotly_white",
        "land": "#E9ECF2",
        "ocean": "#F7F9FC",
        "coast": "rgba(0,0,0,0.25)",
        "country_line": "rgba(0,0,0,0.18)",
        "diverging": ["#B2182B", "#E0E0E0", "#2166AC"],
    },
}

PROJECTIONS = {
    "Globo 3D (ortográfica)": "orthographic",
    "Natural Earth": "natural earth",
    "Robinson": "robinson",
    "Mollweide": "mollweide",
    "Equiretangular": "equirectangular",
    "Azimutal equivalente": "azimuthal equal area",
    "Winkel Tripel": "winkel tripel",
    "Kavrayskiy VII": "kavrayskiy7",
}

SEQUENTIAL_SCALES = ["Viridis", "Plasma", "Turbo", "Cividis", "Blues", "YlGnBu", "Magma"]


# ============================================================
# Carregamento de dados
# ============================================================

def _mtime(*paths):
    return tuple(os.path.getmtime(p) if os.path.exists(p) else 0 for p in paths)


@st.cache_data(show_spinner=False)
def load_panel(_key):
    fixed = ["Country Code", "Country Name"]
    years = [str(y) for y in range(1990, 2025)]

    df_gdp = pd.read_csv(f"{DATA_DIR}/API_NY.GDP.PCAP.PP.KD.csv", skiprows=4)
    df_gdp = df_gdp[[c for c in fixed + years if c in df_gdp.columns]].melt(
        id_vars=fixed, var_name="year", value_name="gdp_per_capita"
    ).rename(columns={"Country Code": "geo", "Country Name": "name"})
    df_gdp["year"] = pd.to_numeric(df_gdp["year"])
    df_gdp["geo"] = df_gdp["geo"].str.upper()

    df_pop = pd.read_csv(f"{DATA_DIR}/API_SP.POP.TOTL_DS2_en_csv_v2_246068.csv", skiprows=4)
    df_pop = df_pop[[c for c in fixed + years if c in df_pop.columns]].melt(
        id_vars=fixed, var_name="year", value_name="population"
    ).rename(columns={"Country Code": "geo", "Country Name": "name"})
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
        df_gdp.merge(df_edu, on=["geo", "year"], how="left")
        .merge(df_pop[["geo", "year", "population"]], on=["geo", "year"], how="left")
        .merge(df_pisa, on=["geo", "year"], how="left")
    )
    return panel


@st.cache_data(show_spinner=False)
def load_meta(_key):
    """Metadados por país: coordenadas da capital, região e faixa de renda.

    As coordenadas são o que torna `px.line_geo` utilizável: o choropleth só
    precisa do código ISO-3, mas qualquer camada de linhas precisa de um ponto
    por país. Gerado por `data/build_country_meta.py`.
    """
    path = f"{DATA_DIR}/country_meta.csv"
    if not os.path.exists(path):
        return pd.DataFrame(columns=["geo", "name", "region", "income", "capital", "lat", "lon"])
    meta = pd.read_csv(path)
    meta["geo"] = meta["geo"].str.upper()
    meta["region"] = meta["region"].str.strip()
    return meta


def _load_wb_json(path: str, value_col: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame(columns=["geo", "year", value_col])
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        return pd.DataFrame(columns=["geo", "year", value_col])
    rows = [
        {"geo": r["countryiso3code"].upper(), "year": int(r["date"]), value_col: float(r["value"])}
        for r in payload[1]
        if len(r.get("countryiso3code") or "") == 3 and r.get("value") is not None
    ]
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def load_context(_key):
    """Recorte transversal mais recente de governança e Gini, por país."""
    ge = _load_wb_json(f"{DATA_DIR}/_wb_wgi_ge.json", "gov_eff")
    cc = _load_wb_json(f"{DATA_DIR}/_wb_wgi_cc.json", "control_corruption")
    gini = _load_wb_json(f"{DATA_DIR}/_wb_gini.json", "gini")

    def latest(df, col):
        if df.empty:
            return pd.DataFrame(columns=["geo", col])
        return (df.dropna(subset=[col]).sort_values("year")
                  .groupby("geo", as_index=False).last()[["geo", col]])

    out = latest(ge, "gov_eff")
    for df, col in ((cc, "control_corruption"), (gini, "gini")):
        out = out.merge(latest(df, col), on="geo", how="outer")
    return out


# ============================================================
# Estado e página
# ============================================================

if "theme" not in st.session_state:
    # Acompanha o padrão do `.streamlit/config.toml`. Este rádio controla só as
    # cores dos graficos. O cromo da pagina e trocado em Menu > Settings > Appearance.
    st.session_state.theme = "light"

st.set_page_config(
    page_title="Laboratorio de mapas. PIB, Educacao e PISA",
    page_icon="🗺",
    layout="wide",
    initial_sidebar_state="expanded",
)

T = THEMES[st.session_state.theme]
TEMPLATE = T["plotly"]

panel = load_panel(_mtime(
    f"{DATA_DIR}/API_NY.GDP.PCAP.PP.KD.csv",
    f"{DATA_DIR}/API_SP.POP.TOTL_DS2_en_csv_v2_246068.csv",
    f"{DATA_DIR}/hdr-data.xlsx",
    f"{DATA_DIR}/pisa_master_dataset.csv",
))
meta = load_meta(_mtime(f"{DATA_DIR}/country_meta.csv"))
context = load_context(_mtime(
    f"{DATA_DIR}/_wb_wgi_ge.json", f"{DATA_DIR}/_wb_wgi_cc.json", f"{DATA_DIR}/_wb_gini.json"
))

# O painel do World Bank traz agregados ("World", "Euro area", ...) que não são
# países. `country_meta.csv` só contém economias, então serve de filtro.
VALID_GEOS = set(meta["geo"]) if not meta.empty else set(panel["geo"])
panel = panel[panel["geo"].isin(VALID_GEOS)].copy()


# ============================================================
# Barra lateral
# ============================================================

with st.sidebar:
    st.title("Laboratorio de mapas")
    st.caption("Experimentos com `px.choropleth` e `px.line_geo`.")

    st.session_state.theme = st.radio(
        "Tema dos mapas", ["dark", "light"],
        format_func=lambda v: "Escuro" if v == "dark" else "Claro",
        horizontal=True,
        index=0 if st.session_state.theme == "dark" else 1,
        help="Afeta apenas as cores dos gráficos. Para escurecer a página inteira, "
             "use Menu › Settings › Appearance.",
    )
    T = THEMES[st.session_state.theme]
    TEMPLATE = T["plotly"]

    st.divider()
    st.subheader("Projeção")
    proj_label = st.selectbox("Tipo de projeção", list(PROJECTIONS), index=0)
    projection = PROJECTIONS[proj_label]
    is_globe = projection in ("orthographic", "azimuthal equal area")

    rot_lon = st.slider("Rotacao da longitude", -180, 180, -30 if is_globe else 0, 5)
    rot_lat = st.slider("Rotacao da latitude", -90, 90, 15 if is_globe else 0, 5)
    show_ocean = st.checkbox("Mostrar oceano", value=True)
    show_borders = st.checkbox("Mostrar fronteiras", value=True)
    map_height = st.slider("Altura do mapa (px)", 400, 900, 640, 20)

    st.divider()
    group = st.selectbox("Grupo de países", ["Todos os países"] + list(GROUPS_BASE))
    group_geos = set(GROUPS_BASE[group]) if group != "Todos os países" else None


def in_group(df: pd.DataFrame) -> pd.DataFrame:
    return df if group_geos is None else df[df["geo"].isin(group_geos)]


# ============================================================
# Estilo compartilhado dos mapas
# ============================================================

def style_geo(fig, *, height=None, scope="world"):
    """Aplica projeção, rotação e cores do tema a qualquer figura geográfica."""
    fig.update_geos(
        scope=scope,
        projection_type=projection,
        projection_rotation=dict(lon=rot_lon, lat=rot_lat, roll=0),
        showland=True, landcolor=T["land"],
        showocean=show_ocean, oceancolor=T["ocean"],
        showcoastlines=True, coastlinecolor=T["coast"], coastlinewidth=0.5,
        showcountries=show_borders, countrycolor=T["country_line"],
        showframe=False,
        lakecolor=T["ocean"],
        bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(
        height=height or map_height,
        autosize=True,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=T["text"]),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=T["text"])),
        coloraxis_colorbar=dict(
            tickfont=dict(color=T["text"]),
            title=dict(font=dict(color=T["text"])),
            thickness=14, len=0.7,
        ),
    )
    return fig


def show(fig, key):
    st.plotly_chart(fig, config={"responsive": True}, width="stretch", key=key)


def log_color_axis(fig, values, prefix=""):
    """Coloca a barra de cores em escala log rotulada na unidade original.

    O prefixo vem do indicador: dolar para PIB, nada para populacao. Os ticks
    saem em 1, 2 e 5 vezes cada potencia de dez, porque so decadas inteiras
    deixam um grupo de faixa estreita, como o G20, com um unico rotulo.
    """
    low, high = float(np.nanmin(values)), float(np.nanmax(values))
    ticks = []
    for exponent in range(int(np.floor(low)), int(np.ceil(high)) + 1):
        for mantissa in (1, 2, 5):
            candidate = exponent + np.log10(mantissa)
            if low - 1e-9 <= candidate <= high + 1e-9:
                ticks.append(candidate)
    if len(ticks) < 2:
        ticks = [low, high]
    fig.update_layout(coloraxis_colorbar=dict(
        tickvals=ticks,
        ticktext=[f"{prefix}{10 ** v:,.0f}" for v in ticks],
        tickfont=dict(color=T["text"]),
        thickness=14, len=0.7,
    ))
    return fig


st.title("Laboratório de mapas")
st.caption(
    "Mesmos dados do painel principal, outra gramática visual. "
    "Cada aba traz o trecho de código que gera o gráfico, para facilitar o transporte para `app.py`."
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1 · Choropleth base",
    "2 · Choropleth animado",
    "3 · Resíduo PISA × PIB",
    "4 · line_geo · Pares",
    "5 · line_geo · Trilha do ranking",
    "6 · Cobertura do PISA",
])


# ------------------------------------------------------------
# 1 · Choropleth base
# ------------------------------------------------------------

# `prefix` rotula a barra de cores em escala log. `num` e o formato d3 usado no
# hover. Contagens de pessoas não levam casa decimal nem cifrão.
INDICATORS = {
    "PIB per capita (PPC, USD 2021)": dict(col="gdp_per_capita", src="panel", log=True, prefix="$", num=",.0f"),
    "Anos médios de escolaridade": dict(col="years_schooling", src="panel", log=False, prefix="", num=".1f"),
    "Pontuação PISA": dict(col="pisa_score", src="panel", log=False, prefix="", num=".0f"),
    "População": dict(col="population", src="panel", log=True, prefix="", num=",.0f"),
    "Eficácia governamental (WGI)": dict(col="gov_eff", src="context", log=False, prefix="", num="+.2f"),
    "Controle de corrupção (WGI)": dict(col="control_corruption", src="context", log=False, prefix="", num="+.2f"),
    "Índice de Gini (renda)": dict(col="gini", src="context", log=False, prefix="", num=".1f"),
}

with tab1:
    st.subheader("Um indicador, um ano, o mundo inteiro")

    c1, c2, c3 = st.columns([2, 1, 1])
    ind_label = c1.selectbox("Indicador", list(INDICATORS), key="ind1")
    spec = INDICATORS[ind_label]

    if spec["src"] == "panel":
        avail_years = sorted(panel.dropna(subset=[spec["col"]])["year"].unique().astype(int))
        year = c2.select_slider("Ano", options=avail_years, value=avail_years[-1], key="yr1")
        view = panel[panel["year"] == year][["geo", "name", spec["col"]]].dropna()
        year_note = f"Ano de referência: {year}."
    else:
        names = panel.sort_values("year").groupby("geo", as_index=False).last()[["geo", "name"]]
        view = context[["geo", spec["col"]]].dropna().merge(names, on="geo", how="left")
        c2.metric("Recorte", "Último disponível")
        year_note = "Recorte transversal: último ano disponível por país."

    view = in_group(view)
    scale = c3.selectbox("Paleta", SEQUENTIAL_SCALES, key="sc1")
    use_log = st.checkbox("Escala logarítmica de cor", value=spec["log"], key="lg1",
                          disabled=not spec["log"])

    if view.empty:
        st.warning("Sem dados para essa combinação.")
    else:
        view = view.copy()
        if use_log and spec["log"]:
            view["color_val"] = np.log10(view[spec["col"]].clip(lower=1))
        else:
            view["color_val"] = view[spec["col"]]

        fig = px.choropleth(
            view,
            locations="geo",
            locationmode="ISO-3",
            color="color_val",
            hover_name="name",
            custom_data=[spec["col"]],
            color_continuous_scale=scale,
            template=TEMPLATE,
            labels={"color_val": ind_label},
        )
        fig.update_traces(
            marker_line_color=T["country_line"],
            marker_line_width=0.3,
            hovertemplate=(
                "<b>%{hovertext}</b><br>" + ind_label + ": "
                + spec["prefix"] + "%{customdata[0]:" + spec["num"] + "}<extra></extra>"
            ),
        )
        style_geo(fig)
        fig.update_layout(coloraxis_colorbar_title_text="")
        if use_log and spec["log"]:
            log_color_axis(fig, view["color_val"], prefix=spec["prefix"])
        show(fig, key=f"map1_{ind_label}_{group}_{scale}_{use_log}")

        st.caption(f"{year_note} {view['geo'].nunique()} países com dado. "
                   "Países em cinza não têm observação. A ausência é informação, não zero.")

        with st.expander("Código do gráfico"):
            st.code(
                'fig = px.choropleth(\n'
                '    view,\n'
                '    locations="geo", locationmode="ISO-3",\n'
                '    color="color_val", hover_name="name",\n'
                f'    color_continuous_scale="{scale}",\n'
                ')\n'
                'fig.update_geos(\n'
                f'    projection_type="{projection}",\n'
                f'    projection_rotation=dict(lon={rot_lon}, lat={rot_lat}),\n'
                '    showocean=True, showframe=False,\n'
                ')',
                language="python",
            )


# ------------------------------------------------------------
# 2 · Choropleth animado
# ------------------------------------------------------------

with tab2:
    st.subheader("O mesmo mapa, ano a ano")
    st.caption(
        "O equivalente geográfico da bolha animada do painel principal. "
        "Anos são quadros; a escala de cor fica fixa para que a comparação entre quadros seja honesta."
    )

    c1, c2, c3 = st.columns(3)
    anim_label = c1.selectbox(
        "Indicador", ["Anos médios de escolaridade", "PIB per capita (PPC, USD 2021)"], key="ind2"
    )
    col = INDICATORS[anim_label]["col"]
    step = c2.select_slider("Passo entre quadros (anos)", options=[1, 2, 5], value=2)
    scale2 = c3.selectbox("Paleta", SEQUENTIAL_SCALES, index=1, key="sc2")

    src = panel.dropna(subset=[col]).copy()
    years_all = sorted(src["year"].unique().astype(int))
    y0, y1 = st.select_slider(
        "Intervalo", options=years_all, value=(years_all[0], years_all[-1]), key="rng2"
    )
    keep_years = [y for y in years_all if y0 <= y <= y1 and (y - y0) % step == 0]
    view2 = in_group(src[src["year"].isin(keep_years)])

    if view2.empty:
        st.warning("Sem dados para essa combinação.")
    else:
        view2 = view2.sort_values("year")
        color_col = col
        if INDICATORS[anim_label]["log"]:
            view2 = view2.assign(color_val=np.log10(view2[col].clip(lower=1)))
            color_col = "color_val"

        fig2 = px.choropleth(
            view2,
            locations="geo", locationmode="ISO-3",
            color=color_col,
            hover_name="name",
            custom_data=[col],
            animation_frame="year",
            color_continuous_scale=scale2,
            range_color=(view2[color_col].min(), view2[color_col].max()),
            template=TEMPLATE,
        )
        spec2 = INDICATORS[anim_label]
        fig2.update_traces(
            marker_line_color=T["country_line"], marker_line_width=0.3,
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                + spec2["prefix"] + "%{customdata[0]:" + spec2["num"] + "}<extra></extra>"
            ),
        )
        style_geo(fig2)
        fig2.update_layout(coloraxis_colorbar_title_text="")
        if color_col == "color_val":
            log_color_axis(fig2, view2["color_val"], prefix=spec2["prefix"])
        # Quadros mais curtos: o padrão do px é lento demais para 30+ anos.
        if fig2.layout.updatemenus:
            for menu in fig2.layout.updatemenus:
                for button in menu.buttons:
                    if button.label == "▶":
                        button.args[1]["frame"]["duration"] = 350
                        button.args[1]["transition"]["duration"] = 200
        show(fig2, key=f"map2_{anim_label}_{group}_{step}_{y0}_{y1}")

        st.caption(
            f"{len(keep_years)} quadros, {view2['geo'].nunique()} países. "
            "Um país que some entre quadros é ausência de dado naquele ano, não queda a zero."
        )

        with st.expander("Código do gráfico"):
            st.code(
                'fig = px.choropleth(\n'
                '    view, locations="geo", locationmode="ISO-3",\n'
                '    color="color_val", animation_frame="year",\n'
                '    range_color=(vmin, vmax),   # trava a escala entre quadros\n'
                ')',
                language="python",
            )


# ------------------------------------------------------------
# 3 · Resíduo PISA × PIB
# ------------------------------------------------------------

with tab3:
    st.subheader("Quem aprende mais do que a renda faria esperar")
    st.markdown(
        "Ajuste linear simples de `PISA ~ log10(PIB per capita)` no recorte transversal do PISA. "
        "O mapa mostra o **resíduo**: pontos acima (azul) ou abaixo (vermelho) do que o modelo "
        "prevê para aquele nível de renda. É descritivo, não causal. Mede desvio em relação "
        "à média condicional, não eficácia de política educacional."
    )

    pisa_years = sorted(panel.dropna(subset=["pisa_score"])["year"].unique().astype(int))
    wave = st.select_slider("Onda do PISA", options=pisa_years, value=pisa_years[-1], key="wave3")

    cross = panel[(panel["year"] == wave)].dropna(subset=["pisa_score", "gdp_per_capita"]).copy()
    cross["log_gdp"] = np.log10(cross["gdp_per_capita"])

    if len(cross) < 5:
        st.warning("Poucos países nessa onda para ajustar a reta.")
    else:
        slope, intercept = np.polyfit(cross["log_gdp"], cross["pisa_score"], 1)
        cross["expected"] = intercept + slope * cross["log_gdp"]
        cross["residual"] = cross["pisa_score"] - cross["expected"]
        r = float(np.corrcoef(cross["log_gdp"], cross["pisa_score"])[0, 1])

        view3 = in_group(cross)
        lim = float(np.abs(view3["residual"]).max())

        m1, m2, m3 = st.columns(3)
        m1.metric("Países na onda", f"{cross['geo'].nunique()}")
        m2.metric("Correlação de Pearson", f"{r:.2f}")
        m3.metric("Inclinação", f"{slope:.0f} pts por década de renda")

        fig3 = px.choropleth(
            view3,
            locations="geo", locationmode="ISO-3",
            color="residual",
            hover_name="name",
            custom_data=["pisa_score", "expected", "gdp_per_capita"],
            # ["#C73E1D", "#F4F1DE", "#2E86AB"]: resíduo negativo em vermelho,
            # zero em creme, positivo em azul.
            color_continuous_scale=T["diverging"],
            color_continuous_midpoint=0,
            range_color=(-lim, lim),
            template=TEMPLATE,
        )
        fig3.update_traces(
            marker_line_color=T["country_line"], marker_line_width=0.3,
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "PISA observado: %{customdata[0]:.0f}<br>"
                "PISA esperado pela renda: %{customdata[1]:.0f}<br>"
                "Resíduo: %{z:+.0f} pontos<br>"
                "PIB per capita: $%{customdata[2]:,.0f}<extra></extra>"
            ),
        )
        style_geo(fig3)
        fig3.update_layout(coloraxis_colorbar_title_text="Resíduo")
        show(fig3, key=f"map3_{wave}_{group}")

        cA, cB = st.columns(2)
        cols = ["name", "gdp_per_capita", "pisa_score", "expected", "residual"]
        headers = {"name": "País", "gdp_per_capita": "PIB per capita",
                   "pisa_score": "PISA", "expected": "Esperado", "residual": "Resíduo"}
        top = view3.nlargest(10, "residual")[cols].rename(columns=headers)
        bottom = view3.nsmallest(10, "residual")[cols].rename(columns=headers)
        cA.markdown("**Maiores resíduos positivos**")
        cA.dataframe(top, hide_index=True, width="stretch")
        cB.markdown("**Maiores resíduos negativos**")
        cB.dataframe(bottom, hide_index=True, width="stretch")

        st.download_button(
            "Baixar resíduos (CSV)",
            data=view3[cols + ["geo"]].to_csv(index=False).encode("utf-8"),
            file_name=f"pisa_residuals_{wave}.csv",
            mime="text/csv",
        )

        with st.expander("Código do gráfico"):
            st.code(
                'slope, intercept = np.polyfit(np.log10(df.gdp_per_capita), df.pisa_score, 1)\n'
                'df["residual"] = df.pisa_score - (intercept + slope * np.log10(df.gdp_per_capita))\n\n'
                'fig = px.choropleth(\n'
                '    df, locations="geo", locationmode="ISO-3", color="residual",\n'
                '    color_continuous_scale=["#C73E1D", "#F4F1DE", "#2E86AB"],\n'
                '    color_continuous_midpoint=0, range_color=(-lim, lim),\n'
                ')',
                language="python",
            )


# ------------------------------------------------------------
# 4 · line_geo · rede de pares
# ------------------------------------------------------------

with tab4:
    st.subheader("Cada país ligado ao seu par de renda com melhor PISA")
    st.markdown(
        "`px.line_geo` desenha ligações entre pontos, então precisa de uma relação real entre "
        "países para não virar enfeite. A relação aqui: para cada país, procuramos o país com "
        "PIB per capita dentro de uma faixa de ±X% e **maior** pontuação no PISA. "
        "A linha vai do país ao seu *benchmark de renda comparável*. "
        "Países sem linha já são o melhor da própria faixa."
    )

    if meta.empty:
        st.error("`data/country_meta.csv` não encontrado. Rode `python data/build_country_meta.py`.")
    else:
        c1, c2, c3 = st.columns(3)
        wave4 = c1.select_slider(
            "Onda do PISA",
            options=sorted(panel.dropna(subset=["pisa_score"])["year"].unique().astype(int)),
            value=2022, key="wave4",
        )
        band = c2.slider("Faixa de renda comparável (±%)", 5, 60, 25, 5)
        top_n = c3.slider("Mostrar as N maiores lacunas", 5, 80, 30, 5)

        base = panel[panel["year"] == wave4].dropna(subset=["pisa_score", "gdp_per_capita"])
        base = base.merge(meta[["geo", "lat", "lon", "region", "capital"]], on="geo", how="inner")
        base = base.dropna(subset=["lat", "lon"])
        base = in_group(base)

        pairs = []
        arr = base.reset_index(drop=True)
        for row in arr.itertuples(index=False):
            lo, hi = row.gdp_per_capita * (1 - band / 100), row.gdp_per_capita * (1 + band / 100)
            peers = arr[(arr.gdp_per_capita.between(lo, hi))
                        & (arr.geo != row.geo)
                        & (arr.pisa_score > row.pisa_score)]
            if peers.empty:
                continue
            best = peers.loc[peers["pisa_score"].idxmax()]
            pairs.append({
                "geo": row.geo, "name": row.name, "lat": row.lat, "lon": row.lon,
                "peer_geo": best["geo"], "peer_name": best["name"],
                "peer_lat": best["lat"], "peer_lon": best["lon"],
                "gap": float(best["pisa_score"] - row.pisa_score),
                "region": row.region,
                "pisa": row.pisa_score, "peer_pisa": float(best["pisa_score"]),
                "gdp": row.gdp_per_capita,
            })

        pdf = pd.DataFrame(pairs)
        if pdf.empty:
            st.warning("Nenhum par encontrado com esses parâmetros. Aumente a faixa de renda.")
        else:
            pdf = pdf.nlargest(min(top_n, len(pdf)), "gap").reset_index(drop=True)
            pdf["pair_id"] = pdf["geo"] + "→" + pdf["peer_geo"]

            # px.line_geo consome uma linha por vertice. Duas linhas por par,
            # separadas por `line_group`, viram um segmento cada.
            segs = pd.concat([
                pdf.assign(lat_v=pdf["lat"], lon_v=pdf["lon"], role="origem", order=0),
                pdf.assign(lat_v=pdf["peer_lat"], lon_v=pdf["peer_lon"], role="par", order=1),
            ]).sort_values(["pair_id", "order"])

            fig4 = px.line_geo(
                segs,
                lat="lat_v", lon="lon_v",
                line_group="pair_id",
                color="region",
                hover_name="name",
                custom_data=["name", "peer_name", "pisa", "peer_pisa", "gap", "gdp"],
                template=TEMPLATE,
            )
            fig4.update_traces(
                line=dict(width=1.4), opacity=0.85,
                hovertemplate=(
                    "<b>%{customdata[0]}</b> → <b>%{customdata[1]}</b><br>"
                    "PISA: %{customdata[2]:.0f} → %{customdata[3]:.0f}<br>"
                    "Lacuna: %{customdata[4]:.0f} pontos<br>"
                    "PIB per capita da origem: $%{customdata[5]:,.0f}<extra></extra>"
                ),
            )
            # Marcadores nas pontas: origem oca, benchmark cheio.
            fig4.add_trace(go.Scattergeo(
                lat=pdf["lat"], lon=pdf["lon"], mode="markers",
                marker=dict(size=6, color=T["diverging"][0], opacity=0.9,
                            line=dict(width=0.5, color=T["text"])),
                name="Origem", text=pdf["name"],
                hovertemplate="<b>%{text}</b><extra>origem</extra>",
            ))
            peers_uni = pdf.drop_duplicates("peer_geo")
            fig4.add_trace(go.Scattergeo(
                lat=peers_uni["peer_lat"], lon=peers_uni["peer_lon"], mode="markers",
                marker=dict(size=9, color=T["diverging"][2], symbol="star",
                            line=dict(width=0.5, color=T["text"])),
                name="Benchmark", text=peers_uni["peer_name"],
                hovertemplate="<b>%{text}</b><extra>benchmark de renda comparável</extra>",
            ))
            style_geo(fig4)
            show(fig4, key=f"map4_{wave4}_{band}_{top_n}_{group}")

            st.caption(
                f"{len(pdf)} pares desenhados. Estrelas são países que servem de referência para "
                "outros de renda parecida. Uma linha longa não significa distância cultural: "
                "significa apenas que o par de renda mais próximo está longe geograficamente."
            )

            st.dataframe(
                pdf[["name", "gdp", "pisa", "peer_name", "peer_pisa", "gap"]].rename(columns={
                    "name": "País", "gdp": "PIB per capita", "pisa": "PISA",
                    "peer_name": "Par de renda comparável", "peer_pisa": "PISA do par",
                    "gap": "Lacuna (pts)",
                }),
                hide_index=True, width="stretch", height=280,
            )

            with st.expander("Código do gráfico"):
                st.code(
                    '# duas linhas por par (origem e destino), separadas por line_group\n'
                    'segs = pd.concat([\n'
                    '    pdf.assign(lat_v=pdf.lat,      lon_v=pdf.lon,      order=0),\n'
                    '    pdf.assign(lat_v=pdf.peer_lat, lon_v=pdf.peer_lon, order=1),\n'
                    ']).sort_values(["pair_id", "order"])\n\n'
                    'fig = px.line_geo(\n'
                    '    segs, lat="lat_v", lon="lon_v",\n'
                    '    line_group="pair_id", color="region", hover_name="name",\n'
                    ')',
                    language="python",
                )


# ------------------------------------------------------------
# 5 · line_geo · trilha do ranking
# ------------------------------------------------------------

with tab5:
    st.subheader("A trilha do ranking sobre o globo")
    st.markdown(
        "Duas rotas ligando os N primeiros colocados em ordem de posição: uma pelo PISA, "
        "outra pelo PIB per capita. Quanto mais as duas trilhas divergem, menos o ranking de "
        "riqueza e o de aprendizagem coincidem. É um artifício de leitura, não uma trajetória real."
    )

    if meta.empty:
        st.error("`data/country_meta.csv` não encontrado. Rode `python data/build_country_meta.py`.")
    else:
        c1, c2 = st.columns(2)
        wave5 = c1.select_slider(
            "Onda do PISA",
            options=sorted(panel.dropna(subset=["pisa_score"])["year"].unique().astype(int)),
            value=2022, key="wave5",
        )
        n5 = c2.slider("Quantos primeiros colocados", 5, 30, 15, 1)

        base5 = panel[panel["year"] == wave5].dropna(subset=["pisa_score", "gdp_per_capita"])
        base5 = base5.merge(meta[["geo", "lat", "lon"]], on="geo", how="inner").dropna(subset=["lat", "lon"])
        base5 = in_group(base5)

        if len(base5) < 3:
            st.warning("Poucos países com dado nessa onda e grupo.")
        else:
            routes = []
            for label, col in (("Ranking PISA", "pisa_score"), ("Ranking PIB per capita", "gdp_per_capita")):
                top = base5.nlargest(min(n5, len(base5)), col).reset_index(drop=True)
                top["rank"] = np.arange(1, len(top) + 1)
                top["route"] = label
                top["value"] = top[col]
                routes.append(top)
            rdf = pd.concat(routes).sort_values(["route", "rank"])
            rdf["label"] = rdf["rank"].astype(str)

            fig5 = px.line_geo(
                rdf,
                lat="lat", lon="lon",
                color="route", line_group="route",
                hover_name="name",
                text="label",
                custom_data=["name", "rank", "value", "route"],
                color_discrete_sequence=[T["diverging"][2], T["diverging"][0]],
                template=TEMPLATE,
            )
            fig5.update_traces(
                mode="lines+markers+text",
                line=dict(width=2),
                marker=dict(size=14, opacity=0.9),
                textfont=dict(size=9, color=T["text"]),
                textposition="middle center",
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "%{customdata[3]}: #%{customdata[1]}<br>"
                    "Valor: %{customdata[2]:,.1f}<extra></extra>"
                ),
            )
            style_geo(fig5)
            fig5.update_layout(legend=dict(orientation="h", y=1.02, x=0))
            show(fig5, key=f"map5_{wave5}_{n5}_{group}")

            overlap = set(routes[0]["geo"]) & set(routes[1]["geo"])
            st.caption(
                f"{len(overlap)} de {n5} países aparecem nas duas listas. "
                "Os que estão só na trilha do PIB são economias ricas que não convertem renda em "
                "aprendizagem na mesma proporção, e vice-versa."
            )

            with st.expander("Código do gráfico"):
                st.code(
                    'top = df.nlargest(n, "pisa_score").assign(rank=lambda d: range(1, len(d)+1))\n\n'
                    'fig = px.line_geo(\n'
                    '    rdf.sort_values(["route", "rank"]),\n'
                    '    lat="lat", lon="lon",\n'
                    '    color="route", line_group="route", text="label",\n'
                    ')\n'
                    'fig.update_traces(mode="lines+markers+text")',
                    language="python",
                )


# ------------------------------------------------------------
# 6 · Cobertura do PISA
# ------------------------------------------------------------

with tab6:
    st.subheader("Quantas vezes cada país fez o PISA")
    st.markdown(
        "Mapa de cobertura, não de desempenho. Serve de nota metodológica visual: boa parte do "
        "mundo nunca participou do PISA, e comparações longitudinais só são possíveis onde há "
        "várias ondas. O painel principal já limita as trajetórias a países com três ou mais "
        "aplicações, e este mapa mostra por quê."
    )

    waves = (panel.dropna(subset=["pisa_score"])
                  .groupby(["geo"], as_index=False)
                  .agg(n_waves=("year", "nunique"),
                       first_year=("year", "min"),
                       last_year=("year", "max")))
    names = panel.sort_values("year").groupby("geo", as_index=False).last()[["geo", "name"]]
    waves = waves.merge(names, on="geo", how="left")
    waves = in_group(waves)

    fig6 = px.choropleth(
        waves,
        locations="geo", locationmode="ISO-3",
        color="n_waves",
        hover_name="name",
        custom_data=["n_waves", "first_year", "last_year"],
        color_continuous_scale="YlGnBu",
        range_color=(1, 8),
        template=TEMPLATE,
    )
    fig6.update_traces(
        marker_line_color=T["country_line"], marker_line_width=0.3,
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Aplicações: %{customdata[0]}<br>"
            "De %{customdata[1]} a %{customdata[2]}<extra></extra>"
        ),
    )
    style_geo(fig6)
    fig6.update_layout(coloraxis_colorbar=dict(
        title=dict(text="Ondas", font=dict(color=T["text"])),
        tickvals=list(range(1, 9)), tickfont=dict(color=T["text"]),
        thickness=14, len=0.7,
    ))
    show(fig6, key=f"map6_{group}")

    n_total = len(VALID_GEOS)
    n_ever = waves["geo"].nunique()
    n_3plus = int((waves["n_waves"] >= 3).sum())
    m1, m2, m3 = st.columns(3)
    m1.metric("Economias na base", f"{n_total}")
    m2.metric("Já participaram do PISA", f"{n_ever}")
    m3.metric("Com 3+ aplicações", f"{n_3plus}")

    st.caption(
        "Cinza não é zero: é país que nunca participou. Tratar essa ausência como zero seria "
        "o erro mais comum de leitura desse tipo de mapa."
    )
