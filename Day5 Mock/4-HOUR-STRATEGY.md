# GreenOps AI Dashboard - 4-Hour Implementation Strategy

## Overview
Deliver a functional MVP of the GreenOps AI Dashboard with simulated cloud data, AI forecasting, visualization, and optimization recommendations.

---

## Phase Breakdown (240 minutes)

### **Phase 1: Foundation & Data Setup (50 minutes)**
**Goal:** Establish project structure and simulate cloud consumption data

#### 1.1 Project Scaffolding (15 min)
- Create Python project structure with virtual environment
- Initialize directories: `data/`, `models/`, `dashboard/`, `api/`
- Install core dependencies:
  - `pandas`, `numpy` - data handling
  - `scikit-learn`, `statsmodels` - ML models
  - `streamlit` - dashboard
  - `flask` or `fastapi` - backend API

#### 1.2 Data Simulation Engine (35 min)
- Create `data/simulator.py` - generates 12 months of simulated AWS/Azure consumption data
- Metrics to simulate:
  - EC2/VM hours by instance type
  - Storage (GB)
  - Data transfer (GB)
  - Regional distribution
- Output: CSV with columns: `[date, service, region, quantity, cost_usd]`
- Include 3-4 different projects/business units
- Store generated data in `data/historical_consumption.csv`

**Deliverable:** Realistic historical dataset ready for ML training

---

### **Phase 2: AI Forecasting & Carbon Calculation (60 minutes)**
**Goal:** Build ML forecasting model and calculate CO2e emissions

#### 2.1 Carbon Emission Calculation (15 min)
- Create `models/carbon_calculator.py`
- Conversion factors:
  - AWS/Azure carbon intensity by region (kgCO2e per kWh)
  - Service-to-power consumption mappings (e.g., 1 EC2 vCPU ≈ 50W)
- Function: `calculate_carbon_emissions(service, region, quantity) → kg_co2e`
- Pre-computed lookup table for common regions

#### 2.2 Time Series Forecasting Model (35 min)
- Create `models/forecaster.py`
- Implement 2 models:
  - **ARIMA**: Quick implementation using `statsmodels` (primary)
  - **Linear Regression with trend**: Fallback for stability
- Train on 12-month historical data
- Forecast next 90 days (Q+1)
- Include confidence intervals (95%)
- Export predictions to `data/carbon_forecast.csv`

#### 2.3 Model Evaluation (10 min)
- Calculate MAE, RMSE on validation set
- Log performance metrics for dashboard

**Deliverable:** Quarterly carbon emissions forecast with accuracy metrics

---

### **Phase 3: Dashboard & Visualization (70 minutes)**
**Goal:** Build interactive Streamlit dashboard with real-time metrics

#### 3.1 Dashboard Structure (20 min)
- Create `dashboard/app.py` (Streamlit main app)
- Layout:
  - Header: "GreenOps AI Dashboard"
  - Sidebar: filters (project, region, date range)
  - Main grid (3 KPI cards + 2 charts)

#### 3.2 KPI Cards (15 min)
Display 4 critical metrics:
1. **Total Carbon Emissions (Current Month)** - kg CO2e
2. **Forecasted Carbon Emissions (Next Quarter)** - kg CO2e
3. **Cloud Cost per kg CO2e** - USD/kg (cost efficiency ratio)
4. **Carbon Intensity Trend** - % change YoY

#### 3.3 Data Visualizations (25 min)
- **Chart 1: Historical + Forecast Timeline**
  - Line chart: 12-month history + 3-month forecast
  - Shaded confidence interval
  - Highlight forecast region
- **Chart 2: Carbon Breakdown by Service**
  - Pie chart: EC2 vs. Storage vs. Data Transfer
- **Chart 3: Regional Carbon Intensity**
  - Bar chart: Carbon emissions by region
- **Chart 4: Project-Level Carbon Distribution**
  - Horizontal bar chart (top 5 projects)

#### 3.4 Interactive Filters (10 min)
- Project/Business Unit selector
- Date range picker
- Region multi-select
- Charts update dynamically based on selections

