import pandas as pd

def parse_fs_config(fs_allocation_df):
    
    fs_config = {}
    for _, row in fs_allocation_df.iterrows():
        fs = row['fs_category']
        parking_type = row['parking_category'].lower()
        quantity = row['quantity']
        if fs not in fs_config:
            fs_config[fs] = {}
        fs_config[fs][parking_type] = quantity
    return fs_config


def generate_parking_spots(dealership_df, fs_allocation_df):
    
    parking_spots = []
    spot_id = 1

    # Convert config table to dictionary
    fs_config = parse_fs_config(fs_allocation_df)

    for _, row in dealership_df.iterrows():
        gssn_id = row['gssn_id']
        fs_key = row['FS_Value']

        if fs_key not in fs_config:
            print(f" FS key {fs_key} not in config. Skipping dealership {gssn_id}.")
            continue

        allocation = fs_config[fs_key]

        for car_type, count in allocation.items():
            for _ in range(count):
                parking_spots.append({
                    'parkingspot_id': spot_id,
                    'gssn_id': gssn_id,
                    'car_type': car_type.lower()
                })
                spot_id += 1

    parking_df = pd.DataFrame(parking_spots)
    print(f"Generated {len(parking_df)} parking spots.")
    return parking_df
