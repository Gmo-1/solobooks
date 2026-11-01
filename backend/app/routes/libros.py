import re
import urllib.parse
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Libro, HistorialPrecio, Tienda
from app.services.normalizador import quitar_acentos

router = APIRouter()


def precios_actuales_por_tienda(db: Session, libro_id: int) -> list:
    """
    Retorna, por cada tienda, el precio más reciente del libro junto con el
    precio del registro anterior y el enlace directo a la tienda original,
    ordenados de menor a mayor precio.
    """
    registros = (
        db.query(HistorialPrecio, Tienda)
        .join(Tienda)
        .filter(HistorialPrecio.libro_id == libro_id)
        .order_by(HistorialPrecio.fecha_extraccion.desc(), HistorialPrecio.id.desc())
        .all()
    )

    por_tienda = {}
    for hist, tienda in registros:
        por_tienda.setdefault(tienda.nombre, {"tienda": tienda, "registros": []})
        if len(por_tienda[tienda.nombre]["registros"]) < 2:
            por_tienda[tienda.nombre]["registros"].append(hist)

    resultado = []
    for nombre, datos in por_tienda.items():
        actual = datos["registros"][0]
        anterior = datos["registros"][1] if len(datos["registros"]) > 1 else None
        variacion = round(actual.precio - anterior.precio, 2) if anterior else 0.0

        # Generar enlace seguro hacia la tienda original (usando el título tras ':' en Antártica si tiene subtítulo como Sapiens)
        titulo_libro = actual.libro.titulo if actual.libro else ""
        editorial_libro = actual.libro.editorial if (actual.libro and actual.libro.editorial) else ""
        titulo_limpio_busqueda = re.sub(r"[:\-–—]+", " ", titulo_libro)
        titulo_limpio_busqueda = re.sub(r"\s+", " ", titulo_limpio_busqueda).strip()

        if nombre.lower() == "buscalibre":
            query_bl = urllib.parse.quote(f"{titulo_limpio_busqueda} {editorial_libro}".strip())
            url_final = actual.url_producto or f"https://www.buscalibre.cl/libros/search?q={query_bl}"
        else:
            query_ant = urllib.parse.quote(titulo_limpio_busqueda)
            url_final = actual.url_producto or f"https://www.antartica.cl/catalogsearch/result/?q={query_ant}"

        resultado.append({
            "historial_id": actual.id,
            "tienda_id": datos["tienda"].id,
            "tienda": nombre,
            "precio": actual.precio,
            "precio_anterior": anterior.precio if anterior else None,
            "variacion": variacion,
            "stock": actual.stock,
            "formato": actual.formato,
            "url": url_final,
            "fecha": actual.fecha_extraccion.isoformat(),
        })

    resultado.sort(key=lambda x: x["precio"])
    return resultado


@router.get("/buscar")
def buscar_libros(
    q: str = Query("", description="Texto de búsqueda por título, autor, editorial o ISBN"),
    tienda: Optional[str] = Query(None, description="Filtrar por tienda específica"),
    precio_min: Optional[float] = Query(None, description="Precio mínimo en CLP"),
    precio_max: Optional[float] = Query(None, description="Precio máximo en CLP"),
    formato: Optional[str] = Query(None, description="Formato: fisico o digital"),
    solo_ofertas: bool = Query(False, description="Solo libros con baja de precio detectada"),
    ordenar: str = Query("relevancia", description="Criterio de ordenamiento"),
    db: Session = Depends(get_db),
):
    """
    RF-04 y RF-05: Busca libros por título, autor, editorial o ISBN (insensible a tildes/mayúsculas)
    y permite filtrar por tienda, rango de precio, formato, bajas de precio y criterio de ordenamiento.
    """
    libros = db.query(Libro).order_by(Libro.id.desc()).all()
    termino_norm = quitar_acentos(q.strip()).lower() if q and q.strip() else ""
    tienda_norm = quitar_acentos(tienda.strip()).lower() if tienda and tienda.strip() and tienda != "todas" else ""
    formato_norm = quitar_acentos(formato.strip()).lower() if formato and formato.strip() and formato != "todos" else ""

    resultados = []
    for libro in libros:
        # RF-04: Búsqueda por título, autor, editorial o ISBN sin importar tildes
        if termino_norm:
            campos = " ".join([
                libro.titulo or "",
                libro.autor or "",
                libro.editorial or "",
                libro.isbn or "",
            ])
            if termino_norm not in quitar_acentos(campos).lower():
                continue

        precios = precios_actuales_por_tienda(db, libro.id)
        if not precios:
            continue

        # RF-05: Filtrar precios por formato si se especifica
        if formato_norm:
            precios = [p for p in precios if quitar_acentos(p.get("formato", "fisico")).lower() == formato_norm]
            if not precios:
                continue

        # RF-05: Validar filtro por tienda
        if tienda_norm:
            tiene_tienda = any(quitar_acentos(p["tienda"]).lower() == tienda_norm for p in precios)
            if not tiene_tienda:
                continue

        # Calcular métricas comparativas multi-tienda (Sprint 2)
        valores = [p["precio"] for p in precios]
        mejor_precio = min(valores)
        peor_precio = max(valores)
        tienda_mejor = next((p["tienda"] for p in precios if p["precio"] == mejor_precio), None)
        ahorro_tiendas = round(peor_precio - mejor_precio, 2) if len(valores) > 1 else 0.0
        porcentaje_ahorro = round((ahorro_tiendas / peor_precio) * 100) if peor_precio > 0 and ahorro_tiendas > 0 else 0
        mayor_baja = min((p.get("variacion") or 0.0 for p in precios), default=0.0)

        # RF-05: Filtrar por rango de precio (sobre el mejor precio vigente o el de la tienda seleccionada)
        precio_referencia = mejor_precio
        if tienda_norm:
            p_tienda = next((p["precio"] for p in precios if quitar_acentos(p["tienda"]).lower() == tienda_norm), mejor_precio)
            precio_referencia = p_tienda

        if precio_min is not None and precio_referencia < precio_min:
            continue
        if precio_max is not None and precio_referencia > precio_max:
            continue
        if solo_ofertas and mayor_baja >= 0:
            continue

        resultados.append({
            "id": libro.id,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "isbn": libro.isbn,
            "editorial": libro.editorial,
            "imagen_url": libro.imagen_url,
            "mejor_precio": mejor_precio,
            "tienda_mejor_precio": tienda_mejor,
            "ahorro_tiendas": ahorro_tiendas,
            "porcentaje_ahorro": porcentaje_ahorro,
            "mayor_baja_historica": mayor_baja,
            "precios": precios,
        })

    # RF-05: Ordenamiento de resultados
    if ordenar == "mejor_precio":
        resultados.sort(key=lambda x: x["mejor_precio"])
    elif ordenar == "mayor_ahorro":
        resultados.sort(key=lambda x: x["ahorro_tiendas"], reverse=True)
    elif ordenar == "mayor_baja":
        resultados.sort(key=lambda x: x["mayor_baja_historica"])
    elif ordenar == "titulo_asc":
        resultados.sort(key=lambda x: quitar_acentos(x["titulo"]).lower())

    return {"total": len(resultados), "resultados": resultados}


@router.get("/{libro_id}/historial")
def historial_libro(libro_id: int, db: Session = Depends(get_db)):
    """
    RF-06: Retorna el historial completo de precios de un libro ordenado por fecha,
    junto con las series cronológicas agrupadas por tienda para graficar la evolución
    y las métricas resumen (mínimo histórico, máximo y mejor precio actual).
    """
    libro = db.query(Libro).filter(Libro.id == libro_id).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    filas = (
        db.query(HistorialPrecio, Tienda.nombre)
        .join(Tienda)
        .filter(HistorialPrecio.libro_id == libro_id)
        .order_by(HistorialPrecio.fecha_extraccion.desc(), HistorialPrecio.id.desc())
        .limit(40)
        .all()
    )

    registros = [
        {
            "id": h.id,
            "tienda": nombre_tienda,
            "precio": h.precio,
            "stock": h.stock,
            "formato": h.formato,
            "fecha": h.fecha_extraccion.isoformat(),
        }
        for h, nombre_tienda in filas
    ]

    # Construir series cronológicas ascendentes (antiguo -> reciente) por cada tienda para el gráfico RF-06
    series_por_tienda = {}
    for reg in reversed(registros):
        series_por_tienda.setdefault(reg["tienda"], []).append({
            "id": reg["id"],
            "precio": reg["precio"],
            "fecha": reg["fecha"],
        })

    precios_vigentes = precios_actuales_por_tienda(db, libro.id)
    todos_los_precios = [r["precio"] for r in registros]

    resumen = {
        "precio_minimo_historico": min(todos_los_precios) if todos_los_precios else 0,
        "precio_maximo_historico": max(todos_los_precios) if todos_los_precios else 0,
        "mejor_precio_actual": precios_vigentes[0]["precio"] if precios_vigentes else 0,
        "tienda_mas_economica": precios_vigentes[0]["tienda"] if precios_vigentes else None,
        "total_capturas": len(registros),
    }

    return {
        "libro_id": libro.id,
        "titulo": libro.titulo,
        "autor": libro.autor,
        "editorial": libro.editorial,
        "isbn": libro.isbn,
        "resumen": resumen,
        "series_por_tienda": series_por_tienda,
        "registros": registros,
    }
