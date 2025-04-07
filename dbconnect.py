import pyodbc

def get_connection(db_path=r"C:\Users\JHATZIU\Database1.accdb"):
    conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={db_path};"
    )
    conn = pyodbc.connect(conn_str)
    return conn