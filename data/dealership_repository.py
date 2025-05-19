from data.dbconnect import get_connection

def get_all_dealerships():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
        "SELECT * FROM Dealership"
        )
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]      # grab the column names
        # build list of dicts:
        return [dict(zip(cols, row)) for row in rows]
    finally:
        cur.close()
        conn.close()
    
