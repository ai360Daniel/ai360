import hashlib

def hash_password(password: str) -> str:
    """
    Genera el hash SHA-256 de una contraseña.

    Args:
        password (str): La contraseña en texto plano.

    Returns:
        str: El hash de la contraseña.
    """
    return hashlib.sha256(password.encode()).hexdigest()