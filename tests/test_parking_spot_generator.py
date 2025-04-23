import pytest
import pandas as pd
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import parking_spot_generator  

def test_parse_fs_config():
    fs_allocation_df = pd.DataFrame({
        'fs_category': ['V2', 'V2', 'P3'],
        'parking_category': ['Commercial', 'Private', 'Private'],
        'quantity': [2, 3, 4]
    })

    expected = {
        'V2': {'commercial': 2, 'private': 3},
        'P3': {'private': 4}
    }

    result = parking_spot_generator.parse_fs_config(fs_allocation_df)
    assert result == expected


def test_generate_parking_spots_basic():
    dealership_df = pd.DataFrame({
        'gssn_id': ['GS001', 'GS002'],
        'FS_Value': ['V2', 'P3']
    })

    fs_allocation_df = pd.DataFrame({
        'fs_category': ['V2', 'V2', 'P3'],
        'parking_category': ['Commercial', 'Private', 'Private'],
        'quantity': [1, 2, 3]
    })

    result_df = parking_spot_generator.generate_parking_spots(dealership_df, fs_allocation_df)

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.shape[0] == 6 
    assert set(result_df.columns) == {'parkingspot_id', 'gssn_id', 'car_type'}
    assert result_df['gssn_id'].isin(['GS001', 'GS002']).all()
    assert result_df['car_type'].isin(['commercial', 'private']).all()


def test_generate_parking_spots_invalid_fs(capfd):
    dealership_df = pd.DataFrame({
        'gssn_id': ['GS001'],
        'FS_Value': ['INVALID']
    })

    fs_allocation_df = pd.DataFrame({
        'fs_category': ['V2'],
        'parking_category': ['Private'],
        'quantity': [1]
    })

    result_df = parking_spot_generator.generate_parking_spots(dealership_df, fs_allocation_df)

    # Check output message
    out, _ = capfd.readouterr()
    assert "FS key INVALID not in config" in out
    assert result_df.empty
