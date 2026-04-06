import json
import os
from tkinter import simpledialog

from .crypto_utils import encrypt_vault, decrypt_vault


VAULT_FILE = "vault.json.enc"


class VaultManager:
    def __init__(self, parent=None, path: str = VAULT_FILE):
        self.parent = parent
        self.path = path

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def ask_master_password(self, title: str, prompt: str) -> str | None:
        return simpledialog.askstring(
            title,
            prompt,
            show="*",
            parent=self.parent
        )

    def init_vault(self) -> None:
        if self.exists():
            raise FileExistsError("Vault already exists.")

        master = self.ask_master_password("Create Vault", "Create master password:")
        if not master:
            raise ValueError("Master password is required.")

        confirm = self.ask_master_password("Create Vault", "Confirm master password:")
        if master != confirm:
            raise ValueError("Passwords do not match.")

        data = {"entries": {}}
        payload = encrypt_vault(master, data)

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def load(self) -> tuple[str, dict]:
        if not self.exists():
            raise FileNotFoundError("Vault does not exist. Create it first.")

        master = self.ask_master_password("Unlock Vault", "Enter master password:")
        if not master:
            raise ValueError("Master password is required.")

        with open(self.path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        data = decrypt_vault(master, payload)
        return master, data

    def save(self, master: str, data: dict) -> None:
        payload = encrypt_vault(master, data)

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def add_entry(self, site: str, username: str, password: str) -> None:
        master, data = self.load()
        data["entries"][site] = {
            "username": username,
            "password": password,
        }
        self.save(master, data)

    def get_entry(self, site: str) -> dict | None:
        _, data = self.load()
        return data["entries"].get(site)

    def list_sites(self) -> list[str]:
        _, data = self.load()
        return sorted(data["entries"].keys())