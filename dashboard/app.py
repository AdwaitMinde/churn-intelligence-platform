import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery

# Page config
st.set_page_config(
    page_title="Churn Intelligence Platform",
    page_icon="📉",
    layout="wide"
)

@st.cache_data(ttl=300)
def load_data():
    client = bigquery.Client()
    query = """
        SELECT *
        FROM `my-project-mail-422110.ecommerce_marts.churn_dashboard_view`
    """
    return client.query(query).to_dataframe()

df = load_data()

# ── HEADER ──────────────────────────────────────────────────────────────
st.title("📉 Real-Time Customer Churn Intelligence Platform")
st.caption("Powered by Kafka · BigQuery · dbt · XGBoost · Claude AI")

# ── KPI ROW ─────────────────────────────────────────────────────────────
total      = len(df)
churned    = df['churned'].sum()
retained   = total - churned
churn_rate = churned / total

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers",   f"{total:,}")
col2.metric("Churned",           f"{churned:,}")
col3.metric("Retained",          f"{retained:,}")
col4.metric("Churn Rate",        f"{churn_rate:.1%}")

st.divider()

# ── TABS ────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🔍 Analyst View", "📊 Executive Summary"])

# ── TAB 1: ANALYST VIEW ─────────────────────────────────────────────────
with tab1:
    st.subheader("High-Risk Customer Explorer")

    # Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        risk_filter = st.multiselect(
            "Filter by Risk Tier",
            options=["High", "Medium", "Low"],
            default=["High", "Medium"]
        )
    with col_f2:
        min_spend = st.slider("Minimum Total Spend ($)", 0, 2000, 0, step=50)

    filtered = df[
        (df['risk_tier'].isin(risk_filter)) &
        (df['monetary'] >= min_spend) &
        (df['churned'] == 1)
    ].sort_values('recency_days', ascending=False)

    st.markdown(f"**{len(filtered):,} customers match filters**")

    # Table
    display_cols = ['user_id', 'risk_tier', 'recency_days', 'frequency',
                    'monetary', 'cart_abandon_rate', 'explanation']
    st.dataframe(
        filtered[display_cols].head(100).rename(columns={
            'user_id':          'User ID',
            'risk_tier':        'Risk',
            'recency_days':     'Days Inactive',
            'frequency':        'Purchases',
            'monetary':         'Total Spend ($)',
            'cart_abandon_rate': 'Cart Abandon %',
            'explanation':      'AI Churn Explanation'
        }),
        use_container_width=True,
        height=400
    )

    # Scatter plot
    st.subheader("Recency vs Spend — Churned Customers")
    fig_scatter = px.scatter(
        filtered.head(500),
        x='recency_days',
        y='monetary',
        color='risk_tier',
        size='frequency',
        hover_data=['user_id', 'explanation'],
        color_discrete_map={'High': '#ef4444', 'Medium': '#f97316', 'Low': '#22c55e'},
        labels={'recency_days': 'Days Since Last Purchase', 'monetary': 'Total Spend ($)'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── TAB 2: EXECUTIVE SUMMARY ────────────────────────────────────────────
with tab2:
    st.subheader("Executive Summary")

    col_a, col_b = st.columns(2)

    # Risk tier distribution
    with col_a:
        st.markdown("**Churned Customers by Risk Tier**")
        risk_counts = df[df['churned'] == 1]['risk_tier'].value_counts().reset_index()
        risk_counts.columns = ['Risk Tier', 'Count']
        fig_pie = px.pie(
            risk_counts,
            names='Risk Tier',
            values='Count',
            color='Risk Tier',
            color_discrete_map={'High': '#ef4444', 'Medium': '#f97316', 'Low': '#22c55e'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Avg spend by risk tier
    with col_b:
        st.markdown("**Average Spend by Risk Tier**")
        spend_by_risk = df.groupby('risk_tier')['monetary'].mean().reset_index()
        spend_by_risk.columns = ['Risk Tier', 'Avg Spend']
        fig_bar = px.bar(
            spend_by_risk,
            x='Risk Tier',
            y='Avg Spend',
            color='Risk Tier',
            color_discrete_map={'High': '#ef4444', 'Medium': '#f97316', 'Low': '#22c55e'},
            labels={'Avg Spend': 'Average Total Spend ($)'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Key insights
    st.subheader("Key Insights")
    high_risk_count  = len(df[(df['risk_tier'] == 'High') & (df['churned'] == 1)])
    high_risk_spend  = df[(df['risk_tier'] == 'High') & (df['churned'] == 1)]['monetary'].mean()
    retained_spend   = df[df['churned'] == 0]['monetary'].mean()

    st.info(f"🔴 **{high_risk_count:,} high-risk customers** have been inactive for 60+ days with avg spend of ${high_risk_spend:.2f}")
    st.success(f"🟢 **{retained:,} retained customers** have an avg spend of ${retained_spend:.2f} — {retained_spend/high_risk_spend:.1f}x higher than high-risk churners")
    st.warning(f"⚠️ Overall churn rate is **{churn_rate:.1%}** — recency and purchase frequency are the top predictors per SHAP analysis")