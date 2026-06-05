"""
Carbon Calculator: Calculate CO2e emissions from cloud service usage
"""
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
    print(f"✓ Carbon calculations added to data/historical_consumption.csv")
    print(f"  Total CO2e: {df['carbon_kg_co2e'].sum():.2f} kg")
    print(f"  Sample data:")
    print(df.head())
