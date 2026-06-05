# GreenOps AI Dashboard - Quick Reference Guide

## 1. Hour-by-Hour Command Cheat Sheet

### **Hour 1 Setup**
```bash
# Initialize project
mkdir greenops-ai-dashboard && cd greenops-ai-dashboard
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install pandas numpy scikit-learn statsmodels streamlit plotly python-dateutil

# Create directory structure
mkdir data models dashboard
touch data/simulator.py models/carbon_calculator.py models/forecaster.py dashboard/app.py requirements.txt

# Freeze requirements
pip freeze > requirements.txt
```

---

## 2. Core Implementation Snippets

### **A. Data Simulator** (`data/simulator.py`)
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_consumption_data(months=12):
    """Generate realistic cloud consumption data for 12 months"""
    dates = pd.date_range(end=datetime.now(), periods=months*30, freq='D')
    
    projects = ['ProjectA', 'ProjectB', 'ProjectC', 'ProjectD']
    regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1']
    services = ['EC2', 'RDS', 'S3', 'DataTransfer']
    
    records = []
    for date in dates:
        for project in projects:
            # Add seasonal variation
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * date.dayofyear / 365)
            
            for service in services:
                base_qty = {'EC2': 100, 'RDS': 50, 'S3': 200, 'DataTransfer': 500}[service]
                region = np.random.choice(regions)
                
                quantity = base_qty * seasonal_factor * np.random.uniform(0.8, 1.2)
                cost = quantity * {'EC2': 0.10, 'RDS': 0.15, 'S3': 0.023, 'DataTransfer': 0.02}[service]
                
                records.append({
                    'date': date,
                    'project': project,
                    'region': region,
                    'service': service,
                    'quantity': quantity,
                    'cost_usd': cost
                })
    
    df = pd.DataFrame(records)
    df.to_csv('data/historical_consumption.csv', index=False)
    print(f"✓ Generated {len(df)} records")
    return df

if __name__ == "__main__":
    generate_consumption_data()
```

### **B. Carbon Calculator** (`models/carbon_calculator.py`)
```python
import pandas as pd

# Carbon intensity factors (kg CO2e per kWh)
CARBON_INTENSITY = {
    'us-east-1': 0.415,
    'eu-west-1': 0.238,
    'ap-southeast-1': 0.420
}

# Power consumption per service unit (Watts)
POWER_CONSUMPTION = {
    'EC2': 50,          # per vCPU per hour
    'RDS': 75,          # per instance per hour
    'S3': 0.5,          # per GB per month
    'DataTransfer': 0.1 # per GB
}

def calculate_carbon(service, region, quantity):
    """Calculate CO2e emissions from cloud service usage"""
    power_w = POWER_CONSUMPTION.get(service, 50)
    intensity = CARBON_INTENSITY.get(region, 0.40)
    
    # Convert quantity to energy (kWh)
    if service in ['EC2', 'RDS']:
        energy_kwh = (quantity * power_w) / 1000  # hours to kWh
    else:
        energy_kwh = (quantity * power_w) / 1000  # simplified
    
    carbon_kg_co2e = energy_kwh * intensity
    return carbon_kg_co2e

def add_carbon_to_consumption(consumption_df):
    """Add carbon emissions to consumption data"""
    consumption_df['carbon_kg_co2e'] = consumption_df.apply(
        lambda row: calculate_carbon(row['service'], row['region'], row['quantity']),
        axis=1
    )
    return consumption_df

if __name__ == "__main__":
    df = pd.read_csv('data/historical_consumption.csv')
    df = add_carbon_to_consumption(df)
    df.to_csv('data/historical_consumption.csv', index=False)
    print(f"✓ Carbon calculations added")
    print(f"Total CO2e: {df['carbon_kg_co2e'].sum():.2f} kg")
```

### **C. ARIMA Forecaster** (`models/forecaster.py`)
```python
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error

def train_arima_model(consumption_df):
    """Train ARIMA model on historical carbon data"""
    # Aggregate daily carbon totals
    daily_carbon = consumption_df.groupby('date')['carbon_kg_co2e'].sum().reset_index()
    daily_carbon = daily_carbon.sort_values('date')
    
    # Split into train/test
    train_size = int(len(daily_carbon) * 0.8)
    train_data = daily_carbon['carbon_kg_co2e'][:train_size]
    test_data = daily_carbon['carbon_kg_co2e'][train_size:]
    
    # Train ARIMA(1,1,1)
    model = ARIMA(train_data, order=(1, 1, 1))
    fitted_model = model.fit()
    
    # Validate on test set
    predictions = fitted_model.get_forecast(steps=len(test_data)).predicted_mean
    mae = mean_absolute_error(test_data, predictions)
    rmse = np.sqrt(mean_squared_error(test_data, predictions))
    
    print(f"Model Validation - MAE: {mae:.2f}, RMSE: {rmse:.2f}")
    return fitted_model, daily_carbon

