import pandas as pd
from data.dbconnect import get_connection

def get_all_recommendations_df():
    """
    Returns a DataFrame of all recommendations, including each spots car_type.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        df = cur.execute("""
            SELECT
                r.recommendation_id,
                r.dealership_id,
                r.gssn_id,
                r.dealership_name,
                r.locality,
                r.parking_spot,
                p.car_type,               
                r.car_model_name,
                r.recommendation_source,
                r.allocation_year,
                r.note
            FROM Recommendation AS r
            LEFT JOIN Parking_Spot AS p
              ON r.parking_spot = p.parkingspot_id
            ORDER BY r.recommendation_id
        """,)
        cols = [col[0] for col in cur.description]
        rows = cur.fetchall()
    except Exception as e:
        print(f"[ERROR] loading recommendations: {e}")
        cols, rows = [], []
    finally:
        conn.close()

    if rows:
        return pd.DataFrame.from_records(rows, columns=cols)
    else:
        return pd.DataFrame(columns=cols)



def update_recommendation(conn, rec_id, new_model_id, new_model_name, note):
    cur = conn.cursor()
    sql = """
    UPDATE [Recommendation]
       SET [car_model]             = ?,
           [car_model_name]        = ?,
           [note]                  = ?,
           [recommendation_source] = ?
     WHERE [recommendation_id]    = ?
    """
    # pass the source as a parameter, too, just to keep everything uniform
    params = (
        new_model_id,
        new_model_name,
        note,
        2,        # your “manual” source
        rec_id
    )
    cur.execute(sql, params)
    conn.commit()



