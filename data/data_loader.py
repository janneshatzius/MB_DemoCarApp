
import pandas as pd
import data.dbconnect as dbconnect

def load_all_data():
    conn = dbconnect.get_connection()

    dealership_df = pd.read_sql("SELECT * FROM Dealership", conn)
    parking_df = pd.read_sql("SELECT * FROM Parking_Spot", conn)
    fs_parking_allocation_df = pd.read_sql("SELECT * FROM Parking_Allocation", conn)

    past_recs_df = pd.read_sql("""
    SELECT dealership_id, allocation_year, car_model_name
    FROM Past_Recommendations
    WHERE allocation_year IN (2024, 2025)
""", conn)

    


    

    car_model_df = pd.read_sql("SELECT * FROM Car_Model", conn)
    car_type_df = pd.read_sql("SELECT * FROM Car_Type", conn)


    car_model_df = (
    car_model_df
    .merge(car_type_df, left_on='car_type', right_on='car_type_id')
    .drop(columns=['car_type', 'car_type_id'])
    .rename(columns={'type_name': 'car_type'})
)
    print("car_model_df.columns:", car_model_df.columns.tolist())
    print("car_type_df.columns:", car_type_df.columns.tolist())




   


    conn.close()
    return dealership_df, parking_df, past_recs_df, car_model_df, car_type_df, fs_parking_allocation_df

