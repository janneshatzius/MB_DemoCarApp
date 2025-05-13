
from data.load_recommendations_repository import (
    get_all_recommendations_df,
    get_car_models_by_type,
    update_recommendation

    
)
from data.car_repository import get_car_models_by_type
from data.dbconnect import get_connection
import pandas as pd
from typing import List, Dict

class RecommendationService:
    AUTO_SOURCE = 1
    MANUAL_SOURCE = 2

    @staticmethod
    def list_all_recommendations():
        return get_all_recommendations_df()

    @staticmethod
    def list_models_for_type(car_type_name: str):
        # returns a list of {"id":…, "name":…}
        return get_car_models_by_type(car_type_name)

    @staticmethod
    def save_changes(rec_id: int, new_model_id: int, new_model_name: str, note: str):
        conn = get_connection()
        try:
            # pass conn *first*, then the other four parameters
            update_recommendation(conn,
                                  rec_id,
                                  new_model_id,
                                  new_model_name,
                                  note)
        except Exception as e:
            # print to terminal instead of messagebox
            print("[ERROR] updating recommendation:", e)
        finally:
            conn.close()