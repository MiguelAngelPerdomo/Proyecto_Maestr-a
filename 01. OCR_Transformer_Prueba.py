import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import json
import re
import unicodedata
import dask
import dask.bag as db
from textblob import TextBlob
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch

# Configuración de rutas
pdf_folder = "C:/Users/Miguel Angel/Desktop/Prueba_1"
POPPLER_PATH = r"C:/Program Files/poppler-24.08.0/Library/bin"

# Carga del modelo TrOCR para mejorar OCR
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten", use_fast = True)
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-handwritten")

print("✅ Modelos TrOCR cargados correctamente.")

# Función para limpiar el texto
def clean_text(text):
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')  
    text = re.sub(r'[^\w\s]', ' ', text)  
    text = re.sub(r'\s+', ' ', text)  
    return text.strip()

# Función de corrección ortográfica
def correct_spelling(text):
    return str(TextBlob(text).correct())

# Función para preprocesar imágenes
def preprocess_image(image):
    image = image.convert("L")
    image = image.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image.thumbnail((2500, 2500))
    return image

# OCR con Tesseract y TrOCR
def extract_text(image):
    # Tesseract OCR
    tess_text = pytesseract.image_to_string(image, lang='spa')
    
    # TrOCR (Deep Learning)
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    trocr_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    # Combinar ambos resultados
    combined_text = tess_text + " " + trocr_text
    return combined_text

# Extraer identificación y fecha desde el nombre del archivo
def extract_info_from_filename(filename):
    match = re.search(r"(?:cc[_\s]*)?(\d{5,10})[_\s]+(\d{1,2})\s*-\s*(\d{1,2})\s*-\s*(\d{4})", filename)
    
    if match:
        identificacion = match.group(1)
        fecha_inicio = f"{match.group(2).zfill(2)}/{match.group(3).zfill(2)}/{match.group(4)}"
        return identificacion, fecha_inicio
    return None, None

# Procesar un archivo
def process_file(filename):
    file_path = os.path.join(pdf_folder, filename)
    file_ext = filename.lower().split('.')[-1]
    full_text = ""

    try:
        if file_ext == 'pdf':
            images = convert_from_path(file_path, dpi=300, poppler_path=POPPLER_PATH)
            if not images:
                return None
            
            for image in images:
                image = preprocess_image(image)
                full_text += extract_text(image)
        
        elif file_ext in ['png', 'jpg', 'jpeg']:
            image = Image.open(file_path)
            image = preprocess_image(image)
            full_text = extract_text(image)
        
        else:
            return None

        # Limpieza y corrección ortográfica
        cleaned_text = clean_text(full_text)
        corrected_text = correct_spelling(cleaned_text)

        # Extraer información del nombre del archivo
        identificacion, fecha_inicio = extract_info_from_filename(filename)

        return {
            "Archivo": filename,
            "Identificación": identificacion,
            "Fecha Inicio Incapacidad": fecha_inicio,
            "Texto": corrected_text
        }
    
    except Exception as e:
        print(f"Error procesando {filename}: {str(e)}")
        return None

# Procesamiento con Dask
def extract_text_from_files():
    files = os.listdir(pdf_folder)
    print(f"📂 Archivos detectados en {pdf_folder}: {files}") 
    bag = db.from_sequence(files).map(process_file)
    extracted_data = bag.compute()
    return [item for item in extracted_data if item]

if __name__ == "__main__":
    # Llamada a la función para extraer el texto
    pdf_data = extract_text_from_files()

    # Guardar resultados en JSON
    output_file = 'soportes_mejorado.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pdf_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Datos extraídos guardados en {output_file}")
 