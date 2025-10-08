import json
import re
from pymongo import MongoClient

# 📌 1. Conectar a MongoDB
client = MongoClient("mongodb+srv://:1OkwRaT9EQSLpGbh@datosincapacidades.t9vkenb.mongodb.net/?retryWrites=true&w=majority&appName=DatosIncapacidades")
db = client["DatosIncapacidades"]

# 📌 2. Cargar datos desde MongoDB
coleccion_soportes = db["soportes"]
coleccion_diagnosticos = db["diagnosticos"]

# Obtener todos los documentos de cada colección
json_data = list(coleccion_soportes.find({}, {"_id": 0}))  # Excluir _id
diagnosticos_data = list(coleccion_diagnosticos.find({}, {"_id": 0}))

# 📌 3. Crear diccionario de diagnóstico (clave = código_4)
diagnosticos_dict = {str(d["codigo_4"]).strip().lower(): d["descripcion_4"] for d in diagnosticos_data}

# 📌 4. Crear expresión regular para detectar códigos precedidos por "diag." en 1 a 5 palabras anteriores
codigos_regex = r'(?:\bdiag\.\b(?:\s+\w+){0,5}\s+)(?P<codigo>' + '|'.join(map(re.escape, diagnosticos_dict.keys())) + r')\b'
patron_codigos = re.compile(codigos_regex, re.IGNORECASE)  # Precompilar regex

# 📌 5. Realizar el cruce con búsqueda optimizada
json_actualizado = []
no_encontrados = []

for doc in json_data:
    texto = str(doc.get('Texto', '')).lower().strip()

    # Buscar códigos con la condición de "diag." antes del código
    coincidencia = patron_codigos.search(texto)

    if coincidencia:
        codigo_encontrado = coincidencia.group("codigo").strip().lower()  # Extraer código exacto
        doc["codigo_4_encontrado"] = codigo_encontrado
        doc["descripcion_4_encontrada"] = diagnosticos_dict[codigo_encontrado]
        json_actualizado.append(doc)
    else:
        no_encontrados.append(doc)

# 🔍 Depuración y estadísticas
print(f"📊 Cantidad de registros en soportes: {len(json_data)}")
print(f"📊 Cantidad de registros en diagnósticos: {len(diagnosticos_data)}")
print(f"🔍 Cantidad de códigos únicos en diagnosticos_dict: {len(diagnosticos_dict)}")
print(f"✅ Cantidad de documentos encontrados: {len(json_actualizado)}")
print(f"❌ Cantidad de documentos NO encontrados: {len(no_encontrados)}")

# 📌 6. Guardar los resultados en MongoDB (si hay datos)
if json_actualizado:
    db["soportes_actualizados"].insert_many(json_actualizado)
if no_encontrados:
    db["soportes_no_encontrados"].insert_many(no_encontrados)

print("✅ Proceso completado. Datos almacenados en MongoDB.")
