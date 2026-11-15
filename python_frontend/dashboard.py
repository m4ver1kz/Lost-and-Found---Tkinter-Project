"""
dashboard.py
-----------------------------------------------------------------------------
Dashboard View Component displaying system-wide lost and found metrics:
- Total reported items
- Active LOST items (awaiting owner)
- Successfully returned FOUND items
- Category distribution summary
All metrics are fetched live from GET /api/dashboard/stats.
-----------------------------------------------------------------------------
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
from api_client import ApiClient, ApiException


class DashboardView(ttk.Frame):
    """Modern, clean dashboard presenting key statistics."""

    def __init__(self, parent, api_client: ApiClient):
        super().__init__(parent)
        self.api_client = api_client
        self._build_ui()

    def _build_ui(self):
        # Configure layout padding
        self.configure(padding=24)

        # Header Title
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 20))

        title = ttk.Label(header_frame, text="System Dashboard", font=("Segoe UI", 18, "bold"))
        title.pack(side="left")

        self.refresh_btn = ttk.Button(header_frame, text="⟳ Refresh Statistics", command=self.load_statistics)
        self.refresh_btn.pack(side="right")

        # Connection status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(header_frame, textvariable=self.status_var, font=("Segoe UI", 9, "italic"))
        self.status_label.pack(side="right", padx=12)

        # Metrics Cards Container
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill="x", pady=(0, 24))

        # Card 1: Total Items
        self.total_var = tk.StringVar(value="--")
        self._create_metric_card(cards_frame, "Total Reported Items", self.total_var, "#2563EB", 0)

        # Card 2: Items Marked LOST
        self.lost_var = tk.StringVar(value="--")
        self._create_metric_card(cards_frame, "Currently LOST (Active)", self.lost_var, "#D97706", 1)

        # Card 3: Items Marked FOUND
        self.found_var = tk.StringVar(value="--")
        self._create_metric_card(cards_frame, "Returned to Owner (FOUND)", self.found_var, "#059669", 2)

        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.columnconfigure(2, weight=1)

        # Category Breakdown Section
        breakdown_frame = ttk.LabelFrame(self, text="  Category Distribution  ", padding=16)
        breakdown_frame.pack(fill="both", expand=True)

        columns = ("category", "count")
        self.cat_tree = ttk.Treeview(breakdown_frame, columns=columns, show="headings", height=8)
        self.cat_tree.heading("category", text="Item Category")
        self.cat_tree.heading("count", text="Total Items")
        self.cat_tree.column("category", width=350, anchor="w")
        self.cat_tree.column("count", width=120, anchor="center")

        tree_scroll = ttk.Scrollbar(breakdown_frame, orient="vertical", command=self.cat_tree.yview)
        self.cat_tree.configure(yscrollcommand=tree_scroll.set)

        self.cat_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

    def _create_metric_card(self, parent, title_text, var, color, col_index):
        """Creates a styled card container for a metric value."""
        card = tk.Frame(parent, bg="#F8FAFC", highlightbackground="#E2E8F0", highlightthickness=1, padx=16, pady=16)
        card.grid(row=0, column=col_index, padx=8, sticky="nsew")

        title_lbl = tk.Label(card, text=title_text, font=("Segoe UI", 10), fg="#64748B", bg="#F8FAFC")
        title_lbl.pack(anchor="w")

        value_lbl = tk.Label(card, textvariable=var, font=("Segoe UI", 26, "bold"), fg=color, bg="#F8FAFC")
        value_lbl.pack(anchor="w", pady=(8, 0))

    def load_statistics(self):
        """Fetches statistics from the backend asynchronously without freezing GUI."""
        self.refresh_btn.config(state="disabled")
        self.status_var.set("Fetching statistics...")

        def worker():
            try:
                stats = self.api_client.get_dashboard_stats()
                # Schedule UI update on main thread
                self.after(0, self._update_ui, stats, None)
            except ApiException as e:
                self.after(0, self._update_ui, None, str(e))
            except Exception as e:
                self.after(0, self._update_ui, None, f"Unexpected error: {str(e)}")

        threading.Thread(target=worker, daemon=True).start()

    def _update_ui(self, stats, error_message):
        self.refresh_btn.config(state="normal")
        if error_message:
            self.status_var.set("Failed to load")
            messagebox.showerror("Dashboard Error", f"Could not load statistics:\n{error_message}")
            return

        self.status_var.set("Updated just now")
        self.total_var.set(str(stats.get("totalItems", 0)))
        self.lost_var.set(str(stats.get("lostCount", 0)))
        self.found_var.set(str(stats.get("foundCount", 0)))

        # Refresh Category Tree
        for row in self.cat_tree.get_children():
            self.cat_tree.delete(row)

        category_counts = stats.get("categoryCounts", {})
        if category_counts:
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                self.cat_tree.insert("", "end", values=(cat, count))
        else:
            self.cat_tree.insert("", "end", values=("No items reported yet", 0))
