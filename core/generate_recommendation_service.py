import random
import pandas as pd

from data.car_repository import (
    get_all_car_models,
) 
from data.dealership_repository import get_all_dealerships
from data.parking_repository import get_all_parking_spots
from data.generate_recommendation_repository import (
    get_past_recommendations,
    insert_recommendations,
    get_recommendations_by_dealership,
    move_recommendations_to_past,
    delete_recommendations_for_year
)


class GenerateRecommendationService:
    AUTO_SOURCE = 1

    @staticmethod
    def list_for_dealership(dealership_id):
        recs = get_recommendations_by_dealership( dealership_id)
        return recs


    @staticmethod
    def generate_recommendations_for_year(target_year: int) -> int:
        """
        Generate and insert recommendations for exactly target_year.
        Returns how many were inserted.
        """
        move_recommendations_to_past(target_year-1)
        delete_recommendations_for_year(target_year-1)
        hist_years = [target_year - 2, target_year - 1]

        # fetch all necessary data
        dealers_df = get_all_dealerships()        
        spots_df   = get_all_parking_spots()       
        past_df    = get_past_recommendations(hist_years)
        models_df  = get_all_car_models()
        def to_records(x):
            return x.to_dict("records") if isinstance(x, pd.DataFrame) else x

        dealers = to_records(dealers_df)
        spots   = to_records(spots_df)
        past    = to_records(past_df)
        models  = to_records(models_df)

        # map dealer → group_id, gssn_id
        dealer_map = {
            d["dealership_id"]: {
                "group_id":    d.get("group_id"),
                "gssn_id":     d.get("gssn_id"),
                "locality":    d.get("locality"),
                "dealership_name":     d.get("dealership_name"),
                "HB":               d.get("HB"),
                "VFNR":             d.get("VFNR"),
                "gssn_company": d.get("gssn_company")
            }
            for d in dealers
        }

        # group models by car_type_name
        model_map = {}
        for m in models:
            t = m["car_type_name"].lower()
            model_map.setdefault(t, []).append({
                "id":         m["car_model_id"],
                "model_name": m["model_name"],
            })

        # build history sets
        past_used = {}
        for r in past:
            past_used.setdefault(r["dealership_id"], set()).add(r["car_model_name"])

        used_by_dealer = {}
        used_by_group  = {}
        recs = []

        for spot in spots:
            did   = spot["dealership_id"]
            ctype = spot["car_type"].lower()
            ps_id  = spot.get("parkingspot_id")
            if ps_id is None:
                continue

            info = dealer_map.get(did)
            if not info:
                continue
            grp, gssn, locality, dealership_name, HB, VFNR, gssn_company = info["group_id"], info["gssn_id"], info["locality"], info["dealership_name"], info["HB"], info["VFNR"], info["gssn_company"]

            history_set = past_used.get(did, set())
            dealer_set  = used_by_dealer .get(did, set())
            group_set   = used_by_group  .get(grp, set())

            candidates = model_map.get(ctype, [])
            if not candidates:
                # no models for that type at all
                continue

            # apply relaxation until we get 1 or more choice
            for test in (
                lambda m: m["model_name"] not in history_set
                          and m["model_name"] not in dealer_set
                          and m["model_name"] not in group_set,
                lambda m: m["model_name"] not in history_set
                          and m["model_name"] not in dealer_set,
                lambda m: m["model_name"] not in dealer_set,
                lambda m: True,
            ):
                possible = [m for m in candidates if test(m)]
                if possible:
                    break

            choice = random.choice(possible)
            mid    = choice["id"]
            mname  = choice["model_name"]

            used_by_dealer.setdefault(did, set()).add(mname)
            used_by_group .setdefault(grp, set()).add(mname)

            recs.append({
                "dealership_id":         did,
                "gssn_id":               gssn,
                "HB":                    HB,
                "VFNR":                  VFNR,
                "parking_type":          ctype,
                "parking_spot":          ps_id,
                "car_model":             mid,
                "car_model_name":        mname,
                "recommendation_source": GenerateRecommendationService.AUTO_SOURCE,
                "allocation_year":       target_year,
                "locality":              locality,
                "dealership_name":       dealership_name,
                "note":                  "",
                "gssn_company": gssn_company
            })

        insert_recommendations(recs)
        return len(recs)
    
    
    

