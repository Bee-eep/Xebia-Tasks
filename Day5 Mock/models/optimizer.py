"""
Optimization Engine: Generate actionable recommendations for carbon reduction
"""
import pandas as pd
import numpy as np

def generate_recommendations(consumption_df, green_scores_df, forecast_df):
    """Generate optimization recommendations based on analysis"""
    
    recommendations = []
    
    # Analyze by service type
    service_carbon = consumption_df.groupby('service')['carbon_kg_co2e'].sum().sort_values(ascending=False)
    service_cost = consumption_df.groupby('service')['cost_usd'].sum()
    
    # Recommendation 1: EC2 Rightsizing
    ec2_data = consumption_df[consumption_df['service'] == 'EC2']
    if len(ec2_data) > 0:
        ec2_carbon = ec2_data['carbon_kg_co2e'].sum()
        recommendations.append({
            'title': 'Rightsize EC2 instances',
            'description': 'Identify and downsize over-provisioned non-prod EC2 instances',
            'estimated_carbon_reduction_kg': ec2_carbon * 0.15,
            'estimated_cost_savings_usd': service_cost.get('EC2', 0) * 0.15,
            'effort': 'Medium',
            'impact_level': 'High'
        })
    
    # Recommendation 2: Regional optimization
    region_carbon = consumption_df.groupby('region')['carbon_kg_co2e'].sum().sort_values(ascending=False)
    high_carbon_region = region_carbon.idxmax()
    low_carbon_region = region_carbon.idxmin()
    
    if high_carbon_region != low_carbon_region:
        migration_volume = region_carbon.max() * 0.3
        recommendations.append({
            'title': f'Migrate to lower-carbon regions',
            'description': f'Move workloads from {high_carbon_region} to {low_carbon_region}',
            'estimated_carbon_reduction_kg': migration_volume,
            'estimated_cost_savings_usd': consumption_df[consumption_df['region'] == high_carbon_region]['cost_usd'].sum() * 0.2,
            'effort': 'High',
            'impact_level': 'High'
        })
    
    # Recommendation 3: Storage optimization
    s3_data = consumption_df[consumption_df['service'] == 'S3']
    if len(s3_data) > 0:
        s3_carbon = s3_data['carbon_kg_co2e'].sum()
        recommendations.append({
            'title': 'Implement S3 lifecycle policies',
            'description': 'Archive unused objects and remove old backups',
            'estimated_carbon_reduction_kg': s3_carbon * 0.25,
            'estimated_cost_savings_usd': service_cost.get('S3', 0) * 0.25,
            'effort': 'Low',
            'impact_level': 'Medium'
        })
    
    # Recommendation 4: Data Transfer optimization
    dt_data = consumption_df[consumption_df['service'] == 'DataTransfer']
    if len(dt_data) > 0:
        dt_carbon = dt_data['carbon_kg_co2e'].sum()
        recommendations.append({
            'title': 'Optimize data transfer patterns',
            'description': 'Use CloudFront CDN and regional endpoints',
            'estimated_carbon_reduction_kg': dt_carbon * 0.20,
            'estimated_cost_savings_usd': service_cost.get('DataTransfer', 0) * 0.20,
            'effort': 'Medium',
            'impact_level': 'Medium'
        })
    
    # Recommendation 5: RDS consolidation
    rds_data = consumption_df[consumption_df['service'] == 'RDS']
    if len(rds_data) > 0:
        rds_carbon = rds_data['carbon_kg_co2e'].sum()
        recommendations.append({
            'title': 'Consolidate RDS instances',
            'description': 'Merge low-traffic databases using read replicas',
            'estimated_carbon_reduction_kg': rds_carbon * 0.12,
            'estimated_cost_savings_usd': service_cost.get('RDS', 0) * 0.12,
            'effort': 'High',
            'impact_level': 'Medium'
        })
    
    # Recommendation 6: Project-level optimization
    worst_project = green_scores_df.iloc[-1]
    recommendations.append({
        'title': f'Focus optimization on {worst_project["project"]}',
        'description': f'Project has lowest Green Score ({worst_project["grade"]})',
        'estimated_carbon_reduction_kg': worst_project['current_carbon_kg'] * 0.20,
        'estimated_cost_savings_usd': worst_project['current_carbon_kg'] * worst_project['cost_per_kg_usd'] * 0.20,
        'effort': 'Medium',
        'impact_level': 'High'
    })
    
    # Recommendation 7: Forecast-based capacity planning
    forecast_total = forecast_df['predicted_carbon_kg'].sum()
    historical_total = consumption_df['carbon_kg_co2e'].sum()
    
    if forecast_total > historical_total * 1.1:
        recommendations.append({
            'title': 'Implement demand forecasting',
            'description': 'Proactively scale down capacity before peak periods end',
            'estimated_carbon_reduction_kg': (forecast_total - historical_total) * 0.5,
            'estimated_cost_savings_usd': (forecast_total - historical_total) * 0.015,
            'effort': 'Low',
            'impact_level': 'Medium'
        })
    
    # Convert to DataFrame
    recs_df = pd.DataFrame(recommendations)
    
    # Calculate ROI (carbon reduction per unit effort)
    effort_weights = {'Low': 3, 'Medium': 2, 'High': 1}
    recs_df['roi_score'] = recs_df['estimated_carbon_reduction_kg'] * recs_df['effort'].map(effort_weights)
    recs_df = recs_df.sort_values('roi_score', ascending=False)
    
    return recs_df

if __name__ == "__main__":
    consumption_df = pd.read_csv('data/historical_consumption.csv')
    consumption_df['date'] = pd.to_datetime(consumption_df['date'])
    green_scores_df = pd.read_csv('data/green_scores.csv')
    forecast_df = pd.read_csv('data/carbon_forecast.csv')
    
    recommendations = generate_recommendations(consumption_df, green_scores_df, forecast_df)
    recommendations.to_csv('data/recommendations.csv', index=False)
    
    print("✓ Recommendations generated and saved to data/recommendations.csv")
    print("\nTop Optimization Recommendations (by ROI):")
    for idx, row in recommendations.head(5).iterrows():
        print(f"\n{idx+1}. {row['title']}")
        print(f"   Description: {row['description']}")
        print(f"   CO2e Reduction: {row['estimated_carbon_reduction_kg']:.1f} kg")
        print(f"   Cost Savings: ${row['estimated_cost_savings_usd']:.2f}")
        print(f"   Effort: {row['effort']}")
