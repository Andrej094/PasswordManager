import json
import os
from datetime import datetime
from tkinter import simpledialog
from .crypto_utils import decrypt_vault, encrypt_vault

VAULT_FILE = "vault.json.enc"


class VaultManager:
    def __init__(self, parent=None, path: str = VAULT_FILE):
        self.parent = parent
        self.path = path
        self.master_password: str | None = None
        self.data: dict | None = None

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def is_unlocked(self) -> bool:
        return self.master_password is not None and self.data is not None

    def ask_password(self, title: str, prompt: str) -> str | None:
        return simpledialog.askstring(title, prompt, show="*",
                                      parent=self.parent)

    def _default_data(self) -> dict:
        return {
            "entries": {},
            "meta": {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            },
        }

    def _touch(self) -> None:
        if self.data is not None:
            self.data.setdefault("meta", {})["updated_at"] = datetime.now().isoformat(timespec="seconds")

    def init_vault(self) -> None:
        if self.exists():
            raise FileExistsError("Vault already exists.")

        master = self.ask_password("Create Vault", "Create master password:")
        if not master:
            raise ValueError("Master password is required.")
        confirm = self.ask_password("Create Vault", "Confirm master password:")
        if master != confirm:
            raise ValueError("Passwords do not match.")
        self.master_password = master
        self.data = self._default_data()
        self.save()

    def unlock(self) -> None:
        if not self.exists():
            raise FileNotFoundError("Vault does not exist. Create it first.")

        master = self.ask_password("Unlock Vault", "Enter master password:")
        if not master:
            raise ValueError("Master password is required.")
        with open(self.path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        data = decrypt_vault(master, payload)
        self.master_password = master
        self.data = data

    def lock(self) -> None:
        self.master_password = None
        self.data = None

    def require_unlocked(self) -> None:
        if not self.is_unlocked():
            raise ValueError("Vault is locked.")

    def save(self) -> None:
        self.require_unlocked()
        self._touch()
        payload = encrypt_vault(self.master_password, self.data)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def add_or_update_entry(
            self,
            site: str,
            username: str,
            password: str,
            url: str = "",
            notes: str = "",
            tags: str = "",
    ) -> None:
        self.require_unlocked()
        now = datetime.now().isoformat(timespec="seconds")
        entries = self.data.setdefault("entries", {})
        created_at = entries.get(site, {}).get("created_at", now)
        entries[site] = {
            "username": username,
            "password": password,
            "url": url,
            "notes": notes,
            "tags": tags,
            "created_at": created_at,
            "updated_at": now,
        }
        self.save()

    def get_entry(self, site: str) -> dict | None:
        self.require_unlocked()
        return self.data.get("entries", {}).get(site)

    def delete_entry(self, site: str) -> bool:
        self.require_unlocked()
        entries = self.data.get("entries", {})
        if site in entries:
            del entries[site]
            self.save()
            return True
        return False

    def list_sites(self) -> list[str]:
        self.require_unlocked()
        return sorted(self.data.get("entries", {}).keys(), key=str.lower)

    def search_sites(self, query: str) -> list[str]:
        self.require_unlocked()
        query = query.strip().lower()
        if not query:
            return self.list_sites()
        matches = []
        for site, entry in self.data.get("entries", {}).items():
            haystack = " ".join(
                [
                    site,
                    entry.get("username", ""),
                    entry.get("url", ""),
                    entry.get("notes", ""),
                    entry.get("tags", ""),
                ]
            ).lower()
        if query in haystack:
            matches.append(site)
        return sorted(matches, key=str.lower)

    def export_encrypted_backup(self, export_path: str) -> None:
        self.require_unlocked()
        payload = encrypt_vault(self.master_password, self.data)
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        def import_encrypted_backup(self, import_path: str) -> None:
            self.require_unlocked()
            with open(import_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            imported = decrypt_vault(self.master_password, payload)
            current_entries = self.data.setdefault("entries", {})
            for site, entry in imported.get("entries", {}).items():
                current_entries[site] = entry
            self.save()

    def change_master_password(self) -> None:
        self.require_unlocked()
        new_password = self.ask_password("Change Master Password", "Enter new master password: ")
        if not new_password:
            raise ValueError("New master password is required.")
        confirm = self.ask_password("Change Master Password", "Confirm new master password: ")
        if new_password != confirm:
            raise ValueError("Passwords do not match.")
        self.master_password = new_password
        self.save()
