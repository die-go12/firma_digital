from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from backend.config import PIMIENTA_SECRETA  # <--- Importamos el secreto global

def _derivar_password_unico(email_usuario: str) -> str:
    """
    Reconstruye la contraseña única (Sal + Pimienta) para poder desencriptar la llave.
    Debe ser EXACTAMENTE igual a la función de keygen.py
    """
    combinacion = email_usuario + PIMIENTA_SECRETA
    h = SHA256.new(combinacion.encode())
    return h.hexdigest()

def sign_pdf_bytes(pdf_bytes: bytes, private_key_encrypted_bytes: bytes, email_usuario: str) -> bytes:
    """
    Firma digitalmente el PDF.
    
    Args:
        pdf_bytes: El archivo PDF.
        private_key_encrypted_bytes: La llave privada ENCRIPTADA (viene de la BD).
        email_usuario: El email del usuario (se usa como SAL para desbloquear la llave).
    """
    try:
        # 1. Reconstruimos la contraseña
        password_unico = _derivar_password_unico(email_usuario)

        # 2. Desencriptamos la llave privada en memoria RAM
        # Aquí está la magia: pasamos 'passphrase' para abrir el candado.
        private_key = RSA.import_key(private_key_encrypted_bytes, passphrase=password_unico)

        # 3. Crear hash del contenido COMPLETO
        h = SHA256.new(pdf_bytes)

        # 4. Firmar
        firma = pkcs1_15.new(private_key).sign(h)

        return firma

    except ValueError:
        # Esto pasa si la PIMIENTA está mal o si el EMAIL no coincide con la llave
        raise Exception("SEGURIDAD: No se pudo desencriptar la llave privada. Contraseña incorrecta.")