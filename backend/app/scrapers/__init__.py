"""
Módulo de Web Scraping de Solobooks.

Cada tienda tiene su propio archivo scraper que implementa la función
`scrape(db)` para extraer los datos de libros y guardarlos en la BD.
"""
from sqlalchemy.orm import Session
from app.scrapers.buscalibre import scrape as scrape_buscalibre
from app.scrapers.antartica import scrape as scrape_antartica


def ejecutar_todos(db: Session) -> dict:
    """Ejecuta todos los scrapers activos y retorna un resumen."""
    resultados = {}

    scrapers = {
        "Buscalibre": scrape_buscalibre,
        "Antartica": scrape_antartica,
    }

    for nombre, scraper_fn in scrapers.items():
        try:
            cantidad = scraper_fn(db)
            resultados[nombre] = {
                "estado": "exitoso",
                "libros_extraidos": cantidad,
            }
        except Exception as e:
            resultados[nombre] = {
                "estado": "error",
                "mensaje": str(e),
            }

    return {
        "mensaje": "Scraping completado",
        "resultados": resultados,
    }
