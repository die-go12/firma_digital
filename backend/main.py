import os
import shutil
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

# IMPORTACIONES DE LA ARQUITECTURA
from backend.db import database
from backend.models import models, schemas
# Importamos TODOS los módulos de criptografia
from backend.crypto import keygen, signer, ca, verifier

# Inicializar Base de Datos (Crea el archivo sql_app.db si no existe)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Sistema de Firma Digital - Equipo Cripto")

# Rutas de almacenamiento
STORAGE_PDF_PATH = "storage/signed_pdfs"
CERTS_PATH = "storage/certs"
os.makedirs(STORAGE_PDF_PATH, exist_ok=True)
os.makedirs(CERTS_PATH, exist_ok=True)

# Dependencia de BD
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"mensaje": "API Activa. Sistema listo para operar."}


# 1. GESTIÓN DE USUARIOS (Generación de Llaves)

@app.post("/usuarios/", response_model=schemas.UsuarioOut)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar duplicados
    db_user = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # GENERAR LLAVES (Llamada a keygen.py)
    try:
        priv, pub = keygen.generate_keys_bytes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando llaves: {e}")

    # Guardar en BD
    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        public_key=pub,
        private_key=priv
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


# 2. FIRMA DE DOCUMENTOS (Usa DB y guarda .bin)

@app.post("/firmar-pdf/")
async def firmar_documento(
    usuario_id: int = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Buscar usuario y su llave privada
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Leer PDF en memoria
    contenido_pdf = await archivo.read()

    # FIRMAR (Llamada a signer.py)
    try:
        firma_digital = signer.sign_pdf_bytes(contenido_pdf, usuario.private_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error firmando: {e}")

    # A. Guardar PDF firmado físico
    nombre_pdf = f"firmado_{usuario.nombre}_{archivo.filename}"
    ruta_pdf = os.path.join(STORAGE_PDF_PATH, nombre_pdf)
    
    await archivo.seek(0) # Regresar el cursor al inicio
    with open(ruta_pdf, "wb") as buffer:
        shutil.copyfileobj(archivo.file, buffer)

    # B. Guardar archivo de FIRMA (.bin) para pruebas manuales
    # Esto te permitirá probar el endpoint de verificar luego
    nombre_firma = f"{nombre_pdf}.bin"
    ruta_firma = os.path.join(STORAGE_PDF_PATH, nombre_firma)
    with open(ruta_firma, "wb") as f:
        f.write(firma_digital)

    # C. Registrar en BD
    nuevo_doc = models.Documento(
        nombre_archivo=archivo.filename,
        ruta_storage=ruta_pdf,
        hash_documento="SHA256-Calculado",
        firma_digital=firma_digital,
        usuario_id=usuario.id
    )
    db.add(nuevo_doc)
    db.commit()
    db.refresh(nuevo_doc)

    return {
        "status": "Firmado correctamente",
        "documento_id": nuevo_doc.id,
        "ruta_pdf": ruta_pdf,
        "ruta_firma_debug": ruta_firma, # Te devolvemos esta ruta para que sepas cual subir al verificador
        "mensaje": "Se generó el PDF y un archivo .bin con la firma suelta."
    }


# 3. VERIFICACIÓN DE FIRMAS (El Juez)

@app.post("/verificar-firma/")
async def verificar_firma(
    usuario_id: int = Form(...),
    archivo_original: UploadFile = File(...),
    archivo_firma: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Sube el PDF original + el archivo .bin generado anteriormente.
    """
    # Buscar la llave pública del supuesto firmante
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario (presunto firmante) no encontrado")

    # Leer archivos en memoria
    pdf_bytes = await archivo_original.read()
    firma_bytes = await archivo_firma.read()

    # Verificar matemáticamente
    es_valida = verifier.verify_signature_bytes(
        pdf_bytes=pdf_bytes,
        signature_bytes=firma_bytes,
        public_key_bytes=usuario.public_key
    )

    if es_valida:
        return {"resultado": "VALIDO", "detalle": "La firma es AUTÉNTICA y el documento NO ha sido alterado."}
    else:
        return {"resultado": "INVALIDO", "detalle": "La firma NO corresponde o el documento fue modificado."}


# 4. CERTIFICADOS (Integración con CA)

@app.post("/emitir-certificado/")
def emitir_certificado_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    autoridad = ca.AutoridadCertificadora()
    try:
        pub_key_str = usuario.public_key.decode('utf-8')
        cert = autoridad.emitir_certificado(usuario.nombre, pub_key_str)
        
        # Opcional: Guardar copia del JSON en disco
        ruta_json = os.path.join(CERTS_PATH, f"{usuario.nombre}_cert.json")
        import json
        with open(ruta_json, "w") as f:
            json.dump(cert, f, indent=4)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error CA: {e}")
        
    return cert

@app.get("/listar-certificados-locales")
def listar_certs():
    if not os.path.exists(CERTS_PATH):
        return []
    return [f for f in os.listdir(CERTS_PATH) if f.endswith(".json")]