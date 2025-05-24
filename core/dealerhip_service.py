from data.dbconnect import get_connection
from data.dealership_repository import (
    get_all_dealerships,
    update_dealership,
    insert_dealership,
    insert_dealership_group
                                        
                                        )

class DealershipService():

    @staticmethod
    def list_all_dealerships():
        return get_all_dealerships()

    @staticmethod
    def update_dealership(dealer_id: int, status: str, note: str):
        conn = get_connection()
        try:
            update_dealership(
                conn,
                dealer_id,
                status,
                note
            )
        except Exception as e:
            # print to terminal instead of messagebox
            print("[ERROR] updating dealership:", e)
        finally:
            conn.close()
         

