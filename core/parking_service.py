from data.dealership_repository import get_all_dealerships
from data.parking_repository import (
    get_allocation_map,
    get_parking_category_map,
    insert_parking_spots_bulk,
    get_existing_spot_counts,
    delete_spots_for_dealers
)

def create_all_parking_spots():
    # 1) load everything in bulk
    alloc_map       = get_allocation_map()        # fs_value → [(cat_id, qty),…]
    category_map    = get_parking_category_map()  # cat_id → {…}
    existing_counts = get_existing_spot_counts()  # dealer_id → existing_count
    dealers         = get_all_dealerships()       # list of dicts

    # 2) figure out which dealers need to be rebuilt
    to_delete = []
    spots      = []

    for d in dealers:
        did    = d["dealership_id"]
        fs_val = d["FS_Value"]
        gssn   = d["gssn_id"]

        desired_total = sum(q for _, q in alloc_map.get(fs_val, []))
        existing      = existing_counts.get(did, 0)

        if existing != desired_total:
            to_delete.append(did)

            # build exactly desired_total spots
            for cat_id, qty in alloc_map.get(fs_val, []):
                mapping = category_map.get(cat_id)
                if not mapping:
                    continue
                for _ in range(qty):
                    spots.append((
                        did,
                        mapping["car_type"],
                        mapping["car_type_id"],
                        gssn
                    ))

    # 3) do one delete + one bulk insert
    delete_spots_for_dealers(to_delete)
    insert_parking_spots_bulk(spots)

