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

    # Used models from past recommendations
    past_models = (
        past_recs_df[past_recs_df['allocation_year'].isin(history_years)]
        .groupby('dealership_id')['car_model_name']
        .apply(set)
        .to_dict()
    )

    # Dealership ID and Group ID mapping
    dealership_group_map = dict(zip(dealership_df['id'], dealership_df['group_id']))
    dealership_gssn_map = dict(zip(dealership_df['id'], dealership_df['gssn_id']))

    used_by_dealer = {}
    used_by_group = {}

    results = []

    for _, row in parking_df.iterrows():
        dealership_id = row['dealership_id']
        gssn_id = dealership_gssn_map.get(dealership_id)
        group_id = dealership_group_map.get(dealership_id)
        car_type = row['car_type']
        parking_spot_id = row['parkingspot_id']

        history_used = past_models.get(dealership_id, set())
        dealer_used = used_by_dealer.get(dealership_id, set())
        group_used = used_by_group.get(group_id, set())

        available_models = model_map.get(car_type, [])

        possible_models = [
            m for m in available_models
            if m not in history_used and m not in dealer_used and m not in group_used
        ]

        if not possible_models:
            possible_models = [m for m in available_models if m not in history_used and m not in dealer_used]

        if not possible_models:
            possible_models = [m for m in available_models if m not in dealer_used]

        if not possible_models:
            possible_models = available_models

        if not possible_models:
            print(f"No models available for {dealership_id} ({car_type})")
            continue

        model = random.choice(possible_models)

        used_by_dealer.setdefault(dealership_id, set()).add(model)
        used_by_group.setdefault(group_id, set()).add(model)

        results.append({
            'dealership_id': dealership_id,
            'gssn_id': gssn_id,
            'parkingspot_id': parking_spot_id,
            'car_model_name': model,
            'allocation_year': rec_year,
            'source': 'auto'
        })

    print(f"Generated {len(results)} recommendations.")
    return results


