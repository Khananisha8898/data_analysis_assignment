import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Kitchen PNL Dashboard",
    layout="wide",
    page_icon="🍽️"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

h1, h2, h3 {
    color: white;
}

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1f2937, #111827);
    border: 1px solid #374151;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
}

[data-testid="metric-container"] label {
    color: #9ca3af !important;
}

[data-testid="metric-container"] div {
    color: white !important;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():

    df = pd.read_excel(
        "Kittchen PNL Data.xlsx",
        engine="openpyxl",
        header=1
    )

    # Clean columns
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
    )

    return df

df = load_data()

# ---------------- TITLE ----------------
st.markdown("""
<h1 style='font-size:55px; color:white;'>
🍽️ Kitchen PNL Dashboard
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style='color:gray; font-size:18px;'>
Cloud Kitchen Profit & Loss Analysis Dashboard
</p>
""", unsafe_allow_html=True)

# ---------------- CATEGORY FUNCTIONS ----------------
def revenue_category(x):

    if x < 1500000:
        return "Below 15 lacs"

    elif x < 2500000:
        return "15 to 25 lacs"

    elif x < 3500000:
        return "25 to 35 lacs"

    elif x < 4500000:
        return "35 to 45 lacs"

    else:
        return "Above 45 lacs"


def variance_category(x):

    if x < 2:
        return "Var <2%"

    elif x < 3:
        return "Var 2% to 3%"

    elif x < 5:
        return "Var 3% to 5%"

    else:
        return "Var >5%"


def ebitda_category(x):

    if x < 0:
        return "Loss"

    elif x < 500000:
        return "Low Profit"

    elif x < 1000000:
        return "Medium Profit"

    else:
        return "High Profit"

# ---------------- CREATE NEW COLUMNS ----------------
df["REVENUE_CATEGORY"] = df["NET_REVENUE"].apply(revenue_category)

df["VARIANCE_CATEGORY"] = df["VARIANCE"].apply(variance_category)

df["EBITDA_CATEGORY"] = df["KITCHEN_EBITDA"].apply(ebitda_category)

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 Dashboard Filters")

store_filter = st.sidebar.multiselect(
    "🏪 Select Store",
    options=df["STORE"].unique(),
    default=df["STORE"].unique()
)

month_filter = st.sidebar.multiselect(
    "📅 Select Month",
    options=df["MONTH"].unique(),
    default=df["MONTH"].unique()
)

variance_filter = st.sidebar.multiselect(
    "📉 Variance Category",
    options=df["VARIANCE_CATEGORY"].unique(),
    default=df["VARIANCE_CATEGORY"].unique()
)

# EBITDA Slider
min_ebitda = int(df["KITCHEN_EBITDA"].min())
max_ebitda = int(df["KITCHEN_EBITDA"].max())

ebitda_filter = st.sidebar.slider(
    "💰 EBITDA Range",
    min_value=min_ebitda,
    max_value=max_ebitda,
    value=(min_ebitda, max_ebitda)
)

# ---------------- FILTER DATA ----------------
filtered_df = df[
    (df["STORE"].isin(store_filter)) &
    (df["MONTH"].isin(month_filter)) &
    (df["VARIANCE_CATEGORY"].isin(variance_filter)) &
    (df["KITCHEN_EBITDA"] >= ebitda_filter[0]) &
    (df["KITCHEN_EBITDA"] <= ebitda_filter[1])
]

# ---------------- KPI SECTION ----------------
st.markdown("## 📊 Business Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💵 Total Revenue",
    f"₹ {filtered_df['NET_REVENUE'].sum():,.0f}"
)

col2.metric(
    "📈 Total EBITDA",
    f"₹ {filtered_df['KITCHEN_EBITDA'].sum():,.0f}"
)

col3.metric(
    "🏪 Total Stores",
    filtered_df["STORE"].nunique()
)

col4.metric(
    "⚠️ Avg Variance %",
    f"{filtered_df['VARIANCE'].mean():.2f}%"
)

# ---------------- CHARTS ----------------
st.markdown("## 📈 Revenue & EBITDA Analysis")

chart1, chart2 = st.columns(2)

# Monthly Revenue
monthly_revenue = (
    filtered_df
    .groupby("MONTH")["NET_REVENUE"]
    .sum()
    .reset_index()
)

fig1 = px.bar(
    monthly_revenue,
    x="MONTH",
    y="NET_REVENUE",
    text_auto=True,
    template="plotly_dark",
    title="Monthly Revenue Trend"
)

chart1.plotly_chart(fig1, use_container_width=True)

# Monthly EBITDA
monthly_ebitda = (
    filtered_df
    .groupby("MONTH")["KITCHEN_EBITDA"]
    .sum()
    .reset_index()
)

fig2 = px.line(
    monthly_ebitda,
    x="MONTH",
    y="KITCHEN_EBITDA",
    markers=True,
    template="plotly_dark",
    title="Monthly EBITDA Trend"
)

chart2.plotly_chart(fig2, use_container_width=True)

# ---------------- SECOND ROW CHARTS ----------------
chart3, chart4 = st.columns(2)

# Revenue Distribution
category_revenue = (
    filtered_df
    .groupby("REVENUE_CATEGORY")["NET_REVENUE"]
    .sum()
    .reset_index()
)

fig3 = px.pie(
    category_revenue,
    names="REVENUE_CATEGORY",
    values="NET_REVENUE",
    hole=0.5,
    template="plotly_dark",
    title="Revenue Category Distribution"
)

chart3.plotly_chart(fig3, use_container_width=True)

# Store Performance Scatter Plot
store_performance = (
    filtered_df
    .groupby("STORE")[["NET_REVENUE", "KITCHEN_EBITDA"]]
    .sum()
    .reset_index()
)

# Bubble size fix
store_performance["BUBBLE_SIZE"] = (
    store_performance["KITCHEN_EBITDA"]
    .abs()
)

fig4 = px.scatter(
    store_performance,
    x="NET_REVENUE",
    y="KITCHEN_EBITDA",
    size="BUBBLE_SIZE",
    hover_name="STORE",
    template="plotly_dark",
    title="Store Revenue vs EBITDA"
)

chart4.plotly_chart(fig4, use_container_width=True)

# ---------------- VARIANCE DASHBOARD ----------------
st.markdown("## 📉 Variance Dashboard")

variance_table = pd.pivot_table(
    filtered_df,
    values="VARIANCE",
    index="REVENUE_CATEGORY",
    columns="MONTH",
    aggfunc="mean"
)

st.dataframe(
    variance_table.style.highlight_max(axis=1),
    use_container_width=True
)

# ---------------- STORE COUNT DASHBOARD ----------------
st.markdown("## 🏬 Store Count Dashboard")

store_table = pd.pivot_table(
    filtered_df,
    values="STORE",
    index="REVENUE_CATEGORY",
    columns="MONTH",
    aggfunc="count"
)

st.dataframe(
    store_table.style.highlight_max(axis=1),
    use_container_width=True
)

# ---------------- RAW DATA ----------------
st.markdown("## 🗂️ Filtered Raw Data")

st.dataframe(
    filtered_df,
    use_container_width=True
)

# ---------------- DOWNLOAD BUTTON ----------------
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="filtered_kitchen_data.csv",
    mime="text/csv"
)