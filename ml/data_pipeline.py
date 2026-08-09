import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, List

def create_footfall_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw footfall timestamp records into rich temporal, lag, rolling, and environmental features.
    """
    df = df.copy()
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Temporal Features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Cyclical Time Embeddings
        df['sin_hour'] = np.sin(2 * np.pi * df['hour'] / 24.0)
        df['cos_hour'] = np.cos(2 * np.pi * df['hour'] / 24.0)
        df['sin_dow'] = np.sin(2 * np.pi * df['day_of_week'] / 7.0)
        df['cos_dow'] = np.cos(2 * np.pi * df['day_of_week'] / 7.0)

    # Environmental & Promotional Defaults if absent
    for col in ['temperature', 'rain_mm', 'is_holiday', 'promotion_active']:
        if col not in df.columns:
            df[col] = 0.0

    df['is_holiday'] = df['is_holiday'].astype(int)
    df['promotion_active'] = df['promotion_active'].astype(int)

    # Lag & Rolling Features
    if 'count' in df.columns:
        df['lag_1h'] = df['count'].shift(1).bfill()
        df['lag_24h'] = df['count'].shift(24).bfill()
        df['lag_168h'] = df['count'].shift(168).bfill()  # 1 week lag
        
        df['rolling_mean_3h'] = df['count'].shift(1).rolling(window=3, min_periods=1).mean()
        df['rolling_std_3h'] = df['count'].shift(1).rolling(window=3, min_periods=1).std().fillna(0)
        df['rolling_mean_24h'] = df['count'].shift(1).rolling(window=24, min_periods=1).mean()
        
    return df

def generate_synthetic_footfall_df(days: int = 180) -> pd.DataFrame:
    """
    Generates realistic 180-day hourly retail store footfall dataset.
    """
    start_date = datetime.now() - timedelta(days=days)
    timestamps = [start_date + timedelta(hours=i) for i in range(days * 24)]
    
    records = []
    for ts in timestamps:
        hour = ts.hour
        dow = ts.weekday()
        
        if 8 <= hour <= 22:
            base = 45
            if 12 <= hour <= 14:
                base = 250
            elif 17 <= hour <= 20:
                base = 320
            elif 8 <= hour <= 10:
                base = 80
            
            weekend_mult = 1.4 if dow >= 5 else 1.0
            holiday = 1 if np.random.random() < 0.04 else 0
            promo = 1 if np.random.random() < 0.12 else 0
            
            mult = weekend_mult * (1.35 if holiday else 1.0) * (1.25 if promo else 1.0)
            noise = np.random.randint(-15, 20)
            count = max(5, int(base * mult + noise))
            
            temp = round(21.0 + np.random.uniform(-5, 5), 1)
            rain = round(np.random.uniform(0, 12), 1) if np.random.random() < 0.18 else 0.0
            
            records.append({
                'timestamp': ts,
                'count': count,
                'temperature': temp,
                'rain_mm': rain,
                'is_holiday': holiday,
                'promotion_active': promo
            })
        else:
            records.append({
                'timestamp': ts,
                'count': 0,
                'temperature': 18.0,
                'rain_mm': 0.0,
                'is_holiday': 0,
                'promotion_active': 0
            })
            
    df = pd.DataFrame(records)
    return create_footfall_features(df)
