
import customtkinter as ctk
from config import APP_ICON_ICO, WINDOW_TITLE, DEFAULT_HEIGHT, DEFAULT_WIDTH


from presentation.screens.start_screen import StartScreen
from presentation.screens.recommendations_screen import RecommendationsScreen
from presentation.screens.update_entries_screen import UpdateEntriesScreen
from presentation.screens.change_car_model_screen import ChangeCarModelScreen
from presentation.screens.update_dealerships_screen import UpdateDealershipsScreen
from presentation.screens.add_dealership_screen import AddDealershipScreen
from presentation.screens.edit_fs_screen import EditFSScreen


from core.recommendations_service import RecommendationService



class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.iconbitmap(str(APP_ICON_ICO))
        

        self.title(WINDOW_TITLE)
        self.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
        


        self.recs_df = RecommendationService.list_all_recommendations()

       
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

       
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)


        self.current_screen = None

        self.frames = {}
        for Screen in (
            StartScreen,
            RecommendationsScreen,
            UpdateEntriesScreen,
            ChangeCarModelScreen,
            UpdateDealershipsScreen,
            AddDealershipScreen,
            EditFSScreen
            

            
        ):
            page_name = Screen.__name__
            frame = Screen(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

       
        self.show_frame("StartScreen")

        self.bind_all("<Control-f>", self.open_find)

    def show_frame(self, page_name: str):
        frame = self.frames.get(page_name)
        if not frame:
            print(f"[MainApp] no such page: {page_name}")
            return
        frame.tkraise()
        self.current_screen = frame

    def open_find(self, event=None):
        if hasattr(self.current_screen, "open_find_dialog"):
            self.current_screen.open_find_dialog()



if __name__ == "__main__":

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = MainApp()
    app.mainloop()