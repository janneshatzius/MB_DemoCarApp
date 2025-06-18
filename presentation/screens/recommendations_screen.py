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

        
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        
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

        
        table_frame = ctk.CTkFrame(left, fg_color="#D3D3D3")
        table_frame.pack(fill="both", expand=True)

        
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure(
            "Custom.Treeview",
            background="#D3D3D3",
            fieldbackground="#D3D3D3",
            foreground="black",
            rowheight=24
        )
        
        style.configure(
            "Custom.Treeview.Heading",
            background="#A9A9A9",
            foreground="white",
            relief="flat"
        )
        
        style.map(
            "Custom.Treeview",
            background=[("selected", "#888888")],
            foreground=[("selected", "white")]
        )

    
        
        self._col_map = {
            "gssn_company": "GC",
            "gssn_id":               "GSSN",
            "HB":                 "HB",
            "VFNR":               "VFNR",
            "dealership_name":       "Name",
            "locality":              "Ortschaft",
            "car_model_name":        "Auto Model",
            "parking_type":          "Parkplatz",
            "note":                  "Notiz",
            "first_allocation": "Erste Zuweisung",
            "second_allocation": "Zweite Zuweisung"
        }

        
        cols = ["index"] + list(self._col_map.keys())

        
        self.tree = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )

        
        self.tree.heading("index", text="#")
        self.tree.column(
            "index",
            width=40,
            minwidth=20,
            anchor="center",
            stretch=False
        )

        
        default_widths = {
            "gssn_id":         80,
            "dealership_name": 180,
            "locality":        100,
            "car_model_name":  120,
            "parking_type":    80,
            "note":            150,
            "first_allocation": 150,
            "second_allocation": 150,
            "recommendation_source": 120
        }
        for key in self._col_map:
            pretty = self._col_map[key]
            w = default_widths.get(key, 80)
            self.tree.heading(key, text=pretty)
            self.tree.column(
                key,
                width=w,
                minwidth=20,
                anchor="w",
                stretch=True
            )

        
        self._highlighted_iids = set()
        self.tree.tag_configure('match', background='#ffff99')

    
        vsb = ctk.CTkScrollbar(
            table_frame, orientation="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=vsb.set)

        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        
        self.detail = ctk.CTkFrame(self, fg_color="#D3D3D3", width=200)
        self.detail.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self._build_detail_form()

    
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
            self.detail, placeholder_text=""
        )
        self.txt_note.pack(fill="x", padx=10, pady=(0,10))

        # Erste Zuweisung entry
        ctk.CTkLabel(self.detail, text="Erste Zuweisung:").pack(
            anchor="w", padx=10, pady=(10,0)
        )
        self.txt_f_allocation = ctk.CTkEntry(
            self.detail, placeholder_text=""
        )
        self.txt_f_allocation.pack(fill="x", padx=10, pady=(0,10))

        # Zweite Zuweisung entry
        ctk.CTkLabel(self.detail, text="Zweite Zuweisung:").pack(
            anchor="w", padx=10, pady=(10,0)
        )
        self.txt_s_allocation = ctk.CTkEntry(
            self.detail, placeholder_text=""
        )
        self.txt_s_allocation.pack(fill="x", padx=10, pady=(0,10))

        # Save button
        ctk.CTkButton(
            self.detail, text="Speichern", command=self._on_save
        ).pack(pady=20)



    def populate_tree(self, df: pd.DataFrame):

        self._highlighted_iids = {
            iid for iid in self.tree.get_children()
            if 'match' in self.tree.item(iid, 'tags')
        }

        self.tree.delete(*self.tree.get_children())

    
        for i, (row_idx, row) in enumerate(df.iterrows(), start=1):
            cells = [i]
            for col in self.tree["columns"]:
                if col == "index":
                    continue

                v = row.get(col)
                if v is None:
                    v = ""
                elif isinstance(v, float) and v.is_integer():
                    v = int(v)
                cells.append(v)

                iid = str(row_idx)
            self.tree.insert("", "end", iid=iid, values=cells)

        
            if iid in self._highlighted_iids:
                self.tree.item(iid, tags=('match',))





    def perform_search(self):
        raw = self.search_entry.get().strip().lower()
    
        if not raw:
            df = self._all_recs
        else:
        
            terms = [t.strip() for t in raw.split(",") if t.strip()]
            if not terms:
                df = self._all_recs
            else:
            
                mask = pd.Series(True, index=self._all_recs.index)
            
                for term in terms:
                    term_match = (
                        self._all_recs['gssn_id'].str.lower().eq(term) |
                        self._all_recs['dealership_name']
                            .str.lower()
                            .str.contains(term, na=False) |
                        self._all_recs['locality'].str.lower().eq(term) |
                        self._all_recs['car_model_name'].str.lower().eq(term) |
                        self._all_recs["parking_type"].str.lower().eq(term)
                    )
            
                    mask &= term_match

                df = self._all_recs.loc[mask]

    
        self._current_df = df
        self.populate_tree(df)




    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        rec = self._all_recs.loc[idx].to_dict()
        self._selected_rec = rec

        
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
        f_allocation = self.txt_f_allocation.get().strip()
        s_allocation = self.txt_s_allocation.get().strip()

        models      = RecommendationService.list_models_for_type(rec["parking_type"])
        model_id    = next(m["id"] for m in models if m["name"] == chosen_name)

        RecommendationService.save_changes(rec_id, model_id, chosen_name, note, f_allocation, s_allocation)

        
        idx = self._all_recs.index[
            self._all_recs['recommendation_id'] == rec_id
        ][0]
        self._all_recs.at[idx, 'car_model_name']        = chosen_name
        self._all_recs.at[idx, 'note']                  = note
        self._all_recs.at[idx, 'recommendation_source'] = RecommendationService.MANUAL_SOURCE
        self._all_recs.at[idx, 'first_allocation'] = f_allocation
        self._all_recs.at[idx, 'second_allocation'] = s_allocation

        
        self.perform_search()

        self.txt_note.delete(0, tk.END)
        self.txt_f_allocation.delete(0, tk.END)
        self.txt_s_allocation.delete(0, tk.END)
    

    def open_find_dialog(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Suchen")
        dlg.geometry("320x150")
        dlg.grab_set()

       
        ctk.CTkLabel(dlg, text="Suchbegriff:").pack(pady=(10,0))
        var = tk.StringVar()
        entry = ctk.CTkEntry(dlg, textvariable=var)
        entry.pack(pady=5, padx=10, fill="x")
        entry.focus()

        
        def on_search(event=None):
            term = var.get().strip().lower()
            if not term:
                return
            matched = []
            for iid in self.tree.get_children():
                vals = [str(v).lower() for v in self.tree.item(iid, 'values')]
                if term in " ".join(vals):
                    self.tree.item(iid, tags=('match',))
                    matched.append(iid)
                else:
                    self.tree.item(iid, tags=())
            if matched:
                first = matched[0]
                self.tree.selection_set(first)
                self.tree.focus(first)
                self.tree.see(first)

       
        def on_clear(event=None):
            for iid in self.tree.get_children():
                self.tree.item(iid, tags=())
            self.tree.selection_remove(self.tree.selection())

        
        btn_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_frame.pack(pady=(10,0), padx=10, fill="x")

       
        ctk.CTkButton(
            btn_frame, text="Suchen", command=on_search
        ).pack(side="left", expand=True, fill="x", padx=(0,5))

        
        ctk.CTkButton(
            btn_frame, text="Markierungen löschen", command=on_clear
        ).pack(side="left", expand=True, fill="x", padx=(5,0))

       
        entry.bind("<Return>", on_search)


    def reload_data(self):
        
      
            self._all_recs = RecommendationService.list_all_recommendations()

   
            raw = self.search_entry.get().strip()
            if raw:
                self.perform_search()
            else:
            
                self.populate_tree(self._all_recs)
