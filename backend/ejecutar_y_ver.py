"""
Script de prueba integral para Solobooks:
1. Ejecuta el web scraping de todas las tiendas activas.
2. Consulta la base de datos PostgreSQL e imprime en pantalla
   los libros guardados con sus precios y tiendas en tiempo real.
"""
from datetime import datetime
from app.database import SessionLocal
from app.scrapers import ejecutar_todos
from app.models.models import Libro, Tienda, HistorialPrecio


def ejecutar_y_mostrar():
    db = SessionLocal()
    print("\n" + "=" * 65)
    print("🚀 PASO 1: EJECUTANDO WEB SCRAPING EN TODAS LAS TIENDAS")
    print("=" * 65)
    
    # 1. Ejecutar el scraping
    resultado = ejecutar_todos(db)
    print(f"Estado: {resultado['mensaje']}")
    for tienda, datos in resultado['resultados'].items():
        print(f"  • {tienda}: {datos['estado'].upper()} ({datos.get('libros_extraidos', 0)} libros procesados)")

    print("\n" + "=" * 65)
    print("📊 PASO 2: CONSULTANDO BASE DE DATOS POSTGRESQL (solobooks)")
    print("=" * 65)
    
    # 2. Consultar métricas
    total_libros = db.query(Libro).count()
    total_tiendas = db.query(Tienda).count()
    total_precios = db.query(HistorialPrecio).count()

    print(f"📚 Total de Libros únicos:    {total_libros}")
    print(f"🏪 Total de Tiendas activas:  {total_tiendas}")
    print(f"📈 Total registros de precio: {total_precios}")
    print("-" * 65)
    print(f"{'ID':<4} | {'TÍTULO':<35} | {'TIENDA':<11} | {'PRECIO CLP':<10}")
    print("-" * 65)

    # 3. Mostrar cada libro con sus precios registrados
    libros = db.query(Libro).order_by(Libro.id.asc()).all()
    for libro in libros:
        for hist in libro.historial_precios:
            titulo_corto = (libro.titulo[:32] + "..") if len(libro.titulo) > 32 else libro.titulo
            precio_fmt = f"${hist.precio:,.0f}"
            print(f"#{libro.id:<3} | {titulo_corto:<35} | {hist.tienda.nombre:<11} | {precio_fmt:<10}")

    print("=" * 65 + "\n")
    db.close()


if __name__ == "__main__":
    ejecutar_y_mostrar()
