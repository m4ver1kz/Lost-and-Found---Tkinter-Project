"""
main.py
-----------------------------------------------------------------------------
Main Desktop GUI Entry Point for Lost and Found Management System.
Built with Python 3, Tkinter, and ttk.

Architecture:
- Left-side navigation bar with responsive button highlighting
- Initial connection check screen verifying backend & MySQL before dashboard
- Dynamic content frame switching between:
  1. ConnectionCheckView (startup & reconnection)
  2. DashboardView
  3. ReportItemView
  4. ViewItemsView
- Real-time backend connectivity indicator in sidebar footer
- Zero direct database access: all interactions route through ApiClient.
-----------------------------------------------------------------------------
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox

from api_client import ApiClient, ApiException
from dashboard import DashboardView
from report_item import ReportItemView
from view_items import ViewItemsView


class ConnectionCheckView(ttk.Frame):
    """Initial screen checking backend connectivity before opening the dashboard."""

    def __init__(self, parent, on_retry):
        super().__init__(parent)
        self.on_retry = on_retry
        self._build_ui()

    def _build_ui(self):
        self.configure(padding=40)

        # Center container
        self.container = ttk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        self.icon_label = ttk.Label(
            self.container,
            text="⏳",
            font=("Segoe UI", 36)
        )
        self.icon_label.pack(pady=(0, 10))

        self.title_label = ttk.Label(
            self.container,
            text="Connecting to Backend...",
            font=("Segoe UI", 16, "bold")
        )
        self.title_label.pack(pady=(0, 6))

        self.info_label = ttk.Label(
            self.container,
            text="Verifying Java Spring Boot REST API and MySQL database connectivity...",
            font=("Segoe UI", 10),
            foreground="#64748B",
            justify="center"
        )
        self.info_label.pack(pady=(0, 16))

        self.retry_btn = ttk.Button(
            self.container,
            text="🔄 Retry Connection",
            command=self.on_retry
        )
        # Initially hidden until error occurs

    def show_checking(self):
        self.icon_label.config(text="⏳")
        self.title_label.config(text="Connecting to Backend...")
        self.info_label.config(
            text="Verifying Java Spring Boot REST API and MySQL database connectivity...",
            foreground="#64748B"
        )
        self.retry_btn.pack_forget()

    def show_error(self, error_message):
        self.icon_label.config(text="⚠️")
        self.title_label.config(text="Backend Connection Required")
        self.info_label.config(
            text=f"{error_message}\n\n"
                 f"Please ensure MySQL is running (port 3306) and the Java backend is started.\n"
                 f"You can launch the complete system using 'run_application.bat'.",
            foreground="#DC2626"
        )
        self.retry_btn.pack(pady=10)


class LostAndFoundApp(tk.Tk):
    """Main desktop application class."""

    def __init__(self):
        super().__init__()
        self.title("Lost and Found Management System")
        self.geometry("1100x700")
        self.minsize(950, 600)

        # Initialize API client (reads API_BASE_URL env var or defaults to localhost:8080/api)
        self.api_client = ApiClient()

        # Configure modern ttk style
        self._setup_styles()

        # Build application structure
        self._build_layout()

        # Perform startup connection check before displaying main dashboard
        self.perform_startup_check()

    def _setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Global fonts and colors
        style.configure(".", font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))

    def _build_layout(self):
        # Master container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ---------------------------------------------------------------------
        # Left-Side Navigation Sidebar
        # ---------------------------------------------------------------------
        sidebar = tk.Frame(self, bg="#0F172A", width=230)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # App Brand Header
        brand_frame = tk.Frame(sidebar, bg="#0F172A", pady=24, padx=16)
        brand_frame.pack(fill="x")

        app_title = tk.Label(
            brand_frame,
            text="LOST & FOUND",
            font=("Segoe UI", 14, "bold"),
            fg="#F8FAFC",
            bg="#0F172A"
        )
        app_title.pack(anchor="w")

        app_subtitle = tk.Label(
            brand_frame,
            text="Management System",
            font=("Segoe UI", 9),
            fg="#94A3B8",
            bg="#0F172A"
        )
        app_subtitle.pack(anchor="w", pady=(2, 0))

        # Navigation Buttons Frame
        nav_frame = tk.Frame(sidebar, bg="#0F172A", pady=8)
        nav_frame.pack(fill="x", expand=True, anchor="n")

        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("report", "📝  Report Item"),
            ("view", "📋  View Items")
        ]

        for key, label_text in nav_items:
            btn = tk.Button(
                nav_frame,
                text=label_text,
                font=("Segoe UI", 10),
                fg="#E2E8F0",
                bg="#0F172A",
                activebackground="#1E293B",
                activeforeground="#FFFFFF",
                bd=0,
                padx=18,
                pady=12,
                anchor="w",
                cursor="hand2",
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        # Sidebar Footer: Connection Health Status
        conn_frame = tk.Frame(sidebar, bg="#1E293B", padx=14, pady=12)
        conn_frame.pack(fill="x", side="bottom")

        self.conn_dot = tk.Label(conn_frame, text="●", font=("Segoe UI", 12), fg="#94A3B8", bg="#1E293B")
        self.conn_dot.pack(side="left")

        self.conn_label = tk.Label(
            conn_frame,
            text="Checking backend...",
            font=("Segoe UI", 8),
            fg="#E2E8F0",
            bg="#1E293B"
        )
        self.conn_label.pack(side="left", padx=6)

        recheck_btn = tk.Button(
            conn_frame,
            text="↻",
            font=("Segoe UI", 9, "bold"),
            fg="#94A3B8",
            bg="#1E293B",
            activebackground="#334155",
            bd=0,
            cursor="hand2",
            command=lambda: self.check_connection(silent=False)
        )
        recheck_btn.pack(side="right")

        # ---------------------------------------------------------------------
        # Main Content Area
        # ---------------------------------------------------------------------
        self.content_container = tk.Frame(self, bg="#FFFFFF")
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Connection check view
        self.connection_view = ConnectionCheckView(self.content_container, self.perform_startup_check)

        # Application main views
        self.views = {
            "connecting": self.connection_view,
            "dashboard": DashboardView(self.content_container, self.api_client),
            "report": ReportItemView(
                self.content_container,
                self.api_client,
                on_item_reported=self._on_item_reported
            ),
            "view": ViewItemsView(
                self.content_container,
                self.api_client,
                on_status_updated=self._on_status_updated
            )
        }

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

    def perform_startup_check(self):
        """Displays connection screen and verifies backend health before opening dashboard."""
        self.connection_view.show_checking()
        self.show_view("connecting")
        self.check_connection(on_startup=True)

    def show_view(self, view_key: str):
        """Switches the active content view and updates navigation highlights."""
        # Highlight active nav button
        for key, btn in self.nav_buttons.items():
            if key == view_key:
                btn.config(bg="#334155", fg="#FFFFFF", font=("Segoe UI", 10, "bold"))
            else:
                btn.config(bg="#0F172A", fg="#E2E8F0", font=("Segoe UI", 10))

        # Raise the selected view
        view = self.views[view_key]
        view.tkraise()

        # Auto-refresh data on navigation
        if view_key == "dashboard":
            view.load_statistics()
        elif view_key == "view":
            view.load_items()

    def _on_item_reported(self):
        """Callback when an item is successfully submitted."""
        self.views["dashboard"].load_statistics()
        self.views["view"].load_items()

    def _on_status_updated(self):
        """Callback when an item status is updated to FOUND."""
        self.views["dashboard"].load_statistics()

    def check_connection(self, silent=True, on_startup=False):
        """Checks backend health asynchronously."""
        self.conn_dot.config(fg="#F59E0B") # Amber
        self.conn_label.config(text="Checking backend...")

        def worker():
            try:
                health = self.api_client.check_health()
                self.after(0, self._on_connection_success, health, silent, on_startup)
            except ApiException as e:
                self.after(0, self._on_connection_failure, str(e), silent, on_startup)
            except Exception as e:
                self.after(0, self._on_connection_failure, str(e), silent, on_startup)

        threading.Thread(target=worker, daemon=True).start()

    def _on_connection_success(self, health_data, silent, on_startup):
        self.conn_dot.config(fg="#10B981") # Green dot
        self.conn_label.config(text="Backend: Connected")

        # If on startup, transition from connecting view to the dashboard
        if on_startup:
            self.show_view("dashboard")
        elif not silent:
            db_product = health_data.get("databaseProduct", "MySQL")
            catalog = health_data.get("catalog", "lost_and_found")
            messagebox.showinfo(
                "Backend Online",
                f"Successfully connected to Java Spring Boot REST backend!\n\n"
                f"• Server Status: {health_data.get('status', 'UP')}\n"
                f"• Database Engine: {db_product}\n"
                f"• Database Schema: {catalog}"
            )

    def _on_connection_failure(self, error_msg, silent, on_startup):
        self.conn_dot.config(fg="#EF4444") # Red dot
        self.conn_label.config(text="Backend: Offline")

        if on_startup:
            self.connection_view.show_error(error_msg)
        elif not silent:
            messagebox.showerror(
                "Backend Disconnected",
                f"Cannot connect to Java backend on port 8080:\n\n{error_msg}\n\n"
                f"Please ensure the Java backend is running using 'run_backend.bat'."
            )


if __name__ == "__main__":
    app = LostAndFoundApp()
    app.mainloop()
