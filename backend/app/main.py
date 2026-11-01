from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routes import libros, admin

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API para la comparación inteligente de precios de libros en Chile",
    version="1.0.0",
)

# Configurar CORS para permitir conexiones desde React (frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar las rutas
app.include_router(libros.router, prefix="/libros", tags=["Libros"])
app.include_router(admin.router, prefix="/admin", tags=["Administración"])


@app.get("/")
def root():
    """Endpoint raíz para verificar que la API está activa."""
    return {
        "nombre": settings.APP_NAME,
        "version": "1.0.0",
        "estado": "activo",
    }
