import pandas as pd
from data.dbconnect import get_connection

def fetch_recommendations(dealership_id: int) -> pd.DataFrame:
    """Load all recommendations for a given dealership."""
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM Recommendation WHERE dealership_id = ? ORDER BY recommendation_id",
        conn,
        params=(dealership_id,)
    )
    conn.close()
    return df

def fetch_all_recommendations() -> pd.DataFrame:
    """Load every recommendation in the table."""
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM Recommendation ORDER BY recommendation_id",
        conn
    )
    conn.close()
    return df

