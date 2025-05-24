import pyodbc

def get_connection(db_path=r"C:\Users\JHATZIU\TestfahrzeugeDB.accdb"):
    conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={db_path};"
    )
    conn = pyodbc.connect(conn_str)
    return conn




#import pyodbc
#from config import DB_PATH

#def get_connection():
#    """
 #   Returns a pyodbc connection to the Access DB at config.DB_PATH.
  #  """
 #   db_file = str(DB_PATH)   # Path → str
  #  conn_str = (
  #      r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
  #      f"DBQ={db_file};"
#   )
 #   return pyodbc.connect(conn_str)
