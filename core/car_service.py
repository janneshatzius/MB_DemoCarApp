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
        types = fetch_all_types()

        if isinstance(types, pd.DataFrame):
            return types["type_name"].tolist()

        if isinstance(types, pd.Series):
            return types.tolist()
        
        if isinstance(types, list):
            
            if types and isinstance(types[0], dict):
                return [t["type_name"] for t in types]
            
            if types and isinstance(types[0], str):
                return types
            
            return [str(t) for t in types]

        
        try:
            return [str(t) for t in types]
        except Exception:
            return []

    @staticmethod
    def get_models_for_type(type_name: str) -> list[dict]:
        
        models = fetch_models_by_type(type_name)

        if isinstance(models, pd.DataFrame):
            return models.rename(columns={"car_model_id": "id",
                                          "model_name":     "name"})\
                         .to_dict("records")

        if isinstance(models, pd.Series):
            return [{"name": v} for v in models.tolist()]

        if isinstance(models, list):
    
            if models and isinstance(models[0], tuple):
                return [{"id": t[0], "name": t[1]} for t in models]
            
            if models and isinstance(models[0], dict):
                
                return [{"id": m.get("car_model_id", m.get("id")),
                         "name": m.get("model_name", m.get("name"))}
                        for m in models]
            
            if models and isinstance(models[0], str):
                return [{"id": None, "name": m} for m in models]
            
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
        return get_all_model_names()
