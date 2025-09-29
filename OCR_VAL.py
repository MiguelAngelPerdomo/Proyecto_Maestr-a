from pymongo import MongoClient, UpdateOne
import re

def evaluar_calidad_texto_limpio(texto):
    if not texto or texto.strip() == "":
        return 0.0

    lineas = texto.split("\n")
    palabras = texto.split()
    palabras_unicas = set(palabras)
    palabras_clave = ["ips", "nit", "incapacidad", "fecha", "diagnostico", "dias", "documento", "cc"]

    lineas_utiles = [l for l in lineas if len(l.strip()) > 10 and re.search(r'\w', l)]
    porcentaje_lineas_utiles = len(lineas_utiles) / len(lineas) if lineas else 0

    diversidad = len(palabras_unicas) / len(palabras) if palabras else 0

    longitudes = [len(p) for p in palabras]
    promedio_longitud = sum(longitudes) / len(longitudes) if longitudes else 0

    claves_encontradas = sum(1 for p in palabras_clave if p in texto.lower())
    proporcion_claves = claves_encontradas / len(palabras_clave)

    score = (
        0.3 * porcentaje_lineas_utiles +
        0.3 * diversidad +
        0.2 * min(promedio_longitud / 7, 1) +
        0.2 * proporcion_claves
    )
    return round(score, 3)

# --- Conexión a MongoDB ---
uri = "mongodb+srv://mperdomol1:1OkwRaT9EQSLpGbh@datosincapacidades.t9vkenb.mongodb.net/?retryWrites=true&w=majority&appName=DatosIncapacidades"
client = MongoClient(uri)
db = client["DatosIncapacidades"]
ocr_collection = db["ocr_texts"]
direct_collection = db["direct_texts"]

batch_size = 500
ocr_buffer = []
direct_buffer = []

total_docs = 0
actualizados_ocr = 0
actualizados_direct = 0

cursor = ocr_collection.find({}, batch_size=100)

for doc in cursor:
    total_docs += 1
    _id = doc["_id"]
    texto_ocr = doc.get("texto") or doc.get("texto_ocr", "")
    ocr_score = evaluar_calidad_texto_limpio(texto_ocr)

    doc_directo = direct_collection.find_one({"_id": _id})
    if doc_directo:
        texto_directo = doc_directo.get("texto") or doc_directo.get("texto_directo", "")
        directo_score = evaluar_calidad_texto_limpio(texto_directo)

        # Instrucción para actualizar la colección direct_texts
        direct_buffer.append(UpdateOne(
            {"_id": _id},
            {"$set": {"directo_score_limpio": directo_score}}
        ))
    else:
        directo_score = None

    comparacion = round(ocr_score - directo_score, 3) if directo_score is not None else None

    # Instrucción para actualizar la colección ocr_texts
    ocr_buffer.append(UpdateOne(
        {"_id": _id},
        {"$set": {
            "ocr_score_limpio": ocr_score,
            "directo_score_limpio": directo_score,
            "comparacion_score": comparacion
        }}
    ))

    # Imprimir depuración (puedes comentar esto si ya validaste)
    print(f"\nDOC: {_id}")
    print("OCR score:", ocr_score)
    print("Directo score:", directo_score)
    print("Comparación:", comparacion)

    # Escritura por lotes
    if len(ocr_buffer) >= batch_size:
        result = ocr_collection.bulk_write(ocr_buffer)
        actualizados_ocr += result.modified_count
        ocr_buffer.clear()

    if len(direct_buffer) >= batch_size:
        result = direct_collection.bulk_write(direct_buffer)
        actualizados_direct += result.modified_count
        direct_buffer.clear()

# Escribir lo que quedó en los buffers
if ocr_buffer:
    result = ocr_collection.bulk_write(ocr_buffer)
    actualizados_ocr += result.modified_count

if direct_buffer:
    result = direct_collection.bulk_write(direct_buffer)
    actualizados_direct += result.modified_count

print("\n--- RESUMEN ---")
print(f"Documentos procesados: {total_docs}")
print(f"Actualizados en OCR: {actualizados_ocr}")
print(f"Actualizados en Directo: {actualizados_direct}")
