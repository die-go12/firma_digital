from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

def sign_pdf_bytes(pdf_bytes: bytes, private_key_bytes: bytes) -> bytes:
    """
    Firma digitalmente el contenido binario de un PDF.
    
    Args:
        pdf_bytes (bytes): El contenido crudo del archivo PDF.
        private_key_bytes (bytes): El contenido crudo de la llave privada (.pem).
        
    Returns:
        bytes: La firma digital binaria.
    """
    # 1. Cargar la clave privada desde los bytes
    private_key = RSA.import_key(private_key_bytes)

    # 2. Crear hash del contenido COMPLETO del archivo (no solo el texto)
    # Esto asegura que si cambia un solo bit del PDF, la firma se rompe.
    h = SHA256.new(pdf_bytes)

    # 3. Firmar el hash usando PKCS#1 v1.5
    firma = pkcs1_15.new(private_key).sign(h)

    return firma