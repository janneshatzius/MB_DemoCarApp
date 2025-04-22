import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data import data_loader  


@pytest.fixture
def mock_db_data():
    # Example DataFrames to return from mock SQL queries
    dealership_df = pd.DataFrame({
        'id': [1],
        'gssn_id': ['GS00001']
    })

    parking_df = pd.DataFrame({
        'parkingspot_id': [101],
        'dealership_id': [1],
        'car_type_id': [2],
        'car_type': ['commercial']
    })

    past_recs_df = pd.DataFrame({
        'dealership_id': [1],
        'allocation_year': [2024],
        'car_model_name': ['Vito']
    })

    car_model_df = pd.DataFrame({
        'car_model_id': [10],
        'model_name': ['Vito'],
        'car_type': [2]
    })

    car_type_df = pd.DataFrame({
        'car_type_id': [2],
        'type_name': ['commercial']
    })

    fs_allocation_df = pd.DataFrame({
        'allocation_id' : [1],
        'fs_category' : ['V2'],
        'parking_category' : [2],
        'quantity' : [2]
    })

    return [dealership_df, parking_df, past_recs_df, car_model_df, car_type_df, fs_allocation_df]


@patch("data.dbconnect.get_connection")
@patch("pandas.read_sql")
def test_load_all_data(mock_read_sql, mock_get_conn, mock_db_data):
    # Arrange: Set return values in order of read_sql calls
    mock_read_sql.side_effect = mock_db_data
    mock_conn = MagicMock()
    mock_get_conn.return_value = mock_conn

    # Act
    dealerships, parking, past_recs, car_models, car_types, allocation = data_loader.load_all_data()

    # Assert: Check types and shape
    assert isinstance(dealerships, pd.DataFrame)
    assert isinstance(parking, pd.DataFrame)
    assert isinstance(past_recs, pd.DataFrame)
    assert isinstance(car_models, pd.DataFrame)
    assert isinstance(car_types, pd.DataFrame)
    assert isinstance(allocation, pd.DataFrame)

    assert 'car_type' in car_models.columns
    assert 'car_type_id' not in car_models.columns  
    assert mock_conn.close.called

    
