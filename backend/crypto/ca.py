import json
import os
from datetime import datetime, timedelta
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

CERTS_PATH = "storage/certs"
CA_PRIVATE_KEY = f"{CERTS_PATH}/ca_private.pem"
CA_PUBLIC_KEY = f"{CERTS_PATH}/ca_public.pem"

class AutoridadCertificadora:

    def __init__(self):
        os.makedirs(CERTS_PATH, exist_ok=True)

        # Si no existen llaves de la CA, crearlas
        if not os.path.exists(CA_PRIVATE_KEY):
            self._crear_llaves_ca()

        # Cargar llaves
        with open(CA_PRIVATE_KEY, "rb") as f:
            self.private_key = RSA.import_key(f.read())

        with open(CA_PUBLIC_KEY, "rb") as f:
            self.public_key = RSA.import_key(f.read())

    def _crear_llaves_ca(self):
        """Genera llaves RSA de la CA"""
        key = RSA.generate(2048)
        
        with open(CA_PRIVATE_KEY, "wb") as f:
            f.write(key.export_key())

        with open(CA_PUBLIC_KEY, "wb") as f:
            f.write(key.publickey().export_key())

        print("Llaves de la CA generadas")

    def emitir_certificado(self, nombre_usuario, public_key_pem):
        """
        Crea un certificado digital JSON firmándolo con la clave privada de la CA.
        """
        certificado = {
            "subject": nombre_usuario,
            "public_key": public_key_pem.decode(),
            "issuer": "CA-Simulada",
            "valid_from": datetime.utcnow().isoformat(),
            "valid_to": (datetime.utcnow() + timedelta(days=365)).isoformat()
        }

        # Crear hash del certificado
        h = SHA256.new(json.dumps(certificado, sort_keys=True).encode())

        # Firmar certificado
        firma = pkcs1_15.new(self.private_key).sign(h)
        certificado["firma_ca"] = firma.hex()

        # Guardar certificado
        cert_file = f"{CERTS_PATH}/{nombre_usuario}_cert.json"
        with open(cert_file, "w") as f:
            json.dump(certificado, f, indent=4)

        return certificado
