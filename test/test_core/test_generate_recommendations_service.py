import random
import pandas as pd
import pytest


from core.generate_recommendation_service import GenerateRecommendationService


@pytest.fixture(autouse=True)
def seed_random(monkeypatch):
    
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])


def test_list_for_dealership_delegates(monkeypatch):
    fake_list = [{"recommendation_id": 42}]
    monkeypatch.setattr(
        "data.generate_recommendation_repository.get_recommendations_by_dealership",
        lambda did: fake_list
    )

    
    out = GenerateRecommendationService.list_for_dealership(123)
    assert out is fake_list
    assert out == fake_list


@pytest.fixture
def fake_env(monkeypatch):
    
    
    dealers = pd.DataFrame([
        {"dealership_id": 1, "group_id": 10, "gssn_id": 100, 
         "locality": "L1", "dealership_name": "D1",
         "HB": "23556", "VFNR": "23456", "gssn_company": "GC11111"},
        {"dealership_id": 2, "group_id": 10, "gssn_id": 200, 
         "locality": "L2", "dealership_name": "D2",
         "HB": "12345", "VFNR": "12345", "gssn_company": "GC00000"},
    ])
    
    spots = pd.DataFrame([
        {"dealership_id": 1, "car_type": "Private", "parkingspot_id": 11},
        {"dealership_id": 1, "car_type": "Commercial", "parkingspot_id": 12},
        {"dealership_id": 2, "car_type": "Private",  "parkingspot_id": 21},
    ])
    # Past: dealer1 used "Old" last two years
    past = pd.DataFrame([
        {"dealership_id": 1, "car_model_name": "OldModel"},
    ])
    # Models: SUV→["OldModel","NewModel"], EV→["EvModel"]
    models = pd.DataFrame([
        {"car_model_id": 101, "model_name": "V-Klasse", "car_type_name": "Private"},
        {"car_model_id": 102, "model_name": "T-Klasse", "car_type_name": "Private"},
        {"car_model_id": 201, "model_name": "Citan Kasten",  "car_type_name": "Commerical"},
    ])

    # Capture inserts
    inserted = []
    monkeypatch.setattr(
        "data.generate_recommendation_repository.insert_recommendations",
        lambda recs: inserted.extend(recs)
    )

    # Stub everything else
    monkeypatch.setattr(
        "data.dealership_repository.get_all_dealerships",
        lambda: dealers
    )
    monkeypatch.setattr(
        "data.parking_repository.get_all_parking_spots",
        lambda: spots
    )
    monkeypatch.setattr(
        "data.generate_recommendation_repository.get_past_recommendations",
        lambda years: past
    )
    monkeypatch.setattr(
        "data.car_repository.get_all_car_models",
        lambda: models
    )
    monkeypatch.setattr(
        "data.generate_recommendation_repository.move_recommendations_to_past",
        lambda y: None
    )
    monkeypatch.setattr(
        "data.generate_recommendation_repository.delete_recommendations_for_year",
        lambda y: None
    )

    return inserted


def test_generate_recommendations_with_new_dummy(fake_env):
    
    count = GenerateRecommendationService.generate_recommendations_for_year(2025)

    
    assert count == 2
    recs = fake_env
    assert len(recs) == 2

    d1 = [r for r in recs if r["dealership_id"] == 1]
    assert len(d1) == 1
    assert d1[0]["car_model_name"] == "V-Klasse"
    assert d1[0]["recommendation_source"] == GenerateRecommendationService.AUTO_SOURCE
    assert d1[0]["allocation_year"] == 2025

    
    d2 = [r for r in recs if r["dealership_id"] == 2]
    assert len(d2) == 1
    assert d2[0]["car_model_name"] == "T-Klasse"


def test_relaxation_when_all_in_history(fake_env, monkeypatch):
    
    monkeypatch.setattr(
        "data.generate_recommendation_repository.get_past_recommendations",
        lambda years: pd.DataFrame([
            {"dealership_id": 1, "car_model_name": "V-Klasse"},
            {"dealership_id": 1, "car_model_name": "T-Klasse"},
        ])
    )
    fake_env.clear()

    count = GenerateRecommendationService.generate_recommendations_for_year(2026)
    
    assert count == 2

    recs = fake_env
    
    d1 = [r for r in recs if r["dealership_id"] == 1]
    assert len(d1) == 1
    assert d1[0]["car_model_name"] == "V-Klasse"

    
    d2 = [r for r in recs if r["dealership_id"] == 2]
    assert len(d2) == 1
    assert d2[0]["car_model_name"] == "T-Klasse"