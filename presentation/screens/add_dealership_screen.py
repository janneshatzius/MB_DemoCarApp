# presentation/screens/add_dealership_screen.py

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image

from core.dealership_service import DealershipService
from config import ICON_HOME, ICON_BACKPAGE


class AddDealershipScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=10, padx=10)
        
        
        
        header.pack_propagate(False)
        header.configure(height=40)
        # home
        home_img = ctk.CTkImage(
            Image.open(ICON_HOME), Image.open(ICON_HOME), size=(25,25)
        )
        ctk.CTkButton(
            header, image=home_img, text="",
            fg_color="transparent", hover_color="#888888",
            width=30, height=30,
            command=lambda: controller.show_frame("StartScreen")
        ).pack(side="left")
        # back
        back_img = ctk.CTkImage(
            Image.open(ICON_BACKPAGE), Image.open(ICON_BACKPAGE), size=(25,25)
        )
        ctk.CTkButton(
            header, image=back_img, text="",
            fg_color="transparent", hover_color="#888888",
            width=30, height=30,
            command=lambda: controller.show_frame("UpdateDealershipsScreen")
        ).pack(side="left")

        
        form = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        form.place(relx=0.5, rely=0.5, anchor="center")

        def labeled(widget, **grid_opts):
            """Helper to pack with uniform padding."""
            widget.grid(padx=10, pady=5, sticky="ew", **grid_opts)

        row = 0
        ctk.CTkLabel(form, text="Neuen Händler hinzufügen", font=("Arial", 18, "bold"))\
            .grid(row=row, column=0, columnspan=2, pady=(0,20))
        row += 1

        
        ctk.CTkLabel(form, text="GSSN ID:").grid(row=row, column=0, sticky="w")
        self.entry_gssn = ctk.CTkEntry(form)
        labeled(self.entry_gssn, row=row, column=1)
        row += 1

        
        ctk.CTkLabel(form, text="Name:").grid(row=row, column=0, sticky="w")
        self.entry_name = ctk.CTkEntry(form)
        labeled(self.entry_name, row=row, column=1)
        row += 1

        
        ctk.CTkLabel(form, text="HB:").grid(row=row, column=0, sticky="w")
        self.entry_hb = ctk.CTkEntry(form)
        labeled(self.entry_hb, row=row, column=1)
        row += 1

        
        ctk.CTkLabel(form, text="VFNR:").grid(row=row, column=0, sticky="w")
        self.entry_vfnr = ctk.CTkEntry(form)
        labeled(self.entry_vfnr, row=row, column=1)
        row += 1

        
        ctk.CTkLabel(form, text="Ortschaft:").grid(row=row, column=0, sticky="w")
        self.entry_locality = ctk.CTkEntry(form)
        labeled(self.entry_locality, row=row, column=1)
        row += 1

        
        ctk.CTkLabel(form, text="FS-Kategorie:").grid(row=row, column=0, sticky="w")
        fs_values = ["P2","P3","P4","P5","V2","V3","V4","V5"]
        self.var_fs = tk.StringVar(value=fs_values[0])
        self.opt_fs = ctk.CTkOptionMenu(form, variable=self.var_fs, values=fs_values)
        labeled(self.opt_fs, row=row, column=1)
        row += 1

        
        ctk.CTkLabel(form, text="Funktion:").grid(row=row, column=0, sticky="w")
        funcs = ["P","PT","V"]
        self.var_func = tk.StringVar(value=funcs[0])
        self.opt_func = ctk.CTkOptionMenu(form, variable=self.var_func, values=funcs)
        labeled(self.opt_func, row=row, column=1)
        row += 1

        
        ctk.CTkLabel(form, text="GSSN Company:").grid(row=row, column=0, sticky="w")
        self.entry_company = ctk.CTkEntry(form)
        labeled(self.entry_company, row=row, column=1)
        row += 1

       
        ctk.CTkButton(
            form, text="Speichern", command=self._on_save
        ).grid(row=row, column=0, columnspan=2, pady=(20,0))

    def _on_save(self):
        gssn    = self.entry_gssn.get().strip()
        name    = self.entry_name.get().strip()
        hb      = self.entry_hb.get().strip()
        vfnr    = self.entry_vfnr.get().strip()
        loc     = self.entry_locality.get().strip()
        fs_val  = self.var_fs.get()
        func    = self.var_func.get()
        company = self.entry_company.get().strip()

        
        if not all([gssn, name, hb, vfnr, loc, company]):
            messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen.")
            return

        
        group = DealershipService.get_group_by_company(company)
        if group:
            group_id = group["DG_ID"]
        else:
            
            vfnrhb = self._prompt_new_group(company)
            if not vfnrhb:
                return
            group_id = DealershipService.create_group(company, vfnrhb)["DG_ID"]

       
        try:
            DealershipService.create_dealership(
                gssn_id=gssn,
                name=name,
                HB=int(hb),
                VFNR=int(vfnr),
                locality=loc,
                fs_value=fs_val,
                function=func,
                group_id=group_id,
                gssn_company=company
            )
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", str(e))
            return
        
        upd = self.controller.frames["UpdateDealershipsScreen"]
        upd._dealers = DealershipService.list_all_dealerships()
        upd.populate_tree(upd._dealers)

        messagebox.showinfo("Erfolg", "Händler erfolgreich hinzugefügt.")
        
        
        

    def _prompt_new_group(self, company) -> str:
        popup = ctk.CTkToplevel(self)
        popup.title("Neue Händlergruppe")
        popup.geometry("300x150")
        ctk.CTkLabel(
            popup,
            text=f"Händlergruppe '{company}' existiert nicht.",
            font=("Arial", 12)
        ).pack(pady=(10,5))
        ctk.CTkLabel(popup, text="Bitte VFNRHB eingeben:").pack(pady=(5,0))
        var = tk.StringVar()
        entry = ctk.CTkEntry(popup, textvariable=var)
        entry.pack(pady=5, padx=20, fill="x")
        result = {}

        def on_ok():
            val = var.get().strip()
            if not val:
                messagebox.showerror("Fehler", "VFNRHB darf nicht leer sein.")
                return
            result["vfnrhb"] = val
            popup.destroy()

        ctk.CTkButton(popup, text="OK", command=on_ok).pack(pady=(10,0))
        popup.grab_set()
        popup.wait_window()
        return result.get("vfnrhb", "")


      
