import pandas as pd
from data_loader import load_all_data
from db_writer import save_parking_spots, assign_dealership_groups

# Load parking spot data
parking_spots = load_all_data()

# Save parking spots and assign groups
save_parking_spots(parking_spots)
assign_dealership_groups()