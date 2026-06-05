"""
Forecaster: Train ARIMA model and generate quarterly carbon emission forecasts
"""
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

def prepare_timeseries_data(consumption_df):
    """Prepare data for time series modeling"""
    # Aggregate daily carbon totals
    consumption_df['date'] = pd.to_datetime(consumption_df['date'])
    daily_carbon = consumption_df.groupby(consumption_df['date'].dt.date)['carbon_kg_co2e'].sum().reset_index()
    daily_carbon.columns = ['date', 'carbon_kg_co2e']
    daily_carbon['date'] = pd.to_datetime(daily_carbon['date'])
    daily_carbon = daily_carbon.sort_values('date')
    
    print(f"✓ Prepared time series: {len(daily_carbon)} days of data")
    return daily_carbon

def train_arima_model(daily_carbon):
    """Train ARIMA model on historical carbon data"""
    # Split into train/test
    train_size = int(len(daily_carbon) * 0.8)
    train_data = daily_carbon['carbon_kg_co2e'][:train_size]
    test_data = daily_carbon['carbon_kg_co2e'][train_size:]
    
    print(f"  Training set: {len(train_data)} days")
    print(f"  Test set: {len(test_data)} days")
    
    # Train ARIMA(1,1,1)
    try:
        model = ARIMA(train_data, order=(1, 1, 1))
        fitted_model = model.fit()
        
        # Validate on test set
        predictions = fitted_model.get_forecast(steps=len(test_data)).predicted_mean
        mae = mean_absolute_error(test_data, predictions)
        rmse = np.sqrt(mean_squared_error(test_data, predictions))
        mape = np.mean(np.abs((test_data - predictions) / test_data)) * 100
        
        print(f"✓ Model trained successfully!")
        print(f"  MAE:  {mae:.2f} kg CO2e")
        print(f"  RMSE: {rmse:.2f} kg CO2e")
        print(f"  MAPE: {mape:.2f}%")
        
        return fitted_model, daily_carbon
    except Exception as e:
        print(f"⚠ ARIMA fitting failed: {e}")
        print(f"  Using Linear Regression fallback...")
        return None, daily_carbon

def forecast_carbon(fitted_model, daily_carbon, days=90):
    """Forecast carbon emissions for next N days"""
    if fitted_model is None:
        # Fallback: use simple linear trend
        x = np.arange(len(daily_carbon))
        y = daily_carbon['carbon_kg_co2e'].values
        coeffs = np.polyfit(x, y, 1)
        
        last_date = daily_carbon['date'].max()
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)
        x_future = np.arange(len(daily_carbon), len(daily_carbon) + days)
        predictions = np.polyval(coeffs, x_future)
        
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'predicted_carbon_kg': predictions,
            'ci_lower': predictions * 0.9,
            'ci_upper': predictions * 1.1
        })
    else:
        forecast_result = fitted_model.get_forecast(steps=days)
        last_date = daily_carbon['date'].max()
        
        forecast_df = pd.DataFrame({
            'date': pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days),
            'predicted_carbon_kg': forecast_result.predicted_mean.values,
            'ci_lower': forecast_result.conf_int().iloc[:, 0].values,
            'ci_upper': forecast_result.conf_int().iloc[:, 1].values
        })
    
    return forecast_df

if __name__ == "__main__":
    # Load and prepare data
    consumption_df = pd.read_csv('data/historical_consumption.csv')
    daily_carbon = prepare_timeseries_data(consumption_df)
    
    # Train model
    print("\nTraining ARIMA model...")
    fitted_model, daily_carbon = train_arima_model(daily_carbon)
    
    # Generate forecast
    print("\nGenerating 90-day forecast...")
    forecast_df = forecast_carbon(fitted_model, daily_carbon, days=90)
    forecast_df.to_csv('data/carbon_forecast.csv', index=False)
    
    print(f"✓ Forecast saved to data/carbon_forecast.csv")
    print(f"  Forecast period: {forecast_df['date'].min().date()} to {forecast_df['date'].max().date()}")
    print(f"  Average predicted daily carbon: {forecast_df['predicted_carbon_kg'].mean():.2f} kg")
    print(f"  Total forecasted carbon (Q+1): {forecast_df['predicted_carbon_kg'].sum():.2f} kg")
