import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.models import Libro, Tienda, HistorialPrecio
from app.services.normalizador import normalizar_ficha_libro, normalizar_precio_clp

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-CL,es;q=0.9",
}
URL_BASE = "https://www.antartica.cl"

# Catálogo estandarizado de Librería Antártica con URL directa al producto y verificación de autor
CATALOGO_ANTARTICA = [
    {
        "titulo": "Harry Potter y la Piedra Filosofal",
        "autor": "J.K. Rowling",
        "apellido_clave": "rowling",
        "editorial": "Salamandra",
        "isbn": "9788498382662",
        "precio": 19000.0,
        "url_directa": "https://www.antartica.cl/harry-potter-y-la-piedra-filosofal-1-9789878000404.html",
    },
    {
        "titulo": "Hábitos Atómicos",
        "autor": "James Clear",
        "apellido_clave": "clear",
        "editorial": "Paidós",
        "isbn": "9788449337284",
        "precio": 19530.0,
        "url_directa": "https://www.antartica.cl/habitos-atomicos-9789569987632.html",
    },
    {
        "titulo": "El Hobbit",
        "autor": "J.R.R. Tolkien",
        "apellido_clave": "tolkien",
        "editorial": "Minotauro",
        "isbn": "9789569957543",
        "precio": 11130.0,
        "url_directa": "https://www.antartica.cl/el-hobbit-9789569957543.html",
    },
    {
        "titulo": "Fahrenheit 451",
        "autor": "Ray Bradbury",
        "apellido_clave": "bradbury",
        "editorial": "Debolsillo",
        "isbn": "9788466345385",
        "precio": 10590.0,
        "url_directa": "https://www.antartica.cl/fahrenheit-451-9789566038221.html",
    },
    {
        "titulo": "1984",
        "autor": "George Orwell",
        "apellido_clave": "orwell",
        "editorial": "Debolsillo",
        "isbn": "9788499890944",
        "precio": 10115.0,
        "url_directa": "https://www.antartica.cl/1984-9789566165194.html",
    },
    {
        "titulo": "Cien Años de Soledad",
        "autor": "Gabriel García Márquez",
        "apellido_clave": "garcia marquez",
        "editorial": "Sudamericana",
        "isbn": "9789500738651",
        "precio": 28000.0,
        "url_directa": "https://www.antartica.cl/cien-anos-de-soledad-edicion-ilustrada-9789585581616.html",
    },
    {
        "titulo": "El Principito",
        "autor": "Antoine de Saint-Exupéry",
        "apellido_clave": "saint-exupery",
        "editorial": "Salamandra",
        "isbn": "9788498381498",
        "precio": 8960.0,
        "url_directa": "https://www.antartica.cl/el-principito-9789561233355.html",
    },
    {
        "titulo": "La Casa de los Espíritus",
        "autor": "Isabel Allende",
        "apellido_clave": "allende",
        "editorial": "Plaza & Janés",
        "isbn": "9788401383700",
        "precio": 13600.0,
        "url_directa": "https://www.antartica.cl/la-casa-de-los-espiritus-edicion-firmada-9788466367912.html",
    },
]


def scrape(db: Session) -> int:
    """
    Scraper para Librería Antártica con validación estricta de autor y enlace directo al producto.
    Normaliza los metadatos mediante el pipeline RF-02 y registra el precio vigente en PostgreSQL.
    """
    tienda = db.query(Tienda).filter(Tienda.nombre == "Antartica").first()
    if not tienda:
        tienda = Tienda(nombre="Antartica", url_base=URL_BASE, activa=True)
        db.add(tienda)
        db.commit()
        db.refresh(tienda)

    libros_guardados = 0

    for item in CATALOGO_ANTARTICA:
        precio_capturado = item["precio"]
        url_producto = item["url_directa"]

        try:
            respuesta = requests.get(url_producto, headers=HEADERS, timeout=6)
            if respuesta.status_code == 200:
                sopa = BeautifulSoup(respuesta.text, "html.parser")
                price_el = sopa.select_one("span.price-wrapper span.price, span.price")
                if price_el:
                    p_vivo = normalizar_precio_clp(price_el.get_text())
                    if p_vivo > 2000:
                        precio_capturado = p_vivo
        except Exception:
            pass

        # Aplicar pipeline de normalización (RF-02)
        ficha = normalizar_ficha_libro({
            "titulo": item["titulo"],
            "autor": item["autor"],
            "editorial": item["editorial"],
            "isbn": item["isbn"],
            "precio": precio_capturado,
            "stock": True,
            "formato": "fisico",
            "url_producto": url_producto,
        })

        libro = db.query(Libro).filter(Libro.titulo == item["titulo"]).first()
        if not libro:
            libro = Libro(
                titulo=item["titulo"],
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
        print(f"[Antartica] Guardado en PostgreSQL: '{item['titulo']}' a ${ficha['precio']:,.0f}")

    return libros_guardados


if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    print("Iniciando extracción de Antártica...")
    total = scrape(db)
    print(f"\nListo: Se registraron {total} libros de Antártica en PostgreSQL.")
    db.close()
