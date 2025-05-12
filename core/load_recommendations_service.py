from data.recommendation_repository import (
    
    update_recommendation
)
from data.load_recommendations_repository import (
    get_all_recommendations_with_type,
    get_car_models_by_type
)
from data.dbconnect import get_connection
import pandas as pd

class RecommendationService:
    AUTO_SOURCE = 1
    MANUAL_SOURCE = 2

    @staticmethod
    def load_all_recs_df() -> pd.DataFrame:
        """
        Load everything once, into a DataFrame.
        """
        records = get_all_recommendations_with_type()
        return pd.DataFrame(records)

    @staticmethod
    def list_models_for_type(car_type: str):
        """
        Returns a list of {"id":…, "name":…} for that car_type.
        """
        return get_car_models_by_type(car_type)

    @staticmethod
    def save_changes(rec_id: int, model_id: int, model_name: str, note: str):
        """
        Persist the user's edits.
        """
        conn = get_connection()
        try:
            update_recommendation(conn, rec_id, model_id, model_name, note)
        finally:
            conn.close()