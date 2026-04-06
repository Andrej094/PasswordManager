import tkinter as tk
from tkinter import messagebox

from .password_gen import generate_password
from .vault import VaultManager


class PasswordManagerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("520x540")

        self.vault = VaultManager(parent=root)

        title = tk.Label(root, text="Password Manager", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        self.site_label = tk.Label(root, text="Site")
        self.site_label.pack()
        self.site_entry = tk.Entry(root, width=40)
        self.site_entry.pack(pady=5)

        self.username_label = tk.Label(root, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(root, width=40)
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(root, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(root, width=40)
        self.password_entry.pack(pady=5)

        self.generate_button = tk.Button(root, text="Generate Password", command=self.generate_password)
        self.generate_button.pack(pady=5)

        self.add_button = tk.Button(root, text="Save Entry", command=self.save_entry)
        self.add_button.pack(pady=5)

        self.get_button = tk.Button(root, text="Get Entry", command=self.get_entry)
        self.get_button.pack(pady=5)

        self.list_button = tk.Button(root, text="List Sites", command=self.list_sites)
        self.list_button.pack(pady=5)

        self.init_button = tk.Button(root, text="Create Vault", command=self.create_vault)
        self.init_button.pack(pady=5)

        self.output = tk.Text(root, height=6, width=55)
        self.output.pack(pady=10)

    def generate_password(self):
        try:
            password = generate_password(20)
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def create_vault(self):
        try:
            self.vault.init_vault()
            messagebox.showinfo("Success", "Vault created successfully.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def save_entry(self):
        site = self.site_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not site or not username or not password:
            messagebox.showwarning("Missing Data", "Please fill all fields.", parent=self.root)
            return

        try:
            self.vault.add_entry(site, username, password)
            messagebox.showinfo("Success", f"Saved entry for {site}.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def get_entry(self):
        site = self.site_entry.get().strip()

        if not site:
            messagebox.showwarning("Missing Data", "Enter a site name.", parent=self.root)
            return

        try:
            entry = self.vault.get_entry(site)
            self.output.delete("1.0", tk.END)

            if entry is None:
                self.output.insert(tk.END, "Entry not found.\n")
                return

            self.output.insert(tk.END, f"Site: {site}\n")
            self.output.insert(tk.END, f"Username: {entry['username']}\n")
            self.output.insert(tk.END, f"Password: {entry['password']}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def list_sites(self):
        try:
            sites = self.vault.list_sites()
            self.output.delete("1.0", tk.END)

            if not sites:
                self.output.insert(tk.END, "No saved entries.\n")
                return

            for site in sites:
                self.output.insert(tk.END, f"{site}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)


def run_app():
    root = tk.Tk()
    PasswordManagerApp(root)
    root.mainloop()