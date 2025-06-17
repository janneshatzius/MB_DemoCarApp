import tkinter as tk
from tkinter import ttk
import pandas as pd
import customtkinter as ctk
from PIL import Image

from core.dealership_service import DealershipService
from config import ICON_HOME, ICON_BACKPAGE

class UpdateDealershipsScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)   
        self.grid_rowconfigure(1, weight=1)  


        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2,
                    sticky="ew", padx=10, pady=(10,0))
        header.grid_columnconfigure(0, weight=0)  
        header.grid_columnconfigure(1, weight=1) 
        header.grid_columnconfigure(2, weight=0)  

        #  Home button 
        home_img = ctk.CTkImage(
            light_image=Image.open(ICON_HOME),
            dark_image=Image.open(ICON_HOME),
            size=(25,25)
        )
        ctk.CTkButton(
            header, image=home_img, text="",
            fg_color="transparent", hover_color="#888888",
            width=40, height=40,
            command=lambda: controller.show_frame("StartScreen")
        ).grid(row=0, column=0, sticky="w")

         #  Backpage 
        back_img = ctk.CTkImage(
            light_image=Image.open(ICON_BACKPAGE),
            dark_image=Image.open(ICON_BACKPAGE),
            size=(25,25)
        )
        ctk.CTkButton(
            header, image=back_img, text="",
            fg_color="transparent", hover_color="#888888",
            width=40, height=40,
            command=lambda: controller.show_frame("UpdateEntriesScreen")
        ).grid(row=0, column=1, sticky="w")




        
        ctk.CTkButton(
            header,
            text="Agentenstandort hinzufügen",
            command=lambda: controller.show_frame("AddDealershipScreen")
        ).grid(row=0, column=2, sticky="e")

        
        table_frame = ctk.CTkFrame(self, fg_color="#D3D3D3")
        table_frame.grid(row=1, column=0, sticky="nsew",
                         padx=10, pady=10)

        
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
            "gssn_id":         "GSSN",
            "HB":              "HB",
            "VFNR":            "VFNR",
            "dealership_name": "Name",
            "locality":        "Ort",
            "FS_Value":        "FS Wert",
            "gssn_company":    "GSSN Company",
            "status":          "Status",
            "note":            "Notiz"
        }

        cols = ["index"] + list(self._col_map.keys())
        self.tree = ttk.Treeview(
            table_frame,              
            columns=cols,             
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )
        self.tree.tag_configure('match', background='#ffff99')


        self.tree.heading("index", text="#")
        self.tree.column(
            "index",
            width=40,
            minwidth=20,
            anchor="center",
            stretch=False
        )


        for data_key, pretty in self._col_map.items():
            self.tree.heading(data_key, text=pretty)
            self.tree.column(
                data_key,
                width=100,    
                minwidth=20,
                anchor="w",
                stretch=True
            )


        vsb = ctk.CTkScrollbar(
            table_frame, orientation="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

       
        self.detail = ctk.CTkFrame(self, fg_color="#D3D3D3", width=200)
        self.detail.grid(row=1, column=1, sticky="nsew",
                         padx=10, pady=10)
        self._build_detail_form()

        
        raw = DealershipService.list_all_dealerships()
        
        if isinstance(raw, pd.DataFrame):
            self._dealers = raw
        else:
            self._dealers = pd.DataFrame(raw or [])

        self._dealers['HB'] = self._dealers['HB'].round(0).astype(int)
        self.populate_tree(self._dealers)

        


    def _build_detail_form(self):
        ctk.CTkLabel(
            self.detail,
            text="Händler Details",
            font=("Arial", 16, "bold")
        ).pack(pady=(0,20))

        ctk.CTkLabel(self.detail, text="Status:").pack(
            anchor="w", padx=10, pady=(10,0)
        )
        self.var_status = tk.StringVar(value="active")
        self.opt_status = ctk.CTkOptionMenu(
            self.detail,
            variable=self.var_status,
            values=["active", "inactive"]
        )
        self.opt_status.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.detail, text="Notiz:").pack(
            anchor="w", padx=10, pady=(10,0)
        )
        self.txt_note = ctk.CTkEntry(
            self.detail,
            placeholder_text="Hier Notiz eingeben…"
        )
        self.txt_note.pack(fill="x", padx=10, pady=(0,10))

        ctk.CTkButton(
            self.detail,
            text="Speichern",
            command=self._on_save
        ).pack(pady=10)


    def populate_tree(self, df: pd.DataFrame):
    
        self.tree.delete(*self.tree.get_children())

    
        for i, (idx, row) in enumerate(df.iterrows(), start=1):
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

            
            self.tree.insert("", "end", iid=idx, values=cells)





    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        rec = self._dealers.loc[idx].to_dict()
        self._selected = rec

        # populate form
        self.var_status.set(rec.get("status", "active"))
        note = rec.get("note") or ""
        self.txt_note.delete(0, tk.END)
        self.txt_note.insert(0, note)


    def _on_save(self):
        rec = getattr(self, "_selected", None)
        if not rec:
            return

        dealer_id = rec["dealership_id"]
        status    = self.var_status.get()
        note      = self.txt_note.get().strip()

        
        DealershipService.update_dealership(dealer_id, status, note)

        
        df_idx = self._dealers.index[
            self._dealers["dealership_id"] == dealer_id
        ][0]
        self._dealers.at[df_idx, "status"] = status
        self._dealers.at[df_idx, "note"]   = note
        self.populate_tree(self._dealers)

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


