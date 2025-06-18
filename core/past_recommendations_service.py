
from data.past_recommendations_repository import (
    get_past_recommendations_df,
    update_past_recommendation,
    get_available_years
)
from data.car_repository import get_car_models_by_type

class PastRecommendationService:

    @staticmethod
    def list_past_recommendations(year):
        return get_past_recommendations_df(year)

    @staticmethod
    def list_models_for_type(car_type_name: str):
        return get_car_models_by_type(car_type_name)

    @staticmethod
    def save_changes(past_rec_id: int, new_model_name: str, note: str, f_allocation: str, s_allocation: str):
            update_past_recommendation(
                                  past_rec_id,
                                  new_model_name,
                                  note,
                                  f_allocation,
                                  s_allocation)
            

    @staticmethod
    def list_available_years():
        return get_available_years()
        