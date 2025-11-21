from fastapi import FastAPI, UploadFile, File
from backend.crypto.generar_llaves import generar_llaves
from backend.crypto.verifier import Verificador
from backend.crypto.ca import AutoridadCertificadora
from backend.crypto.firmar_pdf import firmar_pdf
import shutil
import os

app = FastAPI()

verificador = Verificador()
ca = AutoridadCertificadora()

# --- Ruta raíz ---
@app.get("/")
def root():
    return {"message": "Simulador de firmas digitales"}

# --- Endpoint para generar llaves ---
@app.post("/generate-key")
def api_generate_key():
    generar_llaves()
    return {"message": "Llaves generadas correctamente."}

# --- Endpoint para firmar PDF ---
@app.post("/sign-document")
def api_sign_document(file: UploadFile = File(...)):
    temp_path = f"storage/temp/{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    firma = firmar_pdf(temp_path, private_key_path="storage/keys/private.pem")
    firma_path = f"storage/signed_pdfs/{file.filename}_firma.bin"
    with open(firma_path, "wb") as f:
        f.write(firma)

    return {
        "message": "Documento firmado correctamente.",
        "firma_path": firma_path
    }

# --- Endpoint para verificar PDF ---
@app.post("/verify-signature")
def api_verify_signature(file: UploadFile = File(...), firma_path: str = ""):
    temp_path = f"storage/temp/{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    with open(firma_path, "rb") as f:
        firma = f.read()

    resultado = verificador.verificar_pdf(temp_path, firma, "usuario_test")
    return {"verificado": resultado}

# --- Endpoint para listar certificados ---
@app.get("/get-certificates")
def api_get_certificates():
    certs_dir = "storage/certs"
    certificados = [f for f in os.listdir(certs_dir) if f.endswith(".json")]
    return {"certificados": certificados}
