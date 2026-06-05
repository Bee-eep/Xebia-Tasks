"""
Data Simulator: Generate realistic cloud consumption data for 12 months
"""
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
    print(f"✓ Generated {len(df)} records in data/historical_consumption.csv")
    return df

if __name__ == "__main__":
    generate_consumption_data()
