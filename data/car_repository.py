from data.dbconnect import get_connection
import pandas as pd




def fetch_all_types():
    """
    Returns a simple list of all distinct car_type_name values,
    ordered alphabetically.
    """
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT DISTINCT [car_type_name]
          FROM [Car_Model]
         ORDER BY [car_type_name]
    """)
    rows = cur.fetchall()
    conn.close()
    # each row is a one‐element tuple
    return [r[0] for r in rows]

def fetch_models_by_type(type_name: str) -> list[str]:
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT model_name FROM Car_Model WHERE car_type_name = ? ORDER BY model_name",
        conn,
        params=(type_name,)
    )
    conn.close()
    return df['model_name'].dropna().tolist()



def get_car_models_by_type(car_type_name):
    """
    Returns all models (id + name) for a given car_type.
    """
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute("""
            SELECT car_model_id, model_name
              FROM Car_Model
             WHERE car_type_name = ?
        """, (car_type_name,))
        rows = cur.fetchall()
    finally:
        conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]





def get_all_car_models():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM Car_Model", conn)
    conn.close()
    return df

def insert_car_model(type_name: str, model_name: str):
    conn = get_connection()
    cur = conn.cursor()
    # 1) look up the PK in Car_Type
    cur.execute("SELECT car_type_id FROM Car_Type WHERE type_name = ?", (type_name,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Unknown car-type “{type_name}” – please create it first in Car_Type.")
    car_type_id = row[0]
    # 2) insert into Car_Model (supplying both the FK and the name)
    cur.execute(
        """
        INSERT INTO Car_Model
           (model_name, car_type, car_type_name)
        VALUES (?, ?, ?)
        """,
        (model_name, car_type_id, type_name)
    )
    conn.commit()
    conn.close()

def delete_car_model(model_name: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM Car_Model WHERE model_name = ?",
        (model_name,)
    )
    conn.commit()
    conn.close()


def get_all_model_names(conn):
    cur = conn.cursor()
    cur.execute("SELECT model_name FROM Car_Model")
    return [row[0] for row in cur.fetchall()]

def get_car_model_id_by_name(conn, model_name):
    cur = conn.cursor()
    cur.execute("SELECT car_model_id FROM Car_Model WHERE model_name = ?", model_name)
    row = cur.fetchone()
    return row[0] if row else None