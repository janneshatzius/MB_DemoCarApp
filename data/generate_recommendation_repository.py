import traceback
import pandas as pd
from data.dbconnect import get_connection



def get_past_recommendations(years):
    
    conn = get_connection()
    placeholders = ",".join("?" for _ in years)
    sql = f"SELECT * FROM Past_Recommendations WHERE allocation_year IN ({placeholders})"
    df = pd.read_sql_query(sql, conn, params=years)
    conn.close()
    return df


def get_recommendations_by_dealership(dealership_id):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        SELECT
            recommendation_id,
            dealership_id,
            parking_spot,            
            car_model,
            car_model_name,
            recommendation_source,
            note,
            first_allocation,
            second_allocation
          FROM Recommendation
         WHERE dealership_id = ?
    """
    cur.execute(sql, (dealership_id,))
    rows = cur.fetchall()

    return [
        {
            "recommendation_id":      r[0],
            "dealership_id":          r[1],
            "parking_spot":           r[2],
            "car_model":              r[3],
            "car_model_name":         r[4],
            "recommendation_source":  r[5],
            "note":                   r[6],
            "first_allocation":       r[7],
            "second_allocation":      r[8],
        }
        for r in rows
    ]




def insert_recommendations(recommendations):
    conn = get_connection()
    cur = conn.cursor()
    
    sql = """
        INSERT INTO Recommendation
    ([dealership_id],
     [gssn_id],
     [gssn_company],
     [HB],
     [VFNR],
     [dealership_name],
     [locality],
     [parking_type],
     [car_model],
     [car_model_name],
     [parking_spot],
     [recommendation_source],
     [allocation_year],
     [note],
     [first_allocation],
     [second_allocation])
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """
    

    for rec in recommendations:
        params = (
            rec["dealership_id"],
            rec["gssn_id"],
            rec["gssn_company"], 
            rec["HB"],
            rec["VFNR"],
            rec["dealership_name"],
            rec["locality"],
            rec["parking_type"],
            rec["car_model"], 
            rec["car_model_name"],
            rec["parking_spot"],
            rec["recommendation_source"],
            rec["allocation_year"],      
            rec["note"],
            rec["first_allocation"],
            rec["second_allocation"]
        )
        try:
            cur.execute(sql, params)
        except Exception as e:
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

def delete_recommendations_for_year(year: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM Recommendation WHERE allocation_year = ?",
        (year,)
    )
    conn.commit()

def move_recommendations_to_past(year: int):
    
    conn = get_connection()
    cur = conn.cursor()

    sql_insert = """
INSERT INTO [Past_Recommendations] (
    [gssn_id],
    [allocation_year],
    [car_model_name],
    [dealership_id],
    [gssn_company],
    [HB],
    [VFNR],
    [dealership_name],
    [locality],
    [parking_type],
    [first_allocation],
    [second_allocation],
    [note]
)
SELECT
    [gssn_id],
    [allocation_year],
    [car_model_name],         
    [dealership_id],
    [gssn_company],
    [HB],
    [VFNR],
    [dealership_name],
    [locality],
    [parking_type],
    [first_allocation],
    [second_allocation],
    [note]
  FROM [Recommendation]
 WHERE [allocation_year] = ?
"""

    cur.execute(sql_insert, (year,))
    moved = cur.rowcount
    

    cur.execute(
        "DELETE FROM Recommendation WHERE allocation_year = ?", (year,)
    )
    deleted = cur.rowcount
    

    conn.commit()


