# Archivo base para modelos Pydantic
from pydantic import BaseModel
from datetime import datetime

# ESQUEMAS PARA USUARIOS 

# Base: Datos comunes
class UsuarioBase(BaseModel):
    nombre: str
    email: str

# Create: Lo que recibimos al crear (solo nombre y email)
class UsuarioCreate(UsuarioBase):
    pass

# Out: Lo que devolvemos al usuario (incluye ID y Fecha, pero NO la llave privada)
class UsuarioOut(UsuarioBase):
    id: int
    fecha_creacion: datetime
    # public_key: bytes  <-- Podríamos devolverla si quisiéramos
    
    class Config:
        from_attributes = True # Obligatorio para leer de SQLAlchemy

# ESQUEMAS PARA DOCUMENTOS 

class DocumentoOut(BaseModel):
    id: int
    nombre_archivo: str
    fecha_firma: datetime
    hash_documento: str
    ruta_storage: str
    
    class Config:
        from_attributes = True