
## **Persona 1 – Backend: Generación de llaves y firmas**

### **Objetivo**

Implementar el módulo de generación de llaves y firma de documentos PDF, incluyendo el guardado de las firmas y metadatos.

---

### **1. Configuración del entorno en Windows**

1. Abrir PowerShell en la carpeta del proyecto:

   ```
   C:\Users\luis\OneDrive\Documentos\firma_persona1
   ```

2. Crear un entorno virtual y activarlo:

   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Instalar las librerías necesarias:

   ```powershell
   pip install pycryptodome pypdf2 fastapi
   ```

---

### **2. Generación de llaves públicas y privadas**

1. Crear el archivo `generar_llaves.py` con el siguiente contenido:

   ```python
   from Crypto.PublicKey import RSA

   # Generar llaves RSA de 2048 bits
   key = RSA.generate(2048)

   private_key = key.export_key()
   public_key = key.publickey().export_key()

   # Guardar llaves en archivos
   with open("private.pem", "wb") as priv_file:
       priv_file.write(private_key)

   with open("public.pem", "wb") as pub_file:
       pub_file.write(public_key)

   print("Llaves generadas y guardadas en 'private.pem' y 'public.pem'")
   ```

2. Ejecutar el script:

   ```powershell
   python generar_llaves.py
   ```

   **Resultado esperado:**

   * `private.pem`
   * `public.pem`
   * Mensaje: `"Llaves generadas y guardadas en 'private.pem' y 'public.pem'"`

---

### **3. Firma de PDFs**

1. Crear el archivo `firmar_pdf.py`:

   ```python
   from Crypto.Signature import pkcs1_15
   from Crypto.Hash import SHA256
   from Crypto.PublicKey import RSA

   def firmar_pdf(pdf_path):
       # Cargar la clave privada
       with open("private.pem", "rb") as f:
           private_key = RSA.import_key(f.read())
       
       # Leer el contenido del PDF
       with open(pdf_path, "rb") as f:
           pdf_data = f.read()

       # Crear hash SHA256 del PDF
       h = SHA256.new(pdf_data)

       # Firmar el hash
       signature = pkcs1_15.new(private_key).sign(h)
       return signature
   ```

2. Probar la firma en Python interactivo:

   ```python
   from firmar_pdf import firmar_pdf

   firma = firmar_pdf('constancia.pdf')
   print(firma)
   ```

   **Resultado:** Se obtiene un objeto `bytes` que representa la firma digital del PDF.

---

### **4. Guardar la firma en un archivo**

1. Crear `guardar_firma.py`:

   ```python
   from firmar_pdf import firmar_pdf

   pdf_path = 'constancia.pdf'
   signature = firmar_pdf(pdf_path)

   # Guardar firma en un archivo
   with open('constancia_firma.bin', 'wb') as f:
       f.write(signature)

   print("Firma guardada en 'constancia_firma.bin'")
   ```

2. Ejecutar:

   ```powershell
   python guardar_firma.py
   ```

   **Resultado esperado:**

   * Archivo `constancia_firma.bin` creado con la firma digital del PDF.

---


