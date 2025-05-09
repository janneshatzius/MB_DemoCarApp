from data.dbconnect import get_connection
import pandas as pd

def get_dealerships_for_parking():
    """
    Returns a list of dicts, one per dealership:
      { 'dealership_id': int,
        'fs_value': str_or_int,
        'gssn_id': str }
    """
    conn = get_connection()
    cur  = conn.cursor()
    # pull every row
    cur.execute(
        "SELECT dealership_id, FS_Value, gssn_id "
        "  FROM Dealership"
    )
    rows = cur.fetchall()
    conn.close()

    return [
        { 'dealership_id': r[0], 'fs_value': r[1], 'gssn_id': r[2] }
        for r in rows
    ]

def get_all_dealerships():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM Dealership", conn)
    conn.close()
    return df
