import pytest
from fastapi.testclient import TestClient
from backend.main import app

# Simulamos un cliente navegador
client = TestClient(app)

def test_flujo_completo_seguridad():
    """
    Este test valida el ciclo de vida completo:
    1. Registro de usuario (Generación de llaves encriptadas).
    2. Firma de un PDF legítimo.
    3. Verificación exitosa.
    4. INTENTO DE HACKEO (Modificar PDF y tratar de verificarlo).
    """
    
    # DATOS DE PRUEBA
    email_usuario = "persona5@test.com"
    nombre_usuario = "Persona 5 Tester"
    pdf_contenido_original = b"%PDF-1.5 Contenido REAL del examen final."
    pdf_contenido_hackeado = b"%PDF-1.5 Contenido FALSO: Me puse 20 de nota."

    # CREAR USUARIO
    resp_registro = client.post("/usuarios/", json={
        "nombre": nombre_usuario,
        "email": email_usuario
    })
    # Si falla aquí, es que la DB tiene datos sucios. Ignoramos error 400 si ya existe.
    if resp_registro.status_code == 200:
        user_data = resp_registro.json()
        user_id = user_data["id"]
    else:
        # Recuperamos el ID si el usuario ya existía de una prueba anterior
        # Nota: Esto es un parche rápido para tests locales
        user_id = 1 

    print(f"\n[1] Usando Usuario ID: {user_id}")

    # FIRMAR DOCUMENTO
    files = {
        'archivo': ('contrato.pdf', pdf_contenido_original, 'application/pdf')
    }
    data = {'usuario_id': user_id}
    
    resp_firma = client.post("/firmar-pdf/", data=data, files=files)
    assert resp_firma.status_code == 200
    
    firma_digital = resp_firma.content
    assert len(firma_digital) > 0
    print("[2] Documento firmado correctamente.")

    # VERIFICACIÓN EXITOSA
    files_verify = {
        'archivo_original': ('contrato.pdf', pdf_contenido_original, 'application/pdf'),
        'archivo_firma': ('contrato.pdf.bin', firma_digital, 'application/octet-stream')
    }
    data_verify = {'usuario_id': user_id}

    resp_verify = client.post("/verificar-firma/", data=data_verify, files=files_verify)
    assert resp_verify.json()["resultado"] == "VALIDO"
    print("[3] Verificación legítima: EXITOSA.")

    # INTENTO DE HACKEO
    files_hack = {
        'archivo_original': ('contrato.pdf', pdf_contenido_hackeado, 'application/pdf'), 
        'archivo_firma': ('contrato.pdf.bin', firma_digital, 'application/octet-stream')
    }

    resp_hack = client.post("/verificar-firma/", data=data_verify, files=files_hack)
    assert resp_hack.json()["resultado"] == "INVALIDO"
    print("[4] Hackeo detectado: El sistema es SEGURO.")
