"""
report_item.py
-----------------------------------------------------------------------------
Report Item View Component providing a validated form to report a newly
found item:
- Item name
- Category
- Description
- Found location
- Date found
- Finder contact

Submits via POST /api/items to the Java backend.
Default status is strictly LOST.
-----------------------------------------------------------------------------
"""

import datetime
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from api_client import ApiClient, ApiException


CATEGORIES = [
    "Electronics",
    "Personal Accessories",
    "Documents & Cards",
    "Keys & Wallets",
    "Bags & Luggage",
    "Clothing",
    "Books & Stationery",
    "Other"
]


class ReportItemView(ttk.Frame):
    """Clean form view for registering a newly found item."""

    def __init__(self, parent, api_client: ApiClient, on_item_reported=None):
        super().__init__(parent)
        self.api_client = api_client
        self.on_item_reported = on_item_reported
        self._build_ui()

    def _build_ui(self):
        self.configure(padding=24)

        # Header Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 16))

        title = ttk.Label(title_frame, text="Report a Found Item", font=("Segoe UI", 18, "bold"))
        title.pack(anchor="w")

        subtitle = ttk.Label(
            title_frame,
            text="Please fill in the item details below. Newly reported items will be registered with status 'LOST'.",
            font=("Segoe UI", 9),
            foreground="#64748B"
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        # Main Form Container (Centered, well-padded)
        form_frame = ttk.LabelFrame(self, text="  Item Details Form  ", padding=20)
        form_frame.pack(fill="x", pady=10)

        # 1. Item Name
        ttk.Label(form_frame, text="Item Name *:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=6)
        self.name_entry = ttk.Entry(form_frame, width=45)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=6, padx=(10, 0))

        # 2. Category
        ttk.Label(form_frame, text="Category *:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=6)
        self.category_combo = ttk.Combobox(form_frame, values=CATEGORIES, state="readonly", width=43)
        self.category_combo.set(CATEGORIES[0])
        self.category_combo.grid(row=1, column=1, sticky="ew", pady=6, padx=(10, 0))

        # 3. Found Location
        ttk.Label(form_frame, text="Found Location *:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=6)
        self.location_entry = ttk.Entry(form_frame, width=45)
        self.location_entry.grid(row=2, column=1, sticky="ew", pady=6, padx=(10, 0))

        # 4. Date Found (YYYY-MM-DD)
        ttk.Label(form_frame, text="Date Found (YYYY-MM-DD) *:", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=6)
        self.date_entry = ttk.Entry(form_frame, width=45)
        self.date_entry.insert(0, datetime.date.today().isoformat())
        self.date_entry.grid(row=3, column=1, sticky="ew", pady=6, padx=(10, 0))

        # 5. Finder Contact
        ttk.Label(form_frame, text="Finder Contact (Phone/Email) *:", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="w", pady=6)
        self.contact_entry = ttk.Entry(form_frame, width=45)
        self.contact_entry.grid(row=4, column=1, sticky="ew", pady=6, padx=(10, 0))

        # 6. Description (Multiline Text)
        ttk.Label(form_frame, text="Description:", font=("Segoe UI", 10)).grid(row=5, column=0, sticky="nw", pady=6)
        self.desc_text = tk.Text(form_frame, width=45, height=4, font=("Segoe UI", 9), relief="solid", borderwidth=1)
        self.desc_text.grid(row=5, column=1, sticky="ew", pady=6, padx=(10, 0))

        form_frame.columnconfigure(1, weight=1)

        # Status / Feedback label
        self.msg_var = tk.StringVar(value="")
        self.msg_label = ttk.Label(self, textvariable=self.msg_var, font=("Segoe UI", 9, "italic"))
        self.msg_label.pack(anchor="w", pady=6)

        # Action Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=12)

        self.submit_btn = ttk.Button(btn_frame, text="✓ Submit Item Report", command=self.submit_form)
        self.submit_btn.pack(side="left", padx=(0, 10))

        self.clear_btn = ttk.Button(btn_frame, text="Clear Form", command=self.clear_form)
        self.clear_btn.pack(side="left")

    def validate_inputs(self):
        """Validates all required fields before making network request."""
        name = self.name_entry.get().strip()
        category = self.category_combo.get().strip()
        location = self.location_entry.get().strip()
        date_str = self.date_entry.get().strip()
        contact = self.contact_entry.get().strip()

        if not name:
            messagebox.showwarning("Validation Error", "Item name is required.")
            self.name_entry.focus_set()
            return None

        if len(name) > 100:
            messagebox.showwarning("Validation Error", "Item name cannot exceed 100 characters.")
            return None

        if not category:
            messagebox.showwarning("Validation Error", "Please select a category.")
            return None

        if not location:
            messagebox.showwarning("Validation Error", "Found location is required.")
            self.location_entry.focus_set()
            return None

        if not date_str:
            messagebox.showwarning("Validation Error", "Date found is required.")
            self.date_entry.focus_set()
            return None

        try:
            parsed_date = datetime.date.fromisoformat(date_str)
            if parsed_date > datetime.date.today():
                messagebox.showwarning("Validation Error", "Date found cannot be in the future.")
                return None
        except ValueError:
            messagebox.showwarning("Validation Error", "Date must be in valid format: YYYY-MM-DD.")
            self.date_entry.focus_set()
            return None

        if not contact:
            messagebox.showwarning("Validation Error", "Finder contact is required.")
            self.contact_entry.focus_set()
            return None

        desc = self.desc_text.get("1.0", tk.END).strip()
        if len(desc) > 255:
            messagebox.showwarning("Validation Error", "Description cannot exceed 255 characters.")
            return None

        return {
            "itemName": name,
            "category": category,
            "description": desc if desc else None,
            "foundLocation": location,
            "dateFound": date_str,
            "contact": contact
        }

    def submit_form(self):
        """Handles submission with async backend communication."""
        payload = self.validate_inputs()
        if not payload:
            return

        self.submit_btn.config(state="disabled")
        self.clear_btn.config(state="disabled")
        self.msg_var.set("Submitting item report to server...")

        def worker():
            try:
                result = self.api_client.report_item(payload)
                self.after(0, self._on_success, result)
            except ApiException as e:
                self.after(0, self._on_failure, str(e))
            except Exception as e:
                self.after(0, self._on_failure, f"Unexpected error: {str(e)}")

        threading.Thread(target=worker, daemon=True).start()

    def _on_success(self, result):
        self.submit_btn.config(state="normal")
        self.clear_btn.config(state="normal")
        self.msg_var.set("")

        item_id = result.get("itemId", "N/A")
        item_name = result.get("itemName", "")
        status = result.get("status", "LOST")

        messagebox.showinfo(
            "Report Submitted Successfully",
            f"The item has been saved to MySQL!\n\n"
            f"• Generated Item ID: {item_id}\n"
            f"• Item Name: {item_name}\n"
            f"• Initial Status: {status}\n\n"
            f"The item is now tracked as LOST until claimed."
        )

        self.clear_form()

        # Trigger dashboard and view items refresh callback
        if self.on_item_reported:
            self.on_item_reported()

    def _on_failure(self, error_message):
        self.submit_btn.config(state="normal")
        self.clear_btn.config(state="normal")
        self.msg_var.set("Submission failed.")
        messagebox.showerror("Submission Error", f"Failed to report item:\n{error_message}")

    def clear_form(self):
        """Clears all input fields to defaults."""
        self.name_entry.delete(0, tk.END)
        self.category_combo.set(CATEGORIES[0])
        self.location_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.date.today().isoformat())
        self.contact_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        self.msg_var.set("")
