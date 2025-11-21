import os
from backend.crypto.ca import AutoridadCertificadora

def main():
    print("Generando certificado para usuario_test...")

    # Crear CA simulada
    ca = AutoridadCertificadora()

    # Ruta absoluta a la clave pública del usuario
    pub_path = os.path.abspath("storage/keys/public.pem")
    print("Leyendo clave pública desde:", pub_path)

    with open(pub_path, "rb") as f:
        public_key = f.read()

    # Emitir certificado
    cert = ca.emitir_certificado("usuario_test", public_key)
    print("Certificado generado correctamente.")
    print(cert)

if __name__ == "__main__":
    main()
