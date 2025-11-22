# Archivo base para base de datos (SQLite)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Definimos la ruta de la base de datos

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. Creamos el motor (Engine)
# connect_args={"check_same_thread": False} es necesario SOLO para SQLite 
# porque SQLite por defecto solo permite un hilo a la vez, y FastAPI usa varios.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Creamos la sesión (SessionLocal)
# Esta será la "fábrica" de sesiones de base de datos. Cada petición tendrá su propia sesión.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Creamos la Clase Base
# Todos tus modelos (tablas) en models.py heredarán de esta clase para que SQLAlchemy sepa que son tablas.
Base = declarative_base()

# 5. Dependencia (Utilidad para obtener la DB en otros archivos)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()