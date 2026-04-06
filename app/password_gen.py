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