import pandas as pd
from data_loader import load_all_data
from db_writer import save_parking_spots, assign_dealership_groups
from parking_spot_generator import generate_parking_spots  

# Load required data from the DB
dealerships, _, past_recs, car_models, car_types = load_all_data()

# Generate parking spots based on FS category and allocation logic
parking_spots = generate_parking_spots(dealerships)

# Save the generated parking spots to the DB
save_parking_spots(parking_spots)

# Update dealership group_id assignments
assign_dealership_groups()
