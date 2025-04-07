from data_loader import load_all_data
from recommendation import generate_recommendations
import pandas as pd
from db_writer import save_recommendations_to_db

# Load data from database
dealerships, parking_spots, past_recs, car_models = load_all_data()



print("parking_spots loaded:", len(parking_spots))



# Generate 2026 recommendations
recs = generate_recommendations(parking_spots, past_recs, car_models)

# Convert to DataFrame
recs_df = pd.DataFrame(recs)

print("Generated recommendations:")
print(recs_df.head())



recs = generate_recommendations(parking_spots, past_recs, car_models)
save_recommendations_to_db(recs, car_models)

