from pymongo import MongoClient
import json

# Conectar a MongoDB
client = MongoClient("mongodb+srv://mperdomol1:1OkwRaT9EQSLpGbh@datosincapacidades.t9vkenb.mongodb.net/?retryWrites=true&w=majority&appName=DatosIncapacidades")  # Ajusta la conexión si es necesario
db = client["DatosIncapacidades"]
collection = db["soportes_actualizados"]

# Extraer documentos y convertir a formato Doccano
data = []
for doc in collection.find({}, {"_id": 0, "Texto": 1}):  # Solo extraer el campo de texto
    data.append({"text": doc["Texto"]})

# Guardar en formato JSON
with open("datos_para_doccano.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("✅ Datos exportados correctamente")
