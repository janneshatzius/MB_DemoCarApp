import pyodbc
import traceback
import pandas as pd
from data.dbconnect import get_connection



def get_past_recommendations(years):
    """
    years: list of two ints, e.g. [2023, 2024]
    """
    conn = get_connection()
    placeholders = ",".join("?" for _ in years)
    sql = f"SELECT * FROM Past_Recommendations WHERE allocation_year IN ({placeholders})"
    df = pd.read_sql_query(sql, conn, params=years)
    conn.close()
    return df

def get_model_id_by_name(conn, model_name):
    cur = conn.cursor()
    cur.execute("SELECT Car_Model_ID FROM Car_Model WHERE model_name = ?", model_name)
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Unknown model_name {model_name}")
    return row[0]

def get_recommendations_by_dealership(conn, dealership_id):
    cur = conn.cursor()
    sql = """
        SELECT
            recommendation_id,
            dealership_id,
            parking_spot,            
            car_model,
            car_model_name,
            recommendation_source,
            note
          FROM Recommendation
         WHERE dealership_id = ?
    """
    # pass a tuple, not a bare int
    cur.execute(sql, (dealership_id,))
    rows = cur.fetchall()

    # map to dicts
    return [
        {
            "recommendation_id":      r[0],
            "dealership_id":          r[1],
            "parking_spot":           r[2],
            "car_model":              r[3],
            "car_model_name":         r[4],
            "recommendation_source":  r[5],
            "note":                   r[6],
        }
        for r in rows
    ]

def update_recommendation(conn, recommendation_id, car_model_id, car_model_name, recommendation_source, note):
    cur = conn.cursor()
    cur.execute("""
        UPDATE Recommendation
           SET car_model =    ?
             , car_model_name = ?
             , recommendation_source = ?
             , note = ?
         WHERE recommendation_id = ?
    """,
    car_model_id,
    car_model_name,
    recommendation_source,
    note,
    recommendation_id)
    conn.commit()


def insert_recommendations( recommendations):
    conn = get_connection()
    cur = conn.cursor()
    """
    recommendations: list of dicts with keys
      dealership_id, gssn_id, parkingspot_id, car_model,
      recommendation_source, allocation_year, car_model_name
    """
    sql = """
        INSERT INTO Recommendation
          (dealership_id,
           gssn_id,
           parking_spot,
           car_model,
           recommendation_source,
           allocation_year,
           car_model_name,
           locality,
           dealership_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    

    for rec in recommendations:
        params = (
            rec["dealership_id"],
            rec["gssn_id"],
            rec["parking_spot"],
            rec["car_model"],        
            rec["recommendation_source"],
            rec["allocation_year"],      
            rec["car_model_name"],
            rec["locality"],
            rec["dealership_name"]     
        )
        try:
            cur.execute(sql, params)
        except Exception as e:
            # Print everything for debugging
            print("\n--- Failed to insert recommendation ---")
            print("SQL:", sql.strip())
            print("Parameters:", params)
            print("Parameter types:",
                  [type(x).__name__ for x in params])
            print("Error:")
            traceback.print_exc()
            raise

    conn.commit()
    conn.close()

def delete_recommendations_for_year(conn, year: int):
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM Recommendation WHERE allocation_year = ?",
        (year,)
    )
    conn.commit()

def get_max_allocation_year(conn):
    cur = conn.cursor()
    cur.execute("SELECT MAX(allocation_year) FROM Recommendation")
    row = cur.fetchone()
    return row[0]

def move_recommendations_to_past(conn, year: int):
    """
    Copy all Recommendation rows for a given year into Past_Recommendations
    (dealership_id, gssn_id, allocation_year, car_model_name) and then delete them.
    """
    cur = conn.cursor()

    sql_insert = """
      INSERT INTO Past_Recommendations
        ( dealership_id
        , gssn_id
        , allocation_year
        , car_model_name
        )
      SELECT
        dealership_id
      , gssn_id
      , allocation_year
      , car_model_name
      FROM Recommendation
      WHERE allocation_year = ?
    """
    cur.execute(sql_insert, (year,))
    moved = cur.rowcount
    print(f"[archive] moved {moved} rows to Past_Recommendations for year {year}")

    # 2) Now delete those same rows from Recommendation
    cur.execute(
        "DELETE FROM Recommendation WHERE allocation_year = ?", (year,)
    )
    deleted = cur.rowcount
    print(f"[archive] deleted {deleted} rows from Recommendation for year {year}")

    conn.commit()


