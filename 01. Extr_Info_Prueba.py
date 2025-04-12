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

# Configuración
PDF_FOLDER = "C:/Users/Miguel Angel/Desktop/Soportes_Proyecto"
POPPLER_PATH = r"C:/Program Files/poppler-24.08.0/Library/bin"
Image.MAX_IMAGE_PIXELS = None

# Contadores globales
ocr_count = multiprocessing.Value('i', 0)
text_count = multiprocessing.Value('i', 0)

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
        print(f"❌ Error leyendo PDF con fitz: {file_path} -> {e}")
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
    except (PDFSyntaxError, PDFPageCountError) as e:
        print(f"⚠️ Error OCR en {file_path}: {e}")
        return None

# ------------------- ETAPA 6: Pipeline por archivo -------------------
def process_file(filename):
    file_path = os.path.join(PDF_FOLDER, filename)
    file_ext = filename.lower().split('.')[-1]
    full_text = ""

    try:
        if file_ext == 'pdf':
            # Intentar extracción directa
            direct_text = extract_text_from_pdf_directly(file_path)
            if direct_text:
                with text_count.get_lock():
                    text_count.value += 1
                full_text = direct_text
            else:
                with ocr_count.get_lock():
                    ocr_count.value += 1
                full_text = extract_text_with_ocr(file_path)
        elif file_ext in ['png', 'jpg', 'jpeg']:
            with ocr_count.get_lock():
                ocr_count.value += 1
            image = Image.open(file_path)
            image = preprocess_image(image)
            full_text = pytesseract.image_to_string(image, lang='spa')
        else:
            print(f"⚠️ Formato inválido: {filename}")
            return None

        cleaned_text = clean_text(full_text)
        identificacion, fecha_inicio = extract_info_from_filename(filename)

        return {
            "Archivo": filename,
            "Identificación": identificacion,
            "Fecha Inicio Incapacidad": fecha_inicio,
            "Texto": cleaned_text
        }

    except Exception as e:
        print(f"❌ Error procesando {filename}: {e}")
        return None

# ------------------- ETAPA 7: Paralelización -------------------
def run_pipeline():
    files = os.listdir(PDF_FOLDER)
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(process_file, files)
    return [r for r in results if r]

# ------------------- ETAPA 8: Guardado y resumen -------------------
if __name__ == "__main__":
    data = run_pipeline()

    with open("soportes_2.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Datos extraídos guardados en soportes_2.json")
    print(f"📄 Archivos procesados: {len(data)}")
    print(f"🔤 Extraídos directamente del PDF: {text_count.value}")
    print(f"🧾 Procesados con OCR: {ocr_count.value}")
