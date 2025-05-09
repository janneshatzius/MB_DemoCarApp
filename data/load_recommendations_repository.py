import pandas as pd
from data.dbconnect import get_connection

def get_all_recommendations() -> pd.DataFrame:
    """
    Pull entire Recommendation table into a pandas DataFrame.
    """
    conn = get_connection()
    # note: read_sql works with Access via pyodbc but throws a warning – it still works.
    df = pd.read_sql("SELECT * FROM Recommendation", conn)
    conn.close()
    return df
