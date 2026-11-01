from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Tienda(Base):
    """Representa una librería chilena de la cual se extraen datos."""

    __tablename__ = "tiendas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    url_base = Column(String(500), nullable=False)
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relación con historial de precios
    historial_precios = relationship("HistorialPrecio", back_populates="tienda")

    def __repr__(self):
        return f"<Tienda(id={self.id}, nombre='{self.nombre}')>"


class Libro(Base):
    """Representa un libro con sus metadatos fijos."""

    __tablename__ = "libros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(500), nullable=False)
    autor = Column(String(300), nullable=True)
    isbn = Column(String(20), nullable=True, index=True)
    editorial = Column(String(200), nullable=True)
    imagen_url = Column(String(1000), nullable=True)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relación con historial de precios
    historial_precios = relationship("HistorialPrecio", back_populates="libro")

    def __repr__(self):
        return f"<Libro(id={self.id}, titulo='{self.titulo}')>"


class HistorialPrecio(Base):
    """Registra el precio y stock de un libro en una tienda en un momento dado."""

    __tablename__ = "historial_precios"

    id = Column(Integer, primary_key=True, index=True)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    tienda_id = Column(Integer, ForeignKey("tiendas.id"), nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Boolean, default=True)
    formato = Column(String(20), default="fisico")  # "fisico" o "digital"
    url_producto = Column(String(1000), nullable=True)
    fecha_extraccion = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    libro = relationship("Libro", back_populates="historial_precios")
    tienda = relationship("Tienda", back_populates="historial_precios")

    def __repr__(self):
        return f"<HistorialPrecio(libro_id={self.libro_id}, tienda='{self.tienda_id}', precio={self.precio})>"
