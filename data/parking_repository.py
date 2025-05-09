from data.dbconnect import get_connection
import pandas as pd

def get_allocation_for_fs(fs_value, conn):
    """
    Returns a list of (parking_category_id, quantity) tuples
    for the given FS value.
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT [parking_category], [quantity] "
        "  FROM [Parking_Allocation] "
        " WHERE [fs_category] = ?",
        (fs_value,)
    )
    return cur.fetchall()

def get_all_parking_spots():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM Parking_Spot", conn)
    conn.close()
    return df

def get_parking_category_map(conn):
    """
    Returns a dict mapping parkingcategory_id → {
        "car_type_id": …,
        "car_type":    …
    }
    by pulling Parking_Category and Car_Type into DataFrames
    and merging on category_name == car_type_name.
    """
    # 1) read your two tables
    df_pc = pd.read_sql_query(
        "SELECT [parkingcategory_id], [category_name] FROM [Parking_Category]",
        conn
    )
    df_ct = pd.read_sql_query(
        "SELECT [car_type_id], [type_name] FROM [Car_Type]",
        conn
    )

    # 2) merge on the name columns
    df_map = df_pc.merge(
        df_ct,
        left_on="category_name",
        right_on="type_name",
        how="inner"
    )

    # 3) build and return the dict
    return {
        int(row["parkingcategory_id"]): {
            "car_type_id": int(row["car_type_id"]),
            "car_type":    row["type_name"]
        }
        for _, row in df_map.iterrows()
    }

def insert_parking_spots_bulk(spots, conn):
    cur = conn.cursor()
    for dealer_id, type_name, type_id, gssn in spots:
        cur.execute(
            "INSERT INTO [Parking_Spot] "
            "  ([Dealership_ID],[Car_Type],[Car_Type_ID],[GSSN_ID]) "
            "VALUES (?,?,?,?)",
            (dealer_id, type_name, type_id, gssn)
        )