**Deliverable:** Fully functional Streamlit dashboard with KPIs and visualizations

---

### **Phase 4: Optimization Engine & Green Score (60 minutes)**
**Goal:** Deliver recommendations and Shift-Left Green Score

#### 4.1 Optimization Recommendation Engine (25 min)
- Create `models/optimizer.py`
- Generate 5-8 actionable recommendations:
  - "Rightsize instances with <20% CPU utilization"
  - "Migrate low-traffic services to cheaper regions" (e.g., us-east-1 vs. eu-west-1)
  - "Consolidate databases to reduce redundancy"
  - "Schedule non-prod resources to stop during off-hours"
  - "Switch to spot instances for batch jobs"
- Each recommendation includes:
  - **Impact**: Estimated CO2e reduction (kg) + cost savings (USD)
  - **Effort**: High/Medium/Low
  - **Priority**: Based on impact/effort ratio
- Sort by ROI (carbon reduction vs. implementation effort)

#### 4.2 Green Score Implementation (20 min)
- Create `models/green_scorer.py`
- Score calculation (A-F scale):
  - Input: project's carbon intensity, forecasted trend, cost efficiency
  - Formula: `Green Score = (emission_efficiency + trend_improvement + cost_ratio) / 3`
  - Map to grades:
    - **A**: Excellent (Green Score ≥ 0.9)
    - **B**: Good (0.7-0.89)
    - **C**: Fair (0.5-0.69)
    - **D**: Poor (0.3-0.49)
    - **F**: Critical (< 0.3)
- Add Green Score visualization to dashboard (badge/gauge)

#### 4.3 Recommendations Display in Dashboard (15 min)
- Add recommendations section to dashboard
- Display top 3 recommendations with:
  - Impact badge (green/yellow/red)
  - Estimated savings
  - Implementation difficulty
- Mock CI/CD integration message: "⚠️ Low Green Score detected - Review recommendations before deployment"

**Deliverable:** Actionable optimization engine with Shift-Left Green Score

---

## Implementation Checklist

### **Quick-Start Commands**
```bash
# Initialize project
mkdir greenops-ai-dashboard
cd greenops-ai-dashboard
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install pandas numpy scikit-learn statsmodels streamlit flask

# Run components
python data/simulator.py          # Generate data
python models/forecaster.py       # Train & forecast
streamlit run dashboard/app.py    # Launch dashboard
```

### **File Structure**
```
greenops-ai-dashboard/
├── data/
│   ├── simulator.py
│   ├── historical_consumption.csv
│   └── carbon_forecast.csv
├── models/
│   ├── carbon_calculator.py
│   ├── forecaster.py
│   ├── optimizer.py
│   └── green_scorer.py
├── dashboard/
│   └── app.py
├── api/
│   └── recommendations_api.py (optional expansion)
└── requirements.txt
```

---

## Time Buffer & Flexibility

- **Contingency**: 15-min buffer built-in for debugging/troubleshooting
- **MVP Scope**: Focuses on core functionality; excludes:
  - Real AWS/Azure API integration (use simulation)
  - Database persistence (use CSV files)
  - Authentication/authorization
  - Production deployment

---

## Success Criteria (End of 4 Hours)

✅ Historical consumption data simulated and stored  
✅ Carbon emissions calculated with regional factors  
✅ ARIMA forecasting model trained on 12-month history  
✅ Streamlit dashboard displays 4+ KPIs and 3+ visualizations  
✅ Top 5 optimization recommendations generated  
✅ Green Score (A-F) calculated and displayed  
✅ All components integrated in single dashboard  
✅ Project documented and runnable with single command  

---

## Post-MVP Extensions (Future Sprints)

- Real AWS/Azure API integration
- Database backend (PostgreSQL/DynamoDB)
- CI/CD pipeline integration for Green Score gates
- User authentication and role-based access
- Export reports (PDF/Excel)
- Scheduled forecasting updates
- Alert system for policy violations
