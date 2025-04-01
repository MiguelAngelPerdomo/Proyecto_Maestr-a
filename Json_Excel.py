# 📌 4. Realizar el cruce entre JSON y Excel en Python
diagnosticos_dict = {str(d["COD_4"]).lower(): d["DESCRIPCION CODIGOS DE CUATRO CARACTERES"] for d in diagnosticos}

# Agregar la columna de diagnóstico al JSON
json_actualizado = []
no_encontrados = []

for doc in json_data:
    cod_4 = str(doc.get("COD_4", "")).lower()
    if cod_4 in diagnosticos_dict:
        doc["Diagnostico"] = diagnosticos_dict[cod_4]
        json_actualizado.append(doc)
    else:
        no_encontrados.append(doc)

# 📌 5. Guardar los resultados en dos archivos JSON
with open("encontrados.json", "w", encoding="utf-8") as f:
    json.dump(json_actualizado, f, ensure_ascii=False, indent=4)

with open("no_encontrados.json", "w", encoding="utf-8") as f:
    json.dump(no_encontrados, f, ensure_ascii=False, indent=4)

print("✅ Proceso completado. Archivos guardados.")
