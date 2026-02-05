import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Wealth vs Education",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Wealth & Education: What's the Relationship?")
st.markdown("This interactive application analyzes the historical correlation between **GDP per Capita (PPP)** and **Mean Years of Schooling** across countries from 1990 to 2023.")
st.divider()

@st.cache_data
def load_data():
    df_wb = pd.read_csv('API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_216039.csv', skiprows=4)
    fixed_cols = ['Country Code', 'Country Name']
    years = [str(y) for y in range(1990, 2024)]
    existing_cols = [c for c in fixed_cols + years if c in df_wb.columns]
    
    df_gdp = df_wb[existing_cols].melt(
        id_vars=['Country Code', 'Country Name'], 
        var_name='year', 
        value_name='gdp_per_capita'
    )
    df_gdp = df_gdp.rename(columns={'Country Code': 'geo', 'Country Name': 'name'})
    df_gdp['year'] = pd.to_numeric(df_gdp['year'])
    df_gdp['geo'] = df_gdp['geo'].str.upper()

    df_education = pd.read_excel('hdr-data.xlsx')
    df_education.columns = df_education.columns.str.strip()
    df_education['year'] = pd.to_numeric(df_education['year'], errors='coerce')
    df_education = df_education[(df_education['year'] >= 1990) & (df_education['year'] <= 2023)]
    
    df_education_final = df_education[['countryIsoCode', 'year', 'value']].copy()
    df_education_final = df_education_final.rename(columns={'countryIsoCode': 'geo', 'value': 'years_schooling'})
    df_education_final['geo'] = df_education_final['geo'].str.upper()
    df_education_final['years_schooling'] = pd.to_numeric(df_education_final['years_schooling'], errors='coerce')

    df_population = pd.read_csv('API_SP.POP.TOTL_DS2_en_csv_v2_246068.csv', skiprows=4)
    existing_cols_pop = [c for c in fixed_cols + years if c in df_population.columns]
    df_population = df_population[existing_cols_pop].melt(
        id_vars=['Country Code', 'Country Name'],
        var_name='year',
        value_name='population'
    )
    df_population = df_population.rename(columns={'Country Code': 'geo', 'Country Name': 'name'})
    df_population['year'] = pd.to_numeric(df_population['year'])
    df_population['geo'] = df_population['geo'].str.upper()
    df_population['population'] = pd.to_numeric(df_population['population'], errors='coerce')

    df_final = pd.merge(df_gdp, df_education_final, on=['geo', 'year'], how='inner')
    df_final = pd.merge(df_final, df_population[['geo', 'year', 'population']], on=['geo', 'year'], how='left')
    df_final['population_str'] = df_final['population'].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) else "N/A"
    )
    return df_final

try:
    df = load_data()
except Exception as e:
    st.error("Error loading data. Please check the required files are present in the folder.")
    st.stop()

st.sidebar.header("Analysis Filters")

groups = {
    'G20': ['ARG', 'AUS', 'BRA', 'CAN', 'CHN', 'FRA', 'DEU', 'IND', 'IDN', 'ITA', 'JPN', 'KOR', 'MEX', 'RUS', 'SAU', 'ZAF', 'TUR', 'GBR', 'USA', 'ESP'],
    'BRICS (Expanded)': ['BRA', 'RUS', 'IND', 'CHN', 'ZAF', 'EGY', 'ETH', 'IRN', 'ARE', 'SAU'],
    'G7': ['CAN', 'FRA', 'DEU', 'ITA', 'JPN', 'GBR', 'USA'],
    'South America': ['ARG', 'BOL', 'BRA', 'CHL', 'COL', 'ECU', 'GUY', 'PRY', 'PER', 'SUR', 'URY', 'VEN'],
    'Latin America & Caribbean': ['ARG', 'BHS', 'BRB', 'BLZ', 'BOL', 'BRA', 'CHL', 'COL', 'CRI', 'CUB', 'DOM', 'ECU', 'SLV', 'GTM', 'GUY', 'HTI', 'HND', 'JAM', 'MEX', 'NIC', 'PAN', 'PRY', 'PER', 'SUR', 'TTO', 'URY', 'VEN'],
    'Asia (Major)': ['CHN', 'JPN', 'IND', 'KOR', 'IDN', 'SAU', 'TUR', 'THA', 'MYS', 'VNM', 'PHL', 'SGP', 'BGD', 'PAK'],
    'Europe (European Union)': ['AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE'],
    'Lusophone Countries': ['BRA', 'PRT', 'AGO', 'MOZ', 'CPV', 'GNB', 'STP', 'TLS'],
    'Asian Tigers (+ New)': ['KOR', 'SGP', 'HKG', 'TWN', 'MYS', 'THA', 'VNM', 'IDN'], 
    'OPEC + Others': ['SAU', 'ARE', 'KWT', 'QAT', 'OMN', 'NGA', 'VEN', 'DZA', 'AGO', 'IRN', 'IRQ', 'LBY', 'RUS', 'GUY']
}

groups['All countries'] = list(df['geo'].unique())

selected_group = st.sidebar.selectbox("Choose a Group:", list(groups.keys()))
country_list = groups[selected_group]

st.sidebar.divider()
st.sidebar.markdown("### Data Sources")
st.sidebar.markdown(
    """
    1. **Wealth (GDP PPP):**
    🔗 [World Bank](https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD)
    
    2. **Education (Mean Years of Schooling):**
    🔗 [UNDP HDR](https://hdr.undp.org/data-center/documentation-and-downloads)
    """
)

st.sidebar.divider()
st.sidebar.markdown("### Author")
st.sidebar.info(
    """
    **Thiago Alcebiades Rodrigues**
    
    [thiagoalcebiades@usp.br](mailto:thiagoalcebiades@usp.br)
    
    [LinkedIn Profile](https://www.linkedin.com/in/thiago-alcebiades-rodrigues-95446621b/)
    """
)

st.sidebar.caption(
    """
    **Inspiration:**
    This project was inspired by the work of [Hans Rosling](https://www.gapminder.org/) and the Gapminder foundation.
    """
)

df_filtered = df[df['geo'].isin(country_list)].dropna(subset=['gdp_per_capita', 'years_schooling']).copy()
df_filtered['population_for_size'] = df_filtered['population'].fillna(1)

st.subheader(f"Historical Evolution: {selected_group}")

if df_filtered.empty:
    st.warning("Insufficient data for this group.")
else:
    max_x = df_filtered['gdp_per_capita'].max() * 1.3
    
    fig = px.scatter(
        df_filtered, 
        x="gdp_per_capita", 
        y="years_schooling",
        animation_frame="year",      
        animation_group="name",     
        size="population_for_size",      
        color="name",                
        hover_name="name",  
        custom_data=["gdp_per_capita", "population", "population_str"],   
        log_x=True,                 
        size_max=60,
        range_x=[500, max_x],       
        range_y=[0, 16],
        labels={
            "gdp_per_capita": "GDP per Capita (US$ PPP)",
            "years_schooling": "Years of Schooling",
            "name": "Country",
            "year": "Year"
        }
    )
    
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b>\n"
            "GDP per Capita (US$ PPP): %{customdata[0]:,.2f}\n"
            "Population: %{customdata[2]}\n"
            "Years of Schooling: %{y:.2f}<extra></extra>"
        )
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)