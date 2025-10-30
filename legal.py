# ./legal.py

def get_legal_context_for_contract():
    """
    Devuelve un string con el contexto legal clave para la generación de contratos de alquiler en España.
    Este texto se inyectará en el prompt del LLM.
    """
    return """
- **Ley de Arrendamientos Urbanos (LAU):** La ley principal que regula los alquileres en España (Ley 29/1994).
- **Duración del Contrato:** Para vivienda habitual, la duración es pactada libremente, pero si es inferior a 5 años (7 si el arrendador es persona jurídica), el inquilino tiene derecho a prórrogas anuales hasta alcanzar ese mínimo.
- **Fianza:** Obligatoria y equivalente a una mensualidad de renta. No se puede actualizar durante los primeros 5 (o 7) años.
- **Garantías Adicionales:** Se puede pactar una garantía adicional (aval bancario, depósito, etc.), que no podrá exceder de dos mensualidades de renta.
- **Renta:** Se pacta libremente. La actualización anual se rige por el Índice de Garantía de Competitividad (IGC) o el IPC, según lo pactado y la normativa vigente.
- **Obras y Conservación:** El arrendador debe realizar las obras de conservación necesarias. El inquilino se encarga de las pequeñas reparaciones por el uso ordinario.
- **Subarriendo y Cesión:** Requieren consentimiento escrito del arrendador.
- **Impuestos:** El inquilino está sujeto al Impuesto de Transmisiones Patrimoniales (ITP), aunque en muchas comunidades autónomas está exento para vivienda habitual. El arrendador declara los ingresos en el IRPF.
- **Cláusulas Nulas:** Son nulas las cláusulas que perjudiquen al inquilino en contra de lo que establece la LAU.
"""

def get_initial_legal_html():
    """
    Devuelve un string HTML para ser mostrado en la interfaz de Chainlit
    al inicio del chat, resumiendo los puntos legales más importantes.
    """
    with open("legal.html", "r", encoding="utf-8") as f:
        return f.read()
