import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
from database import DatabaseError
from datetime import datetime, timedelta

# Matplotlib integration
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import matplotlib
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']

# ─── Color Palette (Black Theme) ──────────────────────────────────────────────
BG_MAIN    = "#0d0d0d"     # Main window background
BG_HEADER  = "#111111"     # Header bar
BG_CARD    = "#161616"     # Panel / card backgrounds
BG_INPUT   = "#1e1e1e"     # Entry field backgrounds
BG_TAB     = "#181818"     # Inactive tab
BG_TAB_ACT = "#252525"     # Active tab
FG_TEXT    = "#ffffff"     # Primary text
FG_MUTED   = "#777777"     # Secondary / muted text
FG_LABEL   = "#aaaaaa"     # Label text
BORDER     = "#2a2a2a"     # Borders
BTN_BG     = "#1a1a1a"     # Button background
BTN_HOVER  = "#2d2d2d"     # Button hover
SAVE_BG    = "#1a5c1a"     # Save button green
SAVE_HOVER = "#228b22"     # Save button hover green

# BMI Category Colors
COLOR_UNDERWEIGHT = "#38bdf8"   # Sky blue
COLOR_NORMAL      = "#34d399"   # Emerald green
COLOR_OVERWEIGHT  = "#fbbf24"   # Amber
COLOR_OBESE       = "#f87171"   # Coral red


