"""
AI Time-Series Forecasting
This module implements Steps 1-3 for AI failure prediction using Time-Series Forecasting.
"""
import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Step 1: Library Setup is handled by importing Prophet and Pandas at the top of this file.
# This file serves as the core module for the time-series machine learning.

class PipelineForecaster:
    """Time-series forecaster for pipeline executions using Prophet."""
    
    def __init__(self):
        # We will store trained models in a dictionary in memory for fast access (inference)
        # Structure: Key = pipeline_id, Value = Trained Prophet model object
        self.models: Dict[str, Prophet] = {}
        
    # Step 2: Data Preparation
    def prepare_data(self, execution_history: List[Any], pipeline_id: str) -> pd.DataFrame:
        """
        Extracts time-series data from execution history and creates features.
        Prophet strictly requires column names: 'ds' (datestamp time) and 'y' (target variable).
        """
        # 1. Extract the time-series data from execution history logs
        data = []
        for e in execution_history:
            if not e.started_at:
                continue
            
            # Feature extraction: the AI needs to know if the pipeline failed or passed
            # We assign 1 for failure, 0 for passing.
            is_failed = 1 if e.status == 'failed' else 0
            
            # A pipeline might not report duration if it crashed immediately, so we default to 0.
            duration = e.duration if e.duration is not None else 0.0
            
            # Some Context might contain stage data.
            stage_count = 0
            if getattr(e, 'context', None) and isinstance(e.context, dict):
                stage_count = len(e.context.get('stages', []))
            
            data.append({
                'ds': e.started_at,  # Timestamp
                'y': is_failed,      # The target we want to forecast (failures)
                'duration': duration, # Extracted Feature: duration
                'status': e.status,   # Extracted Feature: status text
                'stage_count': stage_count # Extracted Feature: stage count complexity
            })
            
        df = pd.DataFrame(data)
        
        # 2. Handle missing data and outliers
        if not df.empty:
            # Drop rows with absolutely no timestamps
            df = df.dropna(subset=['ds'])
            
            # Fill missing durations with the median duration to avoid distorting the model
            median_duration = df['duration'].median()
            df['duration'] = df['duration'].fillna(median_duration)
            
            # Outlier handling for duration (Cap duration to the 99th percentile)
            # This ensures crazy high anomalous durations don't completely ruin our average.
            p99 = df['duration'].quantile(0.99)
            df['duration'] = df['duration'].clip(upper=p99)
            
        return df

    # Step 3: Model Training
    def train(self, execution_history: List[Any], pipeline_id: str) -> Prophet:
        """
        Trains the Prophet model on historical execution data for a specific pipeline.
        """
        # We prepare the clean data from our database
        df = self.prepare_data(execution_history, pipeline_id)
        
        # Prophet needs a minimum number of data rows to mathematically find patterns
        if df.empty or len(df) < 5:
            return None
            
        # Initialize Prophet model
        # Prophet automatically finds cyclical calendar patterns
        # We turn on weekly and daily so it catches things like "It always fails on Friday"
        model = Prophet(
            yearly_seasonality=False,  # Not enough data for yearly patterns yet
            weekly_seasonality=True,   # True because pipelines usually run on work-week schedules
            daily_seasonality=True     # True because pipelines often fail at night vs day
        )
        
        # We give the historical DataFrame to Prophet so it learns the patterns
        model.fit(df)
        
        # Store the trained learning model for future forecasting
        self.models[pipeline_id] = model
        
        return model
        
    def validate_model(self, model: Prophet) -> pd.DataFrame:
        """
        Implements cross-validation for accuracy.
        (Simulates training on past data to try and predict known testing data to prove it is accurate).
        """
        if model is None:
            return None
            
        try:
            # We split the history into test blocks to check the AI's accuracy
            # initial: Training dataset period
            # period: spacing between cutoff dates
            # horizon: How far out in the 'future' it is trying to forecast
            df_cv = cross_validation(model, initial='15 days', period='5 days', horizon='7 days')
            df_p = performance_metrics(df_cv)
            return df_p
        except Exception as e:
            # If Prophet throws an error, it is likely because the pipeline doesn't have 15 days of data yet
            return None

    def detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect execution duration anomalies using mathematical Z-scores.
        A Z-score tells us how many standard deviations away from the average a value is.
        """
        anomalies = []
        if df.empty or len(df) < 3:
            return anomalies
            
        # 1. Understand the average and regular variation
        mean_duration = df['duration'].mean()
        std_duration = df['duration'].std()
        
        if std_duration == 0:
            return anomalies
            
        # 2. Calculate Z-score for each execution run
        df['z_score'] = (df['duration'] - mean_duration) / std_duration
        
        # 3. Anything with a score > 3 is incredibly far from the average and is an Anomaly
        anomaly_df = df[df['z_score'].abs() > 3]
        
        for _, row in anomaly_df.iterrows():
            anomalies.append({
                'timestamp': row['ds'],
                'duration': row['duration'],
                'z_score': row['z_score'],
                'is_unusually_high': row['z_score'] > 0
            })
            
        return anomalies

    # Step 4: Forecasting
    def forecast(self, model: Prophet, periods: int = 7) -> List[Dict[str, Any]]:
        """
        Predicts future failure probabilities for the given number of periods (days).
        """
        if model is None:
            return []
            
        try:
            # Tell Prophet to generate a 'future' calendar of dates
            future = model.make_future_dataframe(periods=periods)
            # Make the predictions for those future dates
            forecast_data = model.predict(future)
            
            # We only care about the newly generated future dates, not the past history it just re-predicted
            future_only = forecast_data.tail(periods)
            
            predictions = []
            for _, row in future_only.iterrows():
                # Prophet returns yhat (the prediction), yhat_lower (bottom safety net), and yhat_upper (top limit)
                # Since we trained on 0 (success) and 1 (failure), yhat represents the *probability* of failure.
                # We clap it between 0 and 1 so we don't return impossible probabilities like -0.5 or 1.2
                prob = max(0.0, min(1.0, row['yhat']))
                lower = max(0.0, min(1.0, row['yhat_lower']))
                upper = max(0.0, min(1.0, row['yhat_upper']))
                
                predictions.append({
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'failure_probability': round(prob, 3),
                    'confidence_interval': {
                        'lower': round(lower, 3),
                        'upper': round(upper, 3)
                    }
                })
            
            return predictions
            
        except Exception as e:
            # If forecasting fails (e.g., model is corrupt or data was too weird), return empty
            return []

