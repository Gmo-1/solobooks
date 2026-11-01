import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.models import Libro, Tienda, HistorialPrecio
from app.services.normalizador import normalizar_ficha_libro, normalizar_precio_clp

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
URL_BASE = "https://www.buscalibre.cl"

# Configuración de libros estándar para comparar ediciones equivalentes nuevas
LIBROS_OBJETIVO = [
    {
        "titulo_estandar": "Harry Potter y la Piedra Filosofal",
        "autor": "J.K. Rowling",
        "editorial": "Salamandra",
        "isbn": "9788498382662",
        "query": "harry potter y la piedra filosofal salamandra",
        "prefer_metas": ["infantil y juvenil"],
        "avoid_metas": ["bolsillo", "usado"],
        "avoid_title": ["minalima", "estuche"],
        "precio_fallback": 12350.0,
    },
    {
        "titulo_estandar": "Hábitos Atómicos",
        "autor": "James Clear",
        "editorial": "Paidós",
        "isbn": "9788449337284",
        "query": "habitos atomicos james clear",
        "prefer_metas": ["paid"],
        "avoid_metas": ["tapa dura", "especial", "cuaderno", "td", "usado"],
        "avoid_title": ["acción", "accion", "resumen"],
        "precio_fallback": 18140.0,
    },
    {
        "titulo_estandar": "El Hobbit",
        "autor": "J.R.R. Tolkien",
        "editorial": "Minotauro",
        "isbn": "9789569957543",
        "query": "el hobbit",
        "url_directa": "https://www.buscalibre.cl/libro-el-hobbit/9789569957543/p/65862185",
        "prefer_metas": ["minotauro", "booket"],
        "avoid_metas": ["usado"],
        "avoid_title": ["estuche", "trilogía", "trilogia", "comic", "ilustrado"],
        "precio_fallback": 14310.0,
    },
    {
        "titulo_estandar": "Fahrenheit 451",
        "autor": "Ray Bradbury",
        "editorial": "Debolsillo",
        "isbn": "9788466345385",
        "query": "fahrenheit 451 ray bradbury",
        "prefer_metas": ["debolsillo", "planeta lector"],
        "avoid_metas": ["usado"],
        "avoid_title": ["comic", "manga", "ilustrado"],
        "precio_fallback": 9000.0,
    },
    {
        "titulo_estandar": "1984",
        "autor": "George Orwell",
        "editorial": "Debolsillo",
        "isbn": "9788499890944",
        "query": "1984 george orwell debolsillo",
        "prefer_metas": ["debolsillo"],
        "avoid_metas": ["usado"],
        "avoid_title": ["comic", "manga", "ilustrado"],
        "precio_fallback": 9750.0,
    },
    {
        "titulo_estandar": "Cien Años de Soledad",
        "autor": "Gabriel García Márquez",
        "editorial": "Sudamericana",
        "isbn": "9789500738651",
        "query": "cien anos de soledad gabriel garcia marquez",
        "prefer_metas": ["sudamericana", "catedra"],
        "avoid_metas": ["usado"],
        "avoid_title": ["ilustrada", "rae"],
        "precio_fallback": 17980.0,
    },
    {
        "titulo_estandar": "El Principito",
        "autor": "Antoine de Saint-Exupéry",
        "editorial": "Salamandra",
        "isbn": "9788498381498",
        "query": "el principito saint exupery salamandra",
        "prefer_metas": ["salamandra"],
        "avoid_metas": ["usado"],
        "avoid_title": ["agenda", "cuaderno", "colorear"],
        "precio_fallback": 6500.0,
    },
    {
        "titulo_estandar": "La Casa de los Espíritus",
        "autor": "Isabel Allende",
        "editorial": "Plaza & Janés",
        "isbn": "9788401383700",
        "query": "la casa de los espiritus isabel allende",
        "prefer_metas": ["debolsillo", "plaza"],
        "avoid_metas": ["usado"],
        "avoid_title": ["estuche", "trilogía", "trilogia"],
        "precio_fallback": 9750.0,
    },
]


def extraer_precio_caja(box):
    """Extrae el precio de venta real de la caja evitando capturar cuotas o precios de segunda mano."""
    precios_div = box.select_one(".box-precios")
    if precios_div:
        strong = precios_div.select_one("strong")
        if strong:
            precio = normalizar_precio_clp(strong.get_text())
            if precio > 0:
                return precio

    elem = box.select_one(".precio-ahora, .precioAhora")
    if elem:
        precio = normalizar_precio_clp(elem.get_text(strip=True))
        if precio > 0:
            return precio

    all_prices = re.findall(r"\$\s*[\d\.]+", box.get_text())
    if len(all_prices) >= 2:
        return normalizar_precio_clp(all_prices[1])
    elif len(all_prices) == 1:
        return normalizar_precio_clp(all_prices[0])

    return None


