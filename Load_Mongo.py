import json
from pymongo import MongoClient

# 📌 1. Conectar a MongoDB
client = MongoClient("mongodb+srv://mperdomol1:1OkwRaT9EQSLpGbh@datosincapacidades.t9vkenb.mongodb.net/?retryWrites=true&w=majority&appName=DatosIncapacidades")  # Reemplaza con tu conexión
db = client["DatosIncapacidades"]

# 📌 2. Cargar el JSON de soportes y subirlo a MongoDB
ruta_json_soportes = "soportes_2.json"  # Ruta del archivo JSON de soportes
with open(ruta_json_soportes, encoding="utf-8") as f:
    json_data_soportes = json.load(f)

coleccion_json = db["soportes"]
coleccion_json.insert_many(json_data_soportes)  # Subir JSON a Mongo

# 📌 3. Cargar el JSON de diagnósticos y subirlo a MongoDB
ruta_json_diagnosticos = r"C:/Users/Miguel Angel/OneDrive - colsubsidio.com/MIGUEL ANGEL/DOC.PERSONALES/Proyecto_MaestríaAnalíticaDatos/Diagnósticos_CIE10.json"
with open(ruta_json_diagnosticos, encoding="utf-8") as f:
    json_data_diagnosticos = json.load(f)

coleccion_diagnosticos = db["diagnosticos"]
coleccion_diagnosticos.insert_many(json_data_diagnosticos)  # Subir JSON de diagnósticos a Mongo
