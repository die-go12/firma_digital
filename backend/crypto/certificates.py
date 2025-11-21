import json
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

CERTS_PATH = "storage/certs"
CA_PUBLIC_KEY = f"{CERTS_PATH}/ca_public.pem"

class CertificadoInvalido(Exception):
    pass

class CertificateManager:

    def __init__(self):
        # Cargar clave pública de la CA
        with open(CA_PUBLIC_KEY, "rb") as f:
            self.ca_public_key = RSA.import_key(f.read())

    def cargar_certificado(self, ruta_cert):
        """Carga el certificado JSON desde archivo."""
        with open(ruta_cert, "r") as f:
            return json.load(f)

    def validar_certificado(self, cert):
        """
        Validaciones:
        - El certificado no está expirado
        - La firma CA es válida
        """
        # 1. Validar fechas
        ahora = datetime.utcnow()
        if not (cert["valid_from"] <= ahora.isoformat() <= cert["valid_to"]):
            raise CertificadoInvalido("El certificado está expirado o aún no es válido.")

        # 2. Validar firma digital del certificado (firma de la CA)
        firma_hex = cert["firma_ca"]
        firma = bytes.fromhex(firma_hex)

        # Crear copia del certificado SIN la firma para poder verificarlo
        cert_sin_firma = cert.copy()
        del cert_sin_firma["firma_ca"]

        h = SHA256.new(json.dumps(cert_sin_firma, sort_keys=True).encode())

        try:
            pkcs1_15.new(self.ca_public_key).verify(h, firma)
        except (ValueError, TypeError):
            raise CertificadoInvalido("Firma digital del certificado NO válida.")

        return True

    def obtener_public_key(self, cert):
        """
        Devuelve la clave pública del usuario (que viene dentro del certificado JSON).
        """
        return RSA.import_key(cert["public_key"].encode())
