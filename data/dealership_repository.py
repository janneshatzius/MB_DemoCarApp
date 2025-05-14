from data.dbconnect import get_connection
import pandas as pd

def get_all_dealerships():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM Dealership", conn)
    conn.close()
    return df
