from data.dbconnect import get_connection
from data.car_repository import (
    fetch_all_types,
    fetch_models_by_type,
    insert_car_model,
    delete_car_model,
    get_all_model_names
)

class CarModelService:
    @staticmethod
    def get_all_types() -> list[str]:
        return fetch_all_types()

    @staticmethod
    def get_models_by_type(type_name: str) -> list[str]:
        return fetch_models_by_type(type_name)

    @staticmethod
    def add_model(type_name: str, model_name: str):
        insert_car_model(type_name, model_name)

    @staticmethod
    def delete_model(model_name: str):
        delete_car_model(model_name)
    @staticmethod
    def all_models():
        conn = get_connection()
        try:
            return get_all_model_names(conn)
        finally:
            conn.close()
