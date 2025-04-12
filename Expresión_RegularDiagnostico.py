import re
import csv
from pymongo import MongoClient

# 📌 1. Conectar a MongoDB
client = MongoClient("mongodb+srv://mperdomol1:1OkwRaT9EQSLpGbh@datosincapacidades.t9vkenb.mongodb.net/?retryWrites=true&w=majority&appName=DatosIncapacidades")
db = client["DatosIncapacidades"]

# 📌 2. Expresión regular para códigos válidos (estructuralmente)
codigo_regex = re.compile(r"\b[A-Z][0-9]{2}[0-9X]\b", re.IGNORECASE)

# 📌 3. Cargar todos los diagnósticos en un diccionario
def cargar_diccionario_diagnosticos():
    cursor = db["diagnosticos"].find({}, {"_id": 0})
    return {doc["codigo_4"]: doc for doc in cursor}

# 📌 4. Funciones de corrección OCR
def estrategia_1_mayusculas(texto):
    return texto.upper()

def estrategia_3_busqueda_regex(texto):
    return list(set(codigo_regex.findall(texto)))

def estrategia_2_estructural(texto):
    texto = re.sub(r"([A-Z])\s?(\d{2})\s?(\d|X)", r"\1\2\3", texto)
    texto = re.sub(r"\b([A-Z][0-9]{2}[0-9X])([A-Z]{2,})", r"\1 \2", texto)
    return texto

def estrategia_5_reconstruccion(texto):
    reemplazo_inverso = {'2': 'Z', '5': 'S', '0': 'O', '8': 'B', '6': 'G', '1': 'I'}
    posibles_malos = re.findall(r"\b[0-9]{4}\b", texto)

    # Lista de códigos a excluir de la reconstrucción
    codigos_excluir = {"2000", "2001", "2002", "2022", "2023", "2024"}

    for codigo in posibles_malos:
        if codigo in codigos_excluir:
            continue  # ❌ No aplicar reconstrucción si es uno de los prohibidos

        primera = reemplazo_inverso.get(codigo[0])
        if primera:
            codigo_corregido = primera + codigo[1:]
            if re.fullmatch(r"[A-Z][0-9]{2}[0-9X]", codigo_corregido):
                texto = texto.replace(codigo, codigo_corregido)
    return texto

def estrategia_5_1_palabras_de_4_letras(texto):
    reemplazos = {'I': '1', 'L': '1', 'Z': '2', 'S': '5', 'B': '8', 'G': '6', 'Q': '0', 'O': '0'}
    posibles_palabras = re.findall(r"\b[A-Z]{4}\b", texto)
    for palabra in posibles_palabras:
        corregida = ''.join([reemplazos.get(c, c) for c in palabra])
        if re.fullmatch(r"[A-Z][0-9]{2}[0-9X]", corregida):
            texto = texto.replace(palabra, corregida)
    return texto

def estrategia_4_reemplazos_simples(texto):
    reemplazos = {'I': '1', 'L': '1', 'Z': '2', 'S': '5', 'B': '8', 'G': '6', 'Q': '0', 'O': '0'}
    chars = list(texto)
    for i, c in enumerate(chars):
        if c in reemplazos and ((i > 0 and chars[i-1].isalnum()) or (i < len(chars)-1 and chars[i+1].isalnum())):
            chars[i] = reemplazos[c]
    return ''.join(chars)

# 📌 Filtrar códigos y omitir Z022-Z024 si hay otros
def filtrar_codigos(codigos_extraidos, diccionario_diagnosticos):
    codigos_validos = []

    for c in codigos_extraidos:
        # Si el código extraído ya existe, lo dejamos
        if c in diccionario_diagnosticos:
            codigos_validos.append(c)
        # Si termina en 'X', probamos sin la 'X'
        elif c.endswith('X'):
            c_sin_x = c[:-1]
            if c_sin_x in diccionario_diagnosticos:
                codigos_validos.append(c_sin_x)

    # Si hay códigos reales (no administrativos), filtramos los administrativos
    codigos_reales = [c for c in codigos_validos if c not in {
        "Z022", "Z023", "Z024", "Z000", "Z001", "Z002", "Z003", "Z004"
    }]
    
    if codigos_reales:
        codigos_validos = codigos_reales

    return codigos_validos[:2]

