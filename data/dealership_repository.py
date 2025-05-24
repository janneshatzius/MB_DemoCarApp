from data.dbconnect import get_connection
import traceback
import pandas as pd






def get_all_dealerships():
    conn = get_connection()
    cur = conn.cursor()
    try:
        df = cur.execute("""
                         SELECT * 
                         FROM Dealership
                         ORDER BY gssn_id
                         """,)
        cols = [col[0] for col in cur.description]
        rows = cur.fetchall()
    except Exception as e:
        print(f"[ERROR] loading dealerships: {e}")
        cols, rows = [], []
    finally:
        conn.close()

    if rows:
        return pd.DataFrame.from_records(rows, columns=cols)
    else:
        return pd.DataFrame(columns=cols)
    




def update_dealership(conn, dealer_id, status, note):
    cur = conn.cursor()
    sql = """
    UPDATE [Dealership]
       SET [status]             = ?,
          [note]                  = ?
     WHERE [dealership_id]    = ?
    """
    
    params = (
        status,
        note,
        dealer_id
    )
    cur.execute(sql, params)
    conn.commit()



def insert_dealership(dealership):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
    INSERT INTO Dealership
    ([gssn_id],
    [dealership_name],
    [HB],
    [FS],
    [VFNR],
    [locality],
    [function],
    [FS_Value],
    [group_id],
    [gssn_company],
    [status],
    [note]
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """

    params = (
        dealership["gssn_id"],
        dealership["dealership_name"],
        dealership["HB"],
        dealership["FS"],
        dealership["VFNR"],
        dealership["locality"],
        dealership["function"],
        dealership["FS_Value"],
        dealership["group_id"],
        dealership["gssn_company"],
        dealership["status"],
        dealership["note"]
    )

    try:
        cur.execute(sql, params)
    except Exception as e:
            # Print everything for debugging
        print("\n--- Failed to insert dealership ---")
        print("SQL:", sql.strip())
        print("Parameters:", params)
        print("Parameter types:",
              [type(x).__name__ for x in params])
        print("Error:")
        traceback.print_exc()
        raise


    conn.commit()
    conn.close()
    


def insert_dealership_group(dgroup):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
    INSERT INTO DealershipGroup
    ([gssn_company],
         [vfnrhb])
            VALUES (?,?)
    """

    params = (
        dgroup["gssn_company"],
        dgroup["vfnrhb"]
    )

    try:
        cur.execute(sql, params)
    except Exception as e:
            # Print everything for debugging
        print("\n--- Failed to insert dealership ---")
        print("SQL:", sql.strip())
        print("Parameters:", params)
        print("Parameter types:",
              [type(x).__name__ for x in params])
        print("Error:")
        traceback.print_exc()
        raise


    conn.commit()
    conn.close()



