import os
import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import messagebox
from PIL import Image, ImageTk
from core.car_service import CarModelService

class ChangeCarModelScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- overall styling ---
        self.configure(fg_color="#A9A9A9")
        self.grid_rowconfigure((0,1,2,3), weight=1)   
        self.grid_columnconfigure(0, weight=1)

        # === Home Button ===
        home_icon_path = os.path.join("assets", "home-icon.png")  
        try:
            home_img = Image.open(home_icon_path).resize((25, 25))
            self.home_icon = CTkImage(light_image=home_img, dark_image=home_img, size=(25, 25))

            home_button = ctk.CTkButton(self, image=self.home_icon, text="", width=30, height=30,
                                        fg_color="transparent", hover_color="#888888", command=lambda: controller.show_frame("StartScreen"))
            home_button.place(x=10, y=10)
        except Exception as e:
            print("Home icon load error:", e)

        # === Backpage ===
        arrow_icon_path = os.path.join("assets", "back-arrow.png")  
        try:
            arrow_img = Image.open(arrow_icon_path).resize((25, 25))
            self.arrow_icon = CTkImage(light_image=arrow_img, dark_image=arrow_img, size=(25, 25))

            backpage_button = ctk.CTkButton(self, image=self.arrow_icon, text="", width=30, height=30,
                                        fg_color="transparent", hover_color="#888888", command=lambda: controller.show_frame("UpdateEntriesScreen"))
            backpage_button.place(x=60, y=10)
        except Exception as e:
            print("Home icon load error:", e)

        # --- Title ---
        title = ctk.CTkLabel(
            self,
            text="Auto-Modelle verwalten",
            font=("Arial", 24, "bold")
        )
        title.grid(row=0, column=0, pady=(60, 10), sticky="n")

        # === Add Model Section ===
        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.grid(row=1, column=0, pady=10, padx=40, sticky="nsew")
        add_frame.grid_columnconfigure((0,1,2), weight=1)

        ctk.CTkLabel(
            add_frame,
            text="Neues Modell hinzufügen",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, pady=(0,10))

        # 1) Car Type dropdown
        self.add_type_var = ctk.StringVar(value="Typ wählen")
        self.add_type_menu = ctk.CTkOptionMenu(
            add_frame,
            variable=self.add_type_var,
            values=[],
            fg_color="#1a1a1a",
            button_color="#1a1a1a",
            text_color="white",
            dropdown_text_color="white",
            command=self._on_add_type_selected
        )
        self.add_type_menu.grid(row=1, column=0, padx=5, sticky="ew")

        # 2) Model name entry
        self.add_model_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="Modell-Name eingeben"
        )
        self.add_model_entry.grid(row=1, column=1, padx=5, sticky="ew")

        # 3) Add button
        ctk.CTkButton(
            add_frame,
            text="Hinzufügen",
            fg_color="#1a1a1a",
            text_color="white",
            corner_radius=8,
            command=self._on_add_model
        ).grid(row=1, column=2, padx=5, sticky="ew")

        # === Remove Model Section ===
        rem_frame = ctk.CTkFrame(self, fg_color="transparent")
        rem_frame.grid(row=2, column=0, pady=10, padx=40, sticky="nsew")
        rem_frame.grid_columnconfigure((0,1,2), weight=1)

        ctk.CTkLabel(
            rem_frame,
            text="Modell entfernen",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, pady=(0,10))

        # 1) Car Type dropdown (for removal)
        self.rem_type_var = ctk.StringVar(value="Typ wählen")
        self.rem_type_menu = ctk.CTkOptionMenu(
            rem_frame,
            variable=self.rem_type_var,
            values=[],
            fg_color="#1a1a1a",
            button_color="#1a1a1a",
            text_color="white",
            dropdown_text_color="white",
            command=self._on_rem_type_selected
        )
        self.rem_type_menu.grid(row=1, column=0, padx=5, sticky="ew")

        # 2) Model dropdown
        self.rem_model_var = ctk.StringVar(value="Modell wählen")
        self.rem_model_menu = ctk.CTkOptionMenu(
            rem_frame,
            variable=self.rem_model_var,
            values=[],
            fg_color="#1a1a1a",
            button_color="#1a1a1a",
            text_color="white",
            dropdown_text_color="white"
        )
        self.rem_model_menu.grid(row=1, column=1, padx=5, sticky="ew")

        # 3) Remove button
        ctk.CTkButton(
            rem_frame,
            text="Entfernen",
            fg_color="#1a1a1a",
            text_color="white",
            corner_radius=8,
            command=self._on_remove_model
        ).grid(row=1, column=2, padx=5, sticky="ew")

        # --- load initial dropdown values ---
        self._load_all_types()

    def _load_all_types(self):
        types = CarModelService.get_all_types()
        self.add_type_menu.configure(values=types)
        self.rem_type_menu.configure(values=types)

    def _on_add_type_selected(self, t: str):
        # nothing else to do here for add
        pass

    def _on_rem_type_selected(self, t: str):
        # populate second dropdown with models of this type
        models = CarModelService.get_models_by_type(t)
        self.rem_model_menu.configure(values=models)
        # reset selection
        self.rem_model_var.set("Modell wählen")

    def _on_add_model(self):
        t = self.add_type_var.get()
        name = self.add_model_entry.get().strip()
        if t == "Typ wählen" or not name:
            messagebox.showinfo("Fehler", f"Bitte Typ und Namen angeben", icon="error")
            return
        CarModelService.add_model(t, name)
        self.add_model_entry.delete(0,"end")
        messagebox.showinfo("Erfolg", f"{name} wurde hinzugefügt.")
        # refresh
        self._load_all_types()

    def _on_remove_model(self):
        model = self.rem_model_var.get()
        if model == "Modell wählen":
            messagebox.showinfo("Fehler", f"Bitte Typ und Modell auswählen", icon="error")
            return
        CarModelService.delete_model(model)
        messagebox.showinfo("Erfolg", f"Fahrzeug-Modell wurde entfernt.")
        # refresh models list
        self._on_rem_type_selected(self.rem_type_var.get())
