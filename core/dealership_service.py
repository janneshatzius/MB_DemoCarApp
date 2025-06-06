from data.dealership_repository import (
    get_all_dealerships,
    update_dealership_status,
    insert_dealership,
    insert_dealership_group,
    find_group_by_company
    )

class DealershipService():

    @staticmethod
    def list_all_dealerships():
        return get_all_dealerships()

    @staticmethod
    def update_dealership(dealer_id: int, status: str, note: str):
            update_dealership_status(
                dealer_id,
                status,
                note
            )

    @staticmethod
    def get_group_by_company(company: str) -> dict | None:
        rec = find_group_by_company(company)
        return rec if rec else None

    @staticmethod
    def create_group(company: str, vfnrhb: str) -> dict:
        return insert_dealership_group(company, vfnrhb)
    @staticmethod
    def create_dealership(
        gssn_id: str,
        name: str,
        HB: int,
        VFNR: int,
        locality: str,
        fs_value: str,
        function: str,
        group_id: int,
        gssn_company: str,
        status: str = "active",
        note: str = ""
    ) -> None:
        
        try:
            FS = int(fs_value[1:])
        except (ValueError, TypeError):
            raise ValueError(f"Ungültiges FS-Format: {fs_value!r}")

        insert_dealership(
            gssn_id=gssn_id,
            dealership_name=name,
            HB=HB,
            FS=FS,
            VFNR=VFNR,
            locality=locality,
            function=function,
            FS_Value=fs_value,
            group_id=group_id,
            gssn_company=gssn_company,
            status=status,
            note=note
        )

