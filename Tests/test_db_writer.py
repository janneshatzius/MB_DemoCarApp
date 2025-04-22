import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import module under test
from data import db_writer


@pytest.fixture
def mock_connection():
    with patch("data.dbconnect.get_connection") as mock_conn:
        mock = MagicMock()
        mock_conn.return_value = mock
        yield mock


def test_save_recommendations_to_db_insert(mock_connection):
    
    recommendations = [
        {
            'dealership_id': 1,
            'parkingspot_id': 100,
            'car_model_name': 'V-Klasse',
            'allocation_year': 2026,
            'gssn_id' : 'GS0000354'
        }
    ]
    car_model_df = pd.DataFrame({
        'car_model_id': [4],
        'model_name': ['V-Klasse']
    })

    cursor = mock_connection.cursor.return_value
    cursor.fetchone.return_value = [0]  # Recommendation does NOT exist

    db_writer.save_recommendations_to_db(recommendations, car_model_df)

    expected_args = (
    1, 100, 4, 'V-Klasse', 1, 2026, 'GS0000354'
)

    matches = [
    call_args for call_args in cursor.execute.call_args_list
    if call_args[0][1] == expected_args
]

    assert matches

    


def test_save_recommendations_to_db_update(mock_connection):
    
    recommendations = [
        {
            'dealership_id': 1,
            'parkingspot_id': 100,
            'car_model_name': 'V-Klasse',
            'allocation_year': 2026
        }
    ]
    car_model_df = pd.DataFrame({
        'car_model_id': [4],
        'model_name': ['V-Klasse']
    })

    cursor = mock_connection.cursor.return_value
    cursor.fetchone.return_value = [1]  # Recommendation exists

    db_writer.save_recommendations_to_db(recommendations, car_model_df)

    expected_args = (4, 'V-Klasse', 1, 100, 2026)

    matches = [
    call_args for call_args in cursor.execute.call_args_list
    if call_args[0][1] == expected_args
]

    assert matches
    


def test_save_parking_spots_empty_df(mock_connection):
    
    df = pd.DataFrame()
    result = db_writer.save_parking_spots(df)
    assert result is None
    


def test_assign_dealership_groups(mock_connection):
    
    dealership_df = pd.DataFrame({
        "HB": ["A123"],
        "gssn_id": ["GS001"]
    })

    group_df = pd.DataFrame({
        "vfnrhb": ["A123"],
        "DG_ID": [10],
        "gssn_companyid": ["COMP123"]
    })

    with patch("pandas.read_sql", side_effect=[dealership_df, group_df]):
        db_writer.assign_dealership_groups()

    assert mock_connection.cursor.return_value.execute.called
    

def test_update_past_recommendations(mock_connection):
    
    dealership_df = pd.DataFrame({
        "ID": [1],
        "gssn_id": ["GS001"]
    })

    past_df = pd.DataFrame({
        "gssn_id": ["GS001"],
        "dealership_id": [None] 
    })

    with patch("pandas.read_sql", side_effect=[dealership_df.rename(columns={"ID": "dealership_id"}), past_df]):
        db_writer.update_past_recommendations_with_dealership_ids()

    assert mock_connection.cursor.return_value.execute.called
    

