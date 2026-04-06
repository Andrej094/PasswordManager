import secrets
import string

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"
ALL = LOWER + UPPER + DIGITS + SYMBOLS


def generate_password(length: int = 20) -> str:
    if length < 12:
        raise ValueError("Password length must be at least 12.")

    chars = [
        secrets.choice(LOWER),
        secrets.choice(UPPER),
        secrets.choice(DIGITS),
        secrets.choice(SYMBOLS),
    ]

    chars.extend(secrets.choice(ALL) for _ in range(length - 4))

    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]

    return "".join(chars)


def password_strength(password: str) -> tuple[str, int]:
    score = 0

    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    if any(c in LOWER for c in password):
        score += 1
    if any(c in UPPER for c in password):
        score += 1
    if any(c in DIGITS for c in password):
        score += 1
    if any(c in SYMBOLS for c in password):
        score += 1

    if score <= 2:
        return "Weak", 25
    if score <= 4:
        return "Medium", 55
    if score == 5:
        return "Strong", 80
    return "Very Strong", 100