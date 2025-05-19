import tkinter as tk
from tkinter import ttk
import pandas as pd
import customtkinter as ctk
from PIL import Image

from core.recommendations_service import RecommendationService
from config import ICON_HOME

class RecommendationsScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        # === Home icon ===
        try:
            home_img = ctk.CTkImage(
                light_image=Image.open(ICON_HOME),
                dark_image=Image.open(ICON_HOME),
                size=(20, 20)
            )
            home_btn = ctk.CTkButton(
                self, image=home_img, text="",
                fg_color="transparent", hover_color="#888888",
                width=30, height=30,
                command=lambda: controller.show_frame("StartScreen")
            )
            home_btn.place(x=10, y=10)
        except Exception as e:
            print("Home icon load error:", e)

        # === Layout: 2 columns ===
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # — Left: search + styled Treeview —
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Search bar
        search_frame = ctk.CTkFrame(left, fg_color="transparent")
        search_frame.pack(fill="x", padx=(60,0), pady=(0,10))
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Suche nach GSSN, Name, Ort oder Modell…",
            width=300
        )
        self.search_entry.pack(side="left", padx=(0,10))
        ctk.CTkButton(
            search_frame, text="Suchen",
            command=self.perform_search
        ).pack(side="left")

        # Table container with CTk background
        table_frame = ctk.CTkFrame(left, fg_color="#D3D3D3")
        table_frame.pack(fill="both", expand=True)

        # === Style the Treeview ===
        style = ttk.Style()
        style.theme_use("default")
        # Main tree style: row background & text
        style.configure(
            "Custom.Treeview",
            background="#D3D3D3",
            fieldbackground="#D3D3D3",
            foreground="black",
            rowheight=24
        )
        # Header style: background & text
        style.configure(
            "Custom.Treeview.Heading",
            background="#A9A9A9",
            foreground="white",
            relief="flat"
        )
        # Selection colors
        style.map(
            "Custom.Treeview",
            background=[("selected", "#888888")],
            foreground=[("selected", "white")]
        )

        # Map real DataFrame keys to display names:
        self._col_map = {
            "gssn_id":               "GSSN",
            "dealership_name":       "Name",
            "locality":              "Ortschaft",
            "car_model_name":        "Auto Model",
            "parking_type":          "Parkplatz",
            "note":                  "Notiz",
            "recommendation_source": "Automatisch / Manuell"
        }

        # Use the real keys for the Treeview columns:
        cols = list(self._col_map.keys())
        self.tree = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )

        # Set each heading’s text from the col_map:
        for key in cols:
            self.tree.heading(key, text=self._col_map[key])
            self.tree.column(key, anchor="w", width=120, stretch=True)


        # Scrollbar
        vsb = ctk.CTkScrollbar(
            table_frame, orientation="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=vsb.set)

        # Layout
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # — Right: detail/edit pane —
        self.detail = ctk.CTkFrame(self, fg_color="#D3D3D3", width=200)
        self.detail.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self._build_detail_form()

        # === Load & show initial data ===
        self._all_recs   = RecommendationService.list_all_recommendations()

        self._all_recs_lower = self._all_recs.assign(
            gssn_id=self._all_recs['gssn_id'].str.lower(),
            dealership_name=self._all_recs['dealership_name'].str.lower(),
            locality=self._all_recs['locality'].str.lower(),
            car_model_name=self._all_recs['car_model_name'].str.lower()
        )
        self.populate_tree(self._all_recs)

        home_btn.lift()


    def _build_detail_form(self):
        # Title
        ctk.CTkLabel(
            self.detail, text="Bearbeite Empfehlung",
            font=("Arial", 16, "bold")
        ).pack(pady=(0,20))

        # GSSN
        self.lbl_gssn = ctk.CTkLabel(
            self.detail, text="GSSN: —", font=("Arial", 14)
        )
        self.lbl_gssn.pack(anchor="w", padx=10, pady=5)

        # Parking type
        self.lbl_type = ctk.CTkLabel(
            self.detail, text="Typ: —", font=("Arial", 14)
        )
        self.lbl_type.pack(anchor="w", padx=10, pady=5)

        # Model dropdown
        ctk.CTkLabel(self.detail, text="Modell:").pack(
            anchor="w", padx=10, pady=(10,0)
        )
        self.var_model = tk.StringVar(value="")
        self.dd_model = ctk.CTkOptionMenu(
            self.detail, variable=self.var_model, values=[]
        )
        self.dd_model.pack(fill="x", padx=10, pady=5)

        # Note entry
        ctk.CTkLabel(self.detail, text="Notiz:").pack(
            anchor="w", padx=10, pady=(10,0)
        )
        self.txt_note = ctk.CTkEntry(
            self.detail, placeholder_text="Hier Notiz eingeben…"
        )
        self.txt_note.pack(fill="x", padx=10, pady=(0,10))

        # Save button
        ctk.CTkButton(
            self.detail, text="Speichern", command=self._on_save
        ).pack(pady=20)


    def populate_tree(self, df: pd.DataFrame):
        # clear old rows
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        # insert new rows
        for idx, row in df.iterrows():
            values = [row[col] for col in self.tree["columns"]]
            self.tree.insert("", "end", iid=idx, values=values)


    def perform_search(self):
        raw = self.search_entry.get().strip()
    # empty → show everything
        if not raw:
            df = self._all_recs
        else:
        # split on commas, lowercase each term
            terms = [t.strip().lower() for t in raw.split(",") if t.strip()]
            if not terms:
                df = self._all_recs
            else:
            # start with no rows selected
                mask = pd.Series(False, index=self._all_recs.index)

            # for each term, OR together matches across all 4 cols
                for term in terms:
                    term_match = (
                    self._all_recs['gssn_id'].str.lower().eq(term) |
                    self._all_recs['dealership_name'].str.lower().str.contains(term, na=False) |
                    self._all_recs['locality'].str.lower().eq(term) |
                    self._all_recs['car_model_name'].str.lower().eq(term)
                )
                mask |= term_match

            # apply the union mask
            df = self._all_recs.loc[mask]

        # refresh your view
        self._current_df = df
        self.populate_tree(df)



    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        rec = self._all_recs.loc[idx].to_dict()
        self._selected_rec = rec

        # update detail pane
        self.lbl_gssn.configure(text=f"GSSN: {rec.get('gssn_id','—')}")
        self.lbl_type.configure(text=f"Typ: {rec.get('parking_type','—')}")

        models = RecommendationService.list_models_for_type(rec["parking_type"])
        self.dd_model.configure(values=[m["name"] for m in models])
        self.var_model.set(rec.get("car_model_name",""))

        self.txt_note.delete(0, tk.END)
        self.txt_note.insert(0, rec.get("note",""))


    def _on_save(self):
        rec = getattr(self, "_selected_rec", None)
        if not rec:
            return

        rec_id      = rec["recommendation_id"]
        chosen_name = self.var_model.get()
        note        = self.txt_note.get().strip()

        models      = RecommendationService.list_models_for_type(rec["parking_type"])
        model_id    = next(m["id"] for m in models if m["name"] == chosen_name)

        RecommendationService.save_changes(rec_id, model_id, chosen_name, note)

        # update in-memory DataFrame
        idx = self._all_recs.index[
            self._all_recs['recommendation_id'] == rec_id
        ][0]
        self._all_recs.at[idx, 'car_model_name']        = chosen_name
        self._all_recs.at[idx, 'note']                  = note
        self._all_recs.at[idx, 'recommendation_source']= RecommendationService.MANUAL_SOURCE

        # refresh the tree
        self.perform_search()

