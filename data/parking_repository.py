import pandas as pd
from data.dbconnect import get_connection




def get_all_parking_spots():
    """
    Returns a DataFrame of every row in Parking_Spot.
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM [Parking_Spot]", conn)
        return df
    finally:
        conn.close()

        

def get_allocation_map():
    """
    Returns a dict:
      fs_category_value → [(parking_category_id, quantity), …]
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT [fs_category], [parking_category], [quantity] "
            "  FROM [Parking_Allocation]",
            conn
        )
    finally:
        conn.close()

    alloc_map = {
        fs: list(zip(group["parking_category"], group["quantity"]))
        for fs, group in df.groupby("fs_category")
    }
    return alloc_map


def get_parking_category_map():
    """
    Returns a dict:
      parking_category_id → {car_type_id, car_type}
    """
    conn = get_connection()
    try:
        df_pc = pd.read_sql_query(
            "SELECT [parkingcategory_id], [category_name] FROM [Parking_Category]",
            conn
        )
        df_ct = pd.read_sql_query(
            "SELECT [car_type_id], [type_name]      FROM [Car_Type]",
            conn
        )
    finally:
        conn.close()

    df_map = df_pc.merge(
        df_ct,
        left_on="category_name", right_on="type_name",
        how="inner"
    )
    return {
        int(r["parkingcategory_id"]): {
            "car_type_id": int(r["car_type_id"]),
            "car_type":    r["type_name"]
        }
        for _, r in df_map.iterrows()
    }


def get_existing_spot_counts():
    """
    Returns dict:
      dealership_id → count_of_parking_spots
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT [Dealership_ID], COUNT(*) AS cnt "
            "  FROM [Parking_Spot] "
            " GROUP BY [Dealership_ID]",
            conn
        )
    finally:
        conn.close()

    return dict(zip(df["Dealership_ID"], df["cnt"]))


def delete_spots_for_dealers(dealer_ids: list[int]):
    """
    One DELETE statement for all out-of-sync dealers.
    """
    if not dealer_ids:
        return

    placeholders = ",".join("?" for _ in dealer_ids)
    sql = (
        f"DELETE FROM [Parking_Spot] "
        f" WHERE [Dealership_ID] IN ({placeholders})"
    )

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, dealer_ids)
        conn.commit()
    finally:
        conn.close()


def insert_parking_spots_bulk(spots: list[tuple]):
    """
    One executemany for all new spots:
      spots = [(dealer_id, car_type, car_type_id, gssn_id), …]
    """
    if not spots:
        return

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO [Parking_Spot] "
            " ([Dealership_ID],[Car_Type],[Car_Type_ID],[GSSN_ID]) "
            "VALUES (?,?,?,?)",
            spots
        )
        conn.commit()
    finally:
        conn.close()


# — FS_CATEGORY CRUD —

def list_fs_categories() -> list[dict]:
    """
    Returns a list of existing FS categories, each as {"fs_category": "V2"}.
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT [fscategory] AS [fs_category] "
            "  FROM [FS_Category] "
            " ORDER BY [fscategory]",
            conn
        )
        return df.to_dict("records")
    finally:
        conn.close()


def add_fs_category(fs: str) -> None:
    """
    Inserts a new FS category.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO [FS_Category] ([fscategory]) VALUES (?)",
            (fs,)
        )
        conn.commit()
    finally:
        conn.close()


# — PARKING_CATEGORY list (for editor) —

def list_parking_categories() -> list[dict]:
    """
    Returns a list of all parking categories:
      [{"parkingcategory_id": 1, "category_name": "Private"}, …]
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT [parkingcategory_id], [category_name] "
            "  FROM [Parking_Category] "
            " ORDER BY [parkingcategory_id]",
            conn
        )
        return df.to_dict("records")
    finally:
        conn.close()


# — PARKING_ALLOCATION CRUD —

def list_allocation_for_fs(fs: str) -> list[tuple[int,int]]:
    """
    Returns a list of (parking_category_id, quantity) for this fs_category.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT [parking_category], [quantity] "
            "  FROM [Parking_Allocation] "
            " WHERE [fs_category] = ?",
            (fs,)
        )
        return cur.fetchall()  # list of (int, int)
    finally:
        conn.close()

def insert_allocation(fs: str, parking_cat: int, qty: int) -> None:
    """
    Inserts a new row into Parking_Allocation.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO [Parking_Allocation] "
            "  ([fs_category], [parking_category], [quantity]) "
            "VALUES (?,?,?)",
            (fs, parking_cat, qty)
        )
        conn.commit()
    finally:
        conn.close()

def update_allocation(fs: str, parking_cat: int, qty: int) -> None:
    """
    Updates the quantity for an existing Parking_Allocation row.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE [Parking_Allocation] "
            "   SET [quantity] = ? "
            " WHERE [fs_category] = ? AND [parking_category] = ?",
            (qty, fs, parking_cat)
        )
        conn.commit()
    finally:
        conn.close()

def delete_allocation(fs: str, parking_cat: int) -> None:
    """
    Deletes a specific Parking_Allocation row.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM [Parking_Allocation] "
            " WHERE [fs_category] = ? AND [parking_category] = ?",
            (fs, parking_cat)
        )
        conn.commit()
    finally:
        conn.close()

