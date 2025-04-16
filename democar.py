import pandas as pd
from data_loader import load_all_data
from recommendation import generate_recommendations
from db_writer import save_recommendations_to_db
from db_writer import save_parking_spots
from db_writer import assign_dealership_groups


# Load all necessary tables from the database
dealerships, parking_spots, past_recs, car_models, car_types = load_all_data()



# Generate recommendations
#recs = generate_recommendations(parking_spots, past_recs, car_models, dealerships)

# Save the recommendations to the database
#save_recommendations_to_db(recs, car_models)

save1 = save_parking_spots(parking_spots)
save2 = assign_dealership_groups()



