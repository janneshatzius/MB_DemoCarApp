import pandas as pd
from data.data_loader import load_all_data
from core.recommendation_generator import generate_recommendations
from data.db_writer import save_recommendations_to_db



# Load all necessary tables from the database
dealerships, parking_spots, past_recs, car_models, car_types = load_all_data()

#Generate recommendations
recs = generate_recommendations(parking_spots, past_recs, car_models, dealerships)

#Save the recommendations to the database
save_recommendations_to_db(recs, car_models)





