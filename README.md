# Password Manager (Python)

A local password manager built in Python with encrypted storage, password generation, and a desktop GUI.

This project was created to practice:
- Software architecture
- Cryptography fundamentals
- GUI development
- Secure storage design
- Git workflow

WARNING: This is an educational project and has not been security audited. Do not store critical passwords until thoroughly tested.

---

## Features

### Security
- AES-256-GCM encrypted vault
- Argon2id master password key derivation
- Encrypted backup export and import
- Auto-lock after inactivity
- Manual vault locking
- Clipboard auto-clear protection

### Password Management
- Secure password generator
- Password strength indicator
- Store:
  - Username
  - Password
  - URL
  - Tags
  - Notes
- Entry search
- Entry updates
- Entry deletion with confirmation

### GUI
- Two-panel interface layout
- Dark and light theme toggle
- Entry sidebar list
- Show or hide password
- Copy password button
- Open website button
- Form reset option

### Vault Management
- Create vault
- Unlock vault
- Change master password
- Encrypted backup system

---

## Installation

### Requirements

Python 3.10 or newer

Install dependencies:
pip install cryptography
