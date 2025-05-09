from data.dbconnect import get_connection
from data.dealership_repository import get_all_dealerships
from data.parking_repository    import (
    get_allocation_for_fs,
    get_parking_category_map,
    insert_parking_spots_bulk
)

def create_all_parking_spots():
    conn = get_connection()
    try:
        # build a map: parkingcategory_id → {car_type_id, car_type}
        category_map = get_parking_category_map(conn)

        spots_to_insert = []
        for d in get_all_dealerships():
            dealer_id = d["dealership_id"]
            fs_val    = d["fs_value"]
            gssn_id   = d["gssn_id"]

            # for each (parking_category_id, qty) row in your Parking_Allocation table
            for parking_cat_id, qty in get_allocation_for_fs(fs_val, conn):
                mapping = category_map.get(parking_cat_id)
                if not mapping:
                    continue
                # add as many spots as qty
                for _ in range(qty):
                    spots_to_insert.append((
                        dealer_id,
                        mapping["car_type"],
                        mapping["car_type_id"],
                        gssn_id
                    ))

        insert_parking_spots_bulk(spots_to_insert, conn)
        conn.commit()
    finally:
        conn.close()