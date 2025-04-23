import pandas as pd
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.recommendation_generator import generate_recommendations
from datetime import datetime

def test_generate_recommendations_basic():
    current_year = datetime.now().year
    rec_year = current_year + 1

    parking_df = pd.DataFrame([
        {"dealership_id": 1, "parkingspot_id": 100, "car_type": "Private"},
        {"dealership_id": 2, "parkingspot_id": 200, "car_type": "Commercial"}
    ])

    past_recs_df = pd.DataFrame([
        {"dealership_id": 1, "allocation_year": rec_year - 2, "car_model_name": "Model X"},
        {"dealership_id": 1, "allocation_year": rec_year - 1, "car_model_name": "Model Y"},
        {"dealership_id": 2, "allocation_year": rec_year - 1, "car_model_name": "Model Z"},
    ])

    car_model_df = pd.DataFrame([
        {"model_name": "Model A", "car_type": "Private"},
        {"model_name": "Model B", "car_type": "Private"},
        {"model_name": "Model C", "car_type": "Commercial"}
    ])

    dealership_df = pd.DataFrame([
        {"id": 1, "group_id": 10, "gssn_id": "GS001"},
        {"id": 2, "group_id": 10, "gssn_id": "GS002"}
    ])

    results = generate_recommendations(parking_df, past_recs_df, car_model_df, dealership_df)

    assert isinstance(results, list)
    assert len(results) == 2
    for rec in results:
        assert "dealership_id" in rec
        assert "gssn_id" in rec
        assert "parkingspot_id" in rec
        assert "car_model_name" in rec
        assert "allocation_year" in rec
        assert rec["allocation_year"] == rec_year


def test_generate_recommendations_no_models():
    current_year = datetime.now().year
    rec_year = current_year + 1

    parking_df = pd.DataFrame([
        {"dealership_id": 1, "parkingspot_id": 100, "car_type": "unknown"}
    ])

    past_recs_df = pd.DataFrame(columns=["dealership_id", "allocation_year", "car_model_name"])

    car_model_df = pd.DataFrame([
        {"model_name": "Model A", "car_type": "private"}
    ])

    dealership_df = pd.DataFrame([
        {"id": 1, "group_id": 10, "gssn_id": "GS001"}
    ])

    results = generate_recommendations(parking_df, past_recs_df, car_model_df, dealership_df)

    assert isinstance(results, list)
    assert len(results) == 0  




def test_generate_recommendations_group_model_exclusion():
    current_year = datetime.now().year
    rec_year = current_year + 1

    parking_df = pd.DataFrame([
        {"dealership_id": 1, "parkingspot_id": 100, "car_type": "private"}
    ])

    past_recs_df = pd.DataFrame([
        {"dealership_id": 1, "allocation_year": rec_year - 1, "car_model_name": "Model A"}
    ])

    car_model_df = pd.DataFrame([
        {"model_name": "Model A", "car_type": "private"},
        {"model_name": "Model B", "car_type": "private"}
    ])

    dealership_df = pd.DataFrame([
        {"id": 1, "group_id": 10, "gssn_id": "GS001"}
    ])

    results = generate_recommendations(parking_df, past_recs_df, car_model_df, dealership_df)

    assert len(results) == 1
    assert results[0]['car_model_name'] == "Model B"
