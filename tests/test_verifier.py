from backend.crypto.verifier import Verificador
import os

def test_verificacion_basica():
    # Rutas
    cert_path = "storage/certs/usuario_test_cert.json"
    pdf_path = "storage/temp/constancia.pdf"
    firma_path = "storage/signed_pdfs/constancia_firma.bin"

    # Verificar que los archivos existen
    assert os.path.exists(cert_path)
    assert os.path.exists(pdf_path)
    assert os.path.exists(firma_path)

    # Crear verificador
    ver = Verificador()

    # Cargar firma
    with open(firma_path, "rb") as f:
        firma = f.read()

    # Verificación de PDF firmado
    resultado = ver.verificar_pdf(pdf_path, firma, "usuario_test")
    assert resultado is True
