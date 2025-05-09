# presentation/screens/view_entries_screen.py
import os
import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
from tkinter import Canvas
from core.load_recommendations_service import RecommendationService

class ViewEntriesScreen(ctk.CTkFrame):

    def __init__(self, parent, controller, dealership_id=1):
        super().__init__(parent)
        self.controller     = controller
        self.dealership_id  = dealership_id
        self.configure(fg_color="#A9A9A9")

        # — Search + column chooser —
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(pady=20)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Suche (z.B. Citan Tourer, V-Klasse)…",
            width=300
        )
        self.search_entry.pack(side="left", padx=10)

        self.selected_column = ctk.StringVar(value="all")
        self.column_menu = ctk.CTkOptionMenu(
            search_frame,
            values=["all", "gssn_id", "car_model_name", "recommendation_source"],
            variable=self.selected_column
        )
        self.column_menu.pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Suchen",
            command=self.perform_search
        ).pack(side="left")


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

        # — Scrollable results —
        self.canvas    = Canvas(self, bg="#A9A9A9", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(
            self, orientation="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="#D3D3D3")
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # — Initial load: *all* for dealership 1 —
        initial_df = RecommendationService.get_all(self.dealership_id)
        self.populate_table(initial_df)

    def populate_table(self, df):
        # clear old
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        if df is None or df.empty:
            ctk.CTkLabel(
                self.scrollable_frame,
                text="Keine Einträge gefunden.",
                font=("Arial", 14)
            ).pack(pady=20)
            return

        # headers
        for cidx, col in enumerate(df.columns):
            ctk.CTkLabel(
                self.scrollable_frame,
                text=col,
                font=("Arial", 12, "bold")
            ).grid(row=0, column=cidx, padx=10, pady=5)

        # rows
        for ridx, row in enumerate(df.itertuples(index=False), start=1):
            for cidx, val in enumerate(row):
                ctk.CTkLabel(
                    self.scrollable_frame,
                    text=str(val)
                ).grid(row=ridx, column=cidx, padx=10, pady=2)

    def perform_search(self):
        query  = self.search_entry.get()
        column = self.selected_column.get()
        df = RecommendationService.search_exact(
            raw_query       = query,
            dealership_id   = self.dealership_id,
            column          = column
        )
        self.populate_table(df)
