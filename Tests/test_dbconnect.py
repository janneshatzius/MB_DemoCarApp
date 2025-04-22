import data.dbconnect as dbconnect

def test_connection():
    try:
        conn = dbconnect.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT TOP 1 * FROM Dealership")
        row = cursor.fetchone()

        print("Connection successful.")
        if row:
            print("Sample data from Dealership:", row)
        else:
            print("Dealership table is empty.")

        conn.close()
        return True

    except Exception as e:
        print("Connection failed:", e)
        return False

# Run the test
if __name__ == "__main__":
    test_connection()
