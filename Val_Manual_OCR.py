import re

# === DEFINICIÓN DE VOCABULARIO Y PALABRAS CLAVE ===

VOCABULARIO_VALIDO = set([
    "paciente", "fecha", "inicial", "final", "diagnostico", "dias", "edad", "gestacional", 
    "anterior", "tipo", "ambulatoria", "quirurgica", "nueva", "afiliado", "cotizante",
    "convenio", "seguros", "vida", "telefono", "plan", "riesgos", "laborales",
    "ips", "primaria", "concepto", "estado", "liquidar", "registro",
    "certificado", "hospital", "universitario", "clinica", "cc", "observaciones",
    "profesional", "documento", "incapacidad", "nombre", "medico", "salud"
])

PALABRAS_CLAVE = [
    "incapacidad", "fecha inicial", "diagnostico", "dias", "cc", "ambulatoria",
    "certifica", "identificacion", "autorizacion", "laboral"
]

# === TEXTO DE PRUEBA (puedes cambiarlo o conectarlo con un archivo) ===

texto = """paciente maria ximena araque sandoval 1000007712 cc nivel salarial 1 fecha inicial inc 21 03 2024 fecha final inc 30 03 2024 dias incapacidad 10 0 edad gestacional 0 nro inc anterior tipo incapacidad ambulatoria no quirurgica nueva tipo afiliado cotizante convenio seguros de vida suramericana sa a r l telefono 3246222116 tipo plan riesgos laborales ips primaria concepto incapacidad observaciones estado incapacidad atep sin liquidar william eduardo arias rodriguez profesional registro profesional 1015393948 diagnostico s934 fecha 103010000644049 2024 03 21 no certificado de incapacidad hospital universitario clinica san rafael""".strip()

# === FUNCIÓN DE EVALUACIÓN ===

def evaluar_calidad_texto_limpio(texto):
    if not texto or texto.strip() == "":
        print("Texto vacío. Score: 0.0")
        return 0.0

    palabras = texto.split()
    palabras_unicas = set(palabras)

    # 1. Diversidad léxica
    diversidad = len(palabras_unicas) / len(palabras) if palabras else 0

    # 2. Longitud promedio de palabras
    longitudes = [len(p) for p in palabras]
    promedio_longitud = sum(longitudes) / len(longitudes) if longitudes else 0
    longitud_score = min(promedio_longitud / 5.5, 1)

    # 3. Palabras clave encontradas
    claves_encontradas = sum(1 for p in PALABRAS_CLAVE if p in palabras)
    proporcion_claves = claves_encontradas / len(PALABRAS_CLAVE)

    # 4. Palabras válidas del vocabulario
    palabras_validas = sum(1 for p in palabras if p in VOCABULARIO_VALIDO)
    proporcion_validas = palabras_validas / len(palabras) if palabras else 0

    # 5. Tokens con ruido
    tokens_raros = sum(1 for p in palabras if re.search(r"[a-z]{3,}\d{3,}", p))
    proporcion_ruido = tokens_raros / len(palabras) if palabras else 0
    penalizacion_ruido = min(proporcion_ruido, 0.2)

    # --- Cálculo del score ajustado
    s1 = 0.33 * diversidad
    s2 = 0.27 * longitud_score
    s3 = 0.20 * proporcion_claves
    s4 = 0.20 * proporcion_validas
    penal = 0.10 * penalizacion_ruido

    score = s1 + s2 + s3 + s4 - penal
    score = round(max(0.0, min(score, 1.0)), 3)

    # --- Imprimir detalle
    print("\n=== DETALLE DE CÁLCULO DE SCORE ===")
    print(f"Diversidad léxica              = {diversidad:.3f} → 0.33 × {diversidad:.3f} = {s1:.3f}")
    print(f"Longitud promedio palabras     = {promedio_longitud:.3f} → 0.27 × {longitud_score:.3f} = {s2:.3f}")
    print(f"Proporción palabras clave      = {proporcion_claves:.3f} → 0.20 × {proporcion_claves:.3f} = {s3:.3f}")
    print(f"Proporción palabras válidas    = {proporcion_validas:.3f} → 0.20 × {proporcion_validas:.3f} = {s4:.3f}")
    print(f"Penalización por ruido         = {proporcion_ruido:.3f} → -0.10 × {penalizacion_ruido:.3f} = -{penal:.3f}")
    print("------------------------------------------")
    print(f"🔎 Score final calculado       = {score}\n")

    return score

# === ENTRADA MANUAL DEL USUARIO PARA EL TIPO DE TEXTO ===

def entrada_manual():
    print("\n=== EVALUADOR DE CALIDAD DE TEXTO LIMPIO ===")
    tipo = input("¿Tipo de texto? (ocr/directo): ").strip().lower()
    while tipo not in ["ocr", "directo"]:
        tipo = input("Por favor escribe 'ocr' o 'directo': ").strip().lower()

    score = evaluar_calidad_texto_limpio(texto)

    print(f"\n--- RESULTADO FINAL ({tipo.upper()}) ---")
    print("✅ Calidad ALTA" if score >= 0.7 else "⚠️ Calidad MEDIA" if score >= 0.5 else "❌ Calidad BAJA")

# === PUNTO DE ENTRADA PRINCIPAL ===

if __name__ == "__main__":
    entrada_manual()
