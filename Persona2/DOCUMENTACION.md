## **Persona 2 – Backend: Verificación y Autoridad Certificadora (CA simulada)**

### **Objetivo**

Implementar el módulo de verificación de firmas digitales en PDFs y la Autoridad Certificadora simulada para generar y autenticar certificados de usuarios.

---

### **1. Configuración del entorno en Windows**

1. Abrir PowerShell en la carpeta del proyecto:
```powershell
C:\Users\AQUINO\Documents\Cripto\firma_digital-main
```

2. Activar el entorno virtual si ya existe:

```powershell
.\venv\Scripts\activate
```

3. Instalar librerías necesarias (si no se instalaron aún):

```powershell
pip install pycryptodome pypdf2 fastapi
```

### **2. Creación del módulo de Verificación de PDFs**

1. Crear verifier.py en backends/crypto:
```powershell
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from PyPDF2 import PdfReader

class Verificador:
    def verificar_pdf(self, pdf_path, firma, usuario_cert_json):
        # Leer el PDF
        reader = PdfReader(pdf_path)
        contenido = b"".join(
            page.extract_text().encode('utf-8') for page in reader.pages if page.extract_text()
        )

        # Leer clave pública desde el certificado JSON
        import json
        with open(usuario_cert_json, 'r') as f:
            cert = json.load(f)
        public_key = RSA.import_key(cert['public_key'])

        # Crear hash del contenido
        h = SHA256.new(contenido)

        # Verificar firma
        try:
            pkcs1_15.new(public_key).verify(h, firma)
            return True
        except (ValueError, TypeError):
            return False

```
2. Probar verificación
```powershell
from verifier import Verificador

ver = Verificador()
resultado = ver.verificar_pdf('storage/temp/constancia.pdf', open('storage/signed_pdfs/constancia_firma.bin', 'rb').read(), 'storage/certs/usuario_test_cert.json')
print(resultado)  # True si la firma es válida
```

### **3. Autoridad Certificadora Simulada (CA)**

1. Crear ca.py
```powershell
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

```

2. Emitir certificado
```powershell
from backend.crypto.ca import AutoridadCertificadora

ca = AutoridadCertificadora()
certificado = ca.emitir_certificado("usuario_test", open("storage/keys/public.pem", "rb").read())
print(certificado)
```

### **4. Creación de certificados**

1. Crear generar_certificado.py
```powershell
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
```
2.- Crear certificado
```powershell
python generar_certificado.py
```

### **5. Gestión de certificados**

1. Crear certificates.py
```powershell
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
```

2. Validar certificado.
```powershell
from backend.crypto.certificates import CertificateManager

manager = CertificateManager()
cert = manager.cargar_certificado("storage/certs/usuario_test_cert.json")
manager.validar_certificado(cert)
public_key = manager.obtener_public_key(cert)
```

### **6. Realizar pruebas unitarias**

1. Crear test_verifier.py en /tests
```powershell
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

```

2. Realizar test
```powershell
pytest tests/test_verifier.py
```

### **7. Interfaz Web con FastApi**

1. Editar main.py
```powershell
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
```

2. Ejecutar servidor
```powershell
uvicorn backend.main:app --reload
```

3. Ingresar a http://127.0.0.1:8000/docs.

**¡Y listo!**

En dicho enlace se podrán probar los métodos creados en esta parte. Pudiendo así generar las keys, firmar documentos, verificar las firmas y observar los certificados.
