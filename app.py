
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/data.csv", encoding="ISO-8859-1")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
    return df

df = load_data()

# Sidebar
st.sidebar.title("🔎 Filter Options")
country_list = df["Country"].unique().tolist()
country = st.sidebar.selectbox("Select Country", options=sorted(country_list), index=country_list.index("United Kingdom") if "United Kingdom" in country_list else 0)

# Main Title
st.title("🛍️ E-Commerce Analysis Dashboard")
st.markdown("Interactive insights into customer behavior, product performance, and revenue.")

# Filtered Data
filtered_df = df[df["Country"] == country]

# Tabs
tab1, tab2, tab3 = st.tabs(["📦 Product Insights", "💰 Revenue Trends", "👤 RFM Segmentation"])

# Tab 1: Product Insights
with tab1:
    st.subheader(f"Top 10 Products Sold in {country}")
    top_products = filtered_df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(10)

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.barplot(x=top_products.values, y=top_products.index, palette="viridis", ax=ax1)
    ax1.set_xlabel("Quantity Sold")
    ax1.set_ylabel("Product")
    st.pyplot(fig1)

# Tab 2: Revenue Trends
with tab2:
    st.subheader(f"Revenue Over Time in {country}")
    filtered_df["InvoiceMonth"] = filtered_df["InvoiceDate"].dt.to_period("M").astype(str)
    monthly_revenue = filtered_df.groupby("InvoiceMonth")["TotalPrice"].sum()

    fig2, ax2 = plt.subplots(figsize=(12, 5))
    sns.lineplot(x=monthly_revenue.index, y=monthly_revenue.values, marker="o", ax=ax2)
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Revenue")
    ax2.set_title("Monthly Revenue Trend")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

# Tab 3: RFM Analysis
with tab3:
    st.subheader("Customer Segmentation (RFM Score)")
    latest_date = df["InvoiceDate"].max()
    rfm = df.groupby("CustomerID").agg({
        "InvoiceDate": lambda x: (latest_date - x.max()).days,
        "InvoiceNo": "nunique",
        "TotalPrice": "sum"
    })
    rfm.columns = ["Recency", "Frequency", "Monetary"]
    rfm["R_Score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1])
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4])
    rfm["RFM_Score"] = rfm[["R_Score", "F_Score", "M_Score"]].astype(int).sum(axis=1)

    st.write("Top 10 Customers by RFM Score")
    st.dataframe(rfm.sort_values("RFM_Score", ascending=False).head(10).style.background_gradient(cmap="YlGnBu"))
