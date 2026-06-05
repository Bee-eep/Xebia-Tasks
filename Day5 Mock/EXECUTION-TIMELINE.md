# GreenOps AI Dashboard - Detailed Execution Timeline

## 4-Hour Sprint Schedule

### **Hour 1: Foundation & Data (0:00 - 1:00)**

| Time | Task | Deliverable | Status |
|------|------|-------------|--------|
| 0:00-0:10 | Project setup, venv, dependencies | `requirements.txt`, virtual env ready | ⏳ |
| 0:10-0:25 | Data simulator creation | `data/simulator.py` (generate 12 months) | ⏳ |
| 0:25-0:35 | Run simulator, validate data | `data/historical_consumption.csv` | ⏳ |
| 0:35-1:00 | Carbon calculator implementation | `models/carbon_calculator.py` with region factors | ⏳ |

**Checkpoint:** Historical data ready, carbon conversion functions tested

---

### **Hour 2: AI & Forecasting (1:00 - 2:00)**

| Time | Task | Deliverable | Status |
|------|------|-------------|--------|
| 1:00-1:10 | Data preprocessing for ML | Clean historical data, train/test split | ⏳ |
| 1:10-1:35 | ARIMA model training | `models/forecaster.py` with ARIMA implementation | ⏳ |
| 1:35-1:50 | Generate quarterly forecast | `data/carbon_forecast.csv` (90-day prediction) | ⏳ |
| 1:50-2:00 | Model evaluation & metrics | MAE, RMSE logged, confidence intervals set | ⏳ |

**Checkpoint:** Forecast model validated, predictions ready for visualization

---

### **Hour 3: Dashboard & Visualization (2:00 - 3:00)**

| Time | Task | Deliverable | Status |
|------|------|-------------|--------|
| 2:00-2:10 | Dashboard scaffold | `dashboard/app.py` structure, imports, layout | ⏳ |
| 2:10-2:25 | KPI cards (4 metrics) | Current emissions, forecast, cost efficiency, trend | ⏳ |
| 2:25-2:45 | Data visualization charts | Timeline + forecast, service breakdown, regional view | ⏳ |
| 2:45-3:00 | Interactive filters & polish | Project/region selectors, responsive design | ⏳ |

**Checkpoint:** Dashboard live at `localhost:8501`, all KPIs visible

---

### **Hour 4: Optimization & Integration (3:00 - 4:00)**

| Time | Task | Deliverable | Status |
|------|------|-------------|--------|
| 3:00-3:15 | Optimization recommendations engine | `models/optimizer.py` - 5-8 action items with ROI | ⏳ |
| 3:15-3:30 | Green Score implementation | `models/green_scorer.py` - A-F scale calculation | ⏳ |
| 3:30-3:45 | Add recommendations to dashboard | Display top 3 with impact/effort badges | ⏳ |
| 3:45-4:00 | Final testing & documentation | Verify all flows, document setup in README | ⏳ |

**Checkpoint:** Complete MVP deployed, all features functional

---

## Critical Path & Parallel Work Opportunities

### Can Be Done in Parallel (if team of 2):
- **Stream A**: Data setup (Hour 1)
- **Stream B**: Dashboard scaffolding & visualization (Hour 3, starts at 1:30)

### Sequential Dependencies (must complete in order):
1. Data generation → Carbon calculation
2. Carbon data → Forecasting model
3. Forecast + historical data → Dashboard
4. Dashboard + forecast → Recommendations
5. Recommendations → Green Score display

---

## Risk Mitigation & Fallbacks

| Risk | Mitigation | Fallback |
|------|-----------|----------|
| ARIMA model won't converge | Use simple linear regression | Use last-value-carried-forward (LVCF) forecast |
| Streamlit performance | Limit data to 12 months + 3 months forecast | Pre-aggregate to weekly data |
| Time overrun | Skip advanced visualizations, use simple charts | Focus on 2 KPIs + 1 chart |
| Data quality issues | Validate simulator output early (0:30 mark) | Use mock hardcoded data |

---

## Testing Checkpoints

### **Checkpoint 1 (1:00)** - Data Ready
```python
# Verify CSV exists and is valid
import pandas as pd
df = pd.read_csv('data/historical_consumption.csv')
assert len(df) == 365*3  # ~1 year of daily data
assert 'carbon_kg_co2e' in df.columns
print(f"✓ Data ready: {len(df)} rows")
```

### **Checkpoint 2 (2:00)** - Forecast Ready
```python
forecast_df = pd.read_csv('data/carbon_forecast.csv')
assert len(forecast_df) == 90  # 3 months
assert forecast_df['predicted_carbon_kg'].isna().sum() == 0
print(f"✓ Forecast ready: MAE={mae:.2f}, RMSE={rmse:.2f}")
```

### **Checkpoint 3 (3:00)** - Dashboard Live
```bash
streamlit run dashboard/app.py
# Open http://localhost:8501 in browser
# Verify: 4 KPI cards visible, 1 chart loads, no errors in terminal
```

### **Checkpoint 4 (4:00)** - MVP Complete
```bash
# Run full test suite
python -m pytest tests/  # (basic smoke tests)
# Manual verification:
# - Dashboard displays 4 KPIs
# - 3 charts render without errors
# - Green Score badge shows (A-F)
# - Top 3 recommendations listed
# - No Python exceptions in console
```

---

## Key Assumptions

1. **No Real Cloud Integration**: Using simulated AWS/Azure data (realistic patterns)
2. **Single-User**: No need for authentication or multi-tenancy
3. **CSV Storage**: No database backend (simplifies scope)
4. **Streamlit Frontend**: Faster to prototype than React/custom build
5. **Mock CI/CD**: Display recommendations as if integrated; actual pipeline integration is post-MVP

---

## Success Metrics

By end of 4 hours, demonstrate:

✅ **Data Fidelity**: Simulated data realistic and complete  
✅ **Model Accuracy**: Forecast RMSE < 15% of historical mean  
✅ **Visualization**: Dashboard loads in <3 seconds  
✅ **Recommendations**: At least 5 actionable insights generated  
✅ **Green Score**: All projects have A-F scores  
✅ **Documentation**: README with setup instructions + screenshots  

---

## File Dependencies Map

```
simulator.py
    ↓
historical_consumption.csv
    ↓
    ├→ carbon_calculator.py
    │   ↓
    │   carbon_emissions.csv
    │       ↓
    │       ├→ forecaster.py → carbon_forecast.csv
    │       │       ↓
    │       └→ optimizer.py → recommendations.json
    │
    └→ dashboard/app.py
        ├→ Reads: historical_consumption.csv
        ├→ Reads: carbon_forecast.csv
        ├→ Reads: recommendations.json
        └→ Displays: KPIs, charts, Green Score
```

---

## Next Steps Post-MVP

1. **Real API Integration** (2-3 hours)
   - AWS Cost Explorer API
   - Azure Cost Management API
   - Live data ingestion

2. **Green Score CI/CD Gate** (2 hours)
   - GitHub Actions workflow
   - Automatic scoring on PR submission

3. **Scaling & Optimization** (4+ hours)
   - Database backend (PostgreSQL)
   - REST API for external access
   - Caching layer

4. **Production Hardening** (ongoing)
   - Error handling & logging
   - Authentication & authorization
   - Monitoring & alerts
