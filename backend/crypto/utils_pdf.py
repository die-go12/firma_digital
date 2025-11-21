# backend/crypto/utils_pdf.py

from PyPDF2 import PdfReader
from Crypto.Hash import SHA256

def extraer_contenido_pdf(pdf_path):
    """
    Extrae el contenido textual del PDF y lo convierte en bytes.
    """
    reader = PdfReader(pdf_path)
    contenido = b""

    for page in reader.pages:
        texto = page.extract_text()
        if texto:
            contenido += texto.encode("utf-8")

    return contenido


def hash_pdf(pdf_path):
    """
    Calcula el hash SHA256 del contenido del PDF.
    """
    contenido = extraer_contenido_pdf(pdf_path)
    h = SHA256.new(contenido)
    return h
