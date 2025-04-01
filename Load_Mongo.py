import json
import pandas as pd
from pymongo import MongoClient

# 📌 1. Conectar a MongoDB
client = MongoClient("mongodb+srv://mperdomol1:1OkwRaT9EQSLpGbh@datosincapacidades.t9vkenb.mongodb.net/?retryWrites=true&w=majority&appName=DatosIncapacidades")  # Reemplaza con tu conexión
db = client["DatosIncapacidades"]

# 📌 2. Cargar el JSON y subirlo a MongoDB
ruta_json = "soportes_2.json"  # Ruta del archivo JSON
with open(ruta_json, encoding="utf-8") as f:
    json_data = json.load(f)

coleccion_json = db["soportes"]
coleccion_json.insert_many(json_data)  # Subir JSON a Mongo


# 📌 3. Cargar el Excel y subirlo a MongoDB
ruta_excel = r"C:/Users/Miguel Angel/OneDrive - colsubsidio.com/MIGUEL ANGEL\DOC.PERSONALES/Proyecto_MaestríaAnalíticaDatos/Diagnósticos_CIE10.xlsx"
df = pd.read_excel(ruta_excel, dtype=str)

# Seleccionar solo COD_4 y DESCRIPCION CODIGOS DE CUATRO CARACTERES
df = df[["COD_4", "DESCRIPCION CODIGOS DE CUATRO CARACTERES"]] 

# Convertir a JSON
diagnosticos = json.loads(df.to_json(orient="records"))

coleccion_excel = db["diagnosticos"]
coleccion_excel.insert_many(diagnosticos)  # Subir Excel a Mongo
