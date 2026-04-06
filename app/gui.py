import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .password_gen import generate_password, password_strength
from .vault import VaultManager

AUTO_LOCK_MS = 5 * 60 * 1000
CLIPBOARD_CLEAR_MS = 20 * 1000


class PasswordManagerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("980x700")
        self.root.minsize(940, 660)

        self.dark_mode = True
        self.selected_site = None
        self.auto_lock_job = None
        self.clipboard_job = None

        self.style = ttk.Style()
        self.configure_theme()

        self.vault = VaultManager(parent=root)
        self.site_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.tags_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.length_var = tk.IntVar(value=20)
        self.status_var = tk.StringVar(value="Locked")
        self.strength_var = tk.StringVar(value="Strength: —")
        self.password_visible = tk.BooleanVar(value=False)

        self.search_var.trace_add("write", self.on_search_change)
        self.password_var.trace_add("write", self.on_password_change)

        self.build_layout()
        self.refresh_buttons()
        self.refresh_site_list([])
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.prompt_unlock_on_start()

    def configure_theme(self):
        if self.dark_mode:
            bg = "#10151c"
            panel = "#18202a"
            fg = "#e8eef5"
            entry = "#223041"
            accent = "#52b3ff"
            muted = "#b7c4d3"
        else:
            bg = "#f3f6fa"
            panel = "#ffffff"
            fg = "#102030"
            entry = "#edf2f7"
            accent = "#2563eb"
            muted = "#4b5563"
        self.colors = {
            "bg": bg,
            "panel": panel,
            "fg": fg,
            "entry": entry,
            "accent": accent,
            "muted": muted,
        }

        self.root.configure(bg=bg)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background=bg)
        self.style.configure("Panel.TFrame", background=panel)
        self.style.configure("TLabel", background=bg, foreground=fg,
                             font=("Segoe UI", 10))
        self.style.configure("Muted.TLabel", background=bg, foreground=muted,
                             font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background=bg, foreground=fg,
                             font=("Segoe UI", 22, "bold"))
        self.style.configure("Section.TLabel", background=panel, foreground=fg,
                             font=("Segoe UI", 12, "bold"))

        self.style.configure("TButton", font=("Segoe UI", 10), padding=8)
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"),
                             padding=8)
        self.style.map("Accent.TButton", background=[("active", accent), ("!disabled", accent)],
                       foreground=[("!disabled", "white")])
        self.style.configure("TEntry", fieldbackground=entry, foreground=fg,
                             insertcolor=fg, borderwidth=1)
        self.style.configure("TSpinbox", fieldbackground=entry,
                             foreground=fg,
                             arrowsize=14)
        self.style.configure("Horizontal.TProgressbar", troughcolor=entry)

    def build_layout(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(header, text="Password Manager",
                  style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Toggle Theme",
                   command=self.toggle_theme).pack(side="right", padx=(8, 0))
        ttk.Button(header, text="Lock",
                   command=self.lock_vault).pack(side="right")
        ttk.Button(header, text="Unlock",
                   command=self.unlock_vault).pack(side="right", padx=(0, 8))

        body = ttk.Frame(container)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body, style="Panel.TFrame", padding=14)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = ttk.Frame(body, style="Panel.TFrame", padding=14)
        right.grid(row=0, column=1, sticky="nsew")
        self.build_left_panel(left)
        self.build_right_panel(right)

        footer = ttk.Frame(container)
        footer.pack(fill="x", pady=(12, 0))
        ttk.Label(footer, textvariable=self.status_var,
                  style="Muted.TLabel").pack(side="left")
        ttk.Label(footer, text="Educational project. Don’t store real passwordsyet.",
                  style="Muted.TLabel").pack(side="right")

    def build_left_panel(self, parent):
        ttk.Label(parent, text="Vault", style="Section.TLabel").pack(anchor="w")

        search_row = ttk.Frame(parent, style="Panel.TFrame")
        search_row.pack(fill="x", pady=(12, 8))
        ttk.Label(search_row, text="Search", style="Muted.TLabel").pack(anchor="w")
        self.search_entry = ttk.Entry(search_row, textvariable=self.search_var)
        self.search_entry.pack(fill="x", pady=(4, 0))

        self.site_listbox = tk.Listbox(
            parent,
            height=18,
            bg=self.colors["entry"],
            fg=self.colors["fg"],
            selectbackground=self.colors["accent"],
            selectforeground="white",
            highlightthickness=0,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        self.site_listbox.pack(fill="both", expand=True, pady=(4, 10))
        self.site_listbox.bind("<<ListboxSelect>>", self.on_site_select)
        self.site_listbox.bind("<Double-Button-1>", lambda event:
        self.load_selected_entry())
        row1 = ttk.Frame(parent, style="Panel.TFrame")
        row1.pack(fill="x", pady=4)
        ttk.Button(row1, text="Refresh",
                   command=self.refresh_sites).pack(side="left", expand=True, fill="x")
        ttk.Button(row1, text="Load Selected",
                   command=self.load_selected_entry).pack(side="left", expand=True, fill="x",
                                                          padx=6)
        row2 = ttk.Frame(parent, style="Panel.TFrame")
        row2.pack(fill="x", pady=4)
        ttk.Button(row2, text="Export Backup",
                   command=self.export_backup).pack(side="left", expand=True, fill="x")
        ttk.Button(row2, text="Import Backup",
                   command=self.import_backup).pack(side="left", expand=True, fill="x", padx=6)
        row3 = ttk.Frame(parent, style="Panel.TFrame")
        row3.pack(fill="x", pady=4)
        ttk.Button(row3, text="Change Master Password",
                   command=self.change_master_password).pack(side="left", expand=True, fill="x")
        ttk.Button(row3, text="Create Vault",
                   command=self.create_vault).pack(side="left", expand=True, fill="x", padx=6)

    def build_right_panel(self, parent):
        ttk.Label(parent, text="Entry Details",
                  style="Section.TLabel").grid(row=0, column=0, columnspan=4, sticky="w")
        for col in range(4):
            parent.columnconfigure(col, weight=1)
        self.add_labeled_entry(parent, "Site", self.site_var, 1)
        self.add_labeled_entry(parent, "Username", self.username_var, 3)
        self.add_password_row(parent, 5)
        self.add_labeled_entry(parent, "URL", self.url_var, 7)
        self.add_labeled_entry(parent, "Tags (comma separated)", self.tags_var,
                               9)
        ttk.Label(parent, text="Notes", style="Muted.TLabel").grid(row=11,
                                                                   column=0, columnspan=4, sticky="w", pady=(10, 4))
        self.notes_text = tk.Text(
            parent,
            height=7,
            wrap="word",
            bg=self.colors["entry"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            highlightthickness=0,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        self.notes_text.grid(row=12, column=0, columnspan=4, sticky="nsew")
        parent.rowconfigure(12, weight=1)
        ttk.Label(parent, textvariable=self.strength_var,
                  style="Muted.TLabel").grid(row=13, column=0, sticky="w", pady=(10, 4))
        self.strength_bar = ttk.Progressbar(parent, orient="horizontal",
                                            mode="determinate", maximum=100)
        self.strength_bar.grid(row=14, column=0, columnspan=4, sticky="ew")
        generator_row = ttk.Frame(parent, style="Panel.TFrame")
        generator_row.grid(row=15, column=0, columnspan=4, sticky="ew",
                           pady=(12, 4))
        generator_row.columnconfigure(1, weight=1)
        ttk.Label(generator_row, text="Generated length",
                  style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        self.length_spin = ttk.Spinbox(generator_row, from_=12, to=64,
                                       textvariable=self.length_var, width=8)
        self.length_spin.grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Button(generator_row, text="Generate", style="Accent.TButton",
                   command=self.generate_password).grid(row=0, column=2, padx=(10, 0))
        ttk.Button(generator_row, text="Copy Password",
                   command=self.copy_password).grid(row=0, column=3, padx=(6, 0))
        actions1 = ttk.Frame(parent, style="Panel.TFrame")
        actions1.grid(row=16, column=0, columnspan=4, sticky="ew", pady=(12, 4))
        for c in range(4):
            actions1.columnconfigure(c, weight=1)
        ttk.Button(actions1, text="Save / Update", style="Accent.TButton",
                   command=self.save_entry).grid(row=0, column=0, sticky="ew")
        ttk.Button(actions1, text="Delete",
                   command=self.delete_entry).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(actions1, text="Clear Form",
                   command=self.clear_form).grid(row=0, column=2, sticky="ew")
        ttk.Button(actions1, text="Load Selected",
                   command=self.load_selected_entry).grid(row=0, column=3, sticky="ew", padx=(6,
                                                                                              0))

    def add_labeled_entry(self, parent, label_text, variable, row):
        ttk.Label(parent, text=label_text, style="Muted.TLabel").grid(row=row,
                                                                      column=0, columnspan=4, sticky="w", pady=(10, 4))
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row + 1, column=0, columnspan=4, sticky="ew")
        return entry

    def add_password_row(self, parent, row):
        ttk.Label(parent, text="Password", style="Muted.TLabel").grid(row=row,
                                                                      column=0, columnspan=4, sticky="w", pady=(10, 4))

        self.password_entry = ttk.Entry(parent, textvariable=self.password_var,
                                        show="*")
        self.password_entry.grid(row=row + 1, column=0, columnspan=3,
                                 sticky="ew")
        ttk.Checkbutton(parent, text="Show",
                        command=self.toggle_password_visibility,
                        variable=self.password_visible).grid(row=row + 1, column=3, sticky="e")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.configure_theme()
        self.rebuild_ui()

    def rebuild_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.build_layout()
        self.refresh_buttons()
        self.refresh_sites()
        self.on_password_change()
        current_site = self.site_var.get().strip()
        if current_site:
            self.select_site_in_list(current_site)

    def set_status(self, message: str):
        self.status_var.set(message)

    def touch_activity(self):
        if self.auto_lock_job:
            self.root.after_cancel(self.auto_lock_job)

        if self.vault.is_unlocked():
            self.auto_lock_job = self.root.after(AUTO_LOCK_MS, self.auto_lock_due_to_timeout)

    def auto_lock_due_to_timeout(self):
        self.lock_vault(show_message=True)

    def refresh_buttons(self):
        state = "normal" if self.vault.is_unlocked() else "disabled"
        self.set_status("Unlocked" if self.vault.is_unlocked() else "Locked")

    def prompt_unlock_on_start(self):
        if self.vault.exists():
            self.unlock_vault()

        else:
            self.set_status("No vault yet. Create one to get started.")

    def create_vault(self):
        try:
            self.vault.init_vault()
            self.refresh_buttons()
            self.refresh_sites()
            self.touch_activity()
            messagebox.showinfo("Success", "Vault created and unlocked.",
                                parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def unlock_vault(self):
        try:
            self.vault.unlock()
            self.refresh_buttons()
            self.refresh_sites()
            self.touch_activity()
            messagebox.showinfo("Unlocked", "Vault unlocked.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def lock_vault(self, show_message: bool = False):
        self.vault.lock()
        self.clear_form()
        self.refresh_site_list([])
        self.refresh_buttons()
        if self.auto_lock_job:
            self.root.after_cancel(self.auto_lock_job)
            self.auto_lock_job = None
        if show_message:
            messagebox.showinfo("Locked", "Vault locked.", parent=self.root)

    def on_password_change(self, *_):
        label, value = password_strength(self.password_var.get())
        self.strength_var.set(f"Strength: {label}")
        self.strength_bar["value"] = value

    def toggle_password_visibility(self):
        self.password_entry.config(show="" if self.password_visible.get() else
        "*")

    def generate_password(self):
        try:
            password = generate_password(self.length_var.get())
            self.password_var.set(password)
            self.touch_activity()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def save_entry(self):
        if not self.vault.is_unlocked():
            messagebox.showwarning("Locked", "Unlock the vault first.",
                                   parent=self.root)
            return

        site = self.site_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        url = self.url_var.get().strip()
        tags = self.tags_var.get().strip()
        notes = self.notes_text.get("1.0", tk.END).strip()

        if not site or not username or not password:
            messagebox.showwarning("Missing Data",
                                   "Site, username, and password are required.", parent=self.root)
            return

        try:
            self.vault.add_or_update_entry(site, username, password, url, notes, tags)
            self.refresh_sites()
            self.select_site_in_list(site)
            self.touch_activity()
            messagebox.showinfo("Saved", f"Saved entry for {site}.",
                                parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def delete_entry(self):
        if not self.vault.is_unlocked():
            messagebox.showwarning("Locked", "Unlock the vault first.",
                                   parent=self.root)
            return

        site = self.site_var.get().strip()
        if not site:
            messagebox.showwarning("Missing Data", "Choose or enter a site to delete.", parent=self.root)
            return
        confirmed = messagebox.askyesno("Confirm Delete", f"Delete entry for {site}?", parent=self.root)
        if not confirmed:
            return

        try:
            deleted = self.vault.delete_entry(site)
            if not deleted:
                messagebox.showinfo("Not Found", "Entry not found.",
                                    parent=self.root)
                return
            self.clear_form()
            self.refresh_sites()
            self.touch_activity()
            messagebox.showinfo("Deleted", f"Deleted {site}.", parent=self.root)

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def refresh_sites(self):
        if not self.vault.is_unlocked():
            self.refresh_site_list([])
            return
        try:
            sites = self.vault.search_sites(self.search_var.get())
            self.refresh_site_list(sites)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def refresh_site_list(self, sites):
        self.site_listbox.delete(0, tk.END)
        for site in sites:
            self.site_listbox.insert(tk.END, site)

    def on_search_change(self, *_):
        self.refresh_sites()

    def on_site_select(self, _event=None):
        selection = self.site_listbox.curselection()
        if not selection:
            return
        self.selected_site = self.site_listbox.get(selection[0])

    def load_selected_entry(self):
        if not self.vault.is_unlocked():
            messagebox.showwarning("Locked", "Unlock the vault first.",
                                   parent=self.root)
            return

        selection = self.site_listbox.curselection()
        site = self.site_var.get().strip()
        if selection:
            site = self.site_listbox.get(selection[0])

        if not site:
            messagebox.showwarning("No Selection", "Select a site from the list or enter one.", parent=self.root)
            return

        try:
            entry = self.vault.get_entry(site)
            if not entry:
                messagebox.showinfo("Not Found", "Entry not found.",
                                    parent=self.root)
                return
            self.site_var.set(site)
            self.username_var.set(entry.get("username", ""))
            self.password_var.set(entry.get("password", ""))
            self.url_var.set(entry.get("url", ""))
            self.tags_var.set(entry.get("tags", ""))
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", entry.get("notes", ""))
            self.select_site_in_list(site)
            self.touch_activity()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def select_site_in_list(self, site: str):
        items = self.site_listbox.get(0, tk.END)
        for index, item in enumerate(items):
            if item == site:
                self.site_listbox.selection_clear(0, tk.END)
                self.site_listbox.selection_set(index)
                self.site_listbox.see(index)
                break

    def clear_form(self):
        self.site_var.set("")
        self.username_var.set("")
        self.password_var.set("")
        self.url_var.set("")
        self.tags_var.set("")
        self.notes_text.delete("1.0", tk.END)

    def copy_password(self):
        password = self.password_var.get().strip()
        if not password:
            messagebox.showwarning("No Password", "There is no password to copy.", parent=self.root)
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        if self.clipboard_job:
            self.root.after_cancel(self.clipboard_job)
        self.clipboard_job = self.root.after(CLIPBOARD_CLEAR_MS,
                                             self.clear_clipboard)
        self.touch_activity()
        messagebox.showinfo("Copied", "Password copied. Clipboard will clear in seconds.", parent=self.root)

    def clear_clipboard(self):
        self.root.clipboard_clear()
        self.clipboard_job = None

    def export_backup(self):
        if not self.vault.is_unlocked():
            messagebox.showwarning("Locked", "Unlock the vault first.",
                                   parent=self.root)
            return
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export encrypted backup",
            defaultextension=".encbak",
            filetypes=[("Encrypted Backup", "*.encbak"), ("JSON Files",
                                                          "*.json"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            self.vault.export_encrypted_backup(path)
            self.touch_activity()
            messagebox.showinfo("Exported", "Encrypted backup exported.",
                                parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def import_backup(self):
        if not self.vault.is_unlocked():
            messagebox.showwarning("Locked", "Unlock the vault first.",
                                   parent=self.root)
            return
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Import encrypted backup",
            filetypes=[("Encrypted Backup", "*.encbak"), ("JSON Files",
                                                          "*.json"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            self.vault.import_encrypted_backup(path)
            self.refresh_sites()
            self.touch_activity()
            messagebox.showinfo("Imported", "Encrypted backup imported.",
                            parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def change_master_password(self):
        if not self.vault.is_unlocked():
            messagebox.showwarning("Locked", "Unlock the vault first.",
                                   parent=self.root)
            return

        try:
            self.vault.change_master_password()
            self.touch_activity()
            messagebox.showinfo("Updated", "Master password changed.",
                                parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def on_close(self):
        self.clear_clipboard()
        self.lock_vault()
        self.root.destroy()

def run_app():
    root = tk.Tk()
    PasswordManagerApp(root)
    root.mainloop()