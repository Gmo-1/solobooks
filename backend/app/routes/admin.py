from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import Libro, Tienda, HistorialPrecio
from app.routes.libros import precios_actuales_por_tienda

router = APIRouter()


class EdicionPrecio(BaseModel):
    """Datos para corregir manualmente el precio vigente y disponibilidad de un libro en una tienda."""
    libro_id: int
    tienda_id: int
    precio: float = Field(..., gt=0, description="Nuevo precio en CLP")
    stock: Optional[bool] = Field(default=None, description="Disponibilidad en la tienda")


def obtener_ultimo_registro(db: Session, libro_id: int, tienda_id: int):
    return (
        db.query(HistorialPrecio)
        .filter(HistorialPrecio.libro_id == libro_id, HistorialPrecio.tienda_id == tienda_id)
        .order_by(HistorialPrecio.fecha_extraccion.desc(), HistorialPrecio.id.desc())
        .first()
    )


def foto_precios_vigentes(db: Session) -> dict:
    """Captura el precio vigente de cada par (libro, tienda) para comparar antes y después del scraping."""
    foto = {}
    for libro in db.query(Libro).all():
        for tienda in db.query(Tienda).all():
            registro = obtener_ultimo_registro(db, libro.id, tienda.id)
            if registro:
                foto[(libro.id, tienda.id)] = registro.precio
    return foto


@router.post("/scraping/ejecutar")
def ejecutar_scraping(db: Session = Depends(get_db)):
    """
    Ejecuta manualmente el scraping de todas las tiendas activas y
    reporta los precios que cambiaron respecto de la extracción anterior.
    """
    from app.scrapers import ejecutar_todos

    antes = foto_precios_vigentes(db)
    resultado = ejecutar_todos(db)
    despues = foto_precios_vigentes(db)

    libros = {l.id: l.titulo for l in db.query(Libro).all()}
    tiendas = {t.id: t.nombre for t in db.query(Tienda).all()}

    cambios = []
    for clave, precio_nuevo in despues.items():
        precio_anterior = antes.get(clave)
        if precio_anterior is not None and precio_anterior != precio_nuevo:
            libro_id, tienda_id = clave
            cambios.append({
                "libro": libros.get(libro_id),
                "tienda": tiendas.get(tienda_id),
                "precio_anterior": precio_anterior,
                "precio_nuevo": precio_nuevo,
                "diferencia": precio_nuevo - precio_anterior,
            })

    resultado["cambios"] = cambios
    resultado["total_cambios"] = len(cambios)
    return resultado


@router.put("/precios")
def editar_precio(datos: EdicionPrecio, db: Session = Depends(get_db)):
    """
    Corrige manualmente el precio vigente (último registro) de un libro en una tienda.
    La siguiente sincronización registrará el precio real y dejará visible la variación.
    """
    registro = obtener_ultimo_registro(db, datos.libro_id, datos.tienda_id)
    if not registro:
        raise HTTPException(status_code=404, detail="No existe un precio registrado para ese libro y tienda")

    precio_original = registro.precio
    registro.precio = datos.precio
    if datos.stock is not None:
        registro.stock = datos.stock
    db.commit()
    db.refresh(registro)

    return {
        "mensaje": "Precio y disponibilidad actualizados",
        "historial_id": registro.id,
        "libro_id": datos.libro_id,
        "tienda_id": datos.tienda_id,
        "precio_anterior": precio_original,
        "precio_nuevo": registro.precio,
        "stock": registro.stock,
    }


@router.get("/dashboard")
def obtener_dashboard(db: Session = Depends(get_db)):
    """Devuelve métricas generales del sistema para el panel de administración."""
    total_libros = db.query(func.count(Libro.id)).scalar()
    total_tiendas = db.query(func.count(Tienda.id)).scalar()
    tiendas_activas = db.query(func.count(Tienda.id)).filter(Tienda.activa == True).scalar()
    total_registros = db.query(func.count(HistorialPrecio.id)).scalar()

    ultima_extraccion = (
        db.query(func.max(HistorialPrecio.fecha_extraccion)).scalar()
    )

    return {
        "total_libros": total_libros,
        "total_tiendas": total_tiendas,
        "tiendas_activas": tiendas_activas,
        "total_registros_precio": total_registros,
        "ultima_extraccion": ultima_extraccion.isoformat() if ultima_extraccion else None,
    }


@router.get("/libros-recientes")
def obtener_libros_recientes(db: Session = Depends(get_db)):
    """Retorna los libros registrados con sus precios actuales y variaciones por tienda."""
    libros = db.query(Libro).order_by(Libro.id.desc()).limit(20).all()
    return [
        {
            "id": libro.id,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "isbn": libro.isbn,
            "editorial": libro.editorial,
            "precios": precios_actuales_por_tienda(db, libro.id),
        }
        for libro in libros
    ]
