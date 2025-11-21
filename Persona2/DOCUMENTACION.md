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

