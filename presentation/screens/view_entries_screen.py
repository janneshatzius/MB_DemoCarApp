# presentation/screens/view_entries_screen.py
import os
import tkinter as tk
import customtkinter as ctk
import pandas as pd
from customtkinter import CTkImage
from PIL import Image
from tkinter import Canvas
from core.load_recommendations_service import RecommendationService

class ViewEntriesScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        # === Home button ===
        home_icon_path = os.path.join("assets", "home-icon.png")
        try:
            print("Loading home icon from", home_icon_path)
            home_img = Image.open(home_icon_path).resize((25,25))
            self.home_icon = CTkImage(light_image=home_img, dark_image=home_img, size=(25,25))
            home_btn = ctk.CTkButton(
            self,
            image=self.home_icon,
            text="",
            fg_color="transparent",
            hover_color="#888888",
            width=40, height=40, # give it some room
            command=lambda: controller.show_frame("StartScreen")
        )
            home_btn.place(x=10, y=10)

            home_btn.lift()      # bring it to front
        except Exception as e:
            print("🚨 Home icon load error:", e)

    

        # === Two-column layout: left=table, right=detail form ===
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # — Left: search + scrollable table —
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Search bar
        search_frame = ctk.CTkFrame(left, fg_color="transparent")
        search_frame.pack(pady=10)
        self.search_entry = ctk.CTkEntry(search_frame,
                                         placeholder_text="Suche nach GSSN, Name, Ort oder Modell…",
                                         width=300)
        self.search_entry.pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Suchen", command=self.perform_search).pack(side="left")

        # Scrollable table
        self.canvas = Canvas(left, bg="#A9A9A9", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(left, orientation="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="#D3D3D3")
        self.canvas.create_window((0,0), window=self.scrollable_frame, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # — Right: detail-edit pane —
        self.detail = ctk.CTkFrame(self, fg_color="#D3D3D3", width=200)
        self.detail.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self._build_detail_form()

        # === Load all recommendations once ===
        self._all_recs = RecommendationService.list_all_recommendations()  # pandas.DataFrame
        self._selected_rec = None

        # Show only the first 5 by default
        self._current_df = self._all_recs.head(5)
        self.populate_table(self._current_df)

        home_btn.lift()

    def _build_detail_form(self):
        # — Title —
        self.detail_title = ctk.CTkLabel(
            self.detail, text="Bearbeite Empfehlung", font=("Arial", 16, "bold")
        )
        self.detail_title.pack(pady=(0,20))

        # — Car type (readonly) —
        self.lbl_type = ctk.CTkLabel(self.detail, text="Typ: —", font=("Arial", 14))
        self.lbl_type.pack(anchor="w", padx=10, pady=5)

        # — Car model dropdown —
        ctk.CTkLabel(self.detail, text="Modell:").pack(anchor="w", padx=10, pady=(10,0))
        self.var_model = ctk.StringVar(value="")
        self.dd_model = ctk.CTkOptionMenu(self.detail,
                                          variable=self.var_model,
                                          values=[])
        self.dd_model.pack(fill="x", padx=10, pady=5)

        # Note label + entry
        ctk.CTkLabel(self.detail, text="Notiz:").pack(anchor="w", padx=10, pady=(10,0))
        self.txt_note = ctk.CTkEntry(self.detail, placeholder_text="Hier Notiz eingeben…")
        self.txt_note.pack(fill="x", padx=10, pady=(0,10))

    # Save button
        self.btn_save = ctk.CTkButton(self.detail, text="Speichern", command=self._on_save)
        self.btn_save.pack(pady=20)

    def populate_table(self, df: pd.DataFrame):
        # clear old widgets
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        if df.empty:
            ctk.CTkLabel(self.scrollable_frame, text="Keine Einträge gefunden.", font=("Arial", 14)).pack(pady=20)
            return

        # header row
        for col_idx, col in enumerate(df.columns):
            ctk.CTkLabel(self.scrollable_frame, text=col, font=("Arial", 12, "bold"))\
               .grid(row=0, column=col_idx, padx=5, pady=5)

        # data rows (use to_dict so we get dicts, not namedtuples)
        for row_idx, rec in enumerate(df.to_dict("records"), start=1):
            for col_idx, col in enumerate(df.columns):
                lbl = ctk.CTkLabel(self.scrollable_frame, text=str(rec[col]))
                lbl.grid(row=row_idx, column=col_idx, padx=5, pady=2)
                # bind click on entire row
                lbl.bind("<Button-1>", lambda e, rec=rec: self._on_select(rec))


    def perform_search(self):
        raw = self.search_entry.get().strip().lower()
        if not raw:
            # back to first 5
            df = self._all_recs.head(5)
        else:
            # exact‐match, comma‐separated
            terms = [t.strip() for t in raw.split(",") if t.strip()]
            mask = pd.Series(True, index=self._all_recs.index)
            for term in terms:
                m = (
                    self._all_recs['gssn_id'].str.lower().eq(term) |
                    self._all_recs['dealership_name'].str.lower().eq(term) |
                    self._all_recs['locality'].str.lower().eq(term) |
                    self._all_recs['car_model_name'].str.lower().eq(term)
                )
                mask &= m
            df = self._all_recs[mask]
        self._current_df = df
        self.populate_table(df)



    def _on_select(self, rec: dict):
        self._selected_rec = rec

        # Show the car‐type in the detail pane (if you still want to display it):
        car_type = rec["car_type"]
        self.lbl_type.configure(text=f"Typ: {car_type}")

        models = RecommendationService.list_models_for_type(car_type)
        self.dd_model.configure(values=[m["name"] for m in models])
        self.var_model.set(rec["car_model_name"])

        self.txt_note.delete(0, tk.END)
        note_text = rec.get("note") or ""
        self.txt_note.insert(0, note_text)

    def _on_save(self):
        rec = self._selected_rec
        if not rec:
            return

        rec_id      = rec["recommendation_id"]
        chosen_name = self.var_model.get()
        note        = self.txt_note.get().strip()

        models      = RecommendationService.list_models_for_type(self._selected_rec["car_type"])
        model_id    = next(m["id"] for m in models if m["name"] == chosen_name)

        RecommendationService.save_changes(rec_id, model_id, chosen_name, note)
        

# update in-memory & refresh top-5…
        # --- PATCH our DataFrame ---
    # find the row index
        idx = self._all_recs.index[self._all_recs['recommendation_id'] == rec_id][0]
    # update the in-memory record
        self._all_recs.at[idx, 'car_model_name']       = chosen_name
        self._all_recs.at[idx, 'note']                 = note
        self._all_recs.at[idx, 'recommendation_source']= RecommendationService.MANUAL_SOURCE

    # re-draw
        self.perform_search()
    
    def reload_data(self):
        # 1) re-fetch everything
        self._all_recs = RecommendationService.list_all_recommendations()
        # 2) re-apply your current filter (if you’ve stored it) or show top-5
        #    for now we’ll just push first 5 back into the table
        self.populate_table(self._all_recs.head(5))
