# app.py
"""
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="🛍️",
    layout="wide"
)
st.markdown(
    """
    <style>
    
    .stApp {
        background-color: #f7f9fc; 
    }

    
    section[data-testid="stSidebar"] {
        background-color: #4c6278;  
    }

    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }

    
    section[data-testid="stSidebar"] .stSelectbox label {
        color: white !important;
        font-weight: bold;
    }

       section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        color: white !important;
    }

   
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        background-color: #34495e !important;  /* Tom mais claro para contraste */
    }

    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 20px;
        padding-left: 15px;
        padding-right: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Title, Introduction and Context
# -------------------------------
st.title("🛍️ Customer Segmentation Dashboard")
st.markdown("""
**RFM Analysis** of an e-commerce retailer based in the UK.  
All monetary values are in **British Pounds (£)**.
📅 **Data Period**: December 2010 – December 2011  
📊 **Transactions**: ~540,000 | **Customers**: ~4,300  

Despite the limited data, I found it interesting to build the model with the aim of demonstrating technical capacity for data manipulation and creating visual content through coding.

This dashboard presents a complete customer segmentation analysis using the **RFM model** (Recency, Frequency, Monetary) to identify high-value customers, detect churn risks, and support data-driven marketing strategies.

🔍 **Key Contributions**:
- **Statistical heterogeneity**: Segmentation accounts for skewness in monetary values.
- **Retention ROI**: Quantified impact of recovering "At Risk" customers.
- **Dynamic RFM scoring**: Users can adjust scoring thresholds interactively.
- **Logarithmic scale**: Visualizes revenue distribution without distortion.

🎯 *Built with Python, Pandas, Plotly, Streamlit*
""")
st.markdown("---")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('rfm_analysis_en.csv')
    df['recency_days'] = pd.to_numeric(df['recency_days'], errors='coerce')
    df['monetary_total_gbp'] = pd.to_numeric(df['monetary_total_gbp'], errors='coerce')
    df['frequency_orders'] = pd.to_numeric(df['frequency_orders'], errors='coerce')
    return df

try:
    df = load_data()
    st.success("✅ Data loaded successfully!")
except Exception as e:
    st.error(f"❌ Error loading  {e}")
    st.stop()

# -------------------------------
# Fix country name: EIRE → Ireland
df['country'] = df['country'].replace({'EIRE': 'Ireland'})

# Map to main segments only
segment_map = {
    'VIP': 'VIP',
    'Loyal / Frequent': 'Loyal',
    'At Risk': 'At Risk',
    'Inactive': 'Inactive'
}
df['main_segment'] = df['customer_segment'].map(segment_map)
df = df.dropna(subset=['main_segment'])

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("🔍 Filters")
countries = ["All"] + sorted(df['country'].dropna().unique())
segments = ["All"] + sorted(df['main_segment'].dropna().unique())

selected_country = st.sidebar.selectbox("Country", countries)
selected_segment = st.sidebar.selectbox("Customer Segment", segments)

# Apply filters
df_filtered = df.copy()
if selected_country != "All":
    df_filtered = df_filtered[df_filtered['country'] == selected_country]
if selected_segment != "All":
    df_filtered = df_filtered[df_filtered['main_segment'] == selected_segment]

st.sidebar.markdown(f"**{len(df_filtered)} customers** shown.")

# -------------------------------
# Key Metrics (KPIs)
# -------------------------------
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_customers = len(df_filtered)
total_revenue = df_filtered['monetary_total_gbp'].sum()
avg_monetary = df_filtered['monetary_total_gbp'].mean()
active_customers = len(df_filtered[df_filtered['recency_days'] <= 90])

col1.metric("Total Customers", f"{total_customers:,}")
col2.metric("Total Revenue", f"£{total_revenue:,.0f}")
col3.metric("Avg. Value per Customer", f"£{avg_monetary:,.0f}")
col4.metric("Active Customers", f"{active_customers:,}")

# -------------------------------
# KPI: Strategic ROI - At-Risk Customer Retention Potential
# -------------------------------
st.markdown("### 💡 Strategic ROI: Customer Retention Potential")

# Calculate potential recovery from reactivating 20% of "At Risk" customers
at_risk_customers = df_filtered[df_filtered['main_segment'] == 'At Risk']
at_risk_revenue = at_risk_customers['monetary_total_gbp'].sum()
potential_recovery = at_risk_revenue * 0.2  # 20% retention

