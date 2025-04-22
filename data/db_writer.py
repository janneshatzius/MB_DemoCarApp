import data.dbconnect as dbconnect
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
                INSERT INTO Recommendation (dealership_id, parking_spot, car_model, car_model_name, recommendation_source, allocation_year, gssn_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                rec['dealership_id'],
                rec['parkingspot_id'],
                model_id,
                rec['car_model_name'],
                1,
                rec['allocation_year'],
                rec['gssn_id']
            ))
            inserted += 1

    conn.commit()
    conn.close()

    print(f"{inserted} inserted | {updated} updated | {inserted + updated} total processed.")

import data.dbconnect as dbconnect
import pandas as pd

def save_parking_spots(parking_spots_df):
    if parking_spots_df.empty:
        print("No parking spots to save.")
        return

    conn = dbconnect.get_connection()
    cursor = conn.cursor()

    # Fetch dealership IDs for each gssn_id
    dealership_df = pd.read_sql("SELECT id, gssn_id FROM Dealership", conn)
    print(" Dealership columns:", dealership_df.columns.tolist())

    # Merge to get dealership_id for each parking spot
    parking_spots_df = parking_spots_df.merge(dealership_df, on="gssn_id", how="left")

    if parking_spots_df['id'].isnull().any():
        print(" Some gssn_ids in parking_spots_df did not match any in Dealership. These will be skipped.")
        parking_spots_df = parking_spots_df.dropna(subset=["id"])

    # Clear old parking spots
    cursor.execute("DELETE FROM Parking_Spot")

    inserted = 0

    # Step 1: Get car_type -> ID mapping from DB
    car_type_df = pd.read_sql("SELECT * FROM Car_Type", conn)
    type_map = dict(zip(car_type_df['type_name'].str.lower(), car_type_df['car_type_id']))

    # Step 2: Map car_type to car_type_id
    parking_spots_df['car_type'] = parking_spots_df['car_type'].str.lower()
    parking_spots_df['car_type_id'] = parking_spots_df['car_type'].map(type_map)

    # Step 3: Drop rows with unmapped car types (optional safety net)
    parking_spots_df = parking_spots_df.dropna(subset=['car_type_id'])
    parking_spots_df['car_type_id'] = parking_spots_df['car_type_id'].astype(int)

    for _, spot in parking_spots_df.iterrows():
        cursor.execute("""
            INSERT INTO Parking_Spot (dealership_id, gssn_id, car_type_id, car_type)
            VALUES (?, ?, ?, ?)
        """, (
            int(spot['id']),         
            spot['gssn_id'],
            spot['car_type_id'],
            spot['car_type']
        ))
        inserted += 1

    conn.commit()
    conn.close()

    print(f" {inserted} parking spots inserted (dealership + gssn + car type info).")



    #Create connection between Dealership and DealershipGroup table
def assign_dealership_groups():
    conn = dbconnect.get_connection()

    dealership_df = pd.read_sql("SELECT * FROM Dealership", conn)
    group_df = pd.read_sql("SELECT * FROM Dealershipgroupnew", conn)

    merged_df = dealership_df.merge(group_df, left_on="HB", right_on="vfnrhb", how="left")
    
    

    update_sql = """
    UPDATE Dealership
    SET group_id = ?, gssn_company = ?
    WHERE gssn_id = ?
    """

    cursor = conn.cursor()
    updated_rows = []

    for _, row in merged_df.iterrows():
        group_id = row["DG_ID"]
        company_id = row.get("gssn_companyid")
        gssn_id = row["gssn_id"]

        if pd.notnull(group_id):
            cursor.execute(update_sql, (group_id, company_id, gssn_id))
            updated_rows.append({
                "gssn_id": gssn_id,
                "assigned_group_id": group_id,
                "assigned_company_id": company_id
            })

    conn.commit()
    cursor.close()
    conn.close()

    print(" Dealership group_id and GSSN_COMPANYID updated successfully.")
    return updated_rows


def update_past_recommendations_with_dealership_ids():
    import pandas as pd
    import data.dbconnect as dbconnect

    conn = dbconnect.get_connection()
    cursor = conn.cursor()

    # Make sure you get dealership_id directly in the DataFrame
    dealership_df = pd.read_sql("SELECT ID, gssn_id FROM Dealership", conn)
    dealership_df.rename(columns={"ID": "dealership_id"}, inplace=True)
    past_rec_df = pd.read_sql("SELECT * FROM Past_RecommendationsNEW", conn)

    # Merge on gssn_id
    merged_df = past_rec_df.merge(dealership_df, on="gssn_id", how="left")

    # Warn about unmatched rows
    unmatched = merged_df['dealership_id_y'].isnull().sum()

    if unmatched:
        print(f" {unmatched} records in Past_RecommendationsNEW could not be matched to a Dealership by gssn_id and will be skipped.")

    # Prepare update query
    update_sql = """
    UPDATE Past_RecommendationsNEW
    SET dealership_id = ?
    WHERE gssn_id = ?
    """

    updated_count = 0

    for _, row in merged_df.iterrows():
        if pd.notnull(row["dealership_id_y"]):
            try:
                cursor.execute(update_sql, int(row["dealership_id_y"]), row["gssn_id"])
                updated_count += 1
            except Exception as e:
                print(f" Error updating row with gssn_id={row['gssn_id']}: {e}")
                continue
            
    merged_df.rename(columns={"dealership_id_y": "dealership_id"}, inplace=True)

    conn.commit()
    cursor.close()
    conn.close()

    print(f" Past_RecommendationsNEW updated successfully with {updated_count} dealership_id values.")
    return updated_count




    


    

