
import customtkinter as ctk

from presentation.screens.start_screen import StartScreen
from presentation.screens.view_entries_screen import ViewEntriesScreen
from presentation.screens.update_entries_screen import UpdateEntriesScreen
from presentation.screens.change_car_model_screen import ChangeCarModelScreen
from presentation.screens.change_recommendation_screen import EditRecommendationScreen

from core.load_recommendations_service import RecommendationService



class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- window setup ---
        self.title("Mercedes Benz Testfahrzeuge")
        self.geometry("1024x768")

        self.recs_df = RecommendationService.load_all_recommendations()

        # allow the root window to expand its one cell
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- container for all our screens ---
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew")

        # let container’s single cell grow
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # --- instantiate & grid all screens into the same cell ---
        self.frames = {}
        for Screen in (
            StartScreen,
            ViewEntriesScreen,
            UpdateEntriesScreen,
            ChangeCarModelScreen,
            EditRecommendationScreen
            
            
        ):
            page_name = Screen.__name__
            frame = Screen(parent=container, controller=self)
            self.frames[page_name] = frame

            # put each screen into row=0,col=0 of container
            # and stretch it in both directions
            frame.grid(row=0, column=0, sticky="nsew")

        # show the start screen first
        self.show_frame("StartScreen")

    def show_frame(self, page_name: str):
        frame = self.frames.get(page_name)
        if not frame:
            print(f"[MainApp] no such page: {page_name}")
            return
        frame.tkraise()


if __name__ == "__main__":
    # set theming before creating any CTk widgets
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = MainApp()
    app.mainloop()