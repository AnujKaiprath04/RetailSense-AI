#!/usr/bin/env python3
"""
RetailSense AI — High Performance 100,000 (1 Lakh) Row Dataset Generator
Generates realistic multi-store, multi-department hourly footfall dataset.
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_100k_dataset(filename="retail_footfall_100k.csv", total_rows=100000):
    print(f"Generating {total_rows:,} rows of enterprise footfall dataset...")
    
    np.random.seed(42)
    stores = ['Koramangala', 'Indiranagar', 'Whitefield', 'MG Road', 'Jayanagar']
    departments = ['Grocery', 'Apparel', 'Electronics', 'Beverages', 'Personal Care']
    
    # Generate timestamp series: 100,000 hours divided among 5 stores = 20,000 hours per store (~2.28 years of hourly data)
    hours_per_store = total_rows // len(stores)
    start_date = datetime(2023, 1, 1, 0, 0, 0)
    
    records = []
    
    for store in stores:
        timestamps = [start_date + timedelta(hours=i) for i in range(hours_per_store)]
        
        # Base count pattern
        for ts in timestamps:
            hour = ts.hour
            dow = ts.weekday()
            month = ts.month
            
            # Base diurnal curve
            weekend_mult = 1.35 if dow >= 5 else 1.0
            holiday_mult = 1.40 if (np.random.random() < 0.04) else 1.0
            promo_mult = 1.25 if (np.random.random() < 0.12) else 1.0
            season_mult = 1.15 if month in [10, 11, 12] else 1.0 # Festive season

            if 9 <= hour <= 21:
                if 12 <= hour <= 14: # Lunch peak
                    base = 280
                elif 17 <= hour <= 20: # Evening peak
                    base = 380
                elif 9 <= hour <= 11:
                    base = 110
                else:
                    base = 190
                
                combined_mult = weekend_mult * holiday_mult * promo_mult * season_mult
                noise = np.random.randint(-20, 25)
                footfall = max(10, int(base * combined_mult + noise))
            else:
                footfall = np.random.randint(0, 12)
            
            dept = np.random.choice(departments)
            temp = round(22.0 + np.random.uniform(-6, 8), 1)
            rain = round(np.random.uniform(0, 18), 1) if (np.random.random() < 0.15) else 0.0
            is_holiday = 1 if (holiday_mult > 1.0) else 0
            promo = 1 if (promo_mult > 1.0) else 0
            
            # Derived metrics
            active_staff = max(2, int(footfall / 15))
            active_cashiers = max(1, min(8, int(footfall / 40)))
            recommended_cashiers = max(1, min(8, int(footfall / 35)))
            avg_wait = round(max(0.5, (footfall / (active_cashiers * 45)) * 1.8), 1)
            revenue = round(footfall * np.random.uniform(85, 140), 2)
            
            records.append({
                'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'store_id': store,
                'department': dept,
                'footfall_count': footfall,
                'active_staff': active_staff,
                'active_cashiers': active_cashiers,
                'recommended_cashiers': recommended_cashiers,
                'avg_wait_time_min': avg_wait,
                'estimated_revenue': revenue,
                'temperature_c': temp,
                'rain_mm': rain,
                'is_holiday': is_holiday,
                'promotion_active': promo,
                'day_of_week': dow,
                'hour': hour,
                'is_weekend': 1 if dow >= 5 else 0
            })
            
    df = pd.DataFrame(records)
    
    # Calculate Lag & Rolling features
    df['lag_1h'] = df['footfall_count'].shift(1).fillna(method='bfill')
    df['lag_24h'] = df['footfall_count'].shift(24).fillna(method='bfill')
    df['rolling_mean_24h'] = df['footfall_count'].shift(1).rolling(window=24, min_periods=1).mean().round(1)
    
    # Save to ML directory
    ml_path = os.path.join(r"c:\Retail footfall\ml", filename)
    df.to_csv(ml_path, index=False)
    print(f"[OK] Saved ML dataset: {ml_path} ({len(df):,} rows, {os.path.getsize(ml_path) / (1024*1024):.2f} MB)")

    # Save to backend data directory
    backend_data_dir = r"c:\Retail footfall\backend\data"
    os.makedirs(backend_data_dir, exist_ok=True)
    backend_path = os.path.join(backend_data_dir, filename)
    df.to_csv(backend_path, index=False)
    print(f"[OK] Saved Backend dataset: {backend_path} ({len(df):,} rows)")
    
    return df

if __name__ == '__main__':
    df = generate_100k_dataset()
    print("Sample rows:")
    print(df.head(5))