def forecast_carbon(fitted_model, daily_carbon, days=90):
    """Forecast carbon emissions for next N days"""
    forecast_result = fitted_model.get_forecast(steps=days)
    forecast_df = pd.DataFrame({
        'date': pd.date_range(start=daily_carbon['date'].max() + pd.Timedelta(days=1), periods=days),
        'predicted_carbon_kg': forecast_result.predicted_mean.values,
        'ci_lower': forecast_result.conf_int().iloc[:, 0].values,
        'ci_upper': forecast_result.conf_int().iloc[:, 1].values
    })
    return forecast_df

if __name__ == "__main__":
    df = pd.read_csv('data/historical_consumption.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    model, daily_carbon = train_arima_model(df)
    forecast_df = forecast_carbon(model, daily_carbon, days=90)
    forecast_df.to_csv('data/carbon_forecast.csv', index=False)
    print(f"✓ Forecast saved: {len(forecast_df)} days")
```

### **D. Green Score Calculator** (`models/green_scorer.py`)
```python
import pandas as pd
import numpy as np

def calculate_green_score(project_carbon, forecast_carbon, cost_efficiency):
    """
    Calculate Green Score (0-1, mapped to A-F)
    - project_carbon: current emissions trend (normalized)
    - forecast_carbon: predicted next quarter (normalized)
    - cost_efficiency: USD per kg CO2e (lower is better)
    """
    # Normalize inputs (0-1 scale)
    emission_efficiency = 1 - min(project_carbon / 100, 1)  # Lower is better
    trend_improvement = max(0, (project_carbon - forecast_carbon) / project_carbon)  # Positive trend
    cost_ratio = max(0, 1 - cost_efficiency / 10)  # Lower cost per carbon is better
    
    # Weighted score
    green_score = (emission_efficiency * 0.4 + 
                   trend_improvement * 0.3 + 
                   cost_ratio * 0.3)
    return max(0, min(1, green_score))

def score_to_grade(green_score):
    """Convert numeric score (0-1) to letter grade (A-F)"""
    grades = {
        (0.9, 1.0): 'A',
        (0.7, 0.9): 'B',
        (0.5, 0.7): 'C',
        (0.3, 0.5): 'D',
        (0.0, 0.3): 'F'
    }
    for (min_val, max_val), grade in grades.items():
        if min_val <= green_score < max_val:
            return grade
    return 'F'

def score_all_projects(consumption_df, forecast_df):
    """Generate Green Scores for all projects"""
    results = []
    
    for project in consumption_df['project'].unique():
        project_data = consumption_df[consumption_df['project'] == project]
        current_carbon = project_data['carbon_kg_co2e'].sum()
        
        # Estimate forecast for this project (proportional)
        project_fraction = current_carbon / consumption_df['carbon_kg_co2e'].sum()
        forecast_carbon = forecast_df['predicted_carbon_kg'].sum() * project_fraction
        
        # Calculate cost efficiency
        total_cost = project_data['cost_usd'].sum()
        cost_efficiency = total_cost / current_carbon if current_carbon > 0 else 0
        
        # Calculate score
        green_score = calculate_green_score(current_carbon, forecast_carbon, cost_efficiency)
        grade = score_to_grade(green_score)
        
        results.append({
            'project': project,
            'green_score': green_score,
            'grade': grade,
            'current_carbon_kg': current_carbon,
            'forecast_carbon_kg': forecast_carbon,
            'cost_per_kg_usd': cost_efficiency
        })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    consumption_df = pd.read_csv('data/historical_consumption.csv')
    consumption_df['date'] = pd.to_datetime(consumption_df['date'])
    forecast_df = pd.read_csv('data/carbon_forecast.csv')
    
    scores = score_all_projects(consumption_df, forecast_df)
    print("\nGreen Scores:")
    print(scores)
```

### **E. Streamlit Dashboard** (`dashboard/app.py`)
```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="GreenOps AI Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    consumption = pd.read_csv('../data/historical_consumption.csv')
    consumption['date'] = pd.to_datetime(consumption['date'])
    
    forecast = pd.read_csv('../data/carbon_forecast.csv')
    forecast['date'] = pd.to_datetime(forecast['date'])
    
    return consumption, forecast

consumption_df, forecast_df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_project = st.sidebar.multiselect(
    "Project", 
    consumption_df['project'].unique(),
    default=consumption_df['project'].unique()
)
selected_region = st.sidebar.multiselect(
    "Region",
    consumption_df['region'].unique(),
    default=consumption_df['region'].unique()
)

# Filter data
filtered_df = consumption_df[
    (consumption_df['project'].isin(selected_project)) &
    (consumption_df['region'].isin(selected_region))
]

# Dashboard title
st.title("🌱 GreenOps AI Dashboard")
st.markdown("Real-time Carbon Emissions & Sustainability Metrics")

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

total_carbon = filtered_df['carbon_kg_co2e'].sum()
total_cost = filtered_df['cost_usd'].sum()
forecasted_carbon = forecast_df['predicted_carbon_kg'].sum()
cost_per_carbon = total_cost / total_carbon if total_carbon > 0 else 0

with col1:
    st.metric("Total Emissions (Current)", f"{total_carbon:,.0f} kg CO2e")
with col2:
    st.metric("Forecasted (Q+1)", f"{forecasted_carbon:,.0f} kg CO2e")
with col3:
    st.metric("Cost Efficiency", f"${cost_per_carbon:.2f}/kg CO2e")
with col4:
    trend = ((forecasted_carbon - total_carbon) / total_carbon * 100) if total_carbon > 0 else 0
    st.metric("Trend", f"{trend:+.1f}%")

# Charts
st.subheader("📊 Visualizations")

col1, col2 = st.columns(2)

# Timeline Chart
with col1:
    daily_carbon = filtered_df.groupby('date')['carbon_kg_co2e'].sum().reset_index()
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=daily_carbon['date'], 
        y=daily_carbon['carbon_kg_co2e'],
        mode='lines', 
        name='Historical',
        line=dict(color='#1f77b4')
    ))
    fig1.add_trace(go.Scatter(
        x=forecast_df['date'], 
        y=forecast_df['predicted_carbon_kg'],
        mode='lines', 
        name='Forecast',
        line=dict(color='#ff7f0e', dash='dash')
    ))
    fig1.update_layout(title="Carbon Emissions Timeline", hovermode='x unified')
    st.plotly_chart(fig1, use_container_width=True)

