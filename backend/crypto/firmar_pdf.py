from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from PyPDF2 import PdfReader

def firmar_pdf(pdf_path, private_key_path='private.pem'):
    # Leer el PDF
    reader = PdfReader(pdf_path)
    contenido = b"".join(page.extract_text().encode('utf-8') for page in reader.pages if page.extract_text())

    # Cargar clave privada
    with open(private_key_path, 'rb') as f:
        private_key = RSA.import_key(f.read())

    # Crear hash del contenido
    h = SHA256.new(contenido)

    # Firmar hash
    firma = pkcs1_15.new(private_key).sign(h)

    return firma
