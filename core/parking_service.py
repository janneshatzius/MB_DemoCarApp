from data.dealership_repository import get_all_dealerships
from data.parking_repository import (
    get_allocation_map,
    get_parking_category_map,
    insert_parking_spots_bulk,
    get_existing_spot_counts,
    delete_spots_for_dealers,
    list_fs_categories,
    add_fs_category,
    list_parking_categories,
    list_allocation_for_fs,
    insert_allocation,
    update_allocation,
    delete_allocation
)

class ParkingService:
    @staticmethod
    def create_all_parking_spots():
        alloc_map       = get_allocation_map()        # fs_value → [(cat_id, qty),…]
        category_map    = get_parking_category_map()  # cat_id → {…}
        existing_counts = get_existing_spot_counts()  # dealer_id → existing_count
        dealers         = get_all_dealerships()       # list of dicts


        dealer_records = dealers.to_dict("records")


        inactive_ids   = []
        active_records = []

        for d in dealer_records:
            did    = d["dealership_id"]
            status = d["status"]
            if status is None or str(status).lower() != "active":
            # anything not explicitly "active" becomes a candidate for deletion
                inactive_ids.append(did)
            else:
                active_records.append(d)

    # First, delete all spots for every inactive dealer
        delete_spots_for_dealers(inactive_ids)

        # 2) figure out which dealers need to be rebuilt
        to_delete = []
        spots      = []

        for d in dealers.to_dict("records"):
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

    @staticmethod
    def list_fs_categories() -> list[dict]:
        return list_fs_categories()

    @staticmethod
    def add_fs_category(fs: str) -> None:
        # you could add validation here (e.g. no duplicates)
        existing = [r["fs_category"] for r in list_fs_categories()]
        if fs in existing:
            raise ValueError(f"FS-Kategorie {fs} existiert bereits.")
        add_fs_category(fs)

    # — PARKING_CATEGORY —
    @staticmethod
    def list_parking_categories() -> list[dict]:
        return list_parking_categories()

    # — PARKING_ALLOCATION logic —
    @staticmethod
    def list_allocation_for_fs(fs: str) -> list[tuple[int,int]]:
        return list_allocation_for_fs(fs)

    @staticmethod
    def save_allocations(
        fs: str,
        entries: list[tuple[int,int]]
    ) -> None:
        """
        entries is a list of (parking_category_id, quantity)
        If quantity > 0 and no row exists → INSERT
        If quantity > 0 and row exists     → UPDATE
        If quantity == 0 and row exists    → DELETE
        """
        # fetch existing allocations
        existing = dict(list_allocation_for_fs(fs))  # {cat_id: qty}

        # process each entry
        for cat_id, qty in entries:
            old_qty = existing.get(cat_id)

            if old_qty is None:
                # no row exists
                if qty > 0:
                    insert_allocation(fs, cat_id, qty)
            else:
                # row already exists
                if qty > 0:
                    if qty != old_qty:
                        update_allocation(fs, cat_id, qty)
                else:
                    # qty == 0 → delete row
                    delete_allocation(fs, cat_id)

        # any existing categories not in entries should be removed
        entry_ids = {cat_id for cat_id, _ in entries}
        for cat_id in existing:
            if cat_id not in entry_ids:
                delete_allocation(fs, cat_id)


        


