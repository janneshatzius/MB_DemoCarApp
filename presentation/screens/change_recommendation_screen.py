import customtkinter as ctk
from PIL import Image
import os

from core.recommendation_service import RecommendationService
from core.car_service import CarModelService

class EditRecommendationScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        # ===== Home button =====
        home_icon_path = os.path.join("assets", "home-icon.png")
        try:
            home_img = Image.open(home_icon_path).resize((25, 25))
            self.home_icon = ctk.CTkImage(light_image=home_img, dark_image=home_img, size=(25, 25))
            ctk.CTkButton(
                self, image=self.home_icon, text="", width=30, height=30,
                fg_color="transparent", hover_color="#888888",
                command=lambda: controller.show_frame("StartScreen")
            ).place(x=10, y=10)
        except Exception as e:
            print("Home icon load error:", e)

        # === Backpage ===
        arrow_icon_path = os.path.join("assets", "back-arrow.png")  
        try:
            arrow_img = Image.open(arrow_icon_path).resize((25, 25))
            self.arrow_icon = ctk.CTkImage(light_image=arrow_img, dark_image=arrow_img, size=(25, 25))

            backpage_button = ctk.CTkButton(self, image=self.arrow_icon, text="", width=30, height=30,
                                        fg_color="transparent", hover_color="#888888", command=lambda: controller.show_frame("UpdateEntriesScreen"))
            backpage_button.place(x=60, y=10)
        except Exception as e:
            print("Home icon load error:", e)

        # ===== Page title =====
        ctk.CTkLabel(
            self, text="Jahresplanung bearbeiten / Notiz hinzufügen",
            font=("Arial", 20, "bold")
        ).pack(pady=(60, 20))

        # ===== Recommendation selector =====
        self.recs = RecommendationService.list_for_dealership(dealership_id=1)
        rec_options = [
            f"{r['recommendation_id']}: {r['car_model_name']} (Spot {r['parking_spot']})"
            for r in self.recs
        ]
        self.rec_var = ctk.StringVar()
        self.rec_menu = ctk.CTkOptionMenu(
            self, values=rec_options, variable=self.rec_var,
            command=self._on_rec_selected,
            width=400
        )
        self.rec_menu.pack(pady=10)

        # ===== Car model selector =====
        self.model_var = ctk.StringVar()
        self.model_menu = ctk.CTkOptionMenu(
            self, values=CarModelService.all_models(),
            variable=self.model_var,
            width=400
        )
        self.model_menu.pack(pady=10)

        # ===== Note entry =====
        self.note_entry = ctk.CTkEntry(self, placeholder_text="Notiz eingeben...", width=400)
        self.note_entry.pack(pady=10)

        # ===== Buttons =====
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Speichern", command=self._on_save, width=120).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="Abbrechen", command=lambda: controller.show_frame("UpdateEntriesScreen"), width=120).grid(row=0, column=1, padx=10)

    def _on_rec_selected(self, _=None):
        """ When a recommendation is chosen, prefill model + note. """
        sel = self.rec_var.get()
        if not sel:
            return
        rid = int(sel.split(":")[0])
        rec = next(r for r in self.recs if r["recommendation_id"] == rid)
        self.model_var.set(rec["car_model_name"])
        self.note_entry.delete(0, "end")
        self.note_entry.insert(0, rec.get("note") or "")

    def _on_save(self):
        try:
            rid = int(self.rec_var.get().split(":")[0])
            new_model = self.model_var.get()
            new_note  = self.note_entry.get().strip()
            RecommendationService.update(rid, new_model, new_note)
            print(f"[OK] Empfehlung {rid} aktualisiert → Modell={new_model}, Notiz={new_note!r}")
            self.controller.show_frame("UpdateEntriesScreen")
        except Exception as e:
            print("Fehler beim Speichern der Empfehlung:", e)
