import pandas as pd
import dbconnect

conn = dbconnect.get_connection()
dealership_df = pd.read_sql("SELECT * FROM DealershipGroup", conn)
print("🧾 Columns:", dealership_df.columns.tolist())
