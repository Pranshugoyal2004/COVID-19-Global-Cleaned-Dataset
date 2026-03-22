import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# ⚙️ Page Config
# -------------------------------
st.set_page_config(page_title="COVID Dashboard", layout="wide")

# -------------------------------
# 📂 Load Data (Cached)
# -------------------------------
@st.cache_data
def load_data():
    dataset = pd.read_csv("covid_19_clean_complete.csv")
    dataset['date'] = pd.to_datetime(df['date'])
    return df

dataset = load_data()

# -------------------------------
# 🎛️ Sidebar Filters
# -------------------------------
st.sidebar.header("Filters")

countries = st.sidebar.multiselect(
    "Country",
    dataset['_country_region'].unique(),
    default=dataset['_country_region'].unique()
)

regions = st.sidebar.multiselect(
    "WHO Region",
    dataset['who_region'].unique(),
    default=dataset['who_region'].unique()
)

date_range = st.sidebar.date_input(
    "Date Range",
    [dataset['date'].min(), dataset['date'].max()]
)

min_cases = st.sidebar.slider(
    "Minimum Confirmed Cases",
    0, int(dataset['confirmed'].max()), 1000
)

top_n = st.sidebar.slider("Top Countries", 5, 20, 10)

# Apply filters
filtered_df = dataset[
    (dataset['_country_region'].isin(countries)) &
    (dataset['who_region'].isin(regions)) &
    (dataset['date'] >= pd.to_datetime(date_range[0])) &
    (dataset['date'] <= pd.to_datetime(date_range[1])) &
    (dataset['confirmed'] >= min_cases)
]

latest = filtered_df[filtered_df['date'] == filtered_df['date'].max()].copy()

# -------------------------------
# 🏆 KPI CARDS
# -------------------------------
st.title("🌍 COVID-19 Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Cases", f"{int(latest['confirmed'].sum()):,}")
col2.metric("Total Deaths", f"{int(latest['deaths'].sum()):,}")
col3.metric("Total Recovered", f"{int(latest['recovered'].sum()):,}")
col4.metric("Active Cases", f"{int(latest['active'].sum()):,}")

# -------------------------------
# 📑 TABS
# -------------------------------
tab1, tab2, tab3 = st.tabs(["📈 Overview", "🌍 Country Analysis", "📊 Advanced"])

# -------------------------------
# 📈 TAB 1: OVERVIEW
# -------------------------------
with tab1:

    st.subheader("Global Trend")
    global_trend = dataset.groupby('date')[['confirmed','deaths','recovered']].sum().reset_index()

fig1 = px.area(global_trend, x='date', y=['confirmed','deaths','recovered'],
              title="Global COVID-19 Growth Over Time")
fig1.show()

    st.subheader("Top Countries")
   latest = dataset[dataset['date'] == dataset['date'].max()]

top_countries = latest.groupby('_country_region')['confirmed'].sum() \
                      .sort_values(ascending=False).head(10).reset_index()

fig2= px.bar(top_countries, x='_country_region', y='confirmed',
             title="Top 10 Countries by Confirmed Cases")
fig2.show()
    # Insight
    st.markdown(f"""
    🔍 **Insight:**  
    Highest cases: **{top_countries.iloc[0]['_country_region']}**  
    Cases: **{int(top_countries.iloc[0]['confirmed']):,}**
    """)

# -------------------------------
# 🌍 TAB 2: COUNTRY ANALYSIS
# -------------------------------
with tab2:

    fig3 = px.sunburst(latest,
                  path=['who_region', '_country_region'],
                  values='confirmed',
                  title="COVID-19 Cases by Region and Country")
fig.update_layout(
    height=600,
    width=800
)
    st.plotly_chart(fig3, use_container_width=True)

    # Death Rate
    latest = dataset[dataset['date'] == dataset['date'].max()].copy()
latest['Death Rate'] = latest['deaths'] / latest['confirmed'].replace(0, 1)

top_death_rate = latest.sort_values(by='Death Rate', ascending=False).head(10)
    fig4 = px.pie(top_death_rate,
             names='_country_region',
             values='Death Rate',
             title="Death Rate Distribution (Top 10)")
fig4.update_layout(
    height=500,
    width=600
)
    st.plotly_chart(fig4, use_container_width=True)

latest = dataset[dataset['date'] == dataset['date'].max()].copy()

latest['Recovery Rate'] = latest['recovered'] / latest['confirmed'].replace(0, 1)

# Get top 10 countries by recovery rate
top_recovery = latest.sort_values(by='Recovery Rate', ascending=False).head(10)

fig5 = px.treemap(top_recovery,
                 path=['_country_region'],
                 values='Recovery Rate',
                 title="Recovery Rate by Country")

fig5.show()

# -------------------------------
# 📊 TAB 3: ADVANCED
# -------------------------------
with tab3:

    st.subheader("🌐 Global Spread (Animated)")

    fig6 = px.scatter_geo(df,
                         lat='lat',
                         lon='long',
                         size='confirmed',
                         color='who_region',
                         animation_frame=df['date'].astype(str),
                         hover_name='_country_region',
                         template="plotly_dark")

    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("📦 Distribution")

    cols = ["confirmed", "deaths", "recovered", "active"]
    df_melted = filtered_df[cols].melt(var_name="Feature", value_name="Value")

    fig7 = px.violin(df_melted,
                     x="Feature",
                     y="Value",
                     box=True,
                     points="outliers",
                     template="plotly_dark")

    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("🔗 Correlation")

    corr = filtered_df[cols].corr()

    fig8 = px.imshow(corr,
                     text_auto=True,
                     template="plotly_dark")

    st.plotly_chart(fig8, use_container_width=True)

# -------------------------------
# 📌 FOOTER
# -------------------------------
st.markdown("""
---
### 📌 Key Insights
- COVID spread is highly uneven across regions  
- Few countries dominate global case counts  
- Strong correlation between confirmed & deaths  
- Trends show exponential growth phases  
---
""")