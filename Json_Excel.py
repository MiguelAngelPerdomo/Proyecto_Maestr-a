import json
from pymongo import MongoClient

# 📌 1. Conectar a MongoDB
client = MongoClient("mongodb+srv://mperdomol1:1OkwRaT9EQSLpGbh@datosincapacidades.t9vkenb.mongodb.net/?retryWrites=true&w=majority&appName=DatosIncapacidades")
db = client["DatosIncapacidades"]

# 📌 2. Cargar datos desde MongoDB
coleccion_soportes = db["soportes"]
coleccion_diagnosticos = db["diagnosticos"]

# Obtener todos los documentos de cada colección
json_data = list(coleccion_soportes.find({}, {"_id": 0}))  # Excluir _id
diagnosticos_data = list(coleccion_diagnosticos.find({}, {"_id": 0}))

# 📌 3. Crear diccionario de diagnóstico (clave = código_4)
diagnosticos_dict = {str(d["codigo_4"]).strip().lower(): d["descripcion_4"] for d in diagnosticos_data}

# 📌 4. Realizar el cruce y separar encontrados/no encontrados
json_actualizado = []
no_encontrados = []

for doc in json_data:
    texto = str(doc.get("Texto", "")).lower().strip()  # Limpiar espacios

    # Buscar coincidencia de código en el texto
    codigo_encontrado = None
    descripcion_encontrada = None

    for cod_4, descripcion in diagnosticos_dict.items():
        if cod_4 in texto:  # Verifica si el código está en el texto
            codigo_encontrado = cod_4
            descripcion_encontrada = descripcion
            break  # Toma la primera coincidencia

    # Agregar resultados al documento
    if codigo_encontrado:
        doc["codigo_4_encontrado"] = codigo_encontrado
        doc["descripcion_4_encontrada"] = descripcion_encontrada
        json_actualizado.append(doc)
    else:
        no_encontrados.append(doc)

# 🔍 Depuración y estadísticas
print(f"📊 Cantidad de registros en soportes: {len(json_data)}")
print(f"📊 Cantidad de registros en diagnósticos: {len(diagnosticos_data)}")
print(f"🔍 Cantidad de códigos únicos en diagnósticos_dict: {len(diagnosticos_dict)}")
print(f"✅ Cantidad de documentos encontrados: {len(json_actualizado)}")
print(f"❌ Cantidad de documentos NO encontrados: {len(no_encontrados)}")

# 📌 5. Guardar los resultados en MongoDB (si hay datos)
if json_actualizado:
    db["soportes_actualizados"].insert_many(json_actualizado)
if no_encontrados:
    db["soportes_no_encontrados"].insert_many(no_encontrados)

for doc in db["soportes_actualizados"].find({}, {"_id": 0}):
    descripcion = doc.get("descripcion_4_encontrada", "").strip().lower()
    
    resultado = db["diagnosticos"].find_one({"descripcion_4": {"$regex": f"^{descripcion}$", "$options": "i"}}, {"codigo_4": 1})
    
    codigo_4_recuperado = resultado["codigo_4"] if resultado else "No encontrado"
    
    print(f"🔄 Recuperado - Descripción: {descripcion} | Código: {codigo_4_recuperado}")

print("✅ Proceso completado. Datos almacenados en MongoDB.")
