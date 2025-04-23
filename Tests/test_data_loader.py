import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data import data_loader  


import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from data import data_loader


@pytest.fixture
def mock_db_data():
    dealership_df = pd.DataFrame({'id': [1], 'gssn_id': ['GS00001']})
    parking_df = pd.DataFrame({'parkingspot_id': [101], 'dealership_id': [1], 'car_type_id': [2], 'car_type': ['commercial']})
    fs_allocation_df = pd.DataFrame({'allocation_id': [1], 'fs_category': ['V2'], 'parking_category': ['commercial'], 'quantity': [2]})
    past_recs_df = pd.DataFrame({'dealership_id': [1], 'allocation_year': [2024], 'car_model_name': ['Vito']})
    car_model_df = pd.DataFrame({'car_model_id': [10], 'model_name': ['Vito'], 'car_type': [2]})
    car_type_df = pd.DataFrame({'car_type_id': [2], 'type_name': ['commercial']})

    return [
        dealership_df,        # 1
        parking_df,           # 2
        fs_allocation_df,     # 3
        past_recs_df,         # 4
        car_model_df,         # 5
        car_type_df           # 6
    ]



@patch("data.dbconnect.get_connection")
@patch("pandas.read_sql")
def test_load_all_data(mock_read_sql, mock_get_conn, mock_db_data):  # FIX: inject here
    mock_read_sql.side_effect = mock_db_data
    mock_conn = MagicMock()
    mock_get_conn.return_value = mock_conn

    dealerships, parking, past_recs, car_models, car_types, allocation = data_loader.load_all_data()

    assert isinstance(dealerships, pd.DataFrame)
    assert isinstance(parking, pd.DataFrame)
    assert isinstance(past_recs, pd.DataFrame)
    assert isinstance(car_models, pd.DataFrame)
    assert isinstance(car_types, pd.DataFrame)
    assert isinstance(allocation, pd.DataFrame)

    assert 'car_type' in car_models.columns
    assert 'car_type_id' not in car_models.columns
    assert mock_conn.close.called

    
