import pyodbc
from data.dbconnect import get_connection

def get_all_recommendations_with_type():
    """
    Returns a list of dicts: each recommendation JOINed to its parking_spot.car_type.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.recommendation_id,
               r.dealership_id,
               r.parkingspot_id,
               p.car_type,
               r.car_model         AS car_model_id,
               r.car_model_name,
               r.recommendation_source,
               r.allocation_year,
               r.note
          FROM Recommendation AS r
     LEFT JOIN Parking_Spot   AS p
            ON r.parkingspot_id = p.parkingspot_id
    """)
    cols = [col[0] for col in cur.description]
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]

def get_car_models_by_type(car_type_name):
    """
    Returns all models (id+name) for a given car_type.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT car_model_id, model_name
          FROM Car_Model
         WHERE car_type_name = ?
    """, (car_type_name,))
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]

def update_recommendation(conn, rec_id, new_model_id, new_model_name, note):
    """
    Update a single recommendation (in an existing open conn),
    setting car_model, car_model_name, note and source=2.
    """
    cur = conn.cursor()
    cur.execute("""
        UPDATE Recommendation
           SET car_model             = ?,
               car_model_name        = ?,
               note                  = ?,
               recommendation_source = 2
         WHERE recommendation_id    = ?
    """, (new_model_id, new_model_name, note, rec_id))
    conn.commit()

