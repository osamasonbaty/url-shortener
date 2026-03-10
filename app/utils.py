import secrets
import string

ALPHABET = string.ascii_letters + string.digits  # a-zA-Z0-9


def generate_url_code(length: int = 6) -> str:
    if length <= 0:
        raise ValueError("Length must be positive")

    return "".join(secrets.choice(ALPHABET) for _ in range(length))