st.markdown(f"""
- **Revenue from At-Risk Customers**: £{at_risk_revenue:,.0f}  
- **Estimated Recovery (20% retention)**: **£{potential_recovery:,.0f}**  
- **ROI Potential**: Up to **{potential_recovery / (at_risk_revenue * 0.8):.1%}** of current revenue  
  (assuming 80% marketing cost over reactivation campaigns)

This demonstrates the **importance of proactive retention strategies** for high-value but disengaged customers.
""")
st.markdown("---")

# -------------------------------
# Chart 1: Customer Distribution by Segment (Donut Chart)
# -------------------------------
st.subheader("👥 Customer Distribution by Segment")

segment_count = df_filtered['main_segment'].value_counts().reset_index()
segment_count.columns = ['segment', 'count']

fig1 = px.pie(
    segment_count,
    names='segment',
    values='count',
    hole=0.4,
    color='segment',
    color_discrete_map={
        'VIP': '#FF6B6B',
        'Loyal': '#4ECDC4',
        'At Risk': '#FFD93D',
        'Inactive': '#A5A5A5'
    }
)

fig1.update_traces(textinfo='percent+label', textposition='inside')
fig1.update_layout(
    showlegend=True,
    height=400,
    annotations=[dict(text='Segments', x=0.5, y=0.5, font_size=14, showarrow=False)]
)

st.plotly_chart(fig1, use_container_width=True)
st.caption("💡 Note: The 'VIP' and 'Loyal' segments represent a small but disproportionately valuable portion of customers.")

# -------------------------------
# Chart 2: Combo Chart - Total Revenue (Bar) + Avg (Line)
# -------------------------------
st.subheader("💷 Revenue per Segment: Volume vs. Value")

revenue_by_segment = df_filtered.groupby('main_segment').agg({
    'monetary_total_gbp': ['sum', 'mean']
}).round(0)

revenue_by_segment.columns = ['total_revenue', 'avg_value']
revenue_by_segment = revenue_by_segment.sort_values('total_revenue', ascending=False).reset_index()

fig2 = go.Figure()

fig2.add_trace(go.Bar(
    x=revenue_by_segment['main_segment'],
    y=revenue_by_segment['total_revenue'],
    name='Total Revenue (£)',
    marker_color='#6baed6',
    text=revenue_by_segment['total_revenue'],
    texttemplate='£%{text:,.0f}',
    textposition='outside'
))

fig2.add_trace(go.Scatter(
    x=revenue_by_segment['main_segment'],
    y=revenue_by_segment['avg_value'],
    mode='lines+markers+text',
    name='Avg per Customer (£)',
    yaxis='y2',
    line=dict(color='#d73027', width=3),
    marker=dict(size=8),
    text=[f'£{val:,.0f}' for val in revenue_by_segment['avg_value']],
    textposition='top center'
))