# Service Breakdown
with col2:
    service_carbon = filtered_df.groupby('service')['carbon_kg_co2e'].sum()
    fig2 = px.pie(values=service_carbon.values, names=service_carbon.index, 
                  title="Carbon by Service")
    st.plotly_chart(fig2, use_container_width=True)

# Regional View
col1, col2 = st.columns(2)
with col1:
    region_carbon = filtered_df.groupby('region')['carbon_kg_co2e'].sum().sort_values()
    fig3 = px.bar(x=region_carbon.values, y=region_carbon.index, 
                  orientation='h', title="Carbon by Region")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    project_carbon = filtered_df.groupby('project')['carbon_kg_co2e'].sum().sort_values(ascending=False)
    fig4 = px.bar(x=project_carbon.index, y=project_carbon.values, 
                  title="Carbon by Project")
    st.plotly_chart(fig4, use_container_width=True)

# Recommendations
st.subheader("💡 Optimization Recommendations")
recommendations = [
    ("Rightsize non-prod VMs", "80-120 kg CO2e savings", "Medium", "🟢"),
    ("Migrate to cheaper region", "40-60 kg CO2e savings", "High", "🟡"),
    ("Consolidate RDS instances", "25-35 kg CO2e savings", "Low", "🟢")
]

for title, impact, effort, badge in recommendations:
    st.write(f"{badge} **{title}** | Impact: {impact} | Effort: {effort}")

st.success("Dashboard updated successfully!")
```

---

## 3. Execution Checklist

```
Hour 1:
☐ Create project structure
☐ Install dependencies (pip install -r requirements.txt)
☐ Run data simulator → historical_consumption.csv
☐ Run carbon calculator → data enriched with carbon_kg_co2e
☐ **CHECKPOINT**: CSV has 365+ rows, carbon column populated

Hour 2:
☐ Train ARIMA model
☐ Generate 90-day forecast
☐ Validate model (MAE < 20% of mean)
☐ Export forecast_df to carbon_forecast.csv
☐ **CHECKPOINT**: forecast_df has 90 rows, no NaN values

Hour 3:
☐ Create Streamlit app scaffold
☐ Add KPI cards (4 metrics)
☐ Add visualization charts (timeline, service, region, project)
☐ Add filters (project, region multi-select)
☐ Run: streamlit run dashboard/app.py
☐ **CHECKPOINT**: Dashboard loads at localhost:8501, all 4 charts render

Hour 4:
☐ Create optimizer.py with recommendations engine
☐ Create green_scorer.py with A-F scoring
☐ Add recommendations section to dashboard
☐ Add Green Score badge to dashboard
☐ Final testing & error checking
☐ **CHECKPOINT**: All 5 components integrated, no console errors
```

---

## 4. Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| ARIMA won't converge | Use `order=(0,1,1)` or switch to simple linear regression |
| Streamlit not updating | Use `@st.cache_data` decorator, clear cache with `⬅️ R` |
| Slow data loading | Aggregate to weekly, limit to last 12 months |
| Missing columns | Verify CSV headers match code expectations |
| Plotly charts blank | Check data shape with `df.head()`, ensure no NaN |

---

## 5. Running the Complete Pipeline

```bash
# Full automation (run once per hour)
python data/simulator.py
python models/carbon_calculator.py
python models/forecaster.py
python models/green_scorer.py
streamlit run dashboard/app.py
```

**Expected output**: Dashboard accessible at `http://localhost:8501` with all KPIs, charts, and recommendations visible.
