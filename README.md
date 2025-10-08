# Proyecto_Maestr-a
Este proyecto corresponde a la **fase inicial de un macroproyecto** orientado a la automatización de la gestión de incapacidades médicas en organizaciones de gran tamaño, a través de técnicas de **OCR (Reconocimiento Óptico de Caracteres)**, **Procesamiento de Lenguaje Natural (PLN)** y **almacenamiento en bases de datos NoSQL**.  

El objetivo es **extraer información estructurada de certificados médicos** (en formatos PDF, JPG, PNG) y **clasificar automáticamente el origen de las incapacidades** (común o laboral), optimizando el procesamiento documental y facilitando la trazabilidad en el sistema de seguridad social.

---

## 📂 Estructura del repositorio

PROYECTO_MAESTR-A/
│── .venv/ # Entorno virtual de Python
│── 01. DiagVsSoporte_Prueba.py # Comparación de diagnósticos vs soportes médicos
│── 01. Extr_Info_Prueba.py # Extracción inicial de información de certificados
│── 01. Json_Excel_Prueba.py # Conversión de datos JSON a Excel
│── 01. OCR_Transformer_Prueba.py # Implementación de OCR con modelos transformer
│── 02. Extracción_Full.py # Pipeline completo de extracción de información
│── 02. Load_Mongo.py # Carga de datos procesados a MongoDB
│── Expresión_RegularDiagnostico.py # Validación de diagnósticos mediante regex
│── Load_Docano.py # Carga y gestión de anotaciones en Doccano
│── OCR_VAL.py # Validación automática del OCR
│── Regex_Fuzzy.py # Emparejamiento difuso (fuzzy matching) para validación
│── Val_Manual_OCR.py # Validación manual de salidas OCR
│── Val_OCR.py # Comparación y métricas de validación OCR
│── README.md # Este archivo
---

## ⚙️ Funcionalidades principales

1. **Preprocesamiento de documentos**
   - Deskew, binarización y reducción de ruido en certificados médicos digitalizados.
   - Conversión entre formatos (PDF, JPG, PNG → texto estructurado).

2. **Extracción de información**
   - OCR con Tesseract y modelos Transformer.
   - Normalización y validación de campos clave (cédula, fechas, diagnóstico CIE-10, EPS).

3. **Procesamiento de Lenguaje Natural (PLN)**
   - Uso de **NER (Named Entity Recognition)** para identificar diagnósticos y origen de incapacidad.
   - Reglas + aprendizaje automático para garantizar trazabilidad.

4. **Validación**
   - Scripts de validación automática (`OCR_VAL.py`, `Val_OCR.py`).
   - Validación manual asistida (`Val_Manual_OCR.py`).
   - Uso de expresiones regulares y fuzzy matching para aumentar la precisión.

5. **Almacenamiento y visualización**
   - Carga en **MongoDB** de los certificados procesados.
   - Preparación de datos anotados para entrenamiento de modelos.
   - Integración con **Doccano** para la anotación y curación de datos.

---

## 🚀 Requisitos

- Python 3.8+
- Librerías principales:
  - `pytesseract`
  - `opencv-python`
  - `transformers`
  - `pandas`, `numpy`
  - `pymongo`
  - `regex`, `fuzzywuzzy`
- MongoDB instalado y en ejecución.

---

## 📊 Resultados esperados

- Reducción del **90% en tiempos de procesamiento por certificado** frente al proceso manual.  
- Construcción de un dataset anotado de **1.518 certificados** con más de **3.900 entidades**.  
- Métricas preliminares de calidad en NER y clasificación con valores F1 superiores a **0.65**.  

---

## 📌 Notas finales

Este repositorio constituye la **fase inicial** del proyecto, centrada en la extracción y clasificación del origen de incapacidades. En fases posteriores se espera extender a:
- Licencias de maternidad y paternidad.  
- Prórrogas de incapacidades.  
- Conteo automático de días.  
- Capacidades analíticas predictivas sobre ausentismo laboral.  

---

✍️ Autores:  
- **Andrés Felipe Díaz Castellanos**  
- **Miguel Ángel Perdomo Lomelín**  

🎓 Tutor:  
- **Wilman Javier Rincón Bautista**