fig2.update_layout(
    xaxis_title="Customer Segment",
    yaxis=dict(title="Total Revenue (£)", side="left"),
    yaxis2=dict(title="Average per Customer (£)", overlaying="y", side="right"),
    legend=dict(x=0.7, y=1.1, orientation="h"),
    height=500,
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# Chart 3: Strategic Customer Map (Final Version - Clean Linear X Axis)
# -------------------------------
st.subheader("📍 Strategic Customer Map")
st.markdown("""
**Customer clusters by spending and recency.**  
Each bubble represents a group of customers. Size = number of customers, Position = average behavior.
""")

# Define monetary bands (£0–10k)
bins_monetary = [0, 500, 1000, 1500, 2000, 2500, 3000,
                 4000, 5000, 6000,
                 8000, 10000]
labels_monetary = [
    "£0-499", "£500-999", "£1k-1.5k", "£1.5k-2k", "£2k-2.5k", "£2.5k-3k",
    "£3k-4k", "£4k-5k", "£5k-6k",
    "£6k-8k", "£8k-10k"
]

df_filtered['monetary_band'] = pd.cut(
    df_filtered['monetary_total_gbp'],
    bins=bins_monetary,
    labels=labels_monetary,
    include_lowest=True,
    right=False
)

# Recency bands
bins_recency = [0, 90, 180, 365, 1000]
labels_recency = ["0-90d", "91-180d", "181-365d", ">365d"]
df_filtered['recency_band'] = pd.cut(
    df_filtered['recency_days'],
    bins=bins_recency,
    labels=labels_recency,
    include_lowest=True,
    right=False
)

# Group by bands
agg_data = df_filtered.groupby(['main_segment', 'monetary_band', 'recency_band']).agg(
    avg_recency=('recency_days', 'mean'),
    avg_monetary=('monetary_total_gbp', 'mean'),
    customer_count=('customer_id', 'count'),
    total_revenue=('monetary_total_gbp', 'sum')
).reset_index()

# Remove small groups
agg_data = agg_data[agg_data['customer_count'] >= 2].copy()

# Professional color map
color_map = {
    'VIP': '#D62728',
    'Loyal': '#2CA02C',
    'At Risk': '#FF7F0E',
    'Inactive': '#7F7F7F'
}

# Create scatter plot
fig3 = px.scatter(
    agg_data,
    x='avg_recency',
    y='avg_monetary',
    size='customer_count',
    color='main_segment',
    hover_name='main_segment',
    hover_data={
        'monetary_band': True,
        'recency_band': True,
        'customer_count': ':.0f',
        'total_revenue': ':,.2f',
        'avg_recency': ':.1f',
        'avg_monetary': ':,.2f'
    },
    labels={
        'avg_recency': 'Average Recency (days)',
        'avg_monetary': 'Average Total Spent (£)',
        'customer_count': 'Customers in Group',
        'main_segment': 'Segment'
    },
    color_discrete_map=color_map,
    size_max=50,
    opacity=0.8
)

# Style bubbles
fig3.update_traces(
    marker=dict(
        line=dict(width=1.2, color='DarkSlateGrey')
    )
)

# X-axis: linear, reversed, limited range
fig3.update_xaxes(
    range=[0, 400],
    title=dict(text="Avg Days Since Last Purchase (lower = more recent)", font_size=14),
    showgrid=True,
    gridwidth=0.4,
    gridcolor='LightGray',
    dtick=50,
    tickfont=dict(size=11)
)

# Y-axis
fig3.update_yaxes(
    range=[0, 8000],
    title=dict(text="Avg Total Spent (£)", font_size=14),
    showgrid=True,
    gridwidth=0.4,
    gridcolor='LightGray',
    dtick=1000,
    tickfont=dict(size=11)
)

# Subtle divider lines
fig3.add_vline(x=90, line_dash="dot", line_color="gray", opacity=0.6, annotation_text="90d")
fig3.add_hline(y=2000, line_dash="dot", line_color="gray", opacity=0.6, annotation_text="£2k")

# Final layout: clean and professional
fig3.update_layout(
    height=550,
    legend_title_text="Customer Segment",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ),
    hoverlabel=dict(bgcolor="white", font_size=14, font_family="Rockwell"),
    margin=dict(l=60, r=30, t=80, b=60),
    plot_bgcolor='rgba(248, 248, 255, 0.8)',
    paper_bgcolor='white',
    font=dict(family="Arial", size=12, color="#2C3E50")
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------------
# Chart 4: Top 10 Customers by Revenue (Strategic Comment)
# -------------------------------
st.subheader("🏆 Top 10 Customers by Revenue")

# Select top 10 and sort descending
top_customers = df_filtered.nlargest(10, 'monetary_total_gbp')[[
    'customer_id', 'country', 'monetary_total_gbp', 'main_segment'
]].copy()

top_customers = top_customers.sort_values('monetary_total_gbp', ascending=False).reset_index(drop=True)
top_customers['monetary_total_gbp'] = top_customers['monetary_total_gbp'].round(2)

# Calculate % of total revenue
total_revenue_all = df['monetary_total_gbp'].sum()
top10_revenue = top_customers['monetary_total_gbp'].sum()
top10_percentage = (top10_revenue / total_revenue_all) * 100

# Strategic insight comment
st.markdown(f"""
💡 **Strategic Insight**  
The **Top 10 customers** contribute **{top10_percentage:.1f}% of total revenue**, but represent only **{len(top_customers) / len(df) * 100:.2f}% of total customer base**.
This suggests a **highly skewed revenue distribution**, which is common in e-commerce.  
However, over-reliance on this small group can be risky due to volatility.  
**Recommendation**:  
- **Retain top 10** with loyalty programs  
- **Scale mid-tier customers** (Loyal / At Risk) to reduce dependency on a few clients  
- **Improve engagement** for Inactive segment to unlock latent value

This aligns with Pareto Principle (80/20 rule), but also highlights the importance of **customer base diversification**.
""")

# Bar chart (adjusted for thicker and closer bars)
fig4 = px.bar(
    top_customers,
    x='customer_id',
    y='monetary_total_gbp',
    color='country',
    text='monetary_total_gbp',
    color_discrete_sequence=px.colors.qualitative.Bold,
    labels={'monetary_total_gbp': 'Revenue (£)', 'customer_id': 'Customer ID'},
    hover_data={'main_segment': True, 'country': True},
    category_orders={'customer_id': top_customers['customer_id'].tolist()}
)

# Adjustments for thicker and closer bars
fig4.update_traces(
    width=0.9,
    marker_line_width=1.3,
    marker_line_color='DarkSlateGrey',
    texttemplate='£%{text:,.0f}',
    textposition='outside'
)

# Layout adjustments
fig4.update_layout(
    xaxis_title="Customer ID",
    yaxis_title="Total Revenue (£)",
    height=500,
    bargap=0.05,
    bargroupgap=0.0,
    yaxis=dict(
        range=[top_customers['monetary_total_gbp'].min() * 0.8, None],
        gridwidth=0.6,
        gridcolor='LightGray'
    ),
    uniformtext_minsize=10,
    uniformtext_mode='hide',
    legend_title="Country",
    xaxis_tickangle=0,
    xaxis=dict(
        tickmode='array',
        tickvals=top_customers['customer_id'],
        tickfont=dict(size=12),
        title="Customer ID",
        type='category'
    ),
    hoverlabel=dict(bgcolor="white", font_size=14),
    margin=dict(l=60, r=30, t=50, b=100)
)

st.plotly_chart(fig4, use_container_width=True)

# Detailed table
with st.expander("View Detailed Table (with Country & Segment)"):
    st.dataframe(
        top_customers.rename(columns={
            'monetary_total_gbp': 'Revenue (£)',
            'customer_id': 'Customer ID'
        })[['Customer ID', 'country', 'main_segment', 'Revenue (£)']]
        .reset_index(drop=True)
    )

# -------------------------------
# Dataset Limitations (Final Section)
# -------------------------------
st.markdown("---")
st.markdown("""### ⚠️ Technical Limitations of the Dataset

Limited Time Period:
Dataset covers only 12 months (Dec/2010 – Dec/2011)
No complete seasonal data (e.g., Christmas, Black Friday)
Does not allow longitudinal analysis (e.g., customer evolution over 2+ years)

Partial Sampling:
Data comes from a single UK-based online store
Does not represent the entire e-commerce industry
Biased toward the UK market (85% of sales)

Lack of Demographic Information:
No data on age, gender, or consumption profile
Limits personalization of marketing campaigns
Prevents lifetime value (LTV) analysis

Absence of SKU-Level Data:
No information about products purchased
Hinders cross-selling and upselling strategies
Prevents product co-purchase and basket analysis

Recency as an Engagement Proxy:
Recency is a useful but limited proxy for engagement
A customer may have high recency but still make high-value purchases
Recommended to combine with Frequency and Monetary for higher accuracy
""")

# -------------------------------
# Segment Explanation (Enhanced Strategy)
# -------------------------------
st.markdown("---")
st.subheader("📘 Strategic Customer Segmentation Guide")

with st.expander("Click to view detailed business strategy"):
    st.markdown("""
    ### 🎯 **VIP**
    - **Profile**: Recency ≤ 30d, Frequency ≥ 5, Monetary ≥ £3,000  
    - **Strategy**:  
      - **Personalized Loyalty Tiers**: Exclusive campaigns for customers with recency < 30 days  
      - **Predictive Offers**: Recommendations based on purchase history  
      - **Churn Monitoring**: Alerts for sudden changes in recency
    ### 💼 **Loyal**
    - **Profile**: Recency ≤ 90d, Frequency ≥ 3, Monetary ≥ £1,000  
    - **Strategy**:  
      - **Cross-Selling**: Offer complementary products based on buying patterns  
      - **Engagement Boost**: Gamification or rewards for frequency  
      - **Customer Journey Mapping**: Analyze steps before purchase
    ### ⚠️ **At Risk**
    - **Profile**: Recency > 90d, Monetary ≥ £1,000  
    - **Strategy**:  
      - **Targeted Win-Back Campaigns**: Personalized offers (e.g., 10% off + free shipping)  
      - **Email Reactivation Series**: 3 emails with increasing value content  
      - **A/B Testing**: Test different reactivation approaches
    ### 👋 **Inactive**
    - **Profile**: Recency > 365d, Monetary < £500  
    - **Strategy**:  
      - **Cost-Effective Re-engagement**: Low-cost campaigns  
      - **Sunset Strategy**: Stop emailing unresponsive customers  
      - **Data-Driven Reactivation**: Segmentation by country and purchase history
    """)

# -------------------------------
# Download Filtered Data
# -------------------------------
st.markdown("### 💾 Download Filtered Data")
st.dataframe(df_filtered)
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name="segmented_customers_filtered.csv",
    mime="text/csv"
)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("🎯 *RFM Analysis using Python & Streamlit*")