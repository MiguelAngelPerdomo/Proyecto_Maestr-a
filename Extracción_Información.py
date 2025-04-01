
import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import json                               
import re
import unicodedata
import multiprocessing
from pdf2image.exceptions import PDFSyntaxError,PDFPageCountError

# Aumentar el límite de procesamiento de imágenes grandes
Image.MAX_IMAGE_PIXELS = None  

# Ruta a la carpeta donde se encuentran los archivos
pdf_folder = "C:/Users/Miguel Angel/Desktop/Prueba_1"
POPPLER_PATH = r"C:/Program Files/poppler-24.08.0/Library/bin"

# Función para eliminar tildes y signos de puntuación
def clean_text(text):
    text = text.lower()  # Convertir a minúsculas
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')  # Eliminar tildes
    text = re.sub(r'[^\w\s]', '', text)  # Eliminar signos de puntuación
    text = re.sub(r'\s+', ' ', text)  # Reemplazar múltiples espacios y \n con un solo espacio
    return text.strip()

# Función de preprocesamiento de imágenes para mejorar OCR
def preprocess_image(image):
    image = image.convert("L")  # Convertir a escala de grises
    image = image.filter(ImageFilter.MedianFilter())  # Suavizar ruido
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)  # Aumentar contraste

    # Redimensionar imagen si es demasiado grande
    max_size = (2500, 2500)
    image.thumbnail(max_size)

    return image

# Extrae identificación y fecha desde el nombre del archivo
def extract_info_from_filename(filename):
    match = re.match(r"(\d{5,10})\s(\d{1,2})-(\d{1,2})-(\d{4})", filename.strip())
    if match:
        identificacion = match.group(1)
        fecha_inicio = f"{match.group(2).zfill(2)}/{match.group(3).zfill(2)}/{match.group(4)}"  # Formato DD/MM/AAAA
        return identificacion, fecha_inicio
    return None, None

# Función para extraer texto de un solo archivo
def process_file(filename):
    file_path = os.path.join(pdf_folder, filename)
    file_ext = filename.lower().split('.')[-1]  
    full_text = ""

    try:
        if file_ext == 'pdf':  
            try:
                images = convert_from_path(file_path, dpi=300, poppler_path=POPPLER_PATH)
                if not images:
                    print(f"Advertencia: {filename} no contiene imágenes, podría estar vacío o dañado.")
                    return None
            except PDFSyntaxError:
                print(f"Error: No se pudo leer {filename}. El PDF podría estar corrupto o vacío.")
                return None
            except PDFPageCountError as e:
                if "Incorrect password" in str(e):
                    print(f"Error: {filename} está protegido con contraseña. No se puede procesar.")
                    return None

            for image in images:
                image = preprocess_image(image)  # Preprocesamiento
                full_text += pytesseract.image_to_string(image, lang='spa')  # OCR en español
        
        elif file_ext in ['png', 'jpg', 'jpeg']:  
            image = Image.open(file_path)
            image = preprocess_image(image) 
            full_text = pytesseract.image_to_string(image, lang='spa')
        
        else:
            print(f"Advertencia: {filename} no es un formato válido y será ignorado.")
            return None 
        
        # Limpieza del texto
        cleaned_text = clean_text(full_text)

        # Extraer información del nombre del archivo

        identificacion, fecha_inicio = extract_info_from_filename(filename)

        return {
            "Archivo": filename,
            "Identificación": identificacion,
            "Fecha Inicio Incapacidad": fecha_inicio,
            "Texto": cleaned_text
        }
    
    except Exception as e:
        print(f"Error procesando {filename}: {str(e)}")
        return None

# Función para procesar archivos en paralelo
def extract_text_from_files():
    files = os.listdir(pdf_folder)

    with multiprocessing.Pool(processes=4) as pool:  # Limitar a 4 procesos
        extracted_data = pool.map(process_file, files)

    extracted_data = [item for item in extracted_data if item]

    return extracted_data


if __name__ == "__main__":
        
    # Llamada a la función para extraer el texto
    pdf_data = extract_text_from_files()

    # Guardar los resultados en un archivo JSON
    output_file = 'soportes_2.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pdf_data, f, ensure_ascii=False, indent=4)

    print(f"Datos extraídos guardados en {output_file}")