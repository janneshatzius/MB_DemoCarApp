import dbconnect
import pandas as pd

import dbconnect

import dbconnect

def save_recommendations_to_db(recommendations, car_model_df):
    if not recommendations:
        print("⚠️ No recommendations to save.")
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
            print(f"⚠️ Unknown model: {rec['car_model_name']}, skipping.")
            continue

        # Check if recommendation already exists
        cursor.execute("""
            SELECT COUNT(*) FROM Recommendation
            WHERE parking_spot = ? AND allocation_year = ?
        """, (rec['parkingspot_id'], rec['allocation_year']))

        exists = cursor.fetchone()[0]

        if exists:
            # 🔁 Update existing recommendation
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
            # ➕ Insert new recommendation
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

    print(f"✅ {inserted} inserted | 🔁 {updated} updated | 📦 {inserted + updated} total processed.")
