import customtkinter as ctk
from PIL import Image
from config import ICON_HOME
from core.parking_service import ParkingService

class UpdateEntriesScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        self.grid_rowconfigure((0, 2), weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Home icon 
        try:
            home_img = ctk.CTkImage(light_image=Image.open(ICON_HOME), dark_image=Image.open(ICON_HOME),size=(25,25))

            home_button = ctk.CTkButton(self, image=home_img, text="", width=30, height=30,
                                        fg_color="transparent", hover_color="#888888", command=lambda: controller.show_frame("StartScreen"))
            home_button.place(x=10, y=10)
        except Exception as e:
            print("Home icon load error:", e)


        # Button group 
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0)
        button_frame.grid_rowconfigure((0, 1, 2, 3), pad=15)
        button_frame.grid_columnconfigure(0, weight=1)

        button_style = {
            "width": 250,
            "height": 40,
            "corner_radius": 20,
            "fg_color": "#1a1a1a",
            "text_color": "white",
            "font": ("Arial", 14)
        }

        buttons = [
            ("FS Zuweisung", lambda: controller.show_frame("EditFSScreen")),
            ("Agentenstandorte", lambda: controller.show_frame("UpdateDealershipsScreen")),
            ("Parkplätze erneuern", self._on_refresh_parking),
            ("Automodelle anpassen", lambda: controller.show_frame("ChangeCarModelScreen")),
            
        ]

        for i, (text, command) in enumerate(buttons):
            ctk.CTkButton(button_frame, text=text, command=command, **button_style).grid(row=i, column=0, pady=10)

    


    def _on_refresh_parking(self):
        ParkingService.create_all_parking_spots()
        ctk.CTkLabel(
            self,
            text="Parkplätze erfolgreich angelegt",
            text_color="green",
            font=("Arial", 14)
        ).place(relx=0.5, rely=0.9, anchor="center")

    