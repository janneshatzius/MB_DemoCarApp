import dbconnect
import pandas as pd

def save_recommendations_to_db(recommendations, car_model_df):
    if not recommendations:
        print("No recommendations to save.")
        return

    conn = dbconnect.get_connection()
    cursor = conn.cursor()

    # Model name → ID map
    model_id_map = dict(zip(car_model_df['model_name'], car_model_df['car_model_id']))

    inserted = 0
    updated = 0

    for rec in recommendations:
        model_id = model_id_map.get(rec['car_model_name'])

        if model_id is None:
            print(f"Unknown model: {rec['car_model_name']}, skipping.")
            continue

        # Check if recommendation already exists
        cursor.execute("""
            SELECT COUNT(*) FROM Recommendation
            WHERE parking_spot = ? AND allocation_year = ?
        """, (rec['parkingspot_id'], rec['allocation_year']))

        exists = cursor.fetchone()[0]

        if exists:
            #  Update existing recommendation
            cursor.execute("""
                UPDATE Recommendation
                SET car_model = ?, car_model_name = ?, recommendation_source = ?
                WHERE parking_spot = ? AND allocation_year = ?
            """, (
                model_id,
                rec['car_model_name'],
                1,
                rec['parkingspot_id'],
                rec['allocation_year']
            ))
            updated += 1
        else:
            #Insert new recommendation
            cursor.execute("""
                INSERT INTO Recommendation (dealership, parking_spot, car_model, car_model_name, recommendation_source, allocation_year)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                rec['dealership_id'],
                rec['parkingspot_id'],
                model_id,
                rec['car_model_name'],
                1,
                rec['allocation_year']
            ))
            inserted += 1

    conn.commit()
    conn.close()

    print(f"{inserted} inserted | {updated} updated | {inserted + updated} total processed.")

def save_parking_spots(parking_spots):
    if not parking_spots:
        print("No parking spots to save.")
        return

    conn = dbconnect.get_connection()
    cursor = conn.cursor()

    # Wipe table before re-inserting
    cursor.execute("DELETE FROM Parking_Spot")
    

    inserted = 0

    for spot in parking_spots:
        cursor.execute("""
            INSERT INTO Parking_Spot (parkingspot_id, dealership_id, gssn_id, car_type_id, car_type)
            VALUES (?, ?, ?, ?, ?)
        """, (
            spot['parkingspot_id'],
            spot['dealership_id'],
            spot['gssn_id'],           
            spot['car_type_id'],
            spot['car_type']
        ))
        inserted += 1

    conn.commit()
    conn.close()

    print(f" {inserted} parking spots inserted with gssn_id.")


    #Create connection between Dealership and DealershipGroup table
def assign_dealership_groups():
    conn = dbconnect.get_connection()



    dealership_df = pd.read_sql("SELECT * FROM Dealership", conn)
    group_df = pd.read_sql("SELECT * FROM Dealershipgroup", conn)

    merged_df = dealership_df.merge(group_df, left_on="hb", right_on="vfnrhb", how="left")

    update_sql = """
    UPDATE Dealership
    SET group_id = ?
    WHERE gssn_id = ?
    """

    cursor = conn.cursor()
    updated_rows = []

    

    for a, row in merged_df.iterrows():
        if pd.notnull(row["id"]): 
            cursor.execute(update_sql, row["id"], row["gssn_id"])
            updated_rows.append({
                "gssn_id": row["gssn_id"],
                "assigned_group_id": row["id"]
            })

    conn.commit()
    cursor.close()
    conn.close()



    print(" Dealership group_id updated successfully.")
    return updated_rows

    


    

