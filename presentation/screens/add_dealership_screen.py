import tkinter as tk
from tkinter import ttk
import pandas as pd
import customtkinter as ctk
from PIL import Image

from core.dealerhip_service import DealershipService
from config import ICON_HOME, ICON_BACKPAGE

class AddDealershipScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")


        # === Top header with Home + "Add Agentenstandort" button ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(
            row=0, column=0, columnspan=2,
            sticky="ew",
            padx=10, pady=(10,0)
        )
        header.grid_columnconfigure(0, weight=0)
        header.grid_columnconfigure(1, weight=0)
        header.grid_columnconfigure(2, weight=1)
        header.grid_columnconfigure(3, weight=0)

        # Home button
        home_img = ctk.CTkImage(
            light_image=Image.open(ICON_HOME),
            dark_image=Image.open(ICON_HOME),
            size=(25,25)
        )
        home_btn = ctk.CTkButton(
            header, image=home_img, text="",
            fg_color="transparent", hover_color="#888888",
            width=40, height=40,
            command=lambda: controller.show_frame("StartScreen")
        )
        home_btn.grid(row=0, column=0, sticky="w")

        # Back button
        backpage_img = ctk.CTkImage(
            light_image=Image.open(ICON_BACKPAGE),
            dark_image=Image.open(ICON_BACKPAGE),
            size=(25,25)
        )
        backpage_btn = ctk.CTkButton(
            header, image=backpage_img, text="",
            fg_color="transparent", hover_color="#888888",
            width=40, height=40,
            command=lambda: controller.show_frame("UpdateDealershipScreen")
        )
        backpage_btn.grid(row=0, column=1, sticky="w", padx=(10,0))

        # Add-Agentenstandort button
        add_loc_btn = ctk.CTkButton(
            header,
            text="Agentenstandort hinzufügen",
            command=lambda: controller.show_frame("AddAgentenstandortScreen")
        )
        add_loc_btn.grid(row=0, column=3, sticky="e")

        # === Layout ===
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # — Left: dealer table —
        table_frame = ctk.CTkFrame(self, fg_color="#D3D3D3")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Style the Treeview to match CTk
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
            "gssn_id": "GSSN",
            "HB": "HB",
            "VFNR": "VFNR",
            "dealership_name": "Name",
            "locality": "Ort",
            "FS_Value": "FS Wert",
            "gssn_company": "GSSN Company",
            "status": "Status",
            "note": "Notiz"
        }
        cols = list(self._col_map.keys())

        self.tree = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )
       
        col_widths = {
            "dealership_id":   50,
            "dealership_name": 120,
            "locality":        100,
            "FS_Value":        60,
            "gssn_id":         80
        }
        for key in cols:
            pretty = self._col_map[key]
            w = col_widths.get(key, 80)   # default to 80 i
            self.tree.heading(key, text=pretty)
            self.tree.column(
                key,
                anchor="w",
                width=w,
                minwidth=20,   # don’t allow it to shrink below 20px
                stretch=True  # keep it fixed at `width`
            )

        vsb = ctk.CTkScrollbar(
            table_frame, orientation="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # — Right: dealership detail form (empty for now) —
        self.detail = ctk.CTkFrame(self, fg_color="#D3D3D3", width=200)
        self.detail.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self._build_detail_form()

        # — Button to go to the “Add Agentenstandort” screen —
        add_loc_btn = ctk.CTkButton(
            self,
            text="Agentenstandort hinzufügen",
            command=lambda: controller.show_frame("AddDealershipScreen")
        )
        add_loc_btn.grid(
            row=0, column=0, columnspan=2,
            sticky="e",   # align right, so it sits above the detail pane
            padx=10, pady=(20, 0)
        )

        # === Load & populate ===
        self._dealers = DealershipService.list_all_dealerships()
        self.populate_tree(self._dealers)

        home_btn.lift()


    def _build_detail_form(self):
        ctk.CTkLabel(
            self.detail,
            text="Händler Details",
            font=("Arial", 16, "bold")
        ).pack(pady=(0,20))

        # Status dropdown
        ctk.CTkLabel(self.detail, text="Status:").pack(anchor="w", padx=10, pady=(10,0))
        self.var_status = tk.StringVar(value="active")
        self.opt_status = ctk.CTkOptionMenu(
            self.detail,
            variable=self.var_status,
            values=["active", "inactive"]
        )
        self.opt_status.pack(fill="x", padx=10, pady=5)

        # Note entry
        ctk.CTkLabel(self.detail, text="Notiz:").pack(anchor="w", padx=10, pady=(10,0))
        self.txt_note = ctk.CTkEntry(self.detail, placeholder_text="Hier Notiz eingeben…")
        self.txt_note.pack(fill="x", padx=10, pady=(0,10))

        # Save button
        ctk.CTkButton(
            self.detail,
            text="Speichern",
            command=self._on_save
        ).pack(pady=10)


    def populate_tree(self, df: pd.DataFrame):
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        for idx, row in df.iterrows():
            values = [row.get(col, "") for col in self.tree["columns"]]
            self.tree.insert("", "end", iid=idx, values=values)


    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        rec = self._dealers.loc[idx].to_dict()
        self._selected = rec

        # populate status & note
        self.var_status.set(rec.get('status', 'active'))
        note_text = rec.get('note') or ""
        self.txt_note.delete(0, tk.END)
        self.txt_note.insert(0, note_text)


    def _on_save(self):
        rec = getattr(self, "_selected", None)
        if not rec:
            return

        dealer_id = rec["dealership_id"]
        status    = self.var_status.get()
        note      = self.txt_note.get().strip()

        # call your service to persist
        DealershipService.update_dealership(dealer_id, status, note)

        # update in-memory DF
        df_idx = self._dealers.index[self._dealers["dealership_id"] == dealer_id][0]
        self._dealers.at[df_idx, 'status'] = status
        self._dealers.at[df_idx, 'note']   = note

        # refresh table
        self.populate_tree(self._dealers)