# 📌 Procesar colección con stop si se encuentra código válido
def procesar_coleccion(nombre_coleccion, diccionario_diagnosticos):
    coleccion = db[nombre_coleccion]
    documentos = list(coleccion.find({}, {"_id": 0}))

    encontrados, no_encontrados = [], []

    for doc in documentos:
        texto = str(doc.get("Texto", "")).strip()

        # ✅ Guardar datos originales
        doc["identificacion_original"] = (
            doc.get("identificacion") or
            doc.get("Identificación") or
            "Desconocido"
        )
        doc["fecha_inicio_original"] = (
            doc.get("fecha_inicio") or
            doc.get("Fecha Inicio Incapacidad") or
            "Desconocido"
        )

        # 🧱 Etapa 1: convertir texto a mayúsculas
        texto = estrategia_1_mayusculas(texto)

        # 🔍 Etapa 2: búsqueda directa con regex SIN OCR
        codigos_regex = estrategia_3_busqueda_regex(texto)
        codigos_validos = filtrar_codigos(codigos_regex, diccionario_diagnosticos)

        # Si no encuentra, aplicar otras estrategias
        if not codigos_validos:
            estrategias = [
                estrategia_2_estructural,
                estrategia_5_reconstruccion,
                estrategia_5_1_palabras_de_4_letras,
                estrategia_4_reemplazos_simples,
            ]

            for estrategia in estrategias:
                texto = estrategia(texto)
                codigos_regex = estrategia_3_busqueda_regex(texto)
                codigos_validos = filtrar_codigos(codigos_regex, diccionario_diagnosticos)
                if codigos_validos:
                    break

        # Tomar hasta 2 códigos válidos
        codigos_validos = codigos_validos[:2]

        # Clasificar el documento
        if codigos_validos:
            descripciones = [
                {
                    "codigo": c,
                    "descripcion_especifica": diccionario_diagnosticos[c].get("descripcion_4", "No disponible"),
                    "codigo_general": diccionario_diagnosticos[c].get("codigo_3", "No disponible"),
                    "descripcion_general": diccionario_diagnosticos[c].get("descripcion_3", "No disponible"),
                }
                for c in codigos_validos
            ]
            doc["codigos_4_encontrados"] = descripciones
            encontrados.append(doc)
        else:
            no_encontrados.append(doc)

    return encontrados, no_encontrados

# 📌 Guardar resultados en MongoDB
def reemplazar_coleccion(nombre, documentos):
    db[nombre].delete_many({})
    if documentos:
        db[nombre].insert_many(documentos)
        print(f"🟢 {nombre}: {len(documentos)} documentos insertados")
    else:
        print(f"⚪ {nombre}: colección vacía")

# 📌 Exportar a CSV con identificación y fecha_inicio original
def generar_csv_resultado(nombre_archivo, encontrados_ocr, encontrados_directos):
    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo_csv:
        columnas = [
            "fuente", "identificacion", "fecha_inicio", "codigo_4",
            "descripcion_especifica", "codigo_general", "descripcion_general", "texto_original"
        ]
        writer = csv.DictWriter(archivo_csv, fieldnames=columnas)
        writer.writeheader()

        for fuente, documentos in [("OCR", encontrados_ocr), ("Directo", encontrados_directos)]:
            for doc in documentos:
                identificacion = (
                    doc.get("identificacion_original") or
                    doc.get("identificacion") or
                    doc.get("Identificación") or
                    "Desconocido"
                )
                fecha_inicio = (
                    doc.get("fecha_inicio_original") or
                    doc.get("fecha_inicio") or
                    doc.get("Fecha Inicio Incapacidad") or
                    "Desconocido"
                )
                texto_original = doc.get("Texto", "")
                for cod in doc.get("codigos_4_encontrados", []):
                    writer.writerow({
                        "fuente": fuente,
                        "identificacion": identificacion,
                        "fecha_inicio": fecha_inicio,
                        "codigo_4": cod.get("codigo"),
                        "descripcion_especifica": cod.get("descripcion_especifica"),
                        "codigo_general": cod.get("codigo_general"),
                        "descripcion_general": cod.get("descripcion_general"),
                        "texto_original": texto_original
                    })

    print(f"📁 Archivo CSV generado: {nombre_archivo}")

# 📌 Ejecutar todo el proceso
diagnosticos_dict = cargar_diccionario_diagnosticos()

ocr_encontrados, ocr_no_encontrados = procesar_coleccion("ocr_texts", diagnosticos_dict)
directos_encontrados, directos_no_encontrados = procesar_coleccion("direct_texts", diagnosticos_dict)

reemplazar_coleccion("ocr_encontrados", ocr_encontrados)
reemplazar_coleccion("ocr_no_encontrados", ocr_no_encontrados)
reemplazar_coleccion("directos_encontrados", directos_encontrados)
reemplazar_coleccion("directos_no_encontrados", directos_no_encontrados)

# 📌 Generar archivo CSV con los encontrados
generar_csv_resultado("reporte_resultados.csv", ocr_encontrados, directos_encontrados)

print(f"\n📊 Resultados:")
print(f"✅ OCR encontrados: {len(ocr_encontrados)}")
print(f"❌ OCR no encontrados: {len(ocr_no_encontrados)}")
print(f"✅ Directos encontrados: {len(directos_encontrados)}")
print(f"❌ Directos no encontrados: {len(directos_no_encontrados)}")