class BMICalculatorApp:
    """Premium BMI Calculator with CSV history and matplotlib trend charts."""

    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator")
        self.root.geometry("1050x650")
        self.root.configure(bg=BG_MAIN)
        self.root.minsize(950, 580)

        # Dark combobox dropdown styling
        self.root.option_add("*TCombobox*Listbox.background", BG_CARD)
        self.root.option_add("*TCombobox*Listbox.foreground", FG_TEXT)
        self.root.option_add("*TCombobox*Listbox.selectBackground", "#444444")
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        self.root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))
        self.root.option_add("*TCombobox*Listbox.borderwidth", "0")

        # CSV database path relative to the task 2 directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.abspath(os.path.join(script_dir, "bmi_records.csv"))
        try:
            database.init_csv(self.csv_path)
        except DatabaseError as e:
            messagebox.showerror("Initialization Error", str(e))

        self.current_user_name = None
        self.users_list = []
        self.units_system = tk.StringVar(value="metric")
        self.last_calc = None  # Stores last calculation for separate Save

        self.configure_styles()
        self.create_layout()
        self.refresh_profiles_list()
        self.show_tab("calculate")

    # ─── STYLES ───────────────────────────────────────────────────────────────

    def configure_styles(self):
        """Configure ttk widget styles to match the black theme."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG_MAIN, foreground=FG_TEXT)

        # Treeview (History table)
        style.configure("Treeview",
                         background=BG_CARD, fieldbackground=BG_CARD,
                         foreground=FG_TEXT, rowheight=32,
                         font=("Segoe UI", 10))
        style.map("Treeview",
                   background=[("selected", "#333333")],
                   foreground=[("selected", "#ffffff")])
        style.configure("Treeview.Heading",
                         background="#222222", foreground=FG_TEXT,
                         font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Treeview.Heading", background=[("active", "#444444")])

        # Combobox
        style.configure("TCombobox",
                         fieldbackground=BG_INPUT, background=BG_INPUT,
                         foreground=FG_TEXT, arrowcolor=FG_TEXT, borderwidth=0)
        style.map("TCombobox",
                   fieldbackground=[("readonly", BG_INPUT)],
                   foreground=[("readonly", FG_TEXT)])

        # Scrollbar
        style.configure("Vertical.TScrollbar",
                         background=BG_INPUT, troughcolor=BG_CARD,
                         arrowcolor=FG_TEXT, bordercolor=BG_CARD)

    # ─── LAYOUT ──────────────────────────────────────────────────────────────

    def create_layout(self):
        """Build the header bar, tab bar, and content area."""

        # === HEADER BAR ===
        header = tk.Frame(self.root, bg=BG_HEADER, height=75)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=BG_HEADER)
        title_frame.pack(side="left", padx=25, fill="y")
        tk.Label(title_frame, text="BMI Calculator",
                 font=("Segoe UI", 22, "bold"), fg=FG_TEXT,
                 bg=BG_HEADER).pack(side="left", pady=18)
        tk.Label(title_frame, text="   Track  ·  Analyse  ·  Improve",
                 font=("Segoe UI", 9), fg=FG_MUTED,
                 bg=BG_HEADER).pack(side="left", pady=18)

        # CSV file indicator (top-right)
        db_frame = tk.Frame(header, bg=BG_HEADER)
        db_frame.pack(side="right", padx=20, pady=18)
        self.csv_display_var = tk.StringVar(value=os.path.basename(self.csv_path))
        tk.Label(db_frame, textvariable=self.csv_display_var,
                 font=("Segoe UI", 8), fg=FG_MUTED,
                 bg=BG_HEADER).pack(side="left", padx=(0, 8))
        self._make_btn(db_frame, "Change DB", self.on_change_database,
                       font_size=8, padx=10, pady=3).pack(side="left")

        # === TAB BAR ===
        tab_bar = tk.Frame(self.root, bg=BG_MAIN)
        tab_bar.pack(fill="x", padx=20, pady=(10, 0))

        self.tab_buttons = {}
        for name, label in [("calculate", "Calculate"),
                            ("history", "History"),
                            ("trend", "Trend Chart")]:
            btn = tk.Button(tab_bar, text=label,
                            font=("Segoe UI", 10, "bold"),
                            bg=BG_TAB, fg=FG_MUTED,
                            activebackground=BG_TAB_ACT, activeforeground=FG_TEXT,
                            bd=1, relief="solid", padx=18, pady=7,
                            cursor="hand2",
                            command=lambda n=name: self.show_tab(n))
            btn.pack(side="left", padx=(0, 2))
            self.tab_buttons[name] = btn

        # === CONTENT AREA ===
        self.content = tk.Frame(self.root, bg=BG_MAIN)
        self.content.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        self.tab_frames = {
            "calculate": self._build_calculate_tab(),
            "history":   self._build_history_tab(),
            "trend":     self._build_trend_tab(),
        }

    def _make_btn(self, parent, text, cmd, bg=BTN_BG, fg=FG_TEXT,
                  hover_bg=BTN_HOVER, font_size=10, padx=14, pady=6, bold=True):
        """Helper to create a styled button with hover effects."""
        f = ("Segoe UI", font_size, "bold") if bold else ("Segoe UI", font_size)
        btn = tk.Button(parent, text=text, font=f,
                        bg=bg, fg=fg, activebackground=hover_bg,
                        activeforeground=fg, bd=0, padx=padx, pady=pady,
                        cursor="hand2", command=cmd)
        btn.bind("<Enter>", lambda e, b=btn, c=hover_bg: b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
        return btn

    def show_tab(self, name):
        """Switch visible tab."""
        for f in self.tab_frames.values():
            f.pack_forget()
        for n, btn in self.tab_buttons.items():
            btn.config(bg=BG_TAB_ACT if n == name else BG_TAB,
                       fg=FG_TEXT if n == name else FG_MUTED)
        self.tab_frames[name].pack(fill="both", expand=True)

        if name == "history":
            self.load_history_data()
        elif name == "calculate":
            self.refresh_calculator_dropdowns()
        elif name == "trend":
            if self.current_user_name:
                self.trend_name_entry.delete(0, tk.END)
                self.trend_name_entry.insert(0, self.current_user_name)

    # ─── CALCULATE TAB ───────────────────────────────────────────────────────

    def _build_calculate_tab(self):
        """Build the Calculator view with input panel (left) and result panel (right)."""
        container = tk.Frame(self.content, bg=BG_MAIN)
        container.columnconfigure(0, weight=1, uniform="calc")
        container.columnconfigure(1, weight=1, uniform="calc")
        container.rowconfigure(0, weight=1)

        # ── LEFT PANEL: Inputs ──
        left = tk.Frame(container, bg=BG_CARD, padx=25, pady=20)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(left, text="Enter Your Details",
                 font=("Segoe UI", 14, "bold"), fg=FG_TEXT,
                 bg=BG_CARD).pack(anchor="w", pady=(0, 12))

        # Unit toggle row
        unit_row = tk.Frame(left, bg=BG_CARD)
        unit_row.pack(fill="x", pady=(0, 12))
        tk.Label(unit_row, text="Unit:", font=("Segoe UI", 10),
                 fg=FG_MUTED, bg=BG_CARD).pack(side="left", padx=(0, 8))
        for txt, val in [("Metric (kg / m)", "metric"),
                         ("Imperial (lb / in)", "imperial")]:
            tk.Radiobutton(unit_row, text=txt,
                           variable=self.units_system, value=val,
                           font=("Segoe UI", 9), bg=BG_CARD, fg=FG_TEXT,
                           activebackground=BG_CARD, selectcolor=BG_INPUT,
                           command=self.on_units_changed).pack(side="left", padx=(0, 12))

        # Name selector row
        tk.Label(left, text="Name", font=("Segoe UI", 10),
                 fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(0, 3))
        name_row = tk.Frame(left, bg=BG_CARD)
        name_row.pack(fill="x", pady=(0, 2))

        self.calc_user_var = tk.StringVar()
        self.calc_user_combo = ttk.Combobox(name_row, textvariable=self.calc_user_var,
                                            state="readonly", font=("Segoe UI", 11))
        self.calc_user_combo.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.calc_user_combo.bind("<<ComboboxSelected>>", self.on_calc_user_selected)

        self._make_btn(name_row, "+ New", self.open_add_profile_dialog,
                       font_size=9, padx=10, pady=4).pack(side="right")
        tk.Label(left, text="e.g. Alex", font=("Segoe UI", 8),
                 fg="#555555", bg=BG_CARD).pack(anchor="w", pady=(0, 10))

        # Weight input
        self.weight_lbl_var = tk.StringVar(value="Weight (kg)")
        tk.Label(left, textvariable=self.weight_lbl_var, font=("Segoe UI", 10),
                 fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(0, 3))
        self.weight_entry = tk.Entry(left, bg=BG_INPUT, fg=FG_TEXT,
                                     insertbackground=FG_TEXT,
                                     font=("Segoe UI", 11), bd=0)
        self.weight_entry.pack(fill="x", ipady=8, pady=(0, 2))
        tk.Label(left, text="e.g. 70", font=("Segoe UI", 8),
                 fg="#555555", bg=BG_CARD).pack(anchor="w", pady=(0, 10))

        # Height input
        self.height_lbl_var = tk.StringVar(value="Height (cm)")
        tk.Label(left, textvariable=self.height_lbl_var, font=("Segoe UI", 10),
                 fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(0, 3))

        self.height_container = tk.Frame(left, bg=BG_CARD)
        self.height_container.pack(fill="x", pady=(0, 2))

        # Metric height entry
        self.height_entry = tk.Entry(self.height_container, bg=BG_INPUT,
                                      fg=FG_TEXT, insertbackground=FG_TEXT,
                                      font=("Segoe UI", 11), bd=0)
        self.height_entry.pack(fill="x", ipady=8)

        # Imperial height entries (ft + in) — built but hidden initially
        self.height_imp_frame = tk.Frame(self.height_container, bg=BG_CARD)
        self.height_ft_entry = tk.Entry(self.height_imp_frame, bg=BG_INPUT,
                                         fg=FG_TEXT, insertbackground=FG_TEXT,
                                         font=("Segoe UI", 11), bd=0, width=8)
        self.height_ft_entry.pack(side="left", ipady=8, padx=(0, 4))
        tk.Label(self.height_imp_frame, text="ft", font=("Segoe UI", 9),
                 fg=FG_MUTED, bg=BG_CARD).pack(side="left", padx=(0, 12))
        self.height_in_entry = tk.Entry(self.height_imp_frame, bg=BG_INPUT,
                                         fg=FG_TEXT, insertbackground=FG_TEXT,
                                         font=("Segoe UI", 11), bd=0, width=8)
        self.height_in_entry.pack(side="left", ipady=8, padx=(0, 4))
        tk.Label(self.height_imp_frame, text="in", font=("Segoe UI", 9),
                 fg=FG_MUTED, bg=BG_CARD).pack(side="left")

        self.height_hint_var = tk.StringVar(value="e.g. 175")
        tk.Label(left, textvariable=self.height_hint_var, font=("Segoe UI", 8),
                 fg="#555555", bg=BG_CARD).pack(anchor="w", pady=(0, 8))

        # Validation error label
        self.calc_error_lbl = tk.Label(left, text="", font=("Segoe UI", 9, "bold"),
                                        fg=COLOR_OBESE, bg=BG_CARD, wraplength=340,
                                        justify="left", anchor="w")
        self.calc_error_lbl.pack(fill="x", pady=(0, 5))

        # Calculate button
        self._make_btn(left, "Calculate BMI", self.on_calculate,
                       font_size=12, pady=10).pack(fill="x", pady=(0, 6))

        # Save button
        self._make_btn(left, "💾 Save Record", self.on_save_record,
                       bg=SAVE_BG, hover_bg=SAVE_HOVER,
                       font_size=11, pady=10).pack(fill="x", pady=(0, 8))

        # Delete profile link
        del_link = tk.Button(left, text="✕ Delete Active Profile",
                             font=("Segoe UI", 8), bg=BG_CARD, fg=COLOR_OBESE,
                             activebackground=BG_CARD, activeforeground="#ef4444",
                             bd=0, cursor="hand2", command=self.on_delete_profile)
        del_link.pack(anchor="w")

        # ── RIGHT PANEL: Results ──
        right = tk.Frame(container, bg=BG_CARD, padx=25, pady=20)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(right, text="Result", font=("Segoe UI", 14, "bold"),
                 fg=FG_TEXT, bg=BG_CARD).pack(anchor="w", pady=(0, 15))

        self.result_area = tk.Frame(right, bg=BG_CARD)
        self.result_area.pack(fill="both", expand=True)

        # Placeholder text (shown when no result)
        self.result_placeholder = tk.Label(
            self.result_area,
            text="Enter your details and click\nCalculate BMI to see results.",
            font=("Segoe UI", 11), fg=FG_MUTED, bg=BG_CARD)
        self.result_placeholder.pack(expand=True)

        # Pre-built result widgets (packed only after calculation)
        self.bmi_value_lbl = tk.Label(self.result_area, text="",
                                       font=("Segoe UI", 56, "bold"),
                                       fg=COLOR_NORMAL, bg=BG_CARD)
        self.bmi_category_lbl = tk.Label(self.result_area, text="",
                                          font=("Segoe UI", 12, "bold"),
                                          bg=BG_CARD, padx=12, pady=4)

        # Gauge canvas for the colored BMI scale bar
        self.gauge_canvas = tk.Canvas(self.result_area, height=55,
                                       bg=BG_CARD, highlightthickness=0)

        # Reference ranges table
        self.ref_frame = tk.Frame(self.result_area, bg=BG_CARD)
        tk.Label(self.ref_frame, text="Reference Ranges",
                 font=("Segoe UI", 10, "bold"), fg=FG_LABEL,
                 bg=BG_CARD).pack(anchor="w", pady=(0, 6))
        for val_range, label, color in [
            ("< 18.5",    "Underweight", COLOR_UNDERWEIGHT),
            ("18.5-24.9", "Normal",      COLOR_NORMAL),
            ("25.0-29.9", "Overweight",  COLOR_OVERWEIGHT),
            (">= 30.0",  "Obese",       COLOR_OBESE),
        ]:
            row = tk.Frame(self.ref_frame, bg=BG_CARD)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=val_range, font=("Segoe UI", 10),
                     fg=FG_MUTED, bg=BG_CARD, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=label, font=("Segoe UI", 10, "bold"),
                     fg=color, bg=BG_CARD, anchor="w").pack(side="left")

        # Ideal weight range label
        self.ideal_lbl = tk.Label(self.result_area, text="",
                                   font=("Segoe UI", 10), fg=COLOR_NORMAL,
                                   bg=BG_CARD)

        # Recommendation label
        self.recommend_lbl = tk.Label(self.result_area, text="",
                                       font=("Segoe UI", 10), fg=FG_TEXT,
                                       bg=BG_CARD, wraplength=380, justify="left")

        return container

    # ─── HISTORY TAB ─────────────────────────────────────────────────────────

    def _build_history_tab(self):
        """Build the History view with a table showing ALL users' records."""
        container = tk.Frame(self.content, bg=BG_MAIN)

        # Header row with title and action buttons
        header_row = tk.Frame(container, bg=BG_MAIN)
        header_row.pack(fill="x", pady=(0, 8))
        tk.Label(header_row, text="Saved Records",
                 font=("Segoe UI", 14, "bold"), fg=FG_TEXT,
                 bg=BG_MAIN).pack(side="left")

        self._make_btn(header_row, "Refresh", self.load_history_data,
                       pady=5, padx=15).pack(side="right")
        self._make_btn(header_row, "Delete Selected", self.on_delete_record,
                       bg="#7f1d1d", hover_bg="#991b1b",
                       pady=5, padx=15).pack(side="right", padx=(0, 8))

        # Treeview table
        tree_frame = tk.Frame(container, bg=BG_CARD)
        tree_frame.pack(fill="both", expand=True)

        cols = ("name", "weight", "height", "bmi", "category", "date")
        self.history_tree = ttk.Treeview(tree_frame, columns=cols,
                                          show="headings", selectmode="browse")

        headings = {"name": "Name", "weight": "Weight (kg)",
                    "height": "Height (m)", "bmi": "BMI",
                    "category": "Category", "date": "Date"}
        widths  = {"name": 100, "weight": 100, "height": 100,
                   "bmi": 80, "category": 100, "date": 170}

        for col in cols:
            self.history_tree.heading(col, text=headings[col])
            self.history_tree.column(col, width=widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                   command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return container

    # ─── TREND CHART TAB ─────────────────────────────────────────────────────

    def _build_trend_tab(self):
        """Build the Trend Chart view with a name entry and matplotlib chart."""
        container = tk.Frame(self.content, bg=BG_MAIN)

        # Header row with title and controls
        header_row = tk.Frame(container, bg=BG_MAIN)
        header_row.pack(fill="x", pady=(0, 8))
        tk.Label(header_row, text="BMI Trend",
                 font=("Segoe UI", 14, "bold"), fg=FG_TEXT,
                 bg=BG_MAIN).pack(side="left")

        ctrl = tk.Frame(header_row, bg=BG_MAIN)
        ctrl.pack(side="right")
        tk.Label(ctrl, text="Name:", font=("Segoe UI", 10),
                 fg=FG_MUTED, bg=BG_MAIN).pack(side="left", padx=(0, 5))
        self.trend_name_entry = tk.Entry(ctrl, bg=BG_INPUT, fg=FG_TEXT,
                                          insertbackground=FG_TEXT,
                                          font=("Segoe UI", 10), bd=0, width=15)
        self.trend_name_entry.pack(side="left", ipady=4, padx=(0, 8))
        self._make_btn(ctrl, "Show Chart", self.on_show_trend,
                       pady=4, padx=15).pack(side="left")

        # Chart container
        self.chart_container = tk.Frame(container, bg=BG_CARD)
        self.chart_container.pack(fill="both", expand=True)

        self.chart_placeholder_lbl = tk.Label(
            self.chart_container,
            text="Enter a name and click Show Chart\nto view BMI trends over time.",
            font=("Segoe UI", 11), fg=FG_MUTED, bg=BG_CARD)
        self.chart_placeholder_lbl.pack(expand=True)

        return container

    # ─── PROFILE MANAGEMENT ──────────────────────────────────────────────────

    def open_add_profile_dialog(self):
        """Open a centered modal dialog to create a new user profile."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Profile")
        dialog.configure(bg=BG_MAIN)
        dialog.resizable(False, False)
        dialog.geometry("360x350")

        # Center on root window
        self.root.update_idletasks()
        rx, ry = self.root.winfo_x(), self.root.winfo_y()
        rw, rh = self.root.winfo_width(), self.root.winfo_height()
        dialog.geometry(f"+{rx + (rw - 360) // 2}+{ry + (rh - 350) // 2}")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Create New Profile",
                 font=("Segoe UI", 14, "bold"), fg=FG_TEXT,
                 bg=BG_MAIN).pack(pady=(20, 15))

        form = tk.Frame(dialog, bg=BG_MAIN, padx=25)
        form.pack(fill="both", expand=True)

        # Name field
        tk.Label(form, text="FULL NAME", font=("Segoe UI", 8, "bold"),
                 fg=FG_MUTED, bg=BG_MAIN).pack(anchor="w", pady=(0, 3))
        name_e = tk.Entry(form, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                           font=("Segoe UI", 11), bd=0)
        name_e.pack(fill="x", ipady=6, pady=(0, 12))

        # Age field
        tk.Label(form, text="AGE (optional)", font=("Segoe UI", 8, "bold"),
                 fg=FG_MUTED, bg=BG_MAIN).pack(anchor="w", pady=(0, 3))
        age_e = tk.Entry(form, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                          font=("Segoe UI", 11), bd=0)
        age_e.pack(fill="x", ipady=6, pady=(0, 12))

        # Gender field
        tk.Label(form, text="GENDER (optional)", font=("Segoe UI", 8, "bold"),
                 fg=FG_MUTED, bg=BG_MAIN).pack(anchor="w", pady=(0, 3))
        gender_var = tk.StringVar(value="Unspecified")
        ttk.Combobox(form, textvariable=gender_var,
                     values=["Male", "Female", "Unspecified"],
                     state="readonly", font=("Segoe UI", 10)).pack(fill="x", pady=(0, 8))

        err_lbl = tk.Label(form, text="", font=("Segoe UI", 9, "bold"),
                            fg=COLOR_OBESE, bg=BG_MAIN, anchor="w")
        err_lbl.pack(fill="x", pady=(0, 5))

        btn_bar = tk.Frame(dialog, bg=BG_MAIN, padx=25, pady=15)
        btn_bar.pack(fill="x", side="bottom")

        def on_save():
            err_lbl.config(text="")
            name = name_e.get().strip()
            age_str = age_e.get().strip()
            gender = gender_var.get()

            if not name:
                err_lbl.config(text="⚠ Name is required.")
                return
            if "," in name:
                err_lbl.config(text="⚠ Name cannot contain commas.")
                return

            age = None
            if age_str:
                try:
                    age = int(age_str)
                    if age <= 0 or age > 120:
                        err_lbl.config(text="⚠ Age must be 1–120.")
                        return
                except ValueError:
                    err_lbl.config(text="⚠ Age must be a number.")
                    return

            try:
                new_name = database.add_user(self.csv_path, name, age, gender)
                self.refresh_profiles_list()
                self.select_user(new_name)
                dialog.destroy()
                messagebox.showinfo("Saved", f"Profile '{name}' created.")
            except DatabaseError as e:
                err_lbl.config(text=f"⚠ {e}")

        self._make_btn(btn_bar, "Cancel", dialog.destroy,
                       font_size=10, bold=False).pack(side="left")
        self._make_btn(btn_bar, "Create", on_save,
                       bg=SAVE_BG, hover_bg=SAVE_HOVER, font_size=10).pack(side="right")

    def refresh_profiles_list(self):
        """Fetch profiles from CSV and update dropdowns."""
        try:
            self.users_list = database.get_users(self.csv_path)
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
            return
        self.refresh_calculator_dropdowns()

        if self.current_user_name is None and self.users_list:
            self.select_user(self.users_list[0]['name'])
        elif self.current_user_name:
            exists = any(u['name'].lower() == self.current_user_name.lower()
                         for u in self.users_list)
            if not exists:
                if self.users_list:
                    self.select_user(self.users_list[0]['name'])
                else:
                    self.current_user_name = None
                    self.calc_user_var.set("")

    def refresh_calculator_dropdowns(self):
        """Populate the profile combobox with current users."""
        names = [u['name'] for u in self.users_list]
        self.calc_user_combo['values'] = names
        if self.current_user_name:
            match = next((u for u in self.users_list
                          if u['name'].lower() == self.current_user_name.lower()), None)
            self.calc_user_combo.set(match['name'] if match else "")
        else:
            self.calc_user_combo.set("")

    def select_user(self, name):
        """Set the active profile."""
        self.current_user_name = name
        match = next((u for u in self.users_list
                      if u['name'].lower() == name.lower()), None)
        if match:
            self.calc_user_combo.set(match['name'])
        self.hide_results()

    def on_calc_user_selected(self, event):
        """Handle combobox profile selection."""
        selected = self.calc_user_var.get()
        if selected:
            self.select_user(selected)

    def on_delete_profile(self):
        """Delete the currently selected profile and all its records."""
        if not self.current_user_name:
            messagebox.showwarning("No Profile", "Select a profile first.")
            return
        if messagebox.askyesno("Delete Profile",
                                f"Delete '{self.current_user_name}' and all its records?\n\nThis cannot be undone."):
            try:
                database.delete_user(self.csv_path, self.current_user_name)
                old = self.current_user_name
                self.current_user_name = None
                self.refresh_profiles_list()
                messagebox.showinfo("Deleted", f"Profile '{old}' removed.")
            except DatabaseError as e:
                messagebox.showerror("Error", str(e))

    # ─── UNITS SWITCHING ─────────────────────────────────────────────────────

    def on_units_changed(self):
        """Toggle between metric and imperial input fields."""
        self.calc_error_lbl.config(text="")
        if self.units_system.get() == "metric":
            self.weight_lbl_var.set("Weight (kg)")
            self.height_lbl_var.set("Height (cm)")
            self.height_hint_var.set("e.g. 175")
            self.height_imp_frame.pack_forget()
            self.height_entry.pack(fill="x", ipady=8)
        else:
            self.weight_lbl_var.set("Weight (lbs)")
            self.height_lbl_var.set("Height")
            self.height_hint_var.set("e.g. 5 ft 9 in")
            self.height_entry.pack_forget()
            self.height_imp_frame.pack(fill="x")

    # ─── CALCULATION LOGIC ───────────────────────────────────────────────────

    def validate_inputs(self):
        """Parse and validate weight/height inputs. Returns ((weight_kg, height_m), None) or (None, error_msg)."""
        unit = self.units_system.get()
        w_str = self.weight_entry.get().strip()

        if not w_str:
            return None, "Weight cannot be empty."
        try:
            weight = float(w_str)
            if weight <= 0:
                return None, "Weight must be a positive number."
        except ValueError:
            return None, "Weight must be numeric."

        if unit == "metric":
            h_str = self.height_entry.get().strip()
            if not h_str:
                return None, "Height cannot be empty."
            try:
                height_cm = float(h_str)
                if height_cm <= 0:
                    return None, "Height must be a positive number."
            except ValueError:
                return None, "Height must be numeric (cm)."
            return (weight, height_cm / 100.0), None
        else:
            ft_str = self.height_ft_entry.get().strip()
            in_str = self.height_in_entry.get().strip()
            if not ft_str and not in_str:
                return None, "Height cannot be empty."
            try:
                ft = float(ft_str) if ft_str else 0.0
                inch = float(in_str) if in_str else 0.0
                if ft < 0 or inch < 0:
                    return None, "Height cannot be negative."
                if ft == 0 and inch == 0:
                    return None, "Height must be greater than 0."
            except ValueError:
                return None, "Height values must be numeric."
            height_m = (ft * 12.0 + inch) * 0.0254
            weight_kg = weight * 0.45359237
            return (weight_kg, height_m), None

    def on_calculate(self):
        """Compute BMI and display results (does NOT save to CSV)."""
        self.calc_error_lbl.config(text="")
        result, error = self.validate_inputs()
        if error:
            self.calc_error_lbl.config(text=f"⚠ {error}")
            return

        weight_kg, height_m = result
        bmi = weight_kg / (height_m ** 2)

        # Store for subsequent save
        self.last_calc = {
            "weight_kg": weight_kg,
            "height_m": height_m,
            "bmi": bmi,
        }

        self.show_results(bmi, height_m)

    def on_save_record(self):
        """Save the last calculated BMI record to CSV under the active profile."""
        if not self.last_calc:
            messagebox.showwarning("No Calculation",
                                    "Please calculate BMI first before saving.")
            return
        if not self.current_user_name:
            messagebox.showwarning("No Profile",
                                    "Please select or create a profile first.")
            return
        try:
            database.add_bmi_record(
                self.csv_path, self.current_user_name,
                self.last_calc["weight_kg"],
                self.last_calc["height_m"],
                self.last_calc["bmi"])
            messagebox.showinfo("Saved",
                                f"Record saved for {self.current_user_name}.")
            # Clear inputs after successful save
            self.weight_entry.delete(0, tk.END)
            self.height_entry.delete(0, tk.END)
            self.height_ft_entry.delete(0, tk.END)
            self.height_in_entry.delete(0, tk.END)
            self.last_calc = None
        except DatabaseError as e:
            messagebox.showerror("Save Error", str(e))

    # ─── RESULT DISPLAY ─────────────────────────────────────────────────────

    def draw_gauge(self, bmi):
        """Draw the horizontal colored BMI scale bar with a position pointer."""
        self.gauge_canvas.delete("all")
        w, h_bar = 340, 14
        x0, y0 = 20, 25

        def bmi_x(val):
            return x0 + (max(10.0, min(40.0, val)) - 10.0) / 30.0 * w

        # Draw four colored segments
        segments = [
            (x0,          bmi_x(18.5), COLOR_UNDERWEIGHT),
            (bmi_x(18.5), bmi_x(25.0), COLOR_NORMAL),
            (bmi_x(25.0), bmi_x(30.0), COLOR_OVERWEIGHT),
            (bmi_x(30.0), x0 + w,      COLOR_OBESE),
        ]
        for sx, ex, color in segments:
            self.gauge_canvas.create_rectangle(sx, y0, ex, y0 + h_bar,
                                                fill=color, outline="")

        # Threshold labels underneath the bar
        for val, txt in [(10, "10"), (18.5, "18.5"), (25, "25"),
                          (30, "30"), (40, "40+")]:
            self.gauge_canvas.create_text(bmi_x(val), y0 + h_bar + 10,
                                           text=txt, fill=FG_MUTED,
                                           font=("Segoe UI", 7))

        # Pointer triangle at active BMI position
        px = bmi_x(bmi)
        self.gauge_canvas.create_polygon(
            px, y0 - 3, px - 6, y0 - 11, px + 6, y0 - 11,
            fill=FG_TEXT, outline="")
        self.gauge_canvas.create_text(px, y0 - 18, text=f"{bmi:.1f}",
                                       fill=FG_TEXT,
                                       font=("Segoe UI", 8, "bold"))

    def show_results(self, bmi, height_m=None):
        """Show calculated BMI result, gauge, reference ranges, and recommendation."""
        self.result_placeholder.pack_forget()

        if bmi < 18.5:
            cat, color = "Underweight", COLOR_UNDERWEIGHT
            rec = "Your BMI indicates you are underweight. Consider consulting a healthcare provider about nutritional strategies."
        elif bmi < 25:
            cat, color = "Normal", COLOR_NORMAL
            rec = "Excellent! You have a healthy body weight. Maintain a balanced diet and active lifestyle."
        elif bmi < 30:
            cat, color = "Overweight", COLOR_OVERWEIGHT
            rec = "Your BMI suggests you are slightly overweight. Small dietary and exercise changes can help."
        else:
            cat, color = "Obese", COLOR_OBESE
            rec = "Your BMI indicates an obesity classification. Consult a healthcare provider for personalized guidance."

        self.bmi_value_lbl.config(text=f"{bmi:.2f}", fg=color)
        self.bmi_category_lbl.config(text=cat, fg=color)

        self.bmi_value_lbl.pack(pady=(10, 5))
        self.bmi_category_lbl.pack(pady=(0, 10))

        self.draw_gauge(bmi)
        self.gauge_canvas.pack(fill="x", padx=10, pady=(0, 12))

        self.ref_frame.pack(fill="x", pady=(0, 10))

        # Calculate and display ideal weight range
        if height_m and height_m > 0:
            lo_kg = 18.5 * height_m ** 2
            hi_kg = 24.9 * height_m ** 2
            if self.units_system.get() == "metric":
                self.ideal_lbl.config(text=f"Ideal Weight: {lo_kg:.1f} – {hi_kg:.1f} kg")
            else:
                self.ideal_lbl.config(
                    text=f"Ideal Weight: {lo_kg / 0.45359237:.1f} – {hi_kg / 0.45359237:.1f} lbs")
            self.ideal_lbl.pack(pady=(0, 8))
        else:
            self.ideal_lbl.pack_forget()

        self.recommend_lbl.config(text=rec)
        self.recommend_lbl.pack(fill="x", pady=(0, 5))

    def hide_results(self):
        """Hide result widgets and restore the placeholder text."""
        for widget in [self.bmi_value_lbl, self.bmi_category_lbl,
                       self.gauge_canvas, self.ref_frame,
                       self.ideal_lbl, self.recommend_lbl]:
            widget.pack_forget()
        self.result_placeholder.pack(expand=True)

    # ─── HISTORY TAB LOGIC ───────────────────────────────────────────────────

    def load_history_data(self):
        """Load ALL users' BMI records into the history table."""
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        try:
            records = database.get_all_bmi_records(self.csv_path)
        except DatabaseError as e:
            messagebox.showerror("Error", str(e))
            return

        for i, rec in enumerate(records):
            bmi = rec['bmi']
            if bmi < 18.5:     cat = "Underweight"
            elif bmi < 25.0:   cat = "Normal"
            elif bmi < 30.0:   cat = "Overweight"
            else:              cat = "Obese"

            self.history_tree.insert("", "end", iid=str(i), values=(
                rec['name'],
                f"{rec['weight']:.1f}",
                f"{rec['height']:.2f}",
                f"{bmi:.2f}",
                cat,
                rec['date'],
            ))

    def on_delete_record(self):
        """Delete the selected record from CSV."""
        sel = self.history_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a record to delete.")
            return
        vals = self.history_tree.item(sel[0], "values")
        name = vals[0]
        date_str = vals[5]
        if messagebox.askyesno("Delete Record",
                                f"Delete this record for '{name}'?\n\nThis cannot be undone."):
            try:
                database.delete_bmi_record(self.csv_path, name, date_str)
                self.load_history_data()
            except DatabaseError as e:
                messagebox.showerror("Error", str(e))

    # ─── TREND CHART LOGIC ───────────────────────────────────────────────────

    def on_show_trend(self):
        """Fetch records for the entered name and draw the trend chart."""
        name = self.trend_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Name Required", "Enter a name to show trends.")
            return
        try:
            records = database.get_bmi_records(self.csv_path, name)
        except DatabaseError as e:
            messagebox.showerror("Error", str(e))
            return

        if not records:
            for w in self.chart_container.winfo_children():
                w.destroy()
            tk.Label(self.chart_container,
                     text=f"No records found for '{name}'.",
                     font=("Segoe UI", 11), fg=FG_MUTED,
                     bg=BG_CARD).pack(expand=True)
            return

        self.draw_trend_chart(records, name)

    def draw_trend_chart(self, records, user_name):
        """Render a matplotlib BMI trend chart embedded in the Trend tab."""
        for w in self.chart_container.winfo_children():
            w.destroy()

        sorted_recs = sorted(records, key=lambda r: r['date'])
        dates = [datetime.strptime(r['date'], "%Y-%m-%d %H:%M:%S") for r in sorted_recs]
        bmis = [r['bmi'] for r in sorted_recs]

        fig = Figure(figsize=(6, 4), dpi=100, facecolor=BG_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(BG_CARD)

        # Colored health zone bands
        ax.axhspan(0, 18.5, color=COLOR_UNDERWEIGHT, alpha=0.08)
        ax.axhspan(18.5, 25.0, color=COLOR_NORMAL, alpha=0.08)
        ax.axhspan(25.0, 30.0, color=COLOR_OVERWEIGHT, alpha=0.08)
        ax.axhspan(30.0, 55.0, color=COLOR_OBESE, alpha=0.08)

        # Dashed threshold lines
        ax.axhline(18.5, color=COLOR_UNDERWEIGHT, ls="--", lw=0.8, alpha=0.5)
        ax.axhline(25.0, color=COLOR_NORMAL, ls="--", lw=0.8, alpha=0.5)
        ax.axhline(30.0, color=COLOR_OBESE, ls="--", lw=0.8, alpha=0.5)

        # Threshold labels on the right
        ax.text(1.02, 18.5, "18.5", color=COLOR_UNDERWEIGHT,
                transform=ax.get_yaxis_transform(), fontsize=7.5, va="center", ha="left")
        ax.text(1.02, 25.0, "25.0", color=COLOR_NORMAL,
                transform=ax.get_yaxis_transform(), fontsize=7.5, va="center", ha="left")
        ax.text(1.02, 30.0, "30.0", color=COLOR_OBESE,
                transform=ax.get_yaxis_transform(), fontsize=7.5, va="center", ha="left")

        # Data line plot
        ax.plot(dates, bmis, color="#60a5fa", marker="o", linewidth=2.5,
                markersize=6, markerfacecolor="#ffffff")

        # Axis styling
        ax.tick_params(colors=FG_MUTED, labelsize=8)
        for edge in ["top", "right"]:
            ax.spines[edge].set_visible(False)
        ax.spines["bottom"].set_color("#333333")
        ax.spines["left"].set_color("#333333")

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        fig.subplots_adjust(right=0.88, left=0.10, bottom=0.18, top=0.90)
        fig.autofmt_xdate(rotation=30)

        ax.set_title(f"BMI Trend  {user_name}",
                     fontsize=11, fontweight="bold", color=FG_TEXT, pad=10)
        ax.set_xlabel("Date", fontsize=9, color=FG_MUTED)
        ax.set_ylabel("BMI", fontsize=9, color=FG_MUTED)

        lo, hi = min(bmis), max(bmis)
        ax.set_ylim(max(0, min(18.0, lo - 3)), min(55, max(31.0, hi + 3)))

        # Handle single data point: expand X axis range so it renders properly
        if len(dates) == 1:
            ax.set_xlim(dates[0] - timedelta(days=1), dates[0] + timedelta(days=1))

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ─── DATABASE CHANGE ─────────────────────────────────────────────────────

    def on_change_database(self):
        """Open a file dialog to switch to a different CSV database."""
        path = filedialog.asksaveasfilename(
            title="Open or Create BMI CSV Database",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            defaultextension=".csv",
            initialfile=os.path.basename(self.csv_path))
        if path:
            self.csv_path = os.path.abspath(path)
            self.csv_display_var.set(os.path.basename(self.csv_path))
            try:
                database.init_csv(self.csv_path)
                self.current_user_name = None
                self.calc_user_var.set("")
                self.hide_results()
                self.refresh_profiles_list()
                messagebox.showinfo("Database Changed",
                                    f"Loaded: {os.path.basename(self.csv_path)}")
            except DatabaseError as e:
                messagebox.showerror("Error", str(e))
