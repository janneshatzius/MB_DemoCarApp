import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data import dbconnect


def test_connection():
    try:
        conn = dbconnect.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT TOP 1 * FROM Dealership")
        row = cursor.fetchone()

        conn.close()

        assert row is not None or row is None  # connection and query worked
    except Exception as e:
        pytest.fail(f"Database connection or query failed: {e}")

