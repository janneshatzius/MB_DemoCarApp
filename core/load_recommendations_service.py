# core/recommendation_service.py
from data.load_recommendations_repository import (
    get_all_recommendations
)


class RecommendationService:

    @staticmethod
    def load_all_recommendations() -> pd.DataFrame:
        """
        Load entire recommendation set into memory.
        Called once on app startup.
        """
        df = get_all_recommendations()
        # If you need any pre‐processing, do it here.
        # e.g. ensure certain dtypes:
        # df['car_model_name'] = df['car_model_name'].astype(str)
        return df