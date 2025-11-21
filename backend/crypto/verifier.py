from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from PyPDF2 import PdfReader
import json
import os
import base64

class Verificador:

    def __init__(self, certs_path="storage/certs"):
        self.certs_path = certs_path

    def cargar_certificado(self, usuario):
        cert_file = os.path.join(self.certs_path, f"{usuario}_cert.json")

        if not os.path.exists(cert_file):
            raise FileNotFoundError(f"Certificado no encontrado: {cert_file}")

        with open(cert_file, "r") as f:
            return json.load(f)

    def obtener_public_key(self, usuario):
        cert = self.cargar_certificado(usuario)
        key_pem = cert["public_key"]
        return RSA.import_key(key_pem.encode())

    def extraer_contenido_pdf(self, pdf_path):
        reader = PdfReader(pdf_path)
        contenido = b"".join(
            page.extract_text().encode("utf-8")
            for page in reader.pages
            if page.extract_text()
        )
        return contenido

    def verificar_pdf(self, pdf_path, firma, usuario):
        public_key = self.obtener_public_key(usuario)

        contenido = self.extraer_contenido_pdf(pdf_path)
        h = SHA256.new(contenido)

        try:
            pkcs1_15.new(public_key).verify(h, firma)
            return True
        except Exception:
            return False
