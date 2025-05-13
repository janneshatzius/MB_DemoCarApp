from data.dbconnect import get_connection
import pandas as pd
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
        """
        Always returns a plain list of type_name strings.
        """
        types = fetch_all_types()

        # 1) If it’s a DataFrame, pull the column:
        if isinstance(types, pd.DataFrame):
            return types["type_name"].tolist()

        # 2) If it’s a Series, convert to list of strings:
        if isinstance(types, pd.Series):
            return types.tolist()

        # 3) If it’s already a list:
        if isinstance(types, list):
            # list of dicts?
            if types and isinstance(types[0], dict):
                return [t["type_name"] for t in types]
            # list of strings?
            if types and isinstance(types[0], str):
                return types
            # empty or mixed—just stringify:
            return [str(t) for t in types]

        # 4) Fallback for any other iterable:
        try:
            return [str(t) for t in types]
        except Exception:
            return []

    @staticmethod
    def get_models_for_type(type_name: str) -> list[dict]:
        """
        Returns a list of {"id":…, "name":…}.
        """
        models = fetch_models_by_type(type_name)

        if isinstance(models, pd.DataFrame):
            return models.rename(columns={"car_model_id": "id",
                                          "model_name":     "name"})\
                         .to_dict("records")

        if isinstance(models, pd.Series):
            # unlikely, but just in case
            return [{"name": v} for v in models.tolist()]

        if isinstance(models, list):
            # list of tuples?
            if models and isinstance(models[0], tuple):
                return [{"id": t[0], "name": t[1]} for t in models]
            # list of dicts?
            if models and isinstance(models[0], dict):
                # ensure keys
                return [{"id": m.get("car_model_id", m.get("id")),
                         "name": m.get("model_name", m.get("name"))}
                        for m in models]
            # list of strings?
            if models and isinstance(models[0], str):
                return [{"id": None, "name": m} for m in models]
            # empty/mixed
            return []

        return []

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
