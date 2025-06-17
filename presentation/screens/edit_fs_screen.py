import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image

from core.parking_service import ParkingService
from config import ICON_HOME, ICON_BACKPAGE


class EditFSScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#A9A9A9")

        # Home + Back buttons 
        for name, x, target in (("Home", 10, "StartScreen"),
                               ("Back", 50, "UpdateEntriesScreen")):
            img = ICON_HOME if name=="Home" else ICON_BACKPAGE
            btn = ctk.CTkButton(
                self,
                image=ctk.CTkImage(light_image=Image.open(img),
                                   dark_image=Image.open(img),
                                   size=(25,25)),
                text="",
                width=30, height=30,
                fg_color="transparent",
                hover_color="#888888",
                command=lambda t=target: controller.show_frame(t)
            )
            btn.place(x=x, y=10)

        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True)

        
        panel_width = 400  
        panel_height = 500
        edit_panel = ctk.CTkFrame(container, fg_color="#D3D3D3", width=panel_width, height=panel_height)
        add_panel  = ctk.CTkFrame(container, fg_color="#D3D3D3", width=panel_width, height=panel_height)
        edit_panel.pack_propagate(False)
        add_panel.pack_propagate(False)
        edit_panel.pack(side="left", padx=20, pady=30)
        add_panel.pack( side="left", padx=20, pady=30)


        ctk.CTkLabel(edit_panel, text="FS-Kategorie bearbeiten",
                     font=("Arial", 16, "bold")).pack(pady=(10,10))

        
        self.fs_var = tk.StringVar()
        self.fs_menu = ctk.CTkOptionMenu(edit_panel,
                                         variable=self.fs_var,
                                         values=[],
                                         command=self._on_fs_selected)
        ctk.CTkLabel(edit_panel, text="FS-Kategorie wählen:").pack(anchor="w", padx=10)
        self.fs_menu.pack(fill="x", padx=10, pady=(0,10))

        
        self.parking_cats = ParkingService.list_parking_categories()
        self.qty_vars     = {}
        vcmd = (self.register(self._validate_int), '%P')
        for cat in self.parking_cats:
            row = ctk.CTkFrame(edit_panel, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row, text=cat["category_name"], width=120, anchor="w")\
               .pack(side="left")
            var = tk.StringVar(value=0)
            self.qty_vars[cat["parkingcategory_id"]] = var
            ctk.CTkEntry(row, width=50, textvariable=var, validate='key', validatecommand=vcmd)\
               .pack(side="right")

        
        ctk.CTkLabel(edit_panel, text="").pack(pady=(0, 10), expand=True)

    
        ctk.CTkButton(edit_panel, text="Speichern", command=self._on_save, width=180, height=30, font=("Arial", 14))\
           .pack(pady=(0,20), side="bottom")

        
        ctk.CTkLabel(add_panel, text="Neue FS-Kategorie hinzufügen",
                     font=("Arial", 16, "bold")).pack(pady=(10,10))

        
        self.new_fs_var = tk.StringVar()
        ctk.CTkEntry(add_panel,
                     placeholder_text="z.B. V7",
                     textvariable=self.new_fs_var)\
           .pack(fill="x", padx=10, pady=(0,10))

        
        self.new_qty_vars = {}
        vcmd_new = (self.register(self._validate_int), '%P')
        for cat in self.parking_cats:
            row = ctk.CTkFrame(add_panel, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row, text=cat["category_name"], width=120, anchor="w")\
               .pack(side="left")
            var = tk.StringVar(value=0)
            self.new_qty_vars[cat["parkingcategory_id"]] = var
            ctk.CTkEntry(row, width=50, textvariable=var, validate='key', validatecommand=vcmd_new)\
               .pack(side="right")

        
        ctk.CTkLabel(add_panel, text="").pack(pady=(0, 10), expand=True)

    
        ctk.CTkButton(add_panel, text="Hinzufügen", command=self._on_add_fs, width=180, height=30, font=("Arial", 14))\
           .pack(pady=(0,20), side="bottom")

        
        self._reload_fs_menu()


    def _reload_fs_menu(self):
        choices = [r["fs_category"] for r in ParkingService.list_fs_categories()]
        self.fs_menu.configure(values=choices)
        if choices:
            self.fs_var.set(choices[0])
            self._on_fs_selected(choices[0])


    def _on_fs_selected(self, fs):
        allocs = ParkingService.list_allocation_for_fs(fs)
        amap = {cat:qty for cat, qty in allocs}

        for cat in self.parking_cats:
            vid = cat["parkingcategory_id"]
            self.qty_vars[vid].set(amap.get(vid, 0))


    def _on_save(self):
        fs = self.fs_var.get()
        entries = []
        for cat_id, var in self.qty_vars.items():
            raw = var.get().strip()
            qty = int(raw) if raw.isdigit() else 0
            entries.append((cat_id, qty))
        try:
            ParkingService.save_allocations(fs, entries)
            messagebox.showinfo("Erfolg", "Zuweisungen gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))


    def _on_add_fs(self):
        newfs = self.new_fs_var.get().strip().upper()
        if not newfs:
            return

    
        try:
            ParkingService.add_fs_category(newfs)
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
            return

        
        entries = []
        for cat_id, var in self.new_qty_vars.items():
            raw = var.get().strip()
            qty = int(raw) if raw.isdigit() else 0
            entries.append((cat_id, qty))
        try:
            ParkingService.save_allocations(newfs, entries)
            messagebox.showinfo("Erfolg", f"{newfs} hinzugefügt.")
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", str(e))
            return

        
        self.new_fs_var.set("")
        for var in self.new_qty_vars.values():
            var.set(0)
        self._reload_fs_menu()


    def _validate_int(self, value):
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False