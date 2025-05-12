# presentation/screens/view_entries_screen.py
import os
import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
from tkinter import Canvas
from core.load_recommendations_service import RecommendationService

class ViewEntriesScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        # 1) two‐column layout: left=table, right=edit form
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # — left: search + table —
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        # (search bar as before…)
        search_frame = ctk.CTkFrame(left, fg_color="transparent")
        search_frame.pack(pady=10)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Suche nach Automodell…", width=300)
        self.search_entry.pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Suchen", command=self.perform_search).pack(side="left")
        # scrollable table
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

        # — right: detail/edit pane —
        self.detail = ctk.CTkFrame(self, fg_color="#D3D3D3", width=200)
        self.detail.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self._build_detail_form()

        # load once
        self._all_recs = controller.recs_df
        self._selected_rec = None

        # show top 5
        self.populate_table(df=self._all_recs.head(5))

    def populate_table(self, df):
        # clear
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        if df.empty:
            ctk.CTkLabel(self.scrollable_frame,
                         text="Keine Einträge gefunden.",
                         font=("Arial", 14)).pack(pady=20)
            return

        # header row
        for col_idx, col in enumerate(df.columns):
            ctk.CTkLabel(self.scrollable_frame,
                         text=col,
                         font=("Arial", 12, "bold")
            ).grid(row=0, column=col_idx, padx=10, pady=5)

        # data rows
        for row_idx, row in enumerate(df.itertuples(index=False), start=1):
            for col_idx, val in enumerate(row):
                ctk.CTkLabel(self.scrollable_frame,
                             text=str(val)
                ).grid(row=row_idx, column=col_idx, padx=10, pady=2)

    def perform_search(self):
        """
        Exact-match, comma-separated search on car_model_name.
        """
        raw = self.search_entry.get().strip()
        if not raw:
            # no filter → top 5
            df = self._all_recs.head(5)
        else:
            terms = [t.strip().lower() for t in raw.split(",") if t.strip()]
            # exact-match on car_model_name
            df = self._all_recs[
                self._all_recs['car_model_name']
                    .str.lower()
                    .isin(terms)
            ]
        self.populate_table(df=df)


    def _build_detail_form(self):
        # title
        self.detail_title = ctk.CTkLabel(self.detail, text="Bearbeite Empfehlung", font=("Arial", 16, "bold"))
        self.detail_title.pack(pady=(0,20))

        # car_type (readonly)
        self.lbl_type = ctk.CTkLabel(self.detail, text="Typ: —")
        self.lbl_type.pack(anchor="w", padx=10, pady=5)

        # car_model dropdown
        self.lbl_model = ctk.CTkLabel(self.detail, text="Modell:")
        self.lbl_model.pack(anchor="w", padx=10, pady=(10,0))
        self.var_model = ctk.StringVar(value="")
        self.dd_model = ctk.CTkOptionMenu(self.detail, variable=self.var_model, values=[])
        self.dd_model.pack(fill="x", padx=10)

        # note entry
        self.lbl_note = ctk.CTkLabel(self.detail, text="Notiz:")
        self.lbl_note.pack(anchor="w", padx=10, pady=(10,0))
        self.txt_note = ctk.CTkEntry(self.detail, placeholder_text="Hier Notiz eingeben…")
        self.txt_note.pack(fill="x", padx=10)

        # save button
        self.btn_save = ctk.CTkButton(self.detail, text="Speichern", command=self._on_save)
        self.btn_save.pack(pady=20)


    def _display_recs(self, df):
        # clear table
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        if df.empty:
            ctk.CTkLabel(self.scrollable_frame, text="Keine Einträge.", font=("Arial",14)).pack(pady=20)
            return

        # header
        for c, col in enumerate(df.columns):
            ctk.CTkLabel(self.scrollable_frame, text=col, font=("Arial",12,"bold"))\
               .grid(row=0, column=c, padx=5, pady=5)
        # rows
        for r, rec in enumerate(df.to_dict("records"), start=1):
            for c, col in enumerate(df.columns):
                lbl = ctk.CTkLabel(self.scrollable_frame, text=str(rec[col]))
                lbl.grid(row=r, column=c, padx=5, pady=2)
                # bind click on the first column (or entire row)
                lbl.bind("<Button-1>", lambda e, rec=rec: self._on_select(rec))


    def _on_select(self, rec: dict):
        """
        A recommendation was clicked → populate the detail form.
        """
        self._selected_rec = rec
        # show car_type
        car_type = rec["car_type"]
        self.lbl_type.configure(text=f"Typ: {car_type}")

        # load only models for that type
        models = RecommendationService.list_models_for_type(car_type)
        names  = [m["name"] for m in models]
        self.dd_model.configure(values=names)
        # default to current
        self.var_model.set(rec["car_model_name"])

        # note
        self.txt_note.delete(0, "end")
        self.txt_note.insert(0, rec.get("note","") or "")


    def _on_save(self):
        """
        Save the edited recommendation back to DB & in-memory.
        """
        if not self._selected_rec:
            return
        rec = self._selected_rec
        rec_id = rec["recommendation_id"]
        # find chosen model_id
        chosen_name = self.var_model.get()
        # we must map back name→id from the last list_models_for_type
        models = RecommendationService.list_models_for_type(rec["car_type"])
        model_id = next((m["id"] for m in models if m["name"]==chosen_name), None)
        note     = self.txt_note.get().strip()

        # persist
        RecommendationService.save_changes(rec_id, model_id, chosen_name, note)

        # update in‐memory
        rec["car_model"]      = model_id
        rec["car_model_name"] = chosen_name
        rec["note"]           = note
        rec["recommendation_source"] = RecommendationService.MANUAL_SOURCE

        # refresh table (we simply re‐display the same slice; in a full app
        # you’d want to remember current filter/page and re‐apply it)
        self._display_recs(self._all_recs.head(5))