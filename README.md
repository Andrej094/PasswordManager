# Password Manager (Python)

A local password manager built in Python with encrypted storage, password generation, and a desktop GUI.

This project was created to practice:
- Software architecture
- Cryptography fundamentals
- GUI development
- Secure storage design
- Git workflow

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

Install dependencies: **pip install cryptography**

---

## Running the program

Run: **python main.py**

---

## Building executable

Install PyInstaller: **pip install pyinstaller**

Build: **pyinstaller --onefile --windowed --name PasswordManager main.py**

Executable will appear in: **dist/**

---

## Usage

### First time setup

1. Click **Create Vault**
2. Create a master password
3. The vault unlocks automatically

### Add entry

Fill in:

- Site → service name
- Username → login name
- Password → generate or enter
- URL → login page (optional)
- Tags → categories (optional)
- Notes → extra information

Click: **Save / Update**

### Load entry

1. Select entry from list
2. Click: **Load Selected**

### Copy password

Click: **Copy Password**

Clipboard clears automatically after a short delay.

### Open login page

Add URL such as:


https://github.com/login


Click: **Open Website**

### Search entries

Search filters:
- Site name
- Username
- Tags
- Notes

---
## Known Limitations

This project is still experimental:

- No external security audit
- No password recovery if master password is lost
- Memory is not securely wiped (Python limitation)
- No mobile support
- No browser autofill

