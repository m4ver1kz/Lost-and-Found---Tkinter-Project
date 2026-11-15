"""
view_items.py
-----------------------------------------------------------------------------
View Items Component providing:
- Tabular display of all reported items in a ttk.Treeview
- Real-time / on-demand search by item name (/api/items/search?name=...)
- Multi-criteria filtering by category and status (/api/items?category=...&status=...)
- 'Mark as FOUND' workflow with confirmation dialog and database update
All operations interact exclusively with the Java REST backend.
-----------------------------------------------------------------------------
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
from api_client import ApiClient, ApiException
from report_item import CATEGORIES


class ViewItemsView(ttk.Frame):
    """Component to search, filter, display items and update status to FOUND."""

    def __init__(self, parent, api_client: ApiClient, on_status_updated=None):
        super().__init__(parent)
        self.api_client = api_client
        self.on_status_updated = on_status_updated
        self._build_ui()

    def _build_ui(self):
        self.configure(padding=20)

        # Header Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 14))

        title = ttk.Label(title_frame, text="View & Manage Items", font=("Segoe UI", 18, "bold"))
        title.pack(side="left")

        # Action Buttons on Top Right
        top_btn_frame = ttk.Frame(title_frame)
        top_btn_frame.pack(side="right")

        self.mark_found_btn = ttk.Button(
            top_btn_frame,
            text="✓ Mark Selected as FOUND",
            command=self.mark_selected_as_found
        )
        self.mark_found_btn.pack(side="left", padx=6)

        self.refresh_btn = ttk.Button(top_btn_frame, text="⟳ Refresh", command=self.load_items)
        self.refresh_btn.pack(side="left")

        # Search and Filter Toolbar
        filter_box = ttk.LabelFrame(self, text="  Search & Filter Items  ", padding=12)
        filter_box.pack(fill="x", pady=(0, 14))

        # 1. Search by name
        ttk.Label(filter_box, text="Search Name:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.search_entry = ttk.Entry(filter_box, width=22)
        self.search_entry.grid(row=0, column=1, padx=(0, 12))
        self.search_entry.bind("<Return>", lambda event: self.apply_search())

        self.search_btn = ttk.Button(filter_box, text="Search", command=self.apply_search)
        self.search_btn.grid(row=0, column=2, padx=(0, 16))

        # 2. Category Dropdown
        ttk.Label(filter_box, text="Category:", font=("Segoe UI", 9, "bold")).grid(row=0, column=3, sticky="w", padx=(0, 4))
        cat_options = ["All Categories"] + CATEGORIES
        self.category_var = tk.StringVar(value="All Categories")
        self.category_combo = ttk.Combobox(filter_box, textvariable=self.category_var, values=cat_options, state="readonly", width=18)
        self.category_combo.grid(row=0, column=4, padx=(0, 16))
        self.category_combo.bind("<<ComboboxSelected>>", lambda event: self.apply_filters())

        # 3. Status Dropdown
        ttk.Label(filter_box, text="Status:", font=("Segoe UI", 9, "bold")).grid(row=0, column=5, sticky="w", padx=(0, 4))
        status_options = ["ALL", "LOST", "FOUND"]
        self.status_var = tk.StringVar(value="ALL")
        self.status_combo = ttk.Combobox(filter_box, textvariable=self.status_var, values=status_options, state="readonly", width=10)
        self.status_combo.grid(row=0, column=6, padx=(0, 16))
        self.status_combo.bind("<<ComboboxSelected>>", lambda event: self.apply_filters())

        # 4. Filter and Clear Buttons
        self.filter_btn = ttk.Button(filter_box, text="Filter", command=self.apply_filters)
        self.filter_btn.grid(row=0, column=7, padx=(0, 6))

        self.clear_filter_btn = ttk.Button(filter_box, text="Reset", command=self.reset_filters)
        self.clear_filter_btn.grid(row=0, column=8)

        # Items Treeview Table Container
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True)

        columns = (
            "item_id",
            "item_name",
            "category",
            "description",
            "found_location",
            "date_found",
            "contact",
            "status"
        )

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        # Column headings and widths
        self.tree.heading("item_id", text="ID")
        self.tree.heading("item_name", text="Item Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")
        self.tree.heading("found_location", text="Found Location")
        self.tree.heading("date_found", text="Date Found")
        self.tree.heading("contact", text="Contact")
        self.tree.heading("status", text="Status")

        self.tree.column("item_id", width=50, anchor="center")
        self.tree.column("item_name", width=160, anchor="w")
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("description", width=200, anchor="w")
        self.tree.column("found_location", width=140, anchor="w")
        self.tree.column("date_found", width=90, anchor="center")
        self.tree.column("contact", width=110, anchor="w")
        self.tree.column("status", width=80, anchor="center")

        # Row styling tags for LOST vs FOUND
        self.tree.tag_configure("LOST", foreground="#B45309", background="#FEF3C7")
        self.tree.tag_configure("FOUND", foreground="#047857", background="#D1FAE5")

        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Status Footer Bar
        footer_frame = ttk.Frame(self)
        footer_frame.pack(fill="x", pady=(8, 0))

        self.count_var = tk.StringVar(value="Loading items...")
        self.count_label = ttk.Label(footer_frame, textvariable=self.count_var, font=("Segoe UI", 9, "italic"))
        self.count_label.pack(side="left")

        legend_label = ttk.Label(
            footer_frame,
            text="Legend:  ■ LOST (Yellow)   ■ FOUND (Green)",
            font=("Segoe UI", 9)
        )
        legend_label.pack(side="right")

    def load_items(self):
        """Fetches all items from the Java backend asynchronously."""
        self._fetch_items(lambda: self.api_client.get_items())

    def apply_search(self):
        """Performs name search via GET /api/items/search?name={name}."""
        query = self.search_entry.get().strip()
        if not query:
            self.load_items()
            return

        self._fetch_items(lambda: self.api_client.search_items(query))

    def apply_filters(self):
        """Filters items by category and/or status."""
        cat = self.category_var.get()
        status = self.status_var.get()
        self._fetch_items(lambda: self.api_client.get_items(category=cat, status=status))

    def reset_filters(self):
        """Resets all filter options and loads all items."""
        self.search_entry.delete(0, tk.END)
        self.category_var.set("All Categories")
        self.status_var.set("ALL")
        self.load_items()

    def _fetch_items(self, fetcher_callable):
        self._set_buttons_state("disabled")
        self.count_var.set("Communicating with backend...")

        def worker():
            try:
                items = fetcher_callable()
                self.after(0, self._populate_table, items, None)
            except ApiException as e:
                self.after(0, self._populate_table, None, str(e))
            except Exception as e:
                self.after(0, self._populate_table, None, f"Unexpected error: {str(e)}")

        threading.Thread(target=worker, daemon=True).start()

    def _populate_table(self, items, error_message):
        self._set_buttons_state("normal")

        if error_message:
            self.count_var.set("Error fetching items")
            messagebox.showerror("Error", f"Could not load items from backend:\n{error_message}")
            return

        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not items:
            self.count_var.set("No items found matching criteria.")
            return

        for item in items:
            item_id = item.get("itemId", "")
            name = item.get("itemName", "")
            category = item.get("category", "")
            description = item.get("description", "") or "-"
            location = item.get("foundLocation", "")
            date_found = item.get("dateFound", "")
            contact = item.get("contact", "")
            status = item.get("status", "LOST")

            tag = "FOUND" if status == "FOUND" else "LOST"

            self.tree.insert(
                "",
                "end",
                iid=str(item_id),
                values=(item_id, name, category, description, location, date_found, contact, status),
                tags=(tag,)
            )

        self.count_var.set(f"Displaying {len(items)} item(s)")

    def mark_selected_as_found(self):
        """Validates selection and sends PATCH /api/items/{id}/status to change status to FOUND."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an item from the table first.")
            return

        item_id_str = selected[0]
        item_values = self.tree.item(item_id_str, "values")
        item_name = item_values[1]
        current_status = item_values[7]

        if current_status == "FOUND":
            messagebox.showinfo(
                "Already Returned",
                f"Item '{item_name}' (ID: {item_id_str}) is already marked as FOUND."
            )
            return

        # Confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Status Update",
            f"Are you sure you want to mark this item as FOUND?\n\n"
            f"• ID: {item_id_str}\n"
            f"• Name: {item_name}\n"
            f"• Action: Update status in MySQL from LOST ➔ FOUND\n\n"
            f"Note: Once marked FOUND, it cannot be reverted to LOST."
        )

        if not confirm:
            return

        self._set_buttons_state("disabled")
        self.count_var.set(f"Updating item {item_id_str} status in MySQL...")

        def worker():
            try:
                updated = self.api_client.mark_as_found(int(item_id_str))
                self.after(0, self._on_mark_found_success, updated)
            except ApiException as e:
                self.after(0, self._on_mark_found_failure, str(e))
            except Exception as e:
                self.after(0, self._on_mark_found_failure, f"Unexpected error: {str(e)}")

        threading.Thread(target=worker, daemon=True).start()

    def _on_mark_found_success(self, updated_item):
        self._set_buttons_state("normal")
        item_id = updated_item.get("itemId", "")
        item_name = updated_item.get("itemName", "")
        new_status = updated_item.get("status", "FOUND")

        messagebox.showinfo(
            "Item Status Updated",
            f"Successfully updated in MySQL!\n\n"
            f"• Item ID: {item_id}\n"
            f"• Name: {item_name}\n"
            f"• New Status: {new_status}"
        )

        # Refresh table
        self.apply_filters()

        # Refresh dashboard stats
        if self.on_status_updated:
            self.on_status_updated()

    def _on_mark_found_failure(self, error_message):
        self._set_buttons_state("normal")
        messagebox.showerror("Update Error", f"Failed to update status in database:\n{error_message}")
        self.apply_filters()

    def _set_buttons_state(self, state):
        self.mark_found_btn.config(state=state)
        self.refresh_btn.config(state=state)
        self.search_btn.config(state=state)
        self.filter_btn.config(state=state)
        self.clear_filter_btn.config(state=state)
