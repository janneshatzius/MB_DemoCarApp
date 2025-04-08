import random
from datetime import datetime

def generate_recommendations(parking_df, past_recs_df, car_model_df, dealership_df):

    

    # Normalize car type names
    car_model_df['car_type'] = car_model_df['car_type'].str.lower()
    parking_df['car_type'] = parking_df['car_type'].str.lower()

    # Create model map by car type
    model_map = (
        car_model_df.groupby('car_type')['model_name']
        .apply(list)
        .to_dict()
    )

    current_year = datetime.now().year
    rec_year = current_year + 1
    history_years = [rec_year - 2, rec_year - 1]

    print(f" Generating recommendations for {rec_year} based on {history_years}")

    # Used models from past recommendations
    past_models = (
        past_recs_df[past_recs_df['allocation_year'].isin(history_years)]
        .groupby('dealership_id')['car_model_name']
        .apply(set)
        .to_dict()
    )

    # Dealership -> Group map
    dealership_group_map = dict(zip(dealership_df['dealership_id'], dealership_df['dealership_group']))

    # Track models used during this run
    used_by_dealer = {}
    used_by_group = {}

    results = []

    for _, row in parking_df.iterrows():
        dealership_id = row['dealership_id']
        group_id = dealership_group_map.get(dealership_id)
        car_type = row['car_type']
        parking_spot_id = row['parkingspot_id']

        # Get models used in history, in this dealership, and this group
        history_used = past_models.get(dealership_id, set())
        dealer_used = used_by_dealer.get(dealership_id, set())
        group_used = used_by_group.get(group_id, set())

        available_models = model_map.get(car_type, [])

        # Step 1: exclude history + current dealer + group
        possible_models = [
            m for m in available_models
            if m not in history_used and m not in dealer_used and m not in group_used
        ]

        # Step 2: exclude history + dealer if necessary
        if not possible_models:
            possible_models = [
                m for m in available_models
                if m not in history_used and m not in dealer_used
            ]

        # Step 3: fallback to all models
        if not possible_models:
            possible_models = [m for m in available_models if m not in dealer_used]

        if not possible_models:
            possible_models = available_models  # final fallback

        if not possible_models:
            print(f"No models available for {dealership_id} ({car_type})")
            continue

        model = random.choice(possible_models)

        # Track usage
        used_by_dealer.setdefault(dealership_id, set()).add(model)
        used_by_group.setdefault(group_id, set()).add(model)

        # Save result
        results.append({
            'dealership_id': dealership_id,
            'parkingspot_id': parking_spot_id,
            'car_model_name': model,
            'allocation_year': rec_year,
            'source': 'auto'
        })

    print(f"Generated {len(results)} recommendations.")
    return results

