import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import os
from core.parking_service import create_all_parking_spots

class UpdateEntriesScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        self.grid_rowconfigure((0, 2), weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # === Home icon ===
        home_icon_path = os.path.join("assets", "home-icon.png")  # <- provide this file
        try:
            home_img = Image.open(home_icon_path).resize((25, 25))
            self.home_icon = CTkImage(light_image=home_img, dark_image=home_img, size=(25, 25))

            home_button = ctk.CTkButton(self, image=self.home_icon, text="", width=30, height=30,
                                        fg_color="transparent", hover_color="#888888", command=lambda: controller.show_frame("StartScreen"))
            home_button.place(x=10, y=10)
        except Exception as e:
            print("Home icon load error:", e)

        # === Button group ===
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
            ("Agentenstandorte erneuern", self.not_implemented),
            ("Parkplätze erneuern", self._on_refresh_parking),
            ("Automodelle anpassen", lambda: controller.show_frame("ChangeCarModelScreen")),
            
        ]

        for i, (text, command) in enumerate(buttons):
            ctk.CTkButton(button_frame, text=text, command=command, **button_style).grid(row=i, column=0, pady=10)

    def not_implemented(self):
        print("Not implemented yet.")
# presentation/screens/update_entries_screen.py


    def _on_refresh_parking(self):
        create_all_parking_spots()
        ctk.CTkLabel(
            self,
            text="Parkplätze erfolgreich angelegt",
            text_color="green",
            font=("Arial", 14)
        ).place(relx=0.5, rely=0.9, anchor="center")

    