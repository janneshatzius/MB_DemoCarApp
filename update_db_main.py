import pandas as pd
from data.data_loader import load_all_data
from data.db_writer import (
    save_parking_spots,
    assign_dealership_groups,
    update_past_recommendations_with_dealership_ids
)
from core.parking_spot_generator import generate_parking_spots

def main():
    print("Starting database update process...")

    # Step 1: Load data
    try:
        dealerships, _, _, _, _, fs_allocation = load_all_data()
    except Exception as e:
        print(f"Error while loading data: {e}")
        return

    # Step 2: Generate parking spots from allocation logic
    parking_spots = generate_parking_spots(dealerships, fs_allocation)

    # Step 3: Save to DB
    save_parking_spots(parking_spots)
    assign_dealership_groups()
    update_past_recommendations_with_dealership_ids()

    print("Database update process completed.")

if __name__ == "__main__":
    main()
