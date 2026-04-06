import argparse

from .password_gen import generate_password
from .vault import VaultManager


def main():
    parser = argparse.ArgumentParser(description="Simple Password Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init")

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("site")
    add_parser.add_argument("username")
    add_parser.add_argument("--password", default=None)
    add_parser.add_argument("--generate", action="store_true")
    add_parser.add_argument("--length", type=int, default=20)

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("site")

    subparsers.add_parser("list")

    gen_parser = subparsers.add_parser("generate")
    gen_parser.add_argument("--length", type=int, default=20)

    args = parser.parse_args()
    vault = VaultManager()

    if args.command == "init":
        vault.init_vault()
        print("Vault created successfully.")

    elif args.command == "generate":
        print(generate_password(args.length))

    elif args.command == "add":
        password = args.password

        if args.generate or not password:
            password = generate_password(args.length)

        vault.add_entry(args.site, args.username, password)
        print(f"Entry saved for {args.site}")
        print(f"Password: {password}")

    elif args.command == "get":
        entry = vault.get_entry(args.site)
        if entry is None:
            print("Entry not found.")
            return

        print(f"Site: {args.site}")
        print(f"Username: {entry['username']}")
        print(f"Password: {entry['password']}")

    elif args.command == "list":
        sites = vault.list_sites()
        if not sites:
            print("No entries stored.")
            return

        for site in sites:
            print(site)