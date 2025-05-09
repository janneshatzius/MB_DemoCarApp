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

        # search bar
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(pady=20)
        self.search_entry = ctk.CTkEntry(search_frame,
                                         placeholder_text="Suche nach Automodell...",
                                         width=300)
        self.search_entry.pack(side="left", padx=10)
        search_button = ctk.CTkButton(search_frame,
                                      text="Suchen",
                                      command=self.perform_search)
        search_button.pack(side="left")

        # home button (as before)...
        # === Home icon ===
        home_icon_path = os.path.join("assets", "home-icon.png")  # <- provide this file
        try:
            home_img = Image.open(home_icon_path).resize((25, 25))
            self.home_icon = CTkImage(light_image=home_img, dark_image=home_img, size=(25, 25))

            home_button = ctk.CTkButton(self, image=self.home_icon, text="", width=30, height=30,
                                        fg_color="transparent", hover_color="#888888", command=lambda: controller.show_frame("StartScreen"))
            home_button.place(x=10, y=10)
        except Exception as e:
            print("Home icon load error:", e)
        # [snip]

        # scrolling canvas for table
        self.canvas = Canvas(self, bg="#A9A9A9", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical",
                                          command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="#D3D3D3")
        self.canvas.create_window((0, 0),
                                  window=self.scrollable_frame,
                                  anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        self.scrollbar.pack(side="right", fill="y")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # **IN‐MEMORY** master DataFrame:
        self._all_recs = controller.recs_df

        # **Initial** display: first 5 rows
        self.populate_table(self._all_recs.head(5))

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
        query = self.search_entry.get().strip()
        if not query:
            # empty → show top 5 again
            self.populate_table(self._all_recs.head(5))
            return

        # allow comma‐separated exact matches on car_model_name
        tokens = [t.strip() for t in query.split(",") if t.strip()]
        # filter in‐memory DF
        df = self._all_recs[
            self._all_recs['car_model_name'].isin(tokens)
        ]
        self.populate_table(df)