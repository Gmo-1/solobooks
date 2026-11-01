import re
import unicodedata

# Palabras vacías en español que permanecen en minúscula en medio de un título normalizado
STOPWORDS_TITULO = {"de", "del", "la", "las", "el", "los", "y", "e", "o", "u", "en", "a", "con", "por", "para"}


def quitar_acentos(texto: str) -> str:
    """Elimina tildes y diacríticos para comparaciones y búsquedas insensibles a acentos."""
    if not texto:
        return ""
    normalizado = unicodedata.normalize("NFD", str(texto))
    return "".join(c for c in normalizado if unicodedata.category(c) != "Mn")


def normalizar_titulo(titulo: str) -> str:
    """
    RF-02: Estandariza la estructura de títulos provenientes de distintas librerías.
    Elimina etiquetas comerciales entre paréntesis/corchetes, espacios múltiples y
    aplica capitalización uniforme en español.
    """
    if not titulo:
        return ""
    limpio = str(titulo).strip()
    # Eliminar anotaciones comerciales frecuentes de tiendas (ej. '(Tapa Blanda)', '[Edición Bolsillo]')
    limpio = re.sub(
        r"[\(\[][^)\]]*(tapa\s+blanda|tapa\s+dura|bolsillo|r[uú]stica|edici[oó]n\s+est[aá]ndar|libro\s+f[ií]sico)[^)\]]*[\)\]]",
        "",
        limpio,
        flags=re.IGNORECASE,
    )
    limpio = re.sub(r"\s+", " ", limpio).strip(" -–—:/")

    palabras = limpio.split(" ")
    resultado = []
    for idx, palabra in enumerate(palabras):
        if not palabra:
            continue
        # Respetar siglas o números romanos/años (ej. 1984, RAE, II)
        if palabra.isdigit() or (palabra.isupper() and len(palabra) <= 4):
            resultado.append(palabra)
        elif idx > 0 and palabra.lower() in STOPWORDS_TITULO and not resultado[-1].endswith(":"):
            resultado.append(palabra.lower())
        else:
            resultado.append(palabra[:1].upper() + palabra[1:].lower())
    return " ".join(resultado)


def normalizar_autor(autor: str) -> str:
    """
    RF-02: Estandariza el nombre del autor.
    Convierte formatos 'Apellido, Nombre' a 'Nombre Apellido' y limpia espacios.
    """
    if not autor:
        return "Autor Desconocido"
    limpio = re.sub(r"\s+", " ", str(autor)).strip()
    if "," in limpio and limpio.count(",") == 1:
        partes = [p.strip() for p in limpio.split(",") if p.strip()]
        if len(partes) == 2:
            limpio = f"{partes[1]} {partes[0]}"
    return limpio


def normalizar_editorial(editorial: str) -> str:
    """RF-02: Unifica nombres de sellos editoriales eliminando prefijos redundantes."""
    if not editorial:
        return "Sin Editorial"
    limpio = re.sub(r"^(editorial|ediciones|sello)\s+", "", str(editorial).strip(), flags=re.IGNORECASE)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio[:1].upper() + limpio[1:] if limpio else "Sin Editorial"


def normalizar_isbn(isbn: str) -> str:
    """RF-02: Estandariza códigos ISBN-10 o ISBN-13 dejando únicamente dígitos válidos."""
    if not isbn:
        return ""
    solo_digitos = re.sub(r"[^\dXx]", "", str(isbn)).upper()
    return solo_digitos if len(solo_digitos) in (10, 13) else solo_digitos


def normalizar_precio_clp(valor) -> float:
    """
    RF-02: Unifica cualquier representación monetaria ('$ 14.950', 'CLP 14,950', 14950.0)
    a un valor numérico flotante entero en pesos chilenos (CLP).
    """
    if valor is None:
        return 0.0
    if isinstance(valor, (int, float)):
        return float(round(valor))
    texto = str(valor).strip()
    digitos = re.sub(r"[^\d]", "", texto)
    return float(digitos) if digitos else 0.0


def normalizar_formato(formato: str) -> str:
    """RF-02: Clasifica las variantes de encuadernación en 'fisico' o 'digital'."""
    if not formato:
        return "fisico"
    f = quitar_acentos(formato).lower().strip()
    if any(k in f for k in ("digital", "ebook", "e-book", "epub", "pdf", "kindle")):
        return "digital"
    return "fisico"


def normalizar_ficha_libro(datos: dict) -> dict:
    """
    RF-02: Pipeline completo de normalización de datos de catálogo antes de su
    almacenamiento en PostgreSQL.
    """
    return {
        "titulo": normalizar_titulo(datos.get("titulo") or datos.get("titulo_estandar") or ""),
        "autor": normalizar_autor(datos.get("autor", "")),
        "editorial": normalizar_editorial(datos.get("editorial", "")),
        "isbn": normalizar_isbn(datos.get("isbn", "")),
        "precio": normalizar_precio_clp(datos.get("precio", 0)),
        "stock": bool(datos.get("stock", True)),
        "formato": normalizar_formato(datos.get("formato", "fisico")),
        "url_producto": (datos.get("url_producto") or "").strip() or None,
    }
