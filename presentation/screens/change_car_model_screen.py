import os
import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import messagebox
from PIL import Image, ImageTk
from core.car_service import CarModelService
from config import ICON_HOME, ICON_BACKPAGE

class ChangeCarModelScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        # — first build ALL of your widgets… — 

        # === Home icon ===
        try:
            home_img = ctk.CTkImage(light_image=Image.open(ICON_HOME), dark_image=Image.open(ICON_HOME),size=(25,25))

            home_button = ctk.CTkButton(self, image=home_img, text="", width=30, height=30,
                                        fg_color="transparent", hover_color="#888888", command=lambda: controller.show_frame("StartScreen"))
            home_button.place(x=10, y=10)
        except Exception as e:
            print("Home icon load error:", e)


            # === Backpage ===
        backpage_path = os.path.join("assets", "back-arrow.png")
        try:
            backpage_img = ctk.CTkImage(light_image=Image.open(ICON_BACKPAGE), dark_image=Image.open(ICON_BACKPAGE), size=(25,25))

            backpage_button = ctk.CTkButton(self, image=backpage_img, text="", width=30, height=30,
                                        fg_color="transparent", hover_color="#888888", command=lambda: controller.show_frame("UpdateEntriesScreen"))
            backpage_button.place(x=50, y=10)
        except Exception as e:
            print("Backpage icon load error:", e)

        # ADD MODEL section
        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.pack(pady=20)
        #add_frame.
        ctk.CTkLabel(add_frame, text="Neues Modell hinzufügen").pack()


        self.add_type_var = ctk.StringVar()
        self.add_type_menu = ctk.CTkOptionMenu(
            add_frame,
            variable=self.add_type_var,
            values=[],                    # empty for now
            command=self._on_add_type_selected
        )
        self.add_type_menu.pack(pady=5)

        self.add_model_entry = ctk.CTkEntry(add_frame, placeholder_text="Modellname")
        self.add_model_entry.pack(pady=5)


        ctk.CTkButton(add_frame, text="Hinzufügen", command=self._on_add_model).pack(pady=5)


        # REMOVE MODEL section
        rem_frame = ctk.CTkFrame(self, fg_color="transparent")
        rem_frame.pack(pady=20)
        ctk.CTkLabel(rem_frame, text="Modell entfernen").pack()

        self.rem_type_var = ctk.StringVar()
        self.rem_type_menu = ctk.CTkOptionMenu(
            rem_frame,
            variable=self.rem_type_var,
            values=[],                    # empty for now
            command=self._on_rem_type_selected
        )
        self.rem_type_menu.pack(pady=5)

        self.rem_model_var = ctk.StringVar()
        self.rem_model_menu = ctk.CTkOptionMenu(
            rem_frame,
            variable=self.rem_model_var,
            values=[]
        )
        self.rem_model_menu.pack(pady=5)

        ctk.CTkButton(rem_frame, text="Entfernen", command=self._on_remove_model).pack(pady=5)



        


        # — now that the OptionMenus exist, load your types once —
        self._all_types = CarModelService.get_all_types()

        # populate both dropdowns
        self.add_type_menu.configure(values=self._all_types)
        self.rem_type_menu.configure(values=self._all_types)

        # pick a sensible default
        if self._all_types:
            default = self._all_types[0]
            self.add_type_var.set(default)
            self.rem_type_var.set(default)
            # and load the remove‐side models
            self._on_rem_type_selected(default)


    def _on_add_type_selected(self, car_type_name):
        pass

    def _on_rem_type_selected(self, selected_type):
        models = CarModelService.get_models_for_type(selected_type)
        names  = [m["name"] for m in models]
        self.rem_model_menu.configure(values=names)
        if names:
            self.rem_model_var.set(names[0])
        else:
            self.rem_model_var.set("")

    def _on_add_model(self):
        t    = self.add_type_var.get()
        name = self.add_model_entry.get().strip()
        if name:
            CarModelService.add_model(type_name=t, model_name=name)
            self.add_model_entry.delete(0, "end")
            ctk.CTkLabel(
            self,
            text="Automodel erfolgreich entfernt",
            text_color="black",
            font=("Arial", 14)
            ).place(relx=0.5, rely=0.9, anchor="center")
            self._on_rem_type_selected(t)
            
            
            

    def _on_remove_model(self):
        t = self.rem_type_var.get()
        m = self.rem_model_var.get()
        if m:
            CarModelService.delete_model(model_name=m)
            ctk.CTkLabel(
            self,
            text="Automodel erfolgreich entfernt",
            text_color="black",
            font=("Arial", 14)
            ).place(relx=0.5, rely=0.9, anchor="center")
            self._on_rem_type_selected(t)
