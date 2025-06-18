import pandas as pd
from data.dbconnect import get_connection

import pandas as pd
from data.dbconnect import get_connection

def get_past_recommendations_df(year: int) -> pd.DataFrame:
    conn = get_connection()
    try:
        sql = """
            SELECT
                [past_rec_id],
                [gssn_id],
                [allocation_year],
                [car_model_name],
                [gssn_company],
                [HB],
                [VFNR],
                [dealership_name],
                [locality],
                [parking_type],               
                [first_allocation],
                [second_allocation],
                [note]
            FROM [Past_Recommendations]
            WHERE [allocation_year] = ?
            ORDER BY [gssn_id]
        """
        
        df = pd.read_sql_query(sql, conn, params=[year])
        return df

    except Exception as e:
        print(f"[ERROR] loading past recommendations for year {year}: {e}")
        return pd.DataFrame()  

    finally:
        conn.close()




def update_past_recommendation(past_rec_id, new_model_name, note, f_allocation, s_allocation):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
    UPDATE [Past_Recommendations]
       SET
           [car_model_name]        = ?,
           [note]                  = ?,
           [first_allocation]       = ?,
           [second_allocation]       = ?
     WHERE [past_rec_id]    = ?
    """
    params = (
        
        new_model_name,
        note,
        f_allocation,
        s_allocation,
        past_rec_id
    )
    cur.execute(sql, params)
    conn.commit()


def get_available_years() -> list[int]:
        conn = get_connection()
        try:
            df = pd.read_sql_query(
                "SELECT DISTINCT [allocation_year] "
                "  FROM [Past_Recommendations] "
                " ORDER BY [allocation_year]",
                conn
            )
            return df["allocation_year"].tolist()
        finally:
            conn.close()


