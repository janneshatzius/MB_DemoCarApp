
from data.recommendations_repository import (
    get_all_recommendations_df,
    update_recommendation
)
from data.car_repository import get_car_models_by_type

class RecommendationService:
    AUTO_SOURCE = 1
    MANUAL_SOURCE = 2

    @staticmethod
    def list_all_recommendations():
        return get_all_recommendations_df()

    @staticmethod
    def list_models_for_type(car_type_name: str):
        return get_car_models_by_type(car_type_name)

    @staticmethod
    def save_changes(rec_id: int, new_model_id: int, new_model_name: str, note: str, f_allocation: str, s_allocation: str):
            update_recommendation(
                                  rec_id,
                                  new_model_id,
                                  new_model_name,
                                  note,
                                  f_allocation,
                                  s_allocation)
        