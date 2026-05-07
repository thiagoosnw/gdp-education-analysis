import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
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
}


# ============================================================
# Internationalisation
# ============================================================

I18N = {
    "pt": {
        "page_title": "Riqueza, Educação e PISA — Laboratório de Eficiência",
        "app_title": "Riqueza, Educação e PISA",
        "app_subtitle": (
            "Quais países entregam mais aprendizagem do que sua renda, escolaridade e "
            "instituições prevêm? Este painel constrói um **Índice de Eficiência "
            "Educacional** comparando o desempenho real de 57 países no PISA 2022 com o "
            "esperado a partir desses fundamentos."
        ),
        "ui_language": "Idioma",
        "ui_theme": "Tema",
        "theme_dark": "Escuro",
        "theme_light": "Claro",
        "filters": "Filtros",
        "country_group": "Grupo de países",
        "group_all": "Todos os países",
        "view_options": "Opções de visualização",
        "y_axis": "Métrica do eixo Y",
        "y_pisa": "Pontuação PISA",
        "y_mys": "Anos médios de escolaridade",
        "highlight_label": "Países em destaque (opcional)",
        "highlight_help": "Países selecionados ficam em cor saturada; os demais ficam translúcidos.",
        "data_sources": "Fontes de dados",
        "data_sources_md": (
            "- **PIB per capita PPC** — [World Bank `NY.GDP.PCAP.PP.CD`](https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD)\n"
            "- **População** — [World Bank `SP.POP.TOTL`](https://data.worldbank.org/indicator/SP.POP.TOTL)\n"
            "- **Anos médios de escolaridade** — [UNDP HDR](https://hdr.undp.org/data-center/documentation-and-downloads)\n"
            "- **Escores PISA** — [OECD](https://www.oecd.org/pisa/)\n"
            "- **Gasto por aluno do secundário** — [WB `SE.XPD.SECO.PC.ZS`](https://data.worldbank.org/indicator/SE.XPD.SECO.PC.ZS)\n"
            "- **Gasto total em educação (% PIB)** — [WB `SE.XPD.TOTL.GD.ZS`](https://data.worldbank.org/indicator/SE.XPD.TOTL.GD.ZS)\n"
            "- **Eficácia governamental (WGI)** — [WB Worldwide Governance Indicators](https://www.worldbank.org/en/publication/worldwide-governance-indicators)"
        ),
        "author": "Autor",
        "tab_panel": "Painel histórico",
        "tab_efficiency": "Índice de Eficiência",
        "tab_drivers": "Correlações",
        "tab_simulator": "Simulador",
        "tab_methodology": "Metodologia",
        "panel_subtitle": "Evolução histórica — {group} ({metric})",
        "panel_pisa_note": (
            "Apresentado como recorte transversal de **PISA 2022** (a onda mais recente, "
            "com cobertura de 81 países). 38 dos 84 países só ingressaram no PISA em 2022, "
            "logo a animação contínua induziria leitura equivocada. O painel de tendências "
            "abaixo cobre apenas os países com 3 ou mais aplicações. Para evolução contínua "
            "use *Anos médios de escolaridade*."
        ),
        "panel_pisa_trend_title": "Trajetórias por país (≥ 3 aplicações)",
        "panel_pisa_trend_note": (
            "{n} países do grupo selecionado têm 3 ou mais aplicações do PISA. "
            "Cada linha conecta as ondas reais sem interpolação."
        ),
        "no_data_warning": "Sem dados disponíveis para {metric} em {group}.",
        "m_countries": "Países na visualização",
        "m_years": "Anos de dados",
        "m_median_gdp": "Mediana do PIB per capita ({year})",
        "m_median_y": "Mediana de {metric} ({year})",
        "x_label": "PIB per capita (USD PPC, escala log)",
        "x_label_short": "PIB per capita (USD PPC)",
        "year": "Ano",
        "country": "País",
        "population": "População",
        "footnote_bubble": "As bolhas têm tamanho proporcional à população total. Eixo X em escala logarítmica.",
        "download_panel_csv": "Baixar dados do painel (CSV)",
        "eff_subtitle": "Índice de Eficiência Educacional",
        "eff_description": (
            "Para cada país, o índice é o resíduo padronizado (z-score) da função de "
            "produção "
            r"$\ln(\text{PISA})=\theta\ln(\text{Gasto})+\beta\ln(\text{PIB})+\gamma\ln(\text{MYS})+\eta\,\text{GovEff}+\delta+\varepsilon$, "
            "estimada por **OLS** com erros-padrão robustos HC1. "
            r"$\text{Gasto}$ é o gasto governamental por aluno do secundário (USD PPC), "
            r"$\text{MYS}$ são os anos médios de escolaridade e "
            r"$\text{GovEff}$ é a Eficácia Governamental do Banco Mundial (≈ −2,5 a +2,5). "
            "Um z **positivo** indica que o país pontua acima do que seus insumos "
            "preveriam — eficiência alta; **negativo**, o oposto."
        ),
        "eff_rank_by": "Ordenar por",
        "eff_rank_by_help": (
            "**z-score de eficiência**: resíduo padronizado da regressão — controla por "
            "gasto, PIB, escolaridade e governança simultaneamente. **Pontos PISA por "
            "1 000 USD**: razão simples entre pontuação e gasto, sem controles. As duas "
            "medidas costumam apresentar rankings diferentes."
        ),
        "eff_z_label": "z-score de eficiência",
        "eff_per_1k_label": "Pontos PISA por 1 000 USD",
        "eff_most_efficient": "Mais eficiente",
        "eff_least_efficient": "Menos eficiente",
        "eff_sample_size": "Tamanho da amostra",
        "eff_n_countries": "{n} países",
        "eff_warning_few": (
            "Apenas {n} país do grupo **{group}** tem dados de eficiência. "
            "Mostrando a amostra completa de {total} países."
        ),
        "eff_show_ci": "Mostrar IC 95% (bootstrap)",
        "eff_show_ci_help": (
            "Recalcula o ranking 300 vezes reamostrando os países com reposição "
            "(bootstrap não-paramétrico) e retorna a faixa que contém 95% dos z-scores "
            "obtidos. **Faixas largas** indicam ranking instável (a posição depende "
            "muito de quem está na amostra); **faixas estreitas**, ranking robusto. Útil "
            "para checar se posições surpreendentes — Turquia, Ucrânia — são apoiadas "
            "pelos dados ou são artefato de amostra."
        ),
        "computing_ci": "Calculando intervalos de confiança…",
        "spending_vs_score": "Gastos vs. desempenho",
        "empirical_fit": "Ajuste empírico",
        "pisa_2022": "PISA 2022",
        "country_table": "Tabela por país",
        "download_efficiency_csv": "Baixar índice de eficiência (CSV)",
        "col_country": "País",
        "col_iso": "ISO3",
        "col_pisa_actual": "PISA (real)",
        "col_pisa_pred": "PISA (previsto)",
        "col_spend": "Gasto/aluno (USD PPC)",
        "col_spend_year": "Ano do gasto",
        "col_mys": "Anos médios de escolaridade",
        "col_gdp": "PIB per capita (USD PPC)",
        "col_gov": "Eficácia governamental",
        "col_xpd": "Gasto total em educação (% PIB)",
        "col_z": "z-score de eficiência",
        "drivers_subtitle": "Como cada motor se correlaciona com o PISA",
        "drivers_description": (
            "Associações bivariadas entre o escore PISA 2022 e os quatro motores candidatos do "
            "modelo de eficiência. Cada painel inclui uma reta de ajuste por OLS; o número em "
            "destaque é a correlação de Pearson simples."
        ),
        "driver_spend": "Gasto por aluno",
        "driver_spend_axis": "Gasto por aluno do secundário (USD PPC, escala log)",
        "driver_gdp": "PIB per capita",
        "driver_gdp_axis": "PIB per capita (USD PPC, escala log)",
        "driver_mys": "Anos de escolaridade",
        "driver_mys_axis": "Anos médios de escolaridade",
        "driver_gov": "Eficácia governamental",
        "driver_gov_axis": "Eficácia governamental (-2,5 a +2,5)",
        "driver_help": "Correlação de Pearson entre o PISA 2022 e {label} em {n} países.",
        "sim_subtitle": "Simulador",
        "sim_description": (
            "Mova os controles para alterar as variáveis do modelo M3 e veja como o escore PISA "
            "previsto muda. Os coeficientes vêm da estimação OLS atual sobre o conjunto de "
            "países com dados completos."
        ),
        "sim_baseline": "País de referência",
        "sim_reset": "Restaurar",
        "sim_reset_help": "Restaura todos os controles para os valores reais do país de referência.",
        "sim_spend": "Gasto/aluno (USD PPC)",
        "sim_gdp": "PIB per capita (USD PPC)",
        "sim_mys": "Anos médios de escolaridade",
        "sim_gov": "Eficácia governamental",
        "sim_pisa_actual": "PISA real",
        "sim_pisa_baseline_pred": "PISA previsto (referência)",
        "sim_pisa_new_pred": "PISA previsto (cenário)",
        "sim_contributions": "Contribuição de cada motor (pontos PISA)",
        "sim_contribution_axis": "Contribuição aproximada (pontos PISA)",
        "sim_footnote": "Modelo M3, R² ajustado = {adj_r:.3f}, N = {n}. As contribuições usam a aproximação ΔPISA ≈ PISA·Δlog.",
        "vs_actual": "vs. real",
        "vs_baseline": "vs. referência",
        "meth_specification": "Especificação",
        "meth_specification_md": (
            r"$$\ln(\text{PISA}_i) = \theta\,\ln(\text{Spend}_i) + \beta\,\ln(\text{GDP}_i) + \gamma\,\ln(\text{MYS}_i) + \eta\,\text{GovEff}_i + \delta + \varepsilon_i$$"
            "\n\n"
            "Estimada por OLS com erros-padrão robustos HC1 sobre o corte transversal de 57 "
            "países com escore PISA 2022. O Índice de Eficiência Educacional é o resíduo "
            "padronizado:\n\n"
            r"$$\text{EI}_i = \frac{\hat\varepsilon_i - \bar{\hat\varepsilon}}{\hat\sigma_{\hat\varepsilon}}$$"
            "\n\n"
            "Reportado diretamente como z-score. Valores positivos indicam que o país produz "
            "mais pontos PISA do que seus insumos mensuráveis preveriam; valores negativos "
            "indicam desempenho abaixo do esperado."
        ),
        "meth_variables": "Variáveis e fontes",
        "meth_variables_md": (
            "| Variável | Fonte | Indicador | Ano |\n"
            "|---|---|---|---|\n"
            "| Escore PISA | OECD | média de matemática, leitura e ciências (TOT) | 2022 |\n"
            "| Gasto por aluno do secundário | WB (UNESCO UIS) | `SE.XPD.SECO.PC.ZS` × PIB per capita PPC | 2015–2018 |\n"
            "| PIB per capita PPC | World Bank | `NY.GDP.PCAP.PP.CD` | 2022 |\n"
            "| Anos médios de escolaridade | UNDP HDR | `mys` | 2022 |\n"
            "| Eficácia governamental | WB WGI | `GOV_WGI_GE.EST` | 2018–2023 |\n"
            "| Gasto total em educação (% PIB) | WB (UNESCO UIS) | `SE.XPD.TOTL.GD.ZS` | 2018–2023 |"
        ),
        "meth_search": "Busca de especificação",
        "meth_search_md": (
            "| Spec | Variáveis | R² ajustado | N |\n"
            "|---|---|---|---|\n"
            "| M1 | Spend, GDP, MYS                            | 0,711 | 56 |\n"
            "| M2 | M1 + Gasto total em educação (% PIB)        | 0,708 | 56 |\n"
            "| **M3 (preferido)** | M1 + Eficácia governamental | **0,720** | 56 |\n"
            "| M4 | M1 + Gasto total + Eficácia governamental    | 0,718 | 56 |\n\n"
            "O gasto total em educação como percentual do PIB não é estatisticamente "
            "significativo em nenhuma especificação, em linha com Hanushek: o tamanho do "
            "esforço fiscal não prediz o desempenho uma vez controlados outros insumos. A "
            "Eficácia Governamental contribui positivamente e é mantida no modelo preferido."
        ),
        "meth_nonlinear": "Comparação com métodos não-lineares",
        "meth_nonlinear_md": (
            "A função de produção M3 é log-linear por hipótese — assume elasticidades "
            "constantes e nenhuma interação entre insumos. Para investigar se efeitos "
            "não-lineares (por exemplo, **gasto e governança poderiam ter efeito "
            "multiplicativo**, como sugerido pela orientadora) melhoram a previsão, "
            "estimei modelos alternativos sob o **mesmo conjunto de variáveis** e "
            "avaliei o R² **fora da amostra** com 5-fold cross-validation."
            "\n\n"
            "| Modelo | Forma funcional | CV R² | ± d.p. |\n"
            "|---|---|---|---|\n"
            "{rows}\n\n"
            "**Leitura.** Com N=57 países e 4 preditores, qualquer modelo flexível precisa "
            "de regularização forte para não memorizar a amostra. O OLS log-linear é "
            "transparente mas subajusta. Adicionar a interação Gasto×GovEff piora a "
            "validação (mais um parâmetro, mesmo poder explicativo). A regressão "
            "**polinomial Ridge** (grau 2, α=5) é o melhor compromisso fora da amostra: "
            "captura curvaturas e interações entre os 4 insumos, mas o termo L2 controla "
            "o sobreajuste. A **rede MLP** com 4 neurônios alcança desempenho semelhante, "
            "mas perde a interpretabilidade dos coeficientes."
            "\n\n"
            "Mesmo assim, o **índice de eficiência continua a ser construído a partir do "
            "M3 OLS**, por três motivos: (i) os coeficientes têm interpretação direta como "
            "elasticidades; (ii) o erro-padrão robusto HC1 e o 2SLS de robustez já estão "
            "estabelecidos para essa especificação; (iii) com N=57 a diferença de R² (0,52 "
            "→ 0,65) reflete em parte ruído de validação cruzada (desvios-padrão de ~0,2). "
            "Os modelos não-lineares servem como **complemento metodológico**: indicam "
            "que existe sinal não-linear residual, mas que ainda não justifica abandonar "
            "a especificação interpretável."
        ),
        "meth_2sls": "Verificação de robustez por 2SLS",
        "meth_2sls_md": (
            "O notebook reestima M3 por 2SLS usando o gasto por aluno defasado (2005–2014) "
            r"como instrumento para o gasto corrente. A estatística F do primeiro estágio é 128, bem acima do limiar convencional de 10. O coeficiente 2SLS sobre $\ln(\text{Spend})$ é "
            "moderadamente maior que o de OLS, consistente com viés para baixo no OLS. O "
            "índice do dashboard é construído a partir das predições de OLS; o 2SLS é "
            "reportado no notebook como verificação de sensibilidade."
        ),
        "meth_pred_causal": "Predição vs. identificação causal",
        "meth_pred_causal_md": (
            "OLS é apropriado porque o objetivo é prever o PISA dados os insumos, não "
            "recuperar elasticidades causais. Identificação causal estrita exigiria dados em "
            "painel com variação dentro do país ou instrumentos mais fortes — adiados para "
            "trabalhos futuros."
        ),
        "meth_diag": "Diagnósticos do modelo",
        "meth_diag_pred_actual": "PISA previsto vs. real",
        "meth_diag_resid_hist": "Distribuição dos resíduos (log)",
        "meth_diag_resid_fitted": "Resíduos vs. previstos",
        "residual_log": "Resíduo log(PISA real) − log(PISA previsto)",
        "meth_limits": "Limitações",
        "meth_limits_md": (
            "1. Corte transversal de 57 países — poder estatístico limitado.\n"
            "2. PISA captura uma coorte e três disciplinas.\n"
            "3. Observações de gasto cobrem 2015–2018, não 2022.\n"
            "4. Controles sociodemográficos limitados a PIB, MYS e GovEff.\n"
            "5. A Eficácia Governamental é um composto baseado em percepção."
        ),
        "meth_refs": "Referências",
        "meth_refs_md": (
            "- Hanushek, E. A. (2020). *Education production functions*. The Economics of Education, 2nd ed., Elsevier.\n"
            "- Hanushek, E. A. (1986). The economics of schooling: Production and efficiency in public schools. *Journal of Economic Literature*, 24(3).\n"
            "- Dee, T. S. (2005). Expense preference and student achievement in school districts. *Eastern Economic Journal*, 31(1).\n"
            "- Acemoglu, D., Johnson, S., & Robinson, J. A. (2012). *Why Nations Fail*. Crown Business.\n"
            "- Kaufmann, D., & Kraay, A. (2024). *Worldwide Governance Indicators — 2024 Methodology Update*. World Bank."
        ),
    },
    "en": {
        "page_title": "Wealth, Education & PISA — Efficiency Lab",
        "app_title": "Wealth, Education and PISA",
        "app_subtitle": (
            "Which countries deliver more learning than their income, schooling and "
            "institutions would predict? This dashboard builds an **Education "
            "Efficiency Index** comparing the actual PISA 2022 performance of 57 "
            "countries with what those fundamentals predict."
        ),
        "ui_language": "Language",
        "ui_theme": "Theme",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "filters": "Filters",
        "country_group": "Country group",
        "group_all": "All countries",
        "view_options": "View options",
        "y_axis": "Y-axis metric",
        "y_pisa": "PISA Score",
        "y_mys": "Mean Years of Schooling",
        "highlight_label": "Highlight countries (optional)",
        "highlight_help": "Selected countries appear in saturated colour; others are dimmed.",
        "data_sources": "Data sources",
        "data_sources_md": (
            "- **GDP per capita PPP** — [World Bank `NY.GDP.PCAP.PP.CD`](https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD)\n"
            "- **Population** — [World Bank `SP.POP.TOTL`](https://data.worldbank.org/indicator/SP.POP.TOTL)\n"
            "- **Mean Years of Schooling** — [UNDP HDR](https://hdr.undp.org/data-center/documentation-and-downloads)\n"
            "- **PISA scores** — [OECD](https://www.oecd.org/pisa/)\n"
            "- **Per-secondary-student spending** — [WB `SE.XPD.SECO.PC.ZS`](https://data.worldbank.org/indicator/SE.XPD.SECO.PC.ZS)\n"
            "- **Total ed spending (% GDP)** — [WB `SE.XPD.TOTL.GD.ZS`](https://data.worldbank.org/indicator/SE.XPD.TOTL.GD.ZS)\n"
            "- **Government Effectiveness (WGI)** — [WB Worldwide Governance Indicators](https://www.worldbank.org/en/publication/worldwide-governance-indicators)"
        ),
        "author": "Author",
        "tab_panel": "Historical Panel",
        "tab_efficiency": "Education Efficiency Index",
        "tab_drivers": "Drivers Correlations",
        "tab_simulator": "Simulator",
        "tab_methodology": "Methodology",
        "panel_subtitle": "Historical evolution — {group} ({metric})",
        "panel_pisa_note": (
            "Shown as the **PISA 2022** cross-section (the most recent wave, covering "
            "81 countries). 38 of the 84 countries first joined PISA only in 2022, so a "
            "continuous animation would be misleading. The trends panel below covers "
            "countries with 3 or more assessments only. For continuous evolution use "
            "*Mean Years of Schooling*."
        ),
        "panel_pisa_trend_title": "Country trajectories (≥ 3 assessments)",
        "panel_pisa_trend_note": (
            "{n} countries in the selected group have 3 or more PISA assessments. "
            "Each line connects actual waves with no interpolation."
        ),
        "no_data_warning": "No data available for {metric} within {group}.",
        "m_countries": "Countries in view",
        "m_years": "Years of data",
        "m_median_gdp": "Median GDP per capita ({year})",
        "m_median_y": "Median {metric} ({year})",
        "x_label": "GDP per capita (USD PPP, log scale)",
        "x_label_short": "GDP per capita (USD PPP)",
        "year": "Year",
        "country": "Country",
        "population": "Population",
        "footnote_bubble": "Bubble size scales with total population. X-axis is logarithmic.",
        "download_panel_csv": "Download panel data (CSV)",
        "eff_subtitle": "Education Efficiency Index",
        "eff_description": (
            "Standardised residual (z-score) of the production function "
            r"$\ln(\text{PISA})=\theta\ln(\text{Spend})+\beta\ln(\text{GDP})+\gamma\ln(\text{MYS})+\eta\,\text{GovEff}+\delta+\varepsilon$, "
            "estimated by **OLS** with HC1-robust standard errors. "
            r"$\text{Spend}$ is per-secondary-student government expenditure (USD PPP), "
            r"$\text{MYS}$ is mean years of schooling, "
            r"$\text{GovEff}$ is the World Bank Government Effectiveness score (≈ −2.5 to +2.5). "
            "Positive z ⇒ country produces more PISA points than its measurable inputs predict."
        ),
        "eff_rank_by": "Rank by",
        "eff_rank_by_help": (
            "**Efficiency z-score**: standardised regression residual — controls for "
            "spending, GDP, schooling and governance simultaneously. **PISA per 1 000 "
            "USD**: raw ratio of score to spending, no controls. The two measures "
            "typically yield different rankings."
        ),
        "eff_z_label": "Efficiency z-score",
        "eff_per_1k_label": "PISA per 1 000 USD spent",
        "eff_most_efficient": "Most efficient",
        "eff_least_efficient": "Least efficient",
        "eff_sample_size": "Sample size",
        "eff_n_countries": "{n} countries",
        "eff_warning_few": (
            "Only {n} country in **{group}** has efficiency data. "
            "Showing the full sample of {total} countries instead."
        ),
        "eff_show_ci": "Show 95% CI (bootstrap)",
        "eff_show_ci_help": (
            "Recomputes the ranking 300 times resampling countries with replacement "
            "(non-parametric bootstrap) and reports the band containing 95% of the "
            "resulting z-scores. **Wide bands** indicate unstable ranking (position "
            "depends heavily on who is in the sample); **narrow bands**, robust "
            "ranking. Useful for checking whether surprising positions — Türkiye, "
            "Ukraine — are supported by the data or are sample artefacts."
        ),
        "computing_ci": "Computing confidence intervals…",
        "spending_vs_score": "Spending vs achievement",
        "empirical_fit": "Empirical fit",
        "pisa_2022": "PISA 2022",
        "country_table": "Country-level table",
        "download_efficiency_csv": "Download efficiency index (CSV)",
        "col_country": "Country",
        "col_iso": "ISO3",
        "col_pisa_actual": "PISA (actual)",
        "col_pisa_pred": "PISA (predicted)",
        "col_spend": "Spend / student (USD PPP)",
        "col_spend_year": "Spending year",
        "col_mys": "Mean years of schooling",
        "col_gdp": "GDP per capita (USD PPP)",
        "col_gov": "Govt Effectiveness",
        "col_xpd": "Total ed exp (% GDP)",
        "col_z": "Efficiency z",
        "drivers_subtitle": "How each driver correlates with PISA",
        "drivers_description": (
            "Bivariate associations between PISA 2022 score and the four candidate drivers used "
            "in the efficiency model. Each panel includes an OLS-fit line; the headline number "
            "is the simple Pearson correlation."
        ),
        "driver_spend": "Spending / student",
        "driver_spend_axis": "Per-student spending (USD PPP, log scale)",
        "driver_gdp": "GDP per capita",
        "driver_gdp_axis": "GDP per capita (USD PPP, log scale)",
        "driver_mys": "Years of schooling",
        "driver_mys_axis": "Mean years of schooling",
        "driver_gov": "Govt Effectiveness",
        "driver_gov_axis": "Government Effectiveness (-2.5 to +2.5)",
        "driver_help": "Pearson correlation between PISA 2022 and {label} across {n} countries.",
        "sim_subtitle": "Simulator",
        "sim_description": (
            "Move the sliders to change the M3 model inputs and see how the predicted PISA "
            "score moves. Coefficients come from the current OLS estimation on countries with "
            "complete data."
        ),
        "sim_baseline": "Baseline country",
        "sim_reset": "Reset",
        "sim_reset_help": "Restore every slider to the baseline country's actual values.",
        "sim_spend": "Spend / student (USD PPP)",
        "sim_gdp": "GDP per capita (USD PPP)",
        "sim_mys": "Mean years of schooling",
        "sim_gov": "Government Effectiveness",
        "sim_pisa_actual": "Actual PISA",
        "sim_pisa_baseline_pred": "Predicted PISA (baseline)",
        "sim_pisa_new_pred": "Predicted PISA (scenario)",
        "sim_contributions": "Per-driver contribution (PISA points)",
        "sim_contribution_axis": "Approximate contribution (PISA points)",
        "sim_footnote": "M3 model, adjusted R² = {adj_r:.3f}, N = {n}. Contributions use the approximation ΔPISA ≈ PISA·Δlog.",
        "vs_actual": "vs. actual",
        "vs_baseline": "vs. baseline",
        "meth_specification": "Specification",
        "meth_specification_md": (
            r"$$\ln(\text{PISA}_i) = \theta\,\ln(\text{Spend}_i) + \beta\,\ln(\text{GDP}_i) + \gamma\,\ln(\text{MYS}_i) + \eta\,\text{GovEff}_i + \delta + \varepsilon_i$$"
            "\n\n"
            "Estimated by OLS with HC1-robust standard errors on the cross-section of 57 "
            "countries with a PISA 2022 score. The Education Efficiency Index is the "
            "standardised residual:\n\n"
            r"$$\text{EI}_i = \frac{\hat\varepsilon_i - \bar{\hat\varepsilon}}{\hat\sigma_{\hat\varepsilon}}$$"
            "\n\n"
            "Reported directly as the z-score. Positive values indicate that a country produces "
            "more PISA points than its measurable inputs predict; negative values indicate "
            "underperformance."
        ),
        "meth_variables": "Variables and sources",
        "meth_variables_md": (
            "| Variable | Source | Indicator | Year |\n"
            "|---|---|---|---|\n"
            "| PISA score | OECD | mean of math, reading, science (TOT) | 2022 |\n"
            "| Per-secondary-student spending | World Bank (UNESCO UIS) | `SE.XPD.SECO.PC.ZS` × GDP per capita PPP | 2015–2018 |\n"
            "| GDP per capita PPP | World Bank | `NY.GDP.PCAP.PP.CD` | 2022 |\n"
            "| Mean years of schooling | UNDP HDR | `mys` | 2022 |\n"
            "| Government Effectiveness | World Bank WGI | `GOV_WGI_GE.EST` | 2018–2023 |\n"
            "| Total education expenditure (% GDP) | World Bank (UNESCO UIS) | `SE.XPD.TOTL.GD.ZS` | 2018–2023 |"
        ),
        "meth_search": "Specification search",
        "meth_search_md": (
            "| Spec | Variables | adj R² | N |\n"
            "|---|---|---|---|\n"
            "| M1 | Spend, GDP, MYS                            | 0.711 | 56 |\n"
            "| M2 | M1 + Total ed exp (% GDP)                   | 0.708 | 56 |\n"
            "| **M3 (preferred)** | M1 + Government Effectiveness | **0.720** | 56 |\n"
            "| M4 | M1 + Total ed exp + Government Effectiveness | 0.718 | 56 |\n\n"
            "Total education expenditure as a percentage of GDP is not statistically "
            "significant in any specification, consistent with Hanushek's finding that the "
            "size of the fiscal effort does not predict achievement once other inputs are "
            "controlled for. Government Effectiveness contributes positively and is retained "
            "in the preferred specification."
        ),
        "meth_nonlinear": "Comparison with non-linear methods",
        "meth_nonlinear_md": (
            "The M3 production function is log-linear by assumption — it imposes "
            "constant elasticities and no input interactions. To check whether "
            "non-linear effects (e.g., **spending and governance could have a "
            "multiplicative effect**, as suggested by the supervisor) improve "
            "prediction, I estimate alternative models on the **same variables** and "
            "report **out-of-sample** 5-fold cross-validated R²."
            "\n\n"
            "| Model | Functional form | CV R² | ± s.d. |\n"
            "|---|---|---|---|\n"
            "{rows}\n\n"
            "**Reading.** With N=57 countries and 4 predictors, any flexible model needs "
            "strong regularisation to avoid memorising the sample. Plain log-linear OLS is "
            "transparent but under-fits. Adding the Spend×GovEff interaction worsens "
            "validation (more parameters, no extra signal). **Ridge polynomial regression** "
            "(degree 2, α=5) is the best out-of-sample compromise: it captures curvatures "
            "and interactions across all 4 inputs, while L2 keeps overfitting in check. The "
            "**MLP** with 4 hidden units reaches similar performance but loses the "
            "interpretability of coefficients."
            "\n\n"
            "Even so, the **efficiency index is still built from M3 OLS**, for three "
            "reasons: (i) coefficients have a direct interpretation as elasticities; (ii) "
            "HC1-robust standard errors and the 2SLS robustness check are well-established "
            "for that specification; (iii) at N=57 the 0.52 → 0.65 R² gap is partly noise "
            "(CV s.d. ≈ 0.2). The non-linear models act as a **methodological complement**: "
            "they show some non-linear signal exists but not enough to abandon the "
            "interpretable specification."
        ),
        "meth_2sls": "2SLS robustness check",
        "meth_2sls_md": (
            "The notebook re-estimates M3 by 2SLS using lagged per-student spending "
            "(2005–2014) as instrument for current spending. First-stage F-statistic is 128, "
            r"well above the conventional threshold of 10. The 2SLS coefficient on $\ln(\text{Spend})$ is moderately higher than OLS, consistent with downward bias in OLS. The "
            "dashboard index is built from OLS predictions; 2SLS is reported in the notebook "
            "as a sensitivity check."
        ),
        "meth_pred_causal": "Prediction versus causal identification",
        "meth_pred_causal_md": (
            "OLS is appropriate because the objective is prediction of PISA given inputs, not "
            "recovery of causal elasticities. Causal identification would require panel data "
            "with within-country variation or stronger instruments, which is left for "
            "follow-up work."
        ),
        "meth_diag": "Model diagnostics",
        "meth_diag_pred_actual": "Predicted vs actual PISA",
        "meth_diag_resid_hist": "Residual distribution (log)",
        "meth_diag_resid_fitted": "Residuals vs fitted",
        "residual_log": "Residual log(actual PISA) − log(predicted PISA)",
        "meth_limits": "Limitations",
        "meth_limits_md": (
            "1. Cross-section of 57 countries — limited statistical power.\n"
            "2. PISA captures one cohort and three subjects.\n"
            "3. Spending observations span 2015–2018, not 2022.\n"
            "4. Sociodemographic controls limited to GDP, MYS and GovEff.\n"
            "5. Government Effectiveness is a perception-based composite."
        ),
        "meth_refs": "References",
        "meth_refs_md": (
            "- Hanushek, E. A. (2020). *Education production functions*. The Economics of Education, 2nd ed., Elsevier.\n"
            "- Hanushek, E. A. (1986). The economics of schooling: Production and efficiency in public schools. *Journal of Economic Literature*, 24(3).\n"
            "- Dee, T. S. (2005). Expense preference and student achievement in school districts. *Eastern Economic Journal*, 31(1).\n"
            "- Acemoglu, D., Johnson, S., & Robinson, J. A. (2012). *Why Nations Fail*. Crown Business.\n"
            "- Kaufmann, D., & Kraay, A. (2024). *Worldwide Governance Indicators — 2024 Methodology Update*. World Bank."
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


@st.cache_data(show_spinner=False)
def fit_m3(_mtime_key):
    df = load_efficiency(_mtime_key).dropna(
        subset=["spend_per_student", "gdp_per_capita", "years_schooling", "gov_eff", "pisa_score"]
    )
    y = np.log(df["pisa_score"].astype(float)).values
    X = np.column_stack([
        np.ones(len(df)),
        np.log(df["spend_per_student"].astype(float).values),
        np.log(df["gdp_per_capita"].astype(float).values),
        np.log(df["years_schooling"].astype(float).values),
        df["gov_eff"].astype(float).values,
    ])
    model = sm.OLS(y, X).fit(cov_type="HC1")
    keys = ["const", "ln_spend", "ln_gdp", "ln_mys", "gov_eff"]
    return {
        "params": dict(zip(keys, model.params)),
        "rsquared_adj": float(model.rsquared_adj),
        "n": int(model.nobs),
    }


@st.cache_data(show_spinner=False)
def cv_model_comparison(_mtime_key, n_splits=5, seed=42):
    """5-fold cross-validated R² for OLS, OLS with interaction, Ridge polynomial,
    and a small MLP. Reports out-of-sample fit so models that overfit (e.g., raw
    polynomial without regularisation, deep MLP) are penalised. With N=57 this
    matters a lot — only mildly non-linear models with strong regularisation
    actually generalise."""
    import warnings
    warnings.filterwarnings("ignore")
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.pipeline import Pipeline
    from sklearn.neural_network import MLPRegressor
    from sklearn.model_selection import KFold, cross_val_score

    df = load_efficiency(_mtime_key).dropna(
        subset=["spend_per_student", "gdp_per_capita", "years_schooling", "gov_eff", "pisa_score"]
    )
    y = np.log(df["pisa_score"].astype(float).values)
    X = np.column_stack([
        np.log(df["spend_per_student"].astype(float)),
        np.log(df["gdp_per_capita"].astype(float)),
        np.log(df["years_schooling"].astype(float)),
        df["gov_eff"].astype(float).values,
    ])
    X_int = np.column_stack([X, X[:, 0] * X[:, 3]])  # Spend × GovEff interaction
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)

    models = {
        "M3 — OLS log-linear": Pipeline([
            ("s", StandardScaler()),
            ("lr", LinearRegression()),
        ]),
        "M3+ — OLS + Spend×GovEff": Pipeline([
            ("s", StandardScaler()),
            ("lr", LinearRegression()),
        ]),
        "M5 — Ridge polynomial (d=2, α=5)": Pipeline([
            ("s", StandardScaler()),
            ("p", PolynomialFeatures(degree=2, include_bias=False)),
            ("r", Ridge(alpha=5.0)),
        ]),
        "M6 — MLP (1 camada, 4 neurônios, α=1, tanh)": Pipeline([
            ("s", StandardScaler()),
            ("m", MLPRegressor(
                hidden_layer_sizes=(4,), alpha=1.0, activation="tanh",
                solver="lbfgs", max_iter=5000, random_state=seed,
            )),
        ]),
    }

    rows = []
    for name, pipe in models.items():
        Xi = X_int if "Spend×GovEff" in name else X
        scores = cross_val_score(pipe, Xi, y, cv=kf, scoring="r2")
        rows.append({
            "Modelo": name,
            "CV R²": float(scores.mean()),
            "Desvio": float(scores.std()),
            "Tipo": "Linear" if "OLS" in name else ("Polinomial" if "polynomial" in name.lower() or "polin" in name.lower() else "Rede neural"),
        })
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def bootstrap_z(_mtime_key, B=300, seed=42):
    df = load_efficiency(_mtime_key).dropna(
        subset=["spend_per_student", "gdp_per_capita", "years_schooling", "gov_eff", "pisa_score"]
    ).reset_index(drop=True)
    n = len(df)
    rng = np.random.default_rng(seed)

    y = np.log(df["pisa_score"].astype(float)).values
    X = np.column_stack([
        np.ones(n),
        np.log(df["spend_per_student"].astype(float).values),
        np.log(df["gdp_per_capita"].astype(float).values),
        np.log(df["years_schooling"].astype(float).values),
        df["gov_eff"].astype(float).values,
    ])

    z_boot = np.zeros((B, n))
    for b in range(B):
        idx = rng.integers(0, n, size=n)
        try:
            beta, *_ = np.linalg.lstsq(X[idx], y[idx], rcond=None)
        except np.linalg.LinAlgError:
            continue
        resid = y - X @ beta
        sigma = resid.std(ddof=1)
        if sigma == 0:
            continue
        z_boot[b] = (resid - resid.mean()) / sigma

    return pd.DataFrame({
        "geo": df["geo"].tolist(),
        "z_lo": np.percentile(z_boot, 2.5, axis=0),
        "z_hi": np.percentile(z_boot, 97.5, axis=0),
    })


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
    """Render a plotly figure with transparent backgrounds so the page theme shows through."""
    fig.update_layout(
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
    st.plotly_chart(fig, **kwargs)


def render_html_table(df, fmt=None, max_height_px=420):
    """Render a DataFrame as themed HTML so it inherits the page theme
    instead of the default Streamlit white frame."""
    styler = df.style
    if fmt:
        styler = styler.format(fmt)
    styler = styler.hide(axis="index")
    html = styler.to_html()
    bg = T["bg"]
    sec = T["secondary_bg"]
    txt = T["text"]
    bd = T["border"]
    wrapped = (
        f"<div style='max-height:{max_height_px}px;overflow:auto;border:1px solid {bd};border-radius:8px;'>"
        f"<style>"
        f".themed-tbl table {{border-collapse:collapse;width:100%;background:{bg};color:{txt};}}"
        f".themed-tbl th {{background:{sec};color:{txt};text-align:left;padding:8px 12px;"
        f"position:sticky;top:0;border-bottom:1px solid {bd};}}"
        f".themed-tbl td {{padding:6px 12px;border-bottom:1px solid {bd};}}"
        f".themed-tbl tr:hover td {{background:{sec};}}"
        f"</style>"
        f"<div class='themed-tbl'>{html}</div></div>"
    )
    st.markdown(wrapped, unsafe_allow_html=True)


# ============================================================
# CSS injection (theme-aware, full coverage)
# ============================================================

st.markdown(
    f"""
    <style>
    /* Main containers */
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

    /* Sidebar: reduce gaps and remove inner separators */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 0.55rem; }}
    [data-testid="stSidebar"] hr {{ display: none; }}
    [data-testid="stSidebar"] .stRadio > label,
    [data-testid="stSidebar"] .stSelectbox > label,
    [data-testid="stSidebar"] .stMultiSelect > label {{
        font-size: 0.8rem;
        opacity: 0.78;
        margin-bottom: 0.15rem;
    }}

    /* Text colour: forcefully theme everything that renders text */
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

    /* Inline code: kill the white box on dark, keep readable on light */
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

    /* Metric cards */
    [data-testid="stMetric"] {{
        background: {T['secondary_bg']};
        border: 1px solid {T['border']};
        padding: 14px 18px;
        border-radius: 10px;
    }}
    [data-testid="stMetricValue"] {{ color: {T['text']} !important; }}
    [data-testid="stMetricLabel"] {{ color: {T['text']} !important; opacity: 0.85; }}
    [data-testid="stMetricDelta"] {{ color: {T['text']} !important; }}

    /* Tabs */
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

    /* Inputs: subtle background, no harsh border */
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

    /* Dropdown popover: was unreadable in dark mode */
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

    /* Buttons */
    .stDownloadButton button, .stButton button {{
        background: {T['secondary_bg']};
        border: 1px solid {T['border']};
        color: {T['text']};
    }}
    .stDownloadButton button:hover, .stButton button:hover {{
        border-color: #2E86AB;
    }}

    /* Tables / dataframes */
    [data-testid="stDataFrame"] {{
        background: {T['bg']};
    }}
    .stApp table th {{
        background: {T['table_header_bg']} !important;
        color: {T['text']} !important;
    }}
    .stApp table td {{ color: {T['text']} !important; }}

    /* Expander used for the data sources block */
    [data-testid="stExpander"] {{
        border: 1px solid {T['border']} !important;
        background: transparent !important;
    }}
    [data-testid="stExpander"] summary {{ color: {T['text']} !important; }}

    /* Footnote and dividers */
    .footnote {{ color: {T['muted']}; font-size: 0.85rem; }}
    hr {{ border-color: {T['border']}; }}

    /* Alerts: keep contrast */
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
        f"{DATA_DIR}/API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_216039.csv",
        f"{DATA_DIR}/API_SP.POP.TOTL_DS2_en_csv_v2_246068.csv",
        f"{DATA_DIR}/hdr-data.xlsx",
        f"{DATA_DIR}/pisa_master_dataset.csv",
    )
    panel = load_panel(_mtime(*panel_files))
    eff_mtime = _mtime(f"{DATA_DIR}/efficiency_index.csv")
    eff = load_efficiency(eff_mtime)
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

    y_axis_choice = st.radio(
        t("y_axis"),
        [t("y_mys"), t("y_pisa")],
        index=0,
    )

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
# Build view panel
# ============================================================

if y_axis_choice == t("y_mys"):
    y_col, y_label = "years_schooling", t("y_mys")
else:
    y_col, y_label = "pisa_score", t("y_pisa")

view_panel = panel[panel["geo"].isin(country_list)].dropna(
    subset=["gdp_per_capita", y_col]
).copy()
view_panel["population_for_size"] = view_panel["population"].fillna(1)

# PISA wave coverage is heterogeneous: 38 of 84 countries only have 2022 data
# (those joined the assessment for the first time in 2022). Animating the
# cross-section across waves spawns and despawns bubbles, which is visually
# misleading. We render PISA as a static 2022 cross-section instead, with an
# optional historical trend chart for countries with longitudinal coverage.
if y_col == "pisa_score":
    pisa_panel_full = view_panel.sort_values(["geo", "year"]).copy()
    view_panel = view_panel[view_panel["year"] == 2022].copy()
else:
    pisa_panel_full = None


# ============================================================
# Tabs
# ============================================================

tab_panel, tab_efficiency, tab_drivers, tab_simulator, tab_methodology = st.tabs([
    t("tab_panel"),
    t("tab_efficiency"),
    t("tab_drivers"),
    t("tab_simulator"),
    t("tab_methodology"),
])


# ------------------------------------------------------------
# Tab: Historical Panel
# ------------------------------------------------------------

with tab_panel:
    st.subheader(t("panel_subtitle", group=selected_group, metric=y_label))

    if y_col == "pisa_score":
        st.markdown(
            f"<span class='footnote'>{t('panel_pisa_note')}</span>",
            unsafe_allow_html=True,
        )

    if view_panel.empty:
        st.warning(t("no_data_warning", metric=y_label, group=selected_group))
    else:
        latest_year = int(view_panel["year"].max())
        first_year = int(view_panel["year"].min())
        latest = view_panel[view_panel["year"] == latest_year]
        years_text = f"{first_year}" if first_year == latest_year else f"{first_year} – {latest_year}"

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t("m_countries"), f"{view_panel['geo'].nunique()}")
        c2.metric(t("m_years"), years_text)
        c3.metric(
            t("m_median_gdp", year=latest_year),
            f"${latest['gdp_per_capita'].median():,.0f}" if not latest.empty else "—",
        )
        c4.metric(
            t("m_median_y", metric=y_label, year=latest_year),
            f"{latest[y_col].median():.1f}" if not latest.empty else "—",
        )

        min_x = view_panel["gdp_per_capita"].min() * 0.8
        max_x = view_panel["gdp_per_capita"].max() * 1.2
        min_y = view_panel[y_col].min() * 0.95
        max_y = view_panel[y_col].max() * 1.05

        bubble_line = "rgba(0,0,0,0.55)" if st.session_state.theme == "light" else "rgba(255,255,255,0.55)"
        hover_template = (
            "<b>%{hovertext}</b><br>"
            f"{t('x_label_short')}: %{{customdata[0]:,.0f}}<br>"
            f"{t('population')}: %{{customdata[2]}}<br>"
            + y_label + ": %{customdata[3]:.2f}<extra></extra>"
        )
        highlight_set = set(highlight_names) if highlight_names else set()

        if y_col == "years_schooling":
            fig = px.scatter(
                view_panel,
                x="gdp_per_capita", y=y_col,
                animation_frame="year", animation_group="name",
                size="population_for_size", color="name", hover_name="name",
                custom_data=["gdp_per_capita", "population", "population_str", y_col],
                log_x=True, size_max=55,
                range_x=[min_x, max_x], range_y=[min_y, max_y],
                labels={
                    "gdp_per_capita": t("x_label"),
                    y_col: y_label,
                    "name": t("country"),
                    "year": t("year"),
                },
                template=TEMPLATE,
            )

            def _style_traces(traces):
                for trace in traces:
                    if hasattr(trace, "marker") and trace.marker is not None:
                        trace.marker.line.color = bubble_line
                        trace.marker.line.width = 0.7
                    trace.hovertemplate = hover_template
                    if highlight_set:
                        trace.opacity = 1.0 if trace.name in highlight_set else 0.18
                    else:
                        trace.opacity = 0.85

            _style_traces(fig.data)
            for frame in fig.frames or []:
                _style_traces(frame.data)

            fig.update_layout(
                height=620,
                legend_title_text=t("country"),
                transition=dict(duration=400, easing="cubic-in-out"),
            )
            if fig.layout.updatemenus:
                for menu in fig.layout.updatemenus:
                    for button in menu.buttons:
                        if button.label == "▶":
                            button.args[1]["frame"]["duration"] = 200
                            button.args[1]["transition"]["duration"] = 200
            show_chart(fig, width="stretch")

        else:  # PISA: static 2022 cross-section
            fig = px.scatter(
                view_panel,
                x="gdp_per_capita", y=y_col,
                size="population_for_size", color="name", hover_name="name",
                custom_data=["gdp_per_capita", "population", "population_str", y_col],
                log_x=True, size_max=55,
                range_x=[min_x, max_x], range_y=[min_y, max_y],
                labels={
                    "gdp_per_capita": t("x_label"),
                    y_col: y_label,
                    "name": t("country"),
                },
                template=TEMPLATE,
            )
            for trace in fig.data:
                if hasattr(trace, "marker") and trace.marker is not None:
                    trace.marker.line.color = bubble_line
                    trace.marker.line.width = 0.7
                trace.hovertemplate = hover_template
                if highlight_set:
                    trace.opacity = 1.0 if trace.name in highlight_set else 0.18
                else:
                    trace.opacity = 0.85
            fig.update_layout(height=620, legend_title_text=t("country"))
            show_chart(fig, width="stretch")

            # Trend chart for countries with longitudinal coverage (≥3 waves)
            if pisa_panel_full is not None:
                wave_counts = pisa_panel_full.groupby("geo")["year"].nunique()
                trend_geos = wave_counts[wave_counts >= 3].index
                trend_df = pisa_panel_full[pisa_panel_full["geo"].isin(trend_geos)].copy()
                if not trend_df.empty:
                    st.markdown(f"#### {t('panel_pisa_trend_title')}")
                    trend_fig = px.line(
                        trend_df.sort_values(["name", "year"]),
                        x="year", y="pisa_score", color="name",
                        markers=True, hover_name="name",
                        labels={"year": t("year"), "pisa_score": y_label, "name": t("country")},
                        template=TEMPLATE,
                    )
                    if highlight_set:
                        for trace in trend_fig.data:
                            trace.opacity = 1.0 if trace.name in highlight_set else 0.18
                    trend_fig.update_layout(height=440, legend_title_text=t("country"))
                    show_chart(trend_fig, width="stretch")
                    st.markdown(
                        f"<span class='footnote'>{t('panel_pisa_trend_note', n=len(trend_geos))}</span>",
                        unsafe_allow_html=True,
                    )

        st.markdown(
            f"<span class='footnote'>{t('footnote_bubble')}</span>",
            unsafe_allow_html=True,
        )

        view_csv = view_panel.drop(columns=["population_for_size"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            t("download_panel_csv"),
            data=view_csv,
            file_name=f"panel_{selected_group}_{y_col}.csv",
            mime="text/csv",
        )


# ------------------------------------------------------------
# Tab: Efficiency
# ------------------------------------------------------------

with tab_efficiency:
    st.subheader(t("eff_subtitle"))
    st.markdown(t("eff_description"))

    eff_filtered = eff[eff["geo"].isin(country_list)].copy()
    if len(eff_filtered) < 3:
        match_count = len(eff_filtered)
        eff_filtered = eff.copy()
        st.info(t("eff_warning_few", n=match_count, group=selected_group, total=len(eff_filtered)))

    sort_choice = st.radio(
        t("eff_rank_by"),
        [t("eff_z_label"), t("eff_per_1k_label")],
        horizontal=True,
        help=t("eff_rank_by_help"),
    )
    sort_col = "efficiency_z" if sort_choice == t("eff_z_label") else "pisa_per_1k_usd"
    eff_filtered = eff_filtered.sort_values(sort_col, ascending=True).reset_index(drop=True)
    best = eff_filtered.iloc[-1]
    worst = eff_filtered.iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric(t("eff_most_efficient"), best["name"], f"z = {best['efficiency_z']:+.2f}")
    c2.metric(t("eff_least_efficient"), worst["name"], f"z = {worst['efficiency_z']:+.2f}")
    c3.metric(t("eff_sample_size"), t("eff_n_countries", n=len(eff_filtered)))

    show_ci = st.checkbox(t("eff_show_ci"), value=False, help=t("eff_show_ci_help"))

    bar_kwargs = dict(
        x=sort_col,
        y="name",
        orientation="h",
        color="efficiency_z",
        color_continuous_scale=DIVERGING,
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
            "efficiency_z": t("eff_z_label"),
            "pisa_per_1k_usd": t("eff_per_1k_label"),
            "name": "",
        },
        template=TEMPLATE,
    )

    if show_ci and sort_col == "efficiency_z":
        with st.spinner(t("computing_ci")):
            boot_df = bootstrap_z(eff_mtime)
        eff_filtered = eff_filtered.merge(boot_df, on="geo", how="left")
        eff_filtered["err_minus"] = (eff_filtered["efficiency_z"] - eff_filtered["z_lo"]).clip(lower=0).fillna(0)
        eff_filtered["err_plus"] = (eff_filtered["z_hi"] - eff_filtered["efficiency_z"]).clip(lower=0).fillna(0)
        bar_kwargs["error_x"] = "err_plus"
        bar_kwargs["error_x_minus"] = "err_minus"

    bar = px.bar(eff_filtered, **bar_kwargs)
    if show_ci and sort_col == "efficiency_z":
        bar.update_traces(error_x=dict(color=T["text"], thickness=1.4, width=4))
    bar.update_layout(
        height=max(420, 18 * len(eff_filtered)),
        coloraxis_colorbar_title="z",
    )
    bar.add_vline(x=0, line_color=T["zero_line"], line_width=0.5, opacity=0.6)
    show_chart(bar, width="stretch")

    eff_csv = eff.to_csv(index=False).encode("utf-8")
    st.download_button(
        t("download_efficiency_csv"),
        data=eff_csv,
        file_name="efficiency_index.csv",
        mime="text/csv",
    )

    st.markdown(f"#### {t('spending_vs_score')}")
    fit = eff_filtered.dropna(subset=["spend_per_student", "pisa_score"]).copy()
    scatter = px.scatter(
        fit,
        x="spend_per_student",
        y="pisa_score",
        color="efficiency_z",
        color_continuous_scale=DIVERGING,
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
            "spend_per_student": t("driver_spend_axis"),
            "pisa_score": t("pisa_2022"),
            "efficiency_z": t("eff_z_label"),
        },
        log_x=True,
        template=TEMPLATE,
    )
    scatter.update_traces(
        textposition="top center",
        textfont=dict(size=13, color=T["text"], family="Arial"),
        marker=dict(size=14, opacity=0.85, line=dict(color=T["text"], width=0.6)),
        selector=dict(mode="markers+text"),
    )
    if len(fit) >= 5:
        ln_x = np.log(fit["spend_per_student"])
        slope, intercept = np.polyfit(ln_x, fit["pisa_score"], 1)
        x_grid = np.linspace(fit["spend_per_student"].min(), fit["spend_per_student"].max(), 80)
        scatter.add_trace(
            go.Scatter(
                x=x_grid,
                y=intercept + slope * np.log(x_grid),
                mode="lines",
                line=dict(color=T["fit_line"], dash="dash"),
                name=t("empirical_fit"),
                showlegend=True,
            )
        )
    scatter.update_layout(height=560)
    show_chart(scatter, width="stretch")

    with st.expander(t("country_table")):
        display = eff_filtered[
            ["name", "geo", "pisa_score", "pisa_pred", "spend_per_student", "spend_year",
             "years_schooling", "gdp_per_capita", "gov_eff", "xpd_pct_gdp", "efficiency_z"]
        ].rename(columns={
            "name": t("col_country"),
            "geo": t("col_iso"),
            "pisa_score": t("col_pisa_actual"),
            "pisa_pred": t("col_pisa_pred"),
            "spend_per_student": t("col_spend"),
            "spend_year": t("col_spend_year"),
            "years_schooling": t("col_mys"),
            "gdp_per_capita": t("col_gdp"),
            "gov_eff": t("col_gov"),
            "xpd_pct_gdp": t("col_xpd"),
            "efficiency_z": t("col_z"),
        })
        render_html_table(display, fmt={
            t("col_pisa_actual"): "{:.0f}",
            t("col_pisa_pred"): "{:.0f}",
            t("col_spend"): "{:,.0f}",
            t("col_spend_year"): "{:.0f}",
            t("col_mys"): "{:.1f}",
            t("col_gdp"): "{:,.0f}",
            t("col_gov"): "{:+.2f}",
            t("col_xpd"): "{:.1f}",
            t("col_z"): "{:+.2f}",
        }, max_height_px=420)


# ------------------------------------------------------------
# Tab: Drivers Correlations
# ------------------------------------------------------------

with tab_drivers:
    st.subheader(t("drivers_subtitle"))
    st.markdown(t("drivers_description"))

    drivers = [
        ("spend_per_student", t("driver_spend"), t("driver_spend_axis"), True),
        ("gdp_per_capita", t("driver_gdp"), t("driver_gdp_axis"), True),
        ("years_schooling", t("driver_mys"), t("driver_mys_axis"), False),
        ("gov_eff", t("driver_gov"), t("driver_gov_axis"), False),
    ]

    for col, short_label, axis_label, log_x in drivers:
        sub = eff.dropna(subset=[col, "pisa_score"])
        r = sub[col].corr(sub["pisa_score"])

        c1, c2 = st.columns([1, 3])
        c1.metric(
            short_label,
            f"r = {r:+.2f}",
            help=t("driver_help", label=short_label.lower(), n=len(sub)),
        )
        with c2:
            scat = px.scatter(
                sub,
                x=col, y="pisa_score",
                text="geo",
                color="efficiency_z",
                color_continuous_scale=DIVERGING,
                color_continuous_midpoint=0,
                hover_data={"name": True, col: ":,.2f", "pisa_score": ":.0f", "geo": False},
                log_x=log_x,
                template=TEMPLATE,
                labels={col: axis_label, "pisa_score": t("pisa_2022")},
            )
            scat.update_traces(
                textposition="top center",
                textfont=dict(size=12, color=T["text"], family="Arial"),
                marker=dict(size=11, opacity=0.85, line=dict(color=T["text"], width=0.5)),
                selector=dict(mode="markers+text"),
            )
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
            scat.add_trace(go.Scatter(
                x=xline, y=yline, mode="lines",
                line=dict(color=T["fit_line"], dash="dash"),
                name="OLS fit", showlegend=False,
            ))
            scat.update_layout(height=380, margin=dict(t=20, b=20))
            show_chart(scat, width="stretch")


# ------------------------------------------------------------
# Tab: Simulator
# ------------------------------------------------------------

with tab_simulator:
    st.subheader(t("sim_subtitle"))
    st.markdown(t("sim_description"))

    ols = fit_m3(eff_mtime)
    params = ols["params"]

    eff_sim = eff.dropna(
        subset=["spend_per_student", "gdp_per_capita", "years_schooling", "gov_eff", "pisa_score", "pisa_pred"]
    ).copy()
    countries_sim = sorted(eff_sim["name"].tolist())
    default_idx = countries_sim.index("Brazil") if "Brazil" in countries_sim else 0

    sel_col, btn_col = st.columns([4, 1])
    with sel_col:
        base_country = st.selectbox(t("sim_baseline"), options=countries_sim, index=default_idx)
    with btn_col:
        st.markdown("<div style='height:1.7rem;'></div>", unsafe_allow_html=True)
        reset_clicked = st.button(t("sim_reset"), help=t("sim_reset_help"), use_container_width=True)

    base_row = eff_sim[eff_sim["name"] == base_country].iloc[0]
    base_spend = float(base_row["spend_per_student"])
    base_gdp = float(base_row["gdp_per_capita"])
    base_mys = float(base_row["years_schooling"])
    base_gov = float(base_row["gov_eff"])

    if "sim_version" not in st.session_state:
        st.session_state.sim_version = 0
    if reset_clicked:
        st.session_state.sim_version += 1
        st.rerun()

    suffix = f"{base_country}_{st.session_state.sim_version}"

    spend_min, spend_max = float(eff_sim["spend_per_student"].min()), float(eff_sim["spend_per_student"].max())
    gdp_min, gdp_max = float(eff_sim["gdp_per_capita"].min()), float(eff_sim["gdp_per_capita"].max())
    mys_min, mys_max = float(eff_sim["years_schooling"].min()), float(eff_sim["years_schooling"].max())
    gov_min, gov_max = float(eff_sim["gov_eff"].min()), float(eff_sim["gov_eff"].max())

    c1, c2 = st.columns(2)
    with c1:
        spend = st.slider(
            t("sim_spend"),
            min_value=max(100.0, spend_min * 0.5),
            max_value=spend_max * 1.5,
            value=base_spend,
            step=max(50.0, (spend_max - spend_min) / 100),
            format="$%.0f",
            key=f"sim_spend_{suffix}",
        )
        gdp = st.slider(
            t("sim_gdp"),
            min_value=max(500.0, gdp_min * 0.5),
            max_value=gdp_max * 1.5,
            value=base_gdp,
            step=max(100.0, (gdp_max - gdp_min) / 100),
            format="$%.0f",
            key=f"sim_gdp_{suffix}",
        )
    with c2:
        mys = st.slider(
            t("sim_mys"),
            min_value=max(1.0, mys_min * 0.6),
            max_value=mys_max * 1.2,
            value=base_mys,
            step=0.1,
            format="%.1f",
            key=f"sim_mys_{suffix}",
        )
        gov = st.slider(
            t("sim_gov"),
            min_value=gov_min - 0.5,
            max_value=gov_max + 0.5,
            value=base_gov,
            step=0.05,
            format="%+.2f",
            key=f"sim_gov_{suffix}",
        )

    log_pred_baseline = (
        params["const"]
        + params["ln_spend"] * np.log(base_spend)
        + params["ln_gdp"] * np.log(base_gdp)
        + params["ln_mys"] * np.log(base_mys)
        + params["gov_eff"] * base_gov
    )
    log_pred_new = (
        params["const"]
        + params["ln_spend"] * np.log(spend)
        + params["ln_gdp"] * np.log(gdp)
        + params["ln_mys"] * np.log(mys)
        + params["gov_eff"] * gov
    )
    pred_baseline = float(np.exp(log_pred_baseline))
    pred_new = float(np.exp(log_pred_new))
    actual = float(base_row["pisa_score"])

    c1, c2, c3 = st.columns(3)
    c1.metric(t("sim_pisa_actual"), f"{actual:.0f}")
    c2.metric(
        t("sim_pisa_baseline_pred"),
        f"{pred_baseline:.0f}",
        delta=f"{pred_baseline - actual:+.0f} {t('vs_actual')}",
    )
    c3.metric(
        t("sim_pisa_new_pred"),
        f"{pred_new:.0f}",
        delta=f"{pred_new - pred_baseline:+.0f} {t('vs_baseline')}",
    )

    contrib_log = {
        t("driver_spend"): params["ln_spend"] * (np.log(spend) - np.log(base_spend)),
        t("driver_gdp"): params["ln_gdp"] * (np.log(gdp) - np.log(base_gdp)),
        t("driver_mys"): params["ln_mys"] * (np.log(mys) - np.log(base_mys)),
        t("driver_gov"): params["gov_eff"] * (gov - base_gov),
    }
    contrib_df = pd.DataFrame({
        "variable": list(contrib_log.keys()),
        "delta_pisa": [d * pred_baseline for d in contrib_log.values()],
    })

    st.markdown(f"#### {t('sim_contributions')}")
    contrib_fig = px.bar(
        contrib_df,
        x="delta_pisa",
        y="variable",
        orientation="h",
        color="delta_pisa",
        color_continuous_scale=DIVERGING,
        color_continuous_midpoint=0,
        labels={"delta_pisa": t("sim_contribution_axis"), "variable": ""},
        template=TEMPLATE,
    )
    contrib_fig.update_layout(height=300, coloraxis_showscale=False)
    contrib_fig.add_vline(x=0, line_color=T["zero_line"], line_width=0.5, opacity=0.6)
    show_chart(contrib_fig, width="stretch")

    st.markdown(
        f"<span class='footnote'>{t('sim_footnote', adj_r=ols['rsquared_adj'], n=ols['n'])}</span>",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# Tab: Methodology
# ------------------------------------------------------------

with tab_methodology:
    st.subheader(t("tab_methodology"))

    st.markdown(f"### {t('meth_specification')}")
    st.markdown(t("meth_specification_md"))

    st.markdown(f"### {t('meth_variables')}")
    st.markdown(t("meth_variables_md"))

    st.markdown(f"### {t('meth_search')}")
    st.markdown(t("meth_search_md"))

    st.markdown(f"### {t('meth_nonlinear')}")
    cv_df = cv_model_comparison(eff_mtime)
    cv_rows = "\n".join(
        f"| {r['Modelo']} | {r['Tipo']} | {r['CV R²']:.3f} | {r['Desvio']:.3f} |"
        for _, r in cv_df.iterrows()
    )
    st.markdown(t("meth_nonlinear_md").format(rows=cv_rows))

    st.markdown(f"### {t('meth_2sls')}")
    st.markdown(t("meth_2sls_md"))

    st.markdown(f"### {t('meth_pred_causal')}")
    st.markdown(t("meth_pred_causal_md"))

    st.markdown(f"### {t('meth_diag')}")

    eff_diag = eff.dropna(subset=["pisa_pred", "pisa_score"]).copy()
    eff_diag["log_resid"] = np.log(eff_diag["pisa_score"]) - np.log(eff_diag["pisa_pred"])

    cd1, cd2 = st.columns(2)
    with cd1:
        st.markdown(f"**{t('meth_diag_pred_actual')}**")
        diag1 = px.scatter(
            eff_diag,
            x="pisa_pred", y="pisa_score",
            text="geo",
            labels={"pisa_pred": t("col_pisa_pred"), "pisa_score": t("col_pisa_actual")},
            template=TEMPLATE,
            hover_data={"name": True, "geo": False},
        )
        line_min = float(min(eff_diag["pisa_pred"].min(), eff_diag["pisa_score"].min()))
        line_max = float(max(eff_diag["pisa_pred"].max(), eff_diag["pisa_score"].max()))
        diag1.add_trace(go.Scatter(
            x=[line_min, line_max], y=[line_min, line_max], mode="lines",
            line=dict(color=T["fit_line"], dash="dash"), name="y = x", showlegend=False,
        ))
        diag1.update_traces(
            textposition="top center",
            textfont=dict(size=11, color=T["text"], family="Arial"),
            marker=dict(size=10, opacity=0.85, line=dict(color=T["text"], width=0.5)),
            selector=dict(mode="markers+text"),
        )
        diag1.update_layout(height=380, margin=dict(t=20, b=20))
        show_chart(diag1, width="stretch")

    with cd2:
        st.markdown(f"**{t('meth_diag_resid_hist')}**")
        diag2 = px.histogram(
            eff_diag,
            x="log_resid",
            nbins=20,
            labels={"log_resid": t("residual_log")},
            template=TEMPLATE,
        )
        diag2.update_traces(marker_color="#2E86AB")
        diag2.add_vline(x=0, line_color=T["zero_line"], line_width=0.5, opacity=0.6)
        diag2.update_layout(height=380, showlegend=False, margin=dict(t=20, b=20))
        show_chart(diag2, width="stretch")

    st.markdown(f"**{t('meth_diag_resid_fitted')}**")
    diag3 = px.scatter(
        eff_diag,
        x="pisa_pred", y="log_resid",
        text="geo",
        labels={"pisa_pred": t("col_pisa_pred"), "log_resid": t("residual_log")},
        template=TEMPLATE,
        hover_data={"name": True, "geo": False},
    )
    diag3.add_hline(y=0, line_color=T["zero_line"], line_width=0.5, opacity=0.6)
    diag3.update_traces(
        textposition="top center",
        textfont=dict(size=11, color=T["text"], family="Arial"),
        marker=dict(size=10, opacity=0.85, line=dict(color=T["text"], width=0.5)),
        selector=dict(mode="markers+text"),
    )
    diag3.update_layout(height=380, margin=dict(t=20, b=20))
    show_chart(diag3, width="stretch")

    st.markdown(f"### {t('meth_limits')}")
    st.markdown(t("meth_limits_md"))

    st.markdown(f"### {t('meth_refs')}")
    st.markdown(t("meth_refs_md"))
