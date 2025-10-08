import json
from pymongo import MongoClient

# 📌 1. Conectar a MongoDB
client = MongoClient("mongodb+srv://:1OkwRaT9EQSLpGbh@datosincapacidades.t9vkenb.mongodb.net/?retryWrites=true&w=majority&appName=DatosIncapacidades")  
db = client["DatosIncapacidades"]

# 📌 2. Función para cargar y fusionar archivos JSON
def cargar_y_consolidar_json(rutas_json, nombre_coleccion):
    try:
        data_consolidada = []

        for ruta in rutas_json:
            with open(ruta, encoding="utf-8") as f:
                json_data = json.load(f)
                if isinstance(json_data, list):
                    data_consolidada.extend(json_data)

        if data_consolidada:
            coleccion = db[nombre_coleccion]
            coleccion.delete_many({})  # Eliminar documentos anteriores
            coleccion.insert_many(data_consolidada)
            print(f"✅ Datos consolidados en la colección '{nombre_coleccion}': {len(data_consolidada)} documentos")
        else:
            print("⚠️ No hay datos válidos para insertar.")

    except Exception as e:
        print(f"❌ Error al consolidar archivos JSON en MongoDB: {e}")

# 📌 3. Consolidar Texto_Directo.json + Mixto.json en la colección direct_texts
cargar_y_consolidar_json(["Texto_Directo.json", "Mixto.json"], "direct_texts")

# 📌 4. Cargar OCR.json como siempre
def cargar_json_a_mongo(ruta_json, nombre_coleccion):
    try:
        with open(ruta_json, encoding="utf-8") as f:
            json_data = json.load(f)

        if isinstance(json_data, list) and json_data:
            coleccion = db[nombre_coleccion]
            coleccion.delete_many({})
            coleccion.insert_many(json_data)
            print(f"✅ Datos insertados en la colección '{nombre_coleccion}': {len(json_data)} documentos")
        else:
            print(f"⚠️ El archivo {ruta_json} está vacío o no tiene formato de lista.")

    except Exception as e:
        print(f"❌ Error al cargar {ruta_json} a MongoDB: {e}")

cargar_json_a_mongo("OCR.json", "ocr_texts")
