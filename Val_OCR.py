import re
import math

# --- Diccionarios ---
VOCABULARIO_VALIDO = set([
     "fecha", "inicial", "final", "diagnostico", "dias", "edad", "tipo", "ambulatoria",
    "seguros", "vida", "telefono", "riesgos", "laboral", "ips", "concepto", "estado",
    "liquidar", "registro", "certificado", "hospital", "universitario", "clinica",
    "cc", "profesional", "documento", "incapacidad", "nombre", "medico", "salud", "cedula",
    "nit"
])

PALABRAS_CLAVE = [
    "ips", "nit", "incapacidad", "fecha", "diagnostico", "dias", "documento", "cc", "cedula",
    "identificacion", "emite", "nombre"
]

LONGITUD_ESPERADA = 5.5
DESVIACION_LONGITUD = 1.5

def evaluar_calidad_estadistica(texto):
    if not texto or texto.strip() == "":
        print("Texto vacío. Score: 0.0")
        return 0.0

    palabras = texto.split()
    total_palabras = len(palabras)
    palabras_unicas = set(palabras)

    # 1. Diversidad léxica (Guiraud's Index)
    diversidad = len(palabras_unicas) / math.sqrt(total_palabras) if total_palabras else 0

    # 2. Longitud promedio normalizada (Z-score)
    longitudes = [len(p) for p in palabras]
    promedio_longitud = sum(longitudes) / total_palabras if total_palabras else 0
    z_long = (promedio_longitud - LONGITUD_ESPERADA) / DESVIACION_LONGITUD
    score_longitud = math.exp(-z_long**2)  # ≈ 1 si cercano a esperado, decae si se aleja

    # 3. Proporción palabras clave (modelo saturación exponencial)
    claves_encontradas = sum(1 for p in PALABRAS_CLAVE if p in palabras)
    prop_claves = claves_encontradas / len(PALABRAS_CLAVE)
    score_claves = 1 - math.exp(-5 * prop_claves)  # rápida saturación

    # 4. Proporción de palabras válidas
    validas = sum(1 for p in palabras if p in VOCABULARIO_VALIDO)
    prop_validas = validas / total_palabras
    score_validas = prop_validas

    # 5. Penalización por ruido OCR mejorada
    tokens_raros = 0
    ultimo_token = None
    for p in palabras:
        if re.search(r"[a-z]{2,}\d+[a-z\d]*", p):  # letras seguidas de números
            tokens_raros += 1
        elif re.search(r"\d+[a-z]{2,}", p):        # números seguidos de letras
            tokens_raros += 1
        elif re.search(r"[^a-z0-9]", p):           # caracteres especiales no alfanuméricos
            tokens_raros += 1
        elif len(p) > 20 or len(p) <= 1:           # palabras demasiado largas o cortas
            tokens_raros += 1
        elif p == ultimo_token:                    # repetición inmediata
            tokens_raros += 1
        ultimo_token = p

    prop_ruido = tokens_raros / total_palabras
    penal_ruido = min(prop_ruido, 0.25)

    # --- Score final (ponderación basada en discriminación esperada)
    score = (
        0.30 * min(diversidad / 2.0, 1) +
        0.25 * score_longitud +
        0.20 * score_claves +
        0.25 * score_validas -
        0.10 * penal_ruido
    )
    score = round(max(0.0, min(score, 1.0)), 3)

    # --- Detalle
    print("\n=== DETALLE DE CÁLCULO ESTADÍSTICO ===")
    print(f"Guiraud (diversidad léxica)     = {diversidad:.3f} → 0.30 × {min(diversidad / 2.0, 1):.3f} = {0.30 * min(diversidad / 2.0, 1):.3f}")
    print(f"Longitud promedio (Z-score)     = {promedio_longitud:.3f}, Z = {z_long:.2f} → score = {score_longitud:.3f} → 0.25 × {score_longitud:.3f} = {0.25 * score_longitud:.3f}")
    print(f"Palabras clave encontradas      = {claves_encontradas} → proporción = {prop_claves:.3f} → score = {score_claves:.3f} → 0.20 × {score_claves:.3f} = {0.20 * score_claves:.3f}")
    print(f"Proporción de palabras válidas  = {prop_validas:.3f} → 0.25 × {score_validas:.3f} = {0.25 * score_validas:.3f}")
    print(f"Proporción de ruido OCR         = {prop_ruido:.3f} → Penalización = -0.10 × {penal_ruido:.3f} = -{0.10 * penal_ruido:.3f}")
    print(f"🔎 Score final calculado         = {score}")

    return score

# Ejemplo de uso
if __name__ == "__main__":
    texto = """subsidio familiar c0l ub id caja colombiana 057 sub x salud tip de dcument cedula de ciudadania numer de dcument 1000005504 fecha de nacimient 29 01 2000 edad atencion 24 ans 4 meses sex femenin episdi 80736062 aseguradr famcolscalleep categri a lugar de atencion cm calle 26 fecha ingres a cnsulta 12 06 2024 tip incapacidad inicial no _ 12 06 2024 fecha_ in pwered by camscanner""".strip()
    score = evaluar_calidad_estadistica(texto)
    print("\n--- CLASIFICACIÓN ---")
    if score >= 0.75:
        print("✅ Calidad ALTA")
    elif score >= 0.5:
        print("⚠️ Calidad MEDIA")
    else:
        print("❌ Calidad BAJA")
