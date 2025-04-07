import random
from datetime import datetime

def generate_recommendations(parking_df, past_recs_df, car_model_df):
    print("generate_recommendations() started...")


    # Normalize car type names
    car_model_df['car_type'] = car_model_df['car_type'].str.lower()
    parking_df['car_type'] = parking_df['car_type'].str.lower()

    results = []

    # Current & historical years
    current_year = datetime.now().year
    rec_year = current_year + 1
    history_years = [rec_year - 2, rec_year - 1]

    print(f"Generating recommendations for {rec_year} based on {history_years}")
    print("parking_df rows:", len(parking_df))
    print("past_recs_df rows:", len(past_recs_df))
   


    # Build model map from car model → car type
    model_map = (
        car_model_df.groupby('car_type')['model_name']
        .apply(list)
        .to_dict()
    )


    # Build past model usage by dealership
    recent_recs = past_recs_df[past_recs_df['allocation_year'].isin(history_years)]
    past_models = (
        recent_recs.groupby('dealership_id')['car_model_name']
        .apply(set)
        .to_dict()
    )

    # Loop over parking spots
    for _, row in parking_df.iterrows():
        dealership_id = row['dealership_id']
        car_type = row['car_type']
        parking_spot_id = row['parkingspot_id']

        used_models = past_models.get(dealership_id, set())
        available_models = model_map.get(car_type, [])

        possible_models = [m for m in available_models if m not in used_models]
        if not possible_models:
            possible_models = available_models  # fallback

        if not possible_models:
            continue  # skip if still empty

        model = random.choice(possible_models)

        results.append({
            'dealership_id': dealership_id,
            'parkingspot_id': parking_spot_id,
            'car_model_name': model,
            'allocation_year': rec_year,
            'source': 'auto'
        })

    return results
