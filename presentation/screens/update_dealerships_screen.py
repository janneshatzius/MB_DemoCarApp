import tkinter as tk
from tkinter import ttk
import pandas as pd
import customtkinter as ctk
from PIL import Image

from core.dealerhip_service import DealershipService
from config import ICON_HOME

class UpdateDealershipsScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        # — Layout of this frame: 2 rows, 2 columns —
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)   # header row
        self.grid_rowconfigure(1, weight=1)   # content row

        # === row 0: header ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2,
                    sticky="ew", padx=10, pady=(10,0))
        header.grid_columnconfigure(0, weight=0)  # home
        header.grid_columnconfigure(1, weight=1)  # spacer
        header.grid_columnconfigure(2, weight=0)  # add-agent

        # -- Home button --
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

        # -- Add-Agentenstandort button --
        ctk.CTkButton(
            header,
            text="Agentenstandort hinzufügen",
            command=lambda: controller.show_frame("AddAgentenstandortScreen")
        ).grid(row=0, column=2, sticky="e")

        # === row 1: content ===

        # — Left: dealer table —
        table_frame = ctk.CTkFrame(self, fg_color="#D3D3D3")
        table_frame.grid(row=1, column=0, sticky="nsew",
                         padx=10, pady=10)

        # style the Treeview to match CTk
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

        # real→pretty column mapping
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
        cols = list(self._col_map.keys())

        # create the Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )
        # configure each column
        default_widths = {
            "dealership_id":   50,
            "gssn_id":         80,
            "dealership_name": 120,
            "locality":        100,
            "FS_Value":        60
        }
        for key in cols:
            pretty = self._col_map[key]
            w = default_widths.get(key, 80)
            self.tree.heading(key, text=pretty)
            self.tree.column(key,
                             width=w,
                             minwidth=20,
                             anchor="w",
                             stretch=True)

        vsb = ctk.CTkScrollbar(
            table_frame, orientation="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # — Right: detail form —
        self.detail = ctk.CTkFrame(self, fg_color="#D3D3D3", width=200)
        self.detail.grid(row=1, column=1, sticky="nsew",
                         padx=10, pady=10)
        self._build_detail_form()

        # === Load & populate ===
        raw = DealershipService.list_all_dealerships()
        # ensure DataFrame
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
    # clear existing rows
        for iid in self.tree.get_children():
            self.tree.delete(iid)

    # re-insert
        for idx, row in df.iterrows():
            values = []
            for col in self.tree["columns"]:
                v = row.get(col)
            # empty out None
                if v is None:
                    v = ""
            # also trim .0 from integer floats
                elif isinstance(v, float) and v.is_integer():
                    v = int(v)
                values.append(v)
            self.tree.insert("", "end", iid=idx, values=values)




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

        # persist
        DealershipService.update_dealership(dealer_id, status, note)

        # refresh in-memory & table
        df_idx = self._dealers.index[
            self._dealers["dealership_id"] == dealer_id
        ][0]
        self._dealers.at[df_idx, "status"] = status
        self._dealers.at[df_idx, "note"]   = note
        self.populate_tree(self._dealers)
