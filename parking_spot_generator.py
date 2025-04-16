import pandas as pd
# Sample FS category to parking type allocation config
# You can later load this from DB or config file
FS_PARKING_CONFIG = {
    "V2": {"commercial": 1, "private": 2, "evan com": 1, "evan pr": 1},
    "V3": {"commercial": 2, "private": 2, "evan com": 2, "evan pr": 2, "mp": 1, "vansol": 1},
    "V4": {"commercial": 2, "private": 2, "evan com": 2, "evan pr": 2, "mp": 1, "vansol": 1},
    "V5": {"commercial": 3, "private": 3, "evan com": 3, "evan pr": 2, "mp": 2, "vansol": 2},
    "P2": {"private": 2},
    "P3": {"private": 3, "commercial": 1},
    "P4": {"private": 3, "commercial": 2},
    "P5": {"private": 4, "commercial": 3}
}

def generate_parking_spots(dealership_df):
    print("Generating parking spots from dealership FS values...")

    parking_spots = []
    spot_id = 1

    for _, row in dealership_df.iterrows():
        gssn_id = row['gssn_id']
        fs_key = row['fs_value']  # already in format like 'V2', 'P3', etc.

        # Skip if no FS mapping exists
        if fs_key not in FS_PARKING_CONFIG:
            print(f"FS key {fs_key} not in config. Skipping dealership {gssn_id}.")
            continue

        allocation = FS_PARKING_CONFIG[fs_key]

        for car_type, count in allocation.items():
            for _ in range(count):
                parking_spots.append({
                    'parkingspot_id': spot_id,
                    'gssn_id': gssn_id,
                    'car_type': car_type.lower(),
                })
                spot_id += 1

    parking_df = pd.DataFrame(parking_spots)

    # You can later map car_type -> car_type_id using a merge in db_writer
    print(f"Generated {len(parking_df)} parking spots.")
    return parking_df
