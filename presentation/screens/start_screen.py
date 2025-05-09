import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import messagebox, simpledialog
from datetime import datetime
from PIL import Image
import traceback
import os
from core.recommendation_service import RecommendationService


class StartScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        # Grid layout for main container
        self.grid_rowconfigure((0, 2), weight=1)  
        self.grid_rowconfigure(1, weight=0)       
        self.grid_columnconfigure(0, weight=1)

        # Mercedes-Benz Logo
        logo_path = os.path.join("assets", "Mercedes-Benz-Logo.png")
        try:
            image = Image.open(logo_path).resize((100, 100))
            self.logo_img = CTkImage(light_image=image, dark_image=image, size=(100, 100))
            logo_label = ctk.CTkLabel(self, image=self.logo_img, text="")
            logo_label.place(x=15, y=15)  
        except Exception as e:
            print("Logo load error:", e)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0)
        button_frame.grid_rowconfigure((0, 1, 2), pad=20)
        button_frame.grid_columnconfigure(0, weight=1)

        button_style = {
            "width": 400,
            "height": 50,
            "corner_radius": 25,
            "fg_color": "#1a1a1a",
            "text_color": "white",
            "font": ("Arial", 16, "bold")
        }

        buttons = [
            ("Datenbankeinträge einsehen", lambda: controller.show_frame("ViewEntriesScreen")),
            ("Datenbankeinträge erneuern", lambda: controller.show_frame("UpdateEntriesScreen")),
            ("Jahresplanung erstellen",      self._on_create_recommendations),
        ]

        for i, (text, command) in enumerate(buttons):
            ctk.CTkButton(button_frame, text=text, command=command, **button_style).grid(row=i, column=0, pady=10)

    def not_implemented(self):
        print("Not yet implemented.")
    
    def _on_create_recommendations(self):
        default = datetime.now().year + 1
        year = simpledialog.askinteger(
            "Jahresplanung",
            "Für welches Jahr möchten Sie die Planung erstellen?",
            initialvalue=default,
            minvalue=2000, maxvalue=2100,
            parent=self
        )
        if not year:
            return

        try:
            count = RecommendationService.generate_recommendations_for_year(year)
            messagebox.showinfo(
                "Erfolg",
                f"{count} Empfehlungen für {year} erstellt.",
                parent=self
            )
        except Exception as e:
            print("[ERROR]", e)
            messagebox.showerror("Fehler", str(e), parent=self)

