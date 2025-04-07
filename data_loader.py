# data_loader.py
import pandas as pd
import dbconnect

def load_all_data():
    conn = dbconnect.get_connection()

    dealership_df = pd.read_sql("SELECT * FROM Dealership", conn)
    parking_df = pd.read_sql("SELECT * FROM Parking_Spot", conn)
    past_recs_df = pd.read_sql("""
        SELECT dealership_id, allocation_year, car_model_name
        FROM PastRecommendations
        WHERE allocation_year IN (2024, 2025)
    """, conn)
    car_model_df = pd.read_sql("SELECT * FROM Car_Model", conn)
    car_type_df = pd.read_sql("SELECT * FROM Car_Type", conn)

    conn.close()
    return dealership_df, parking_df, past_recs_df, car_model_df, car_type_df
