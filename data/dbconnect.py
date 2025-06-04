




import pyodbc
from config import DB_PATH

def get_connection():
    """
    Returns a pyodbc connection to the Access DB at config.DB_PATH.
    """
    db_file = str(DB_PATH)   
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={db_file};"
   )
    return pyodbc.connect(conn_str)
