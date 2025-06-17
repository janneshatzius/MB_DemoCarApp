from data.dbconnect import get_connection
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
    

def update_dealership_status(dealership_id: int, status: str, note: str) -> None:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE [Dealership]
               SET [status] = ?,
                    [note] = ?
             WHERE [dealership_id] = ?
            """,
            (status, note, dealership_id)
        )
        conn.commit()
    finally:
        conn.close()


def find_group_by_company(company: str) -> dict | None:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DG_ID, gssn_company, vfnrhb
              FROM DealershipGroup
             WHERE gssn_company = ?
            """,
            (company,)
        )
        row = cur.fetchone()
        if not row:
            return None
        cols = [col[0] for col in cur.description]
        return dict(zip(cols, row))
    finally:
        conn.close()


def insert_dealership_group(company: str, vfnrhb: str) -> dict:
    
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO DealershipGroup (gssn_company, vfnrhb)
            VALUES (?, ?)
            """,
            (company, vfnrhb)
        )
        conn.commit()

        # Fetch the generated identity (works in Access via @@IDENTITY)
        cur.execute("SELECT @@IDENTITY AS DG_ID")
        dg_id = cur.fetchone()[0]

        return {"DG_ID": dg_id, "gssn_company": company, "vfnrhb": vfnrhb}
    finally:
        conn.close()


def insert_dealership(
    gssn_id: str,
    dealership_name: str,
    HB: int,
    FS: int,
    VFNR: int,
    locality: str,
    function: str,
    FS_Value: str,
    group_id: int,
    gssn_company: str,
    status: str,
    note: str
) -> None:
   
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO [Dealership]
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
                [note])
            VALUES
               (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                gssn_id,
                dealership_name,
                HB,
                FS,
                VFNR,
                locality,
                function,
                FS_Value,
                group_id,
                gssn_company,
                status,
                note
            )
        )
        conn.commit()
    finally:
        conn.close()
