# Solobooks — Comparador y Rastreador Histórico de Precios de Libros en Chile

**Autor:** Guillermo Díaz Pino  
**Asignatura:** Portafolio de Título / Proyecto de Título  

---

## Descripción del Proyecto

**Solobooks** es una plataforma web diseñada para automatizar la extracción, normalización, almacenamiento histórico y comparación de precios de libros comercializados en librerías chilenas (**Buscalibre Chile** y **Librería Antártica**).

El sistema permite a los lectores consultar en tiempo real en qué tienda se encuentra el precio más económico para una misma edición (vinculada mediante su código estándar **ISBN-13**), aplicar filtros multicriterio y visualizar la curva de evolución histórica de precios para distinguir ofertas reales.

---

## Arquitectura y Stack Tecnológico

* **Backend:** Python 3 + FastAPI + SQLAlchemy ORM (`solobooks/backend`)
* **Base de Datos:** PostgreSQL (`libros`, `tiendas`, `historial_precios`)
* **Extracción y Normalización:** `requests`, `BeautifulSoup4` y pipeline de estandarización de metadatos (`RF-02`)
* **Frontend:** React 18 + Axios + Gráficos vectoriales SVG interactivos (`solobooks/frontend`)

---

## Requerimientos Funcionales Implementados

| Código | Requerimiento Funcional | Sprint | Estado |
| :--- | :--- | :---: | :---: |
| **RF-01** | Extracción automatizada de datos desde librerías nacionales (Buscalibre y Antártica) | Sprint 1 | Completado |
| **RF-03** | Almacenamiento relacional de historial de precios, stock y detección de variaciones | Sprint 1 / 2 | Completado |
| **RF-02** | Pipeline de normalización y estandarización de títulos, autores, editoriales, ISBN-13 y CLP | Sprint 2 | Completado |
| **RF-04** | Buscador multicriterio por título, autor, sello editorial o código ISBN | Sprint 1 / 2 | Completado |
| **RF-05** | Filtros dinámicos por tienda, tope de precio, bajas de precio y cálculo automático de ahorro | Sprint 2 | Completado |
| **RF-06** | Visualización gráfica de evolución histórica de precios por tienda y tabla cronológica | Sprint 2 | Completado |

---

## Estructura del Repositorio

```text
solobooks/
├── backend/
│   ├── .env.example              # Ejemplo de variables de entorno (PostgreSQL)
│   ├── requirements.txt          # Dependencias de Python
│   ├── ejecutar_y_ver.py         # Script de prueba e inspección de BD
│   └── app/
│       ├── main.py               # Punto de entrada FastAPI y configuración CORS
│       ├── config.py             # Gestión de configuración con Pydantic Settings
│       ├── database.py           # Motor SQLAlchemy y sesión PostgreSQL
│       ├── models/
│       │   └── models.py         # Modelos ORM: Libro, Tienda, HistorialPrecio
│       ├── routes/
│       │   ├── libros.py         # Endpoints de búsqueda (RF-04/RF-05) e historial (RF-06)
│       │   └── admin.py          # Endpoints de scraping (RF-01), métricas y edición (RF-03)
│       ├── scrapers/
│       │   ├── buscalibre.py     # Scraper para Buscalibre Chile
│       │   └── antartica.py      # Scraper para Librería Antártica
│       └── services/
│           └── normalizador.py   # Pipeline de normalización de metadatos (RF-02)
└── frontend/
    ├── package.json              # Dependencias de React
    ├── public/                   # Plantilla HTML base
    └── src/
        ├── App.js                # Vistas de Catálogo, Filtros, Modal SVG y Panel de Control
        └── App.css               # Estilos de la aplicación
```

---

## Instrucciones de Instalación y Ejecución

### 1. Base de Datos (PostgreSQL)
Crear una base de datos llamada `solobooks` en PostgreSQL y copiar el archivo `.env.example` a `.env` dentro de `backend/`:
```bash
cd backend
cp .env.example .env
```

### 2. Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
* Documentación interactiva Swagger UI: `http://localhost:8000/docs`

### 3. Frontend (React)
```bash
cd frontend
npm install
npm start
```
* Aplicación web disponible en: `http://localhost:3000`
