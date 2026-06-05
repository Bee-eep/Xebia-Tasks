"""
Green Score Calculator: Calculate A-F sustainability scores for projects
"""
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
    emission_efficiency = max(0, 1 - min(project_carbon / 100, 1))  # Lower is better
    trend_improvement = max(0, (project_carbon - forecast_carbon) / max(project_carbon, 1))  # Positive trend
    cost_ratio = max(0, 1 - cost_efficiency / 10)  # Lower cost per carbon is better
    
    # Weighted score
    green_score = (emission_efficiency * 0.4 + 
                   trend_improvement * 0.3 + 
                   cost_ratio * 0.3)
    return max(0, min(1, green_score))

def score_to_grade(green_score):
    """Convert numeric score (0-1) to letter grade (A-F)"""
    if 0.9 <= green_score <= 1.0:
        return 'A'
    elif 0.7 <= green_score < 0.9:
        return 'B'
    elif 0.5 <= green_score < 0.7:
        return 'C'
    elif 0.3 <= green_score < 0.5:
        return 'D'
    else:
        return 'F'

def score_all_projects(consumption_df, forecast_df):
    """Generate Green Scores for all projects"""
    results = []
    
    total_carbon = consumption_df['carbon_kg_co2e'].sum()
    total_forecast = forecast_df['predicted_carbon_kg'].sum()
    
    for project in sorted(consumption_df['project'].unique()):
        project_data = consumption_df[consumption_df['project'] == project]
        current_carbon = project_data['carbon_kg_co2e'].sum()
        
        # Estimate forecast for this project (proportional)
        project_fraction = current_carbon / total_carbon if total_carbon > 0 else 0
        forecast_carbon = total_forecast * project_fraction
        
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
    
    return pd.DataFrame(results).sort_values('green_score', ascending=False)

if __name__ == "__main__":
    consumption_df = pd.read_csv('data/historical_consumption.csv')
    consumption_df['date'] = pd.to_datetime(consumption_df['date'])
    forecast_df = pd.read_csv('data/carbon_forecast.csv')
    
    scores = score_all_projects(consumption_df, forecast_df)
    scores.to_csv('data/green_scores.csv', index=False)
    
    print("✓ Green Scores calculated and saved to data/green_scores.csv")
    print("\nProject Sustainability Scores:")
    print(scores.to_string(index=False))
