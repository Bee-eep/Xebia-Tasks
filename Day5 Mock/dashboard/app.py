"""
Streamlit Dashboard: GreenOps AI Dashboard - Real-time carbon emissions & sustainability metrics
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="GreenOps AI Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .recommendation-item {
        padding: 15px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# Load data with caching
@st.cache_data
def load_data():
    consumption = pd.read_csv('data/historical_consumption.csv')
    consumption['date'] = pd.to_datetime(consumption['date'])
    
    forecast = pd.read_csv('data/carbon_forecast.csv')
    forecast['date'] = pd.to_datetime(forecast['date'])
    
    green_scores = pd.read_csv('data/green_scores.csv')
    recommendations = pd.read_csv('data/recommendations.csv')
    
    return consumption, forecast, green_scores, recommendations

consumption_df, forecast_df, green_scores_df, recommendations_df = load_data()

# ===== DASHBOARD TITLE =====
st.title("🌱 GreenOps AI Dashboard")
st.markdown("**Real-time Carbon Emissions & Sustainability Metrics**")
st.markdown("---")

# ===== SIDEBAR FILTERS =====
with st.sidebar:
    st.header("📊 Filters")
    
    selected_projects = st.multiselect(
        "Projects",
        options=sorted(consumption_df['project'].unique()),
        default=list(consumption_df['project'].unique()),
        key="project_filter"
    )
    
    selected_regions = st.multiselect(
        "Regions",
        options=sorted(consumption_df['region'].unique()),
        default=list(consumption_df['region'].unique()),
        key="region_filter"
    )
    
    selected_services = st.multiselect(
        "Services",
        options=sorted(consumption_df['service'].unique()),
        default=list(consumption_df['service'].unique()),
        key="service_filter"
    )

# Apply filters
filtered_df = consumption_df[
    (consumption_df['project'].isin(selected_projects)) &
    (consumption_df['region'].isin(selected_regions)) &
    (consumption_df['service'].isin(selected_services))
]

# ===== KPI CARDS =====
st.subheader("📈 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

total_carbon = filtered_df['carbon_kg_co2e'].sum()
total_cost = filtered_df['cost_usd'].sum()
forecasted_carbon = forecast_df['predicted_carbon_kg'].sum()
cost_per_carbon = total_cost / total_carbon if total_carbon > 0 else 0

# Calculate trend
historical_avg = filtered_df['carbon_kg_co2e'].sum() / len(filtered_df['date'].unique()) if len(filtered_df) > 0 else 0
forecast_avg = forecasted_carbon / 90
trend = ((forecast_avg - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0

with col1:
    st.metric(
        label="Total Emissions (Current Period)",
        value=f"{total_carbon:,.0f}",
        delta="kg CO₂e",
        help="Total carbon emissions for selected filters"
    )

with col2:
    st.metric(
        label="Forecasted (Q+1)",
        value=f"{forecasted_carbon:,.0f}",
        delta="kg CO₂e",
        help="Predicted emissions for next quarter"
    )

with col3:
    st.metric(
        label="Cost Efficiency",
        value=f"${cost_per_carbon:.2f}",
        delta="per kg CO₂e",
        help="Cloud cost per unit of carbon"
    )

with col4:
    st.metric(
        label="Emission Trend",
        value=f"{trend:+.1f}%",
        delta="vs. current",
        help="Predicted change in emissions"
    )

st.markdown("---")

# ===== VISUALIZATIONS =====
st.subheader("📊 Carbon Emissions Analysis")

col1, col2 = st.columns(2)

# Chart 1: Historical + Forecast Timeline
with col1:
    daily_carbon = filtered_df.groupby(filtered_df['date'].dt.date)['carbon_kg_co2e'].sum().reset_index()
    daily_carbon.columns = ['date', 'carbon_kg_co2e']
    daily_carbon['date'] = pd.to_datetime(daily_carbon['date'])
    
    fig1 = go.Figure()
    
    # Historical data
    fig1.add_trace(go.Scatter(
        x=daily_carbon['date'],
        y=daily_carbon['carbon_kg_co2e'],
        mode='lines',
        name='Historical',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Emissions: %{y:.1f} kg<extra></extra>'
    ))
    
    # Forecast data
    fig1.add_trace(go.Scatter(
        x=forecast_df['date'],
        y=forecast_df['predicted_carbon_kg'],
        mode='lines',
        name='Forecast',
        line=dict(color='#ff7f0e', dash='dash', width=2),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Predicted: %{y:.1f} kg<extra></extra>'
    ))
    
    # Confidence interval
    fig1.add_trace(go.Scatter(
        x=forecast_df['date'].tolist() + forecast_df['date'].tolist()[::-1],
        y=forecast_df['ci_upper'].tolist() + forecast_df['ci_lower'].tolist()[::-1],
        fill='toself',
        name='95% Confidence Interval',
        fillcolor='rgba(255, 127, 14, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hovertemplate='<extra></extra>'
    ))
    
    fig1.update_layout(
        title="Carbon Emissions Timeline & Forecast",
        xaxis_title="Date",
        yaxis_title="CO₂e (kg)",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Service Breakdown
with col2:
    service_carbon = filtered_df.groupby('service')['carbon_kg_co2e'].sum()
    
    fig2 = go.Figure(data=[go.Pie(
        labels=service_carbon.index,
        values=service_carbon.values,
        hole=0.3,
        hovertemplate='<b>%{label}</b><br>CO₂e: %{value:.1f} kg (%{percent})<extra></extra>'
    )])
    
    fig2.update_layout(
        title="Carbon Emissions by Service",
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)

# Charts 3 & 4: Regional and Project views
col1, col2 = st.columns(2)

with col1:
    region_carbon = filtered_df.groupby('region')['carbon_kg_co2e'].sum().sort_values()
    
    fig3 = go.Figure(data=[go.Bar(
        x=region_carbon.values,
        y=region_carbon.index,
        orientation='h',
        marker=dict(color=region_carbon.values, colorscale='Viridis'),
        hovertemplate='<b>%{y}</b><br>CO₂e: %{x:.1f} kg<extra></extra>'
    )])
    
    fig3.update_layout(
        title="Carbon Emissions by Region",
        xaxis_title="CO₂e (kg)",
        height=350
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    project_carbon = filtered_df.groupby('project')['carbon_kg_co2e'].sum().sort_values(ascending=False)
    
    fig4 = go.Figure(data=[go.Bar(
        x=project_carbon.index,
        y=project_carbon.values,
        marker=dict(color=project_carbon.values, colorscale='Reds'),
        hovertemplate='<b>%{x}</b><br>CO₂e: %{y:.1f} kg<extra></extra>'
    )])
    
    fig4.update_layout(
        title="Carbon Emissions by Project",
        yaxis_title="CO₂e (kg)",
        height=350
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ===== GREEN SCORES =====
st.subheader("🟢 Project Sustainability Scores")

score_cols = st.columns(len(green_scores_df))
for idx, (col, row) in enumerate(zip(score_cols, green_scores_df.itertuples())):
    with col:
        grade = row.grade
        color_map = {'A': '🟢', 'B': '🟡', 'C': '🟠', 'D': '🔴', 'F': '🔴'}
        color = color_map.get(grade, '⚪')
        
        st.metric(
            label=row.project,
            value=f"{color} {grade}",
            delta=f"Score: {row.green_score:.2f}",
            help=f"Carbon: {row.current_carbon_kg:.0f} kg | Cost/kg: ${row.cost_per_kg_usd:.2f}"
        )

st.markdown("---")

# ===== RECOMMENDATIONS =====
st.subheader("💡 Optimization Recommendations")

top_recs = recommendations_df.head(5)
for idx, row in top_recs.iterrows():
    effort_color = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}[row['effort']]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {idx + 1}. {row['title']}")
        st.write(f"**{row['description']}**")
        
        rec_col1, rec_col2, rec_col3 = st.columns(3)
        with rec_col1:
            st.metric("CO₂e Reduction", f"{row['estimated_carbon_reduction_kg']:.0f} kg")
        with rec_col2:
            st.metric("Cost Savings", f"${row['estimated_cost_savings_usd']:.0f}")
        with rec_col3:
            st.metric("Effort", f"{effort_color} {row['effort']}")
    
    st.markdown("---")

# ===== CI/CD INTEGRATION MESSAGE =====
st.subheader("🚀 CI/CD Integration")

worst_project = green_scores_df.iloc[-1]
if worst_project['grade'] in ['D', 'F']:
    st.warning(
        f"⚠️ **Low Green Score Detected**\n\n"
        f"Project '{worst_project['project']}' has a Green Score of **{worst_project['grade']}**. "
        f"Please review and implement recommendations before deployment.\n\n"
        f"This would be a **soft gate** in your CI/CD pipeline.",
        icon="🚨"
    )
else:
    st.success(
        f"✅ All projects have acceptable Green Scores. Deployment approved.",
        icon="✅"
    )

st.markdown("---")
st.caption("GreenOps AI Dashboard | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
