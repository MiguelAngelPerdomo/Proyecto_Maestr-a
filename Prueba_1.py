import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageOps, ImageFilter  # 🔹 Agregar ImageFilter e Image
import json
import re
import unicodedata
import multiprocessing
import pdfplumber
import logging

# Ruta a la carpeta donde se encuentran los archivos
pdf_folder = "C:/Users/Miguel Angel/Desktop/Soportes_Prueba"

# Función para eliminar tildes y signos de puntuación
def clean_text(text):
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Función de preprocesamiento de imágenes para mejorar OCR
def preprocess_image(image):
    image = image.convert("L")  # Convertir a escala de grises
    image = ImageOps.autocontrast(image)  # Suavizar ruido
    image = image.filter(ImageFilter.SHARPEN)  # 🔹 Aplicar filtro correctamente
    return image

POPPLER_PATH = r"C:/Program Files/poppler-24.08.0/Library/bin"

# Función para extraer texto de un solo archivo
def process_file(filename):
    file_path = os.path.join(pdf_folder, filename)
    file_ext = filename.lower().split('.')[-1]
    full_text = ""

    try:
        if file_ext == 'pdf':
            images = convert_from_path(file_path, dpi=300)
            for image in images:
                image = preprocess_image(image)
                full_text += pytesseract.image_to_string(image, lang='spa')

        elif file_ext in ['png', 'jpg', 'jpeg']:
            image = Image.open(file_path)
            image = preprocess_image(image)
            full_text = pytesseract.image_to_string(image, lang='spa')

        else:
            return None

        cleaned_text = clean_text(full_text)

        return {
            "Archivo": filename,
            "Texto": cleaned_text
        }

    except Exception as e:
        logging.error(f"Error en {filename}: {str(e)}")  # 🔹 Agregar logging correctamente
        return None

# Extraer texto con pdfplumber (si el PDF tiene texto digital)
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    return text if text.strip() else None

# Procesar archivos en paralelo
def extract_text_from_files():
    files = os.listdir(pdf_folder)
    
    with multiprocessing.Pool(processes=4) as pool:
        extracted_data = pool.map(process_file, files)

    return [item for item in extracted_data if item]

# Configuración de logging para registrar errores
logging.basicConfig(filename="error_log.txt", level=logging.ERROR)

if __name__ == "__main__":
    # Llamar a la función para extraer el texto
    pdf_data = extract_text_from_files()

    # Guardar los resultados en un archivo JSON
    output_file = 'soportes_1.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pdf_data, f, ensure_ascii=False, indent=4)

    print(f"Datos extraídos guardados en {output_file}")
