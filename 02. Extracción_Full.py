import os
import json
import re
import unicodedata
import pytesseract
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFSyntaxError, PDFPageCountError
import multiprocessing
import csv

# ------------------- CONFIGURACIÓN -------------------
PDF_FOLDER = "C:/Users/Miguel Angel/Desktop/Soportes_Proyecto"
POPPLER_PATH = r"C:/Program Files/poppler-24.08.0/Library/bin"
Image.MAX_IMAGE_PIXELS = None

# Contadores globales
ocr_count = multiprocessing.Value('i', 0)
text_count = multiprocessing.Value('i', 0)
mixed_count = multiprocessing.Value('i', 0)

# ------------------- ETAPA 1: Limpieza de texto -------------------
def clean_text(text):
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ------------------- ETAPA 2: Preprocesamiento imagen -------------------
def preprocess_image(image):
    image = image.convert("L")
    image = image.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image.thumbnail((2500, 2500))
    return image

# ------------------- ETAPA 3: Extraer info desde nombre archivo -------------------
def extract_info_from_filename(filename):
    filename = filename.lower().strip()
    match = re.search(
        r"(?:cc[_\s]*)?(\d{5,10})[_\s\-]*(\d{1,2})\s*[-_\s]*\s*(\d{1,2})\s*[-_\s]*\s*(\d{4})",
        filename
    )
    if match:
        identificacion = match.group(1)
        fecha_inicio = f"{match.group(2).zfill(2)}/{match.group(3).zfill(2)}/{match.group(4)}"
        return identificacion, fecha_inicio
    return None, None

# ------------------- ETAPA 4: Extracción directa del PDF -------------------
def extract_text_from_pdf_directly(file_path):
    try:
        with fitz.open(file_path) as doc:
            text = "".join(page.get_text() for page in doc)
        return text if text.strip() else None
    except Exception as e:
        return None

# ------------------- ETAPA 5: Extracción por OCR -------------------
def extract_text_with_ocr(file_path):
    try:
        images = convert_from_path(file_path, dpi=300, poppler_path=POPPLER_PATH)
        full_text = ""
        for image in images:
            image = preprocess_image(image)
            full_text += pytesseract.image_to_string(image, lang='spa')
        return full_text
    except Exception:
        return None

# ------------------- ETAPA 6: Pipeline por archivo -------------------
def process_file(filename):
    file_path = os.path.join(PDF_FOLDER, filename)
    file_ext = filename.lower().split('.')[-1]
    result = {
        "Archivo": filename,
        "Identificación": None,
        "Fecha Inicio Incapacidad": None,
        "Texto": "",
        "Método": None,
        "Estado": "Error",
        "Palabras": 0
    }

    try:
        if file_ext == 'pdf':
            direct_text = extract_text_from_pdf_directly(file_path)
            ocr_text = extract_text_with_ocr(file_path)

            if direct_text and ocr_text:
                with mixed_count.get_lock():
                    mixed_count.value += 1
                metodo = "Mixto"
                final_text = direct_text + "\n\n--- OCR ---\n\n" + ocr_text
            elif direct_text:
                with text_count.get_lock():
                    text_count.value += 1
                metodo = "Texto directo"
                final_text = direct_text
            elif ocr_text:
                with ocr_count.get_lock():
                    ocr_count.value += 1
                metodo = "OCR"
                final_text = ocr_text
            else:
                result["Estado"] = "Error extracción"
                return result

        elif file_ext in ['png', 'jpg', 'jpeg']:
            with ocr_count.get_lock():
                ocr_count.value += 1
            image = Image.open(file_path)
            image = preprocess_image(image)
            final_text = pytesseract.image_to_string(image, lang='spa')
            metodo = "OCR"
        else:
            result["Estado"] = "Formato no válido"
            return result

        if not final_text:
            result["Estado"] = "Error extracción"
            return result

        cleaned_text = clean_text(final_text)
        identificacion, fecha_inicio = extract_info_from_filename(filename)
        result.update({
            "Identificación": identificacion,
            "Fecha Inicio Incapacidad": fecha_inicio,
            "Texto": cleaned_text,
            "Método": metodo,
            "Estado": "OK",
            "Palabras": len(cleaned_text.split())
        })        
        return result

    except Exception as e:
        result["Estado"] = f"Error: {str(e)}"
        return result

# ------------------- ETAPA 7: Paralelización núcleos disponibles -------------------
def run_pipeline():
    files = os.listdir(PDF_FOLDER)
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(process_file, files)
    return results

# ------------------- ETAPA 8: Guardado y Reporte-------------------
if __name__ == "__main__":
    data = run_pipeline()

    texto_directo = [d for d in data if d["Método"] == "Texto directo"]
    ocr = [d for d in data if d["Método"] == "OCR"]
    mixto = [d for d in data if d["Método"] == "Mixto"]

    # Guardar como JSON por método
    with open("Texto_Directo.json", "w", encoding="utf-8") as f:
        json.dump(texto_directo, f, ensure_ascii=False, indent=4)

    with open("OCR.json", "w", encoding="utf-8") as f:
        json.dump(ocr, f, ensure_ascii=False, indent=4)

    with open("Mixto.json", "w", encoding="utf-8") as f:
        json.dump(mixto, f, ensure_ascii=False, indent=4)

    # Guardar reporte CSV
    csv_path = "reporte_soportes.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Archivo", "Identificación", "Fecha Inicio Incapacidad",
            "Método", "Estado", "Palabras", "Texto"
        ])
        writer.writeheader()
        writer.writerows(data)

    # Resumen
    print(f"\n✅ Proceso finalizado")
    print(f"📄 Total archivos procesados: {len(data)}")
    print(f"🔤 Extraídos directamente del PDF: {text_count.value}")
    print(f"🧾 Procesados con OCR: {ocr_count.value}")
    print(f"🔀 Procesados como Mixto (texto + OCR): {mixed_count.value}")
    print(f"📁 Reportes guardados:\n- Texto_Directo.json\n- OCR.json\n- Mixto.json\n- {csv_path}")