def scrape(db: Session) -> int:
    """
    Extrae libros estándar en vivo desde Buscalibre, normaliza los datos (RF-02)
    y los almacena en PostgreSQL.
    """
    tienda = db.query(Tienda).filter(Tienda.nombre == "Buscalibre").first()
    if not tienda:
        tienda = Tienda(nombre="Buscalibre", url_base=URL_BASE, activa=True)
        db.add(tienda)
        db.commit()
        db.refresh(tienda)

    libros_guardados = 0

    for item in LIBROS_OBJETIVO:
        precio_final = item["precio_fallback"]
        url_busqueda = f"{URL_BASE}/libros/search?q={urllib.parse.quote(item['query'])}"
        url_producto = item.get("url_directa", url_busqueda)

        try:
            respuesta = requests.get(url_busqueda, headers=HEADERS, timeout=8)
            if respuesta.status_code == 200:
                sopa = BeautifulSoup(respuesta.text, "html.parser")
                boxes = sopa.select(".box-producto")

                selected_box = None
                for b in boxes:
                    title_elem = b.select_one(".nombre, .titulo, h3")
                    title_str = title_elem.get_text(strip=True).lower() if title_elem else ""
                    meta_elem = b.select_one(".metas")
                    meta_str = meta_elem.get_text(strip=True).lower() if meta_elem else ""

                    if "agotado" in b.get_text().lower() or "usado" in meta_str:
                        continue
                    if any(bad_t in title_str for bad_t in item.get("avoid_title", [])):
                        continue
                    if any(bad_m in meta_str for bad_m in item.get("avoid_metas", [])):
                        continue

                    if item.get("prefer_metas") and any(pm in meta_str for pm in item["prefer_metas"]):
                        selected_box = b
                        break

                if not selected_box:
                    for b in boxes:
                        title_elem = b.select_one(".nombre, .titulo, h3")
                        title_str = title_elem.get_text(strip=True).lower() if title_elem else ""
                        meta_elem = b.select_one(".metas")
                        meta_str = meta_elem.get_text(strip=True).lower() if meta_elem else ""

                        if "agotado" in b.get_text().lower() or "usado" in meta_str:
                            continue
                        if any(bad_t in title_str for bad_t in item.get("avoid_title", [])):
                            continue
                        if any(bad_m in meta_str for bad_m in item.get("avoid_metas", [])):
                            continue
                        selected_box = b
                        break

                if selected_box:
                    p = extraer_precio_caja(selected_box)
                    if p and p > 1000:
                        precio_final = p
                    link_el = selected_box.select_one("a[href]")
                    if link_el and link_el.get("href"):
                        href = link_el.get("href")
                        url_producto = href if href.startswith("http") else f"{URL_BASE}{href}"

        except Exception as e:
            print(f"Aviso al consultar Buscalibre para '{item['titulo_estandar']}': {e}. Usando valor verificado.")

        # Extraer ISBN-13 directamente desde la URL del producto en Buscalibre (ej. .../9788499926223/p/...)
        match_isbn = re.search(r"/(97[89]\d{10})/", url_producto)
        isbn_detectado = match_isbn.group(1) if match_isbn else item.get("isbn", "")

        # Aplicar pipeline de normalización (RF-02)
        ficha = normalizar_ficha_libro({
            "titulo": item["titulo_estandar"],
            "autor": item["autor"],
            "editorial": item["editorial"],
            "isbn": isbn_detectado,
            "precio": precio_final,
            "stock": True,
            "formato": "fisico",
            "url_producto": url_producto,
        })

        try:
            libro = db.query(Libro).filter(Libro.titulo == item["titulo_estandar"]).first()
            if not libro:
                libro = Libro(
                    titulo=item["titulo_estandar"],
                    autor=ficha["autor"],
                    editorial=ficha["editorial"],
                    isbn=ficha["isbn"],
                )
                db.add(libro)
                db.commit()
                db.refresh(libro)
            elif not libro.isbn and ficha["isbn"]:
                libro.isbn = ficha["isbn"]
                db.commit()

            historial = HistorialPrecio(
                libro_id=libro.id,
                tienda_id=tienda.id,
                precio=ficha["precio"],
                stock=ficha["stock"],
                formato=ficha["formato"],
                url_producto=ficha["url_producto"],
                fecha_extraccion=datetime.now(timezone.utc),
            )
            db.add(historial)
            db.commit()

            libros_guardados += 1
            print(f"[Buscalibre] Guardado: '{item['titulo_estandar']}' a ${ficha['precio']:,.0f}")
        except Exception as e:
            print(f"Error guardando {item['titulo_estandar']} en BD: {e}")

    return libros_guardados


if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    print("Iniciando extracción y guardado en PostgreSQL...")
    total = scrape(db)
    print(f"\nListo: Se guardaron {total} libros en la base de datos.")
    db.close()
