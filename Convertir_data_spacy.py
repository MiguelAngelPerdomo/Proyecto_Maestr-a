import json

# Cargar el archivo JSON de NER Annotator
with open("annotations.json", "r", encoding="utf-8") as f:
    data = json.load(f)

TRAIN_DATA = []

# Verificar que "annotations" exista y sea una lista
if "annotations" in data and isinstance(data["annotations"], list):
    for idx, annotation in enumerate(data["annotations"]):
        if not annotation or annotation == "" or annotation[0] == "":
            print(f"⚠️ Anotación vacía en el índice {idx}, se omite.")
            continue

        if isinstance(annotation, list) and len(annotation) == 2:
            text_part, entity_part = annotation

            if isinstance(text_part, str):
                try:
                    text_data = json.loads(text_part.strip())  
                    if "text" not in text_data or not text_data["text"].strip():
                        print(f"⚠️ Texto vacío en la anotación {idx}, se omite.")
                        continue

                    text = text_data["text"]
                    entities = entity_part.get("entities", [])

                    if isinstance(entities, list):
                        formatted_entities = [
                            (start, end, label) for start, end, label in entities
                            if isinstance(start, int) and isinstance(end, int) and isinstance(label, str)
                        ]
                        TRAIN_DATA.append((text, {"entities": formatted_entities}))
                    else:
                        print(f"⚠️ Entidades no válidas en la anotación {idx}, se omite.")
                except json.JSONDecodeError as e:
                    print(f"❌ Error decodificando JSON en la anotación {idx}: {e}")
                except Exception as e:
                    print(f"❌ Error inesperado en la anotación {idx}: {e}")
            else:
                print(f"⚠️ Primer elemento de la anotación {idx} no es un JSON válido, se omite.")
        else:
            print(f"⚠️ Estructura incorrecta en la anotación {idx}, se omite.")

else:
    print("❌ Error: El JSON no contiene una lista 'annotations' válida.")

# Guardar el archivo convertido solo si hay datos válidos
if TRAIN_DATA:
    with open("spacy_train_data.json", "w", encoding="utf-8") as f:
        json.dump(TRAIN_DATA, f, ensure_ascii=False, indent=4)
    print("✅ Conversión completada. Datos guardados en 'spacy_train_data.json'")
else:
    print("❌ No se generaron datos válidos para spaCy.")