"""
SafeHer Colombia – Streamlit Prototype
--------------------------------------

Este módulo implementa una versión simplificada del prototipo “SafeHer” utilizando
Streamlit. La aplicación original se escribió en React/JSX y ofrece
funcionalidades de predicción de riesgo, mapas interactivos, recomendaciones de
viaje, formularios de denuncias, páginas de ayuda cercana y una sección de
acerca de. Esta implementación pretende trasladar lo esencial a un único
archivo Python compatible con Streamlit, sin depender de APIs externas. Las
predicciones y sugerencias se calculan de manera local utilizando datos
ficticios proporcionados en el prototipo original.

Para ejecutar este archivo instale primero las dependencias necesarias:
```
pip install streamlit pandas altair numpy
```
Luego ejecute:
```
streamlit run safeher_streamlit.py
```

El diseño utiliza componentes básicos de Streamlit como `st.sidebar` para la
navegación y `st.expander`, `st.selectbox`, `st.slider` y gráficos con Altair
para visualizar resultados. No se realiza ninguna llamada a servicios externos
como Anthropic o Google Maps.
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

###############################################################################
# Datos de referencia
###############################################################################

# Paleta de colores simplificada basada en el diseño original.  Utilizamos
# nombres descriptivos para facilitar la selección de colores en la interfaz.
C = {
    "primary": "#4C1D95",
    "primary_light": "#7C3AED",
    "primary_pale": "#F5F3FF",
    "accent": "#EC4899",
    "danger": "#DC2626",
    "success": "#059669",
    "warning": "#D97706",
    "blue": "#1D4ED8",
    "text": "#0F172A",
    "text_muted": "#64748B",
}

# Niveles de riesgo y su configuración (etiqueta y colores).  Se utilizan para
# mostrar etiquetas de forma coherente en diferentes páginas.
RISK_LEVELS = {
    "MÍNIMO":    {"color": "#059669", "label": "Mínimo"},
    "MUY BAJO":  {"color": "#10B981", "label": "Muy Bajo"},
    "BAJO":      {"color": "#3B82F6", "label": "Bajo"},
    "MEDIO-BAJO":{"color": "#F59E0B", "label": "Medio‑Bajo"},
    "MEDIO-ALTO":{"color": "#EF4444", "label": "Medio‑Alto"},
    "ALTO":      {"color": "#DC2626", "label": "Alto"},
    "MUY ALTO":  {"color": "#991B1B", "label": "Muy Alto"},
    "CRÍTICO":   {"color": "#7F1D1D", "label": "Crítico"},
}

# Lista de departamentos de Colombia utilizados en la aplicación.  Este listado
# proviene del prototipo original y se conserva para mantener coherencia.
DEPARTAMENTOS = [
    "AMAZONAS", "ANTIOQUIA", "ARAUCA", "ATLÁNTICO", "BOGOTÁ D.C.", "BOLÍVAR",
    "BOYACÁ", "CALDAS", "CAQUETÁ", "CASANARE", "CAUCA", "CESAR", "CHOCÓ",
    "CÓRDOBA", "CUNDINAMARCA", "GUAINÍA", "GUAVIARE", "HUILA", "LA GUAJIRA",
    "MAGDALENA", "META", "NARIÑO", "NORTE DE SANTANDER", "PUTUMAYO",
    "QUINDÍO", "RISARALDA", "SAN ANDRÉS", "SANTANDER", "SUCRE", "TOLIMA",
    "VALLE DEL CAUCA", "VAUPÉS", "VICHADA"
]

# Tipos de delitos usados en las predicciones y comparativas.
DELITOS = [
    "VIOLENCIA INTRAFAMILIAR",
    "VIOLENCIA SEXUAL",
    "LESIONES PERSONALES",
    "AMENAZAS",
    "HURTO",
    "HOMICIDIO",
]

# Municipios de ejemplo por departamento.  Si un departamento no aparece en
# este diccionario se proporcionarán ejemplos genéricos.
MUNICIPIOS_SAMPLE = {
    "ANTIOQUIA": ["MEDELLÍN", "BELLO", "ITAGÜÍ", "ENVIGADO", "APARTADÓ"],
    "BOGOTÁ D.C.": ["BOGOTÁ"],
    "VALLE DEL CAUCA": ["CALI", "BUENAVENTURA", "PALMIRA", "TULUÁ"],
    "CUNDINAMARCA": ["SOACHA", "FACATATIVÁ", "ZIPAQUIRÁ", "FUSAGASUGÁ"],
    "ATLÁNTICO": ["BARRANQUILLA", "SOLEDAD", "MALAMBO", "SABANAGRANDE"],
    "SANTANDER": ["BUCARAMANGA", "FLORIDABLANCA", "GIRÓN", "PIEDECUESTA"],
    "NARIÑO": ["PASTO", "TUMACO", "IPIALES", "TÚQUERRES"],
    "CÓRDOBA": ["MONTERÍA", "CERETÉ", "LORICA", "SAHAGÚN"],
    "BOLÍVAR": ["CARTAGENA", "MAGANGUÉ", "EL CARMEN", "MOMPÓS"],
    "TOLIMA": ["IBAGUÉ", "ESPINAL", "MELGAR", "HONDA"],
}

# Función auxiliar para obtener municipios de un departamento. Si el
# departamento no está definido en MUNICIPIOS_SAMPLE se devuelven valores
# genéricos.
def get_municipios(departamento: str):
    return MUNICIPIOS_SAMPLE.get(departamento, ["Capital", "Municipio 1", "Municipio 2"])

# Datos sintéticos de riesgo por departamento.  Cada registro incluye un
# promedio de “score”, una zona de riesgo y una gravedad.  Estas cifras
# representan valores ficticios generados para el prototipo.
CRIME_DATA = {
    "ANTIOQUIA":              {"score": 4.2, "zona": "ALTO",        "gravedad": "ALTO",        "municipios": 125},
    "BOGOTÁ D.C.":            {"score": 3.8, "zona": "MEDIO-ALTO",   "gravedad": "MEDIO-ALTO",   "municipios": 1},
    "VALLE DEL CAUCA":        {"score": 4.5, "zona": "MUY ALTO",    "gravedad": "ALTO",        "municipios": 42},
    "CUNDINAMARCA":           {"score": 2.9, "zona": "MEDIO-BAJO",  "gravedad": "BAJO",        "municipios": 116},
    "ATLÁNTICO":              {"score": 3.1, "zona": "MEDIO-BAJO",  "gravedad": "MEDIO-BAJO",  "municipios": 23},
    "SANTANDER":              {"score": 2.5, "zona": "BAJO",        "gravedad": "BAJO",        "municipios": 87},
    "NARIÑO":                 {"score": 3.7, "zona": "MEDIO-ALTO",   "gravedad": "MEDIO-ALTO",   "municipios": 64},
    "CÓRDOBA":                {"score": 3.0, "zona": "MEDIO-BAJO",  "gravedad": "BAJO",        "municipios": 30},
    "BOLÍVAR":                {"score": 3.4, "zona": "MEDIO-BAJO",  "gravedad": "MEDIO-BAJO",  "municipios": 46},
    "TOLIMA":                 {"score": 2.7, "zona": "BAJO",        "gravedad": "BAJO",        "municipios": 47},
    "HUILA":                  {"score": 2.8, "zona": "BAJO",        "gravedad": "BAJO",        "municipios": 37},
    "CAUCA":                  {"score": 4.0, "zona": "ALTO",        "gravedad": "ALTO",        "municipios": 42},
    "META":                   {"score": 3.3, "zona": "MEDIO-BAJO",  "gravedad": "MEDIO-BAJO",  "municipios": 29},
    "CESAR":                  {"score": 3.2, "zona": "MEDIO-BAJO",  "gravedad": "MEDIO-BAJO",  "municipios": 25},
    "MAGDALENA":              {"score": 3.0, "zona": "MEDIO-BAJO",  "gravedad": "BAJO",        "municipios": 30},
    "BOYACÁ":                 {"score": 2.2, "zona": "MUY BAJO",    "gravedad": "MUY BAJO",    "municipios": 123},
    "CALDAS":                 {"score": 2.6, "zona": "BAJO",        "gravedad": "BAJO",        "municipios": 27},
    "RISARALDA":              {"score": 2.8, "zona": "BAJO",        "gravedad": "BAJO",        "municipios": 14},
    "QUINDÍO":                {"score": 2.5, "zona": "BAJO",        "gravedad": "BAJO",        "municipios": 12},
    "NORTE DE SANTANDER":     {"score": 3.6, "zona": "MEDIO-ALTO",   "gravedad": "MEDIO-ALTO",   "municipios": 40},
    "SUCRE":                  {"score": 2.9, "zona": "MEDIO-BAJO",  "gravedad": "BAJO",        "municipios": 26},
    "LA GUAJIRA":             {"score": 3.5, "zona": "MEDIO-ALTO",   "gravedad": "MEDIO-BAJO",   "municipios": 15},
    "CAQUETÁ":                {"score": 3.8, "zona": "ALTO",        "gravedad": "MEDIO-ALTO",   "municipios": 16},
    "ARAUCA":                 {"score": 3.9, "zona": "ALTO",        "gravedad": "ALTO",        "municipios": 7},
    "CASANARE":               {"score": 2.7, "zona": "BAJO",        "gravedad": "BAJO",        "municipios": 19},
    "VICHADA":                {"score": 2.3, "zona": "MUY BAJO",    "gravedad": "MUY BAJO",    "municipios": 4},
    "GUAINÍA":                {"score": 2.1, "zona": "MUY BAJO",    "gravedad": "MÍNIMO",      "municipios": 8},
    "GUAVIARE":               {"score": 3.2, "zona": "MEDIO-BAJO",  "gravedad": "MEDIO-BAJO",  "municipios": 4},
    "VAUPÉS":                 {"score": 2.0, "zona": "MUY BAJO",    "gravedad": "MÍNIMO",      "municipios": 6},
    "AMAZONAS":               {"score": 2.1, "zona": "MUY BAJO",    "gravedad": "MÍNIMO",      "municipios": 9},
    "PUTUMAYO":               {"score": 3.6, "zona": "MEDIO-ALTO",   "gravedad": "MEDIO-ALTO",   "municipios": 13},
    "CHOCÓ":                  {"score": 4.1, "zona": "ALTO",        "gravedad": "ALTO",        "municipios": 30},
    "SAN ANDRÉS":             {"score": 2.8, "zona": "BAJO",        "gravedad": "BAJO",        "municipios": 2},
}

# Factores de multiplicación por tipo de delito.  Estos valores se usan para
# ajustar el score base de un departamento dependiendo del delito elegido.
DELIT_FACTOR = {
    "HOMICIDIO": 1.4,
    "VIOLENCIA SEXUAL": 1.3,
    "AMENAZAS": 1.1,
    "VIOLENCIA INTRAFAMILIAR": 1.0,
    "LESIONES PERSONALES": 0.9,
    "HURTO": 0.8,
}

###############################################################################
# Funciones de utilidades
###############################################################################

def get_risk_color(score: float) -> str:
    """Devuelve un color acorde al valor del score (entre 0 y 6)."""
    if score >= 4.5:
        return "#7F1D1D"
    if score >= 4.0:
        return "#DC2626"
    if score >= 3.5:
        return "#EF4444"
    if score >= 3.0:
        return "#F59E0B"
    if score >= 2.5:
        return "#3B82F6"
    if score >= 2.0:
        return "#10B981"
    return "#059669"


def calc_prediction(departamento: str, delito: str, year: int) -> dict:
    """
    Calcula una predicción simple del riesgo para un departamento, delito y año
    específico.  Emula la lógica del prototipo original generando valores
    derivados: zona de riesgo, gravedad, número estimado de víctimas, curva de
    tendencia, comparativa con otros delitos y distribución mensual.

    Args:
        departamento: Nombre del departamento.
        delito: Tipo de delito seleccionado.
        year: Año para el cual se calcula la predicción.

    Returns:
        Un diccionario con los valores calculados.
    """
    base = CRIME_DATA.get(departamento, {"score": 3.0, "zona": "MEDIO-BAJO", "gravedad": "BAJO"})
    año_factor = 1.05 if year >= 2024 else (1.0 if year >= 2020 else 0.9)
    adjusted = base["score"] * DELIT_FACTOR.get(delito, 1.0) * año_factor

    # Determinar zona y gravedad en función del score ajustado
    zonas = ["MUY BAJO", "BAJO", "MEDIO-BAJO", "MEDIO-ALTO", "ALTO", "MUY ALTO"]
    gravedades = ["MÍNIMO", "MUY BAJO", "BAJO", "MEDIO-BAJO", "MEDIO-ALTO", "ALTO", "MUY ALTO", "CRÍTICO"]
    zona_idx = min(max(int(round(adjusted)) - 1, 0), 5)
    grav_idx = min(max(int(round(adjusted)), 0), 7)
    zona = zonas[zona_idx]
    gravedad = gravedades[grav_idx]
    victimas = int(round(adjusted * 18 + np.random.rand() * 10))

    # Probabilidades de zona (distribución simple para ilustrar)
    probs_zona = {}
    for i, z in enumerate(zonas):
        dist = abs(i - zona_idx)
        # valores mayores cerca del valor central
        probs_zona[z] = max(2, 100 - dist * 28 + (np.random.rand() * 6 - 3))
    total = sum(probs_zona.values())
    probs_zona = {k: round((v / total) * 100, 1) for k, v in probs_zona.items()}

    # Tendencia temporal (2019–2027). Los años >=2025 se marcan como proyectados.
    years = list(range(2019, 2028))
    trend = []
    for y in years:
        yf = 1.05 if y >= 2024 else (1.0 if y >= 2020 else 0.9)
        noise = np.random.uniform(-0.15, 0.15)
        s = base["score"] * DELIT_FACTOR.get(delito, 1.0) * yf * (1 + (y - 2020) * 0.025) + noise
        score = max(0.5, min(round(s, 2), 6.0))
        trend.append({"year": y, "score": score, "projected": y >= 2025})

    # Comparativa de delitos (score y zona)
    comparativa = []
    for d in DELITOS:
        fac = DELIT_FACTOR.get(d, 1.0)
        sc = base["score"] * fac * año_factor
        zi = min(max(int(round(sc)) - 1, 0), 5)
        comparativa.append({"Delito": d, "Score": round(sc, 1), "Zona": zonas[zi]})
    comparativa.sort(key=lambda x: x["Score"], reverse=True)

    # Datos mensuales (factor estacional simplificado)
    months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    seasonal_factors = [0.85, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.0, 0.95, 1.1, 1.3]
    monthly = []
    for m, fac in zip(months, seasonal_factors):
        value = adjusted * fac * (1 + (np.random.rand() * 0.1 - 0.05))
        cases = int(round(victimas / 12 * fac * (1 + (np.random.rand() * 0.2 - 0.1))))
        monthly.append({"Mes": m, "Índice": round(value, 2), "Casos": cases})

    return {
        "zona": zona,
        "gravedad": gravedad,
        "victimas": victimas,
        "probs_zona": probs_zona,
        "trend": trend,
        "comparativa": comparativa,
        "score": round(adjusted, 1),
        "monthly": monthly,
    }

###############################################################################
# Definición de cada página
###############################################################################

def home_page():
    """Muestra la página de inicio con una descripción general del proyecto."""
    st.title("🛡️ SafeHer Colombia")
    st.markdown(
        """
        **Plataforma Inteligente de Predicción, Prevención y Apoyo para Mujeres en Colombia**

        Este prototipo académico utiliza datos ficticios inspirados en el Sistema de Información
        Estadístico de la Policía Nacional para ofrecer una visión sobre los niveles de riesgo
        en distintas regiones de Colombia. Las funcionalidades incluyen predicción de riesgo,
        información de seguridad para viajes, contactos de emergencia, formularios de denuncia
        y recursos de ayuda. **No debe utilizarse en situaciones de emergencia real**; para ello
        llama inmediatamente a **123** o a la **Línea 155**.
        """
    )

    # Estadísticas generales presentadas en tarjetas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Municipios", "1 121")
    col2.metric("Departamentos", "33")
    col3.metric("Modelos IA", "3 ML")
    col4.metric("Disponible", "24/7")

    st.markdown("---")
    st.subheader("Módulos disponibles")
    st.write(
        "Esta aplicación se compone de varias secciones accesibles desde el menú lateral.\n"
        "- **Predicción ML**: Calcula el nivel de riesgo para un delito y ubicación.\n"
        "- **Mapa de riesgo**: Consulta cómo se distribuye el riesgo entre departamentos.\n"
        "- **Viaje seguro**: Obtén un índice de seguridad antes de viajar.\n"
        "- **Emergencias**: Contactos y consejos en caso de peligro.\n"
        "- **Denuncias**: Formulario anónimo para reportar un hecho.\n"
        "- **Ayuda cercana**: Directorio de entidades de apoyo en tu ciudad.\n"
        "- **Acerca de**: Información sobre este proyecto académico."
    )


def prediccion_page():
    """Página de predicción con formularios y gráficos."""
    st.header("📊 Predicción de Riesgo (ML)")
    st.markdown("Completa los datos para estimar el nivel de riesgo en tu localidad.")

    # Selección de parámetros mediante formularios
    with st.form("prediccion_form"):
        col1, col2 = st.columns(2)
        departamento = col1.selectbox("Departamento", DEPARTAMENTOS, index=1)
        municipio = col2.selectbox("Municipio", get_municipios(departamento))
        delito = st.selectbox("Tipo de delito", DELITOS, index=0)
        sexo = st.selectbox("Sexo de la víctima", ["FEMENINO", "MASCULINO", "OTRO"], index=0)
        edad = st.selectbox(
            "Rango etario",
            ["DE 0 A 12 AÑOS", "DE 13 A 26 AÑOS", "DE 27 A 59 AÑOS", "DE 60 AÑOS EN ADELANTE"],
            index=2,
        )
        year = st.slider("Año", 2019, 2027, 2024)
        submitted = st.form_submit_button("🔍 Calcular predicción")

    if submitted:
        with st.spinner("Calculando predicción..."):
            result = calc_prediction(departamento, delito, year)
        # Mostrar resultados principales
        st.success(f"Zona de Riesgo: **{result['zona']}** · Gravedad: **{result['gravedad']}**")
        st.write(f"Número estimado de víctimas: **{result['victimas']}**")
        st.write(f"Score ajustado: **{result['score']} / 6.0**")

        # Probabilidades de zonas en una tabla
        st.subheader("Probabilidad de cada zona")
        probs_df = pd.DataFrame({"Zona": list(result["probs_zona"].keys()), "Probabilidad (%)": list(result["probs_zona"].values())})
        st.table(probs_df)

        # Comparativa de delitos en forma de gráfico
        st.subheader("Comparativa por tipo de delito")
        compar_df = pd.DataFrame(result["comparativa"])
        chart = alt.Chart(compar_df).mark_bar().encode(
            x=alt.X("Score", title="Score ajustado"),
            y=alt.Y("Delito", sort="-x", title="Delito"),
            color=alt.Color("Score", scale=alt.Scale(domain=[0, 6], range=["#059669", "#7F1D1D"]), legend=None),
        ).properties(height=200)
        st.altair_chart(chart, use_container_width=True)

        # Tendencia temporal
        st.subheader("Tendencia 2019–2027")
        trend_df = pd.DataFrame(result["trend"])
        line_chart = alt.Chart(trend_df).mark_line(point=True).encode(
            x=alt.X("year", title="Año"),
            y=alt.Y("score", title="Score"),
            color=alt.value(C["primary"]),
            tooltip=["year", "score"]
        )
        st.altair_chart(line_chart, use_container_width=True)

        # Distribución mensual
        st.subheader("Distribución mensual estimada")
        monthly_df = pd.DataFrame(result["monthly"])
        bar_month = alt.Chart(monthly_df).mark_bar().encode(
            x=alt.X("Mes", sort=list(monthly_df["Mes"]), title="Mes"),
            y=alt.Y("Índice", title="Índice ajustado"),
            color=alt.value(C["primary_light"])
        )
        st.altair_chart(bar_month, use_container_width=True)


def mapa_page():
    """Página que visualiza el riesgo por departamento en forma de tabla y gráfico."""
    st.header("🗺️ Mapa de Riesgo (resumen)")
    st.markdown(
        "Aquí se presenta un resumen de los niveles de riesgo por departamento. "
        "Para una visualización geográfica detallada se necesitaría integrar un mapa interactivo, "
        "lo cual no se incluye en esta versión simplificada."
    )

    # Crear un DataFrame con los datos de riesgo
    data = []
    for dep, vals in CRIME_DATA.items():
        data.append({"Departamento": dep, "Score": vals["score"], "Zona": vals["zona"], "Gravedad": vals["gravedad"]})
    df = pd.DataFrame(data).sort_values("Score", ascending=False).reset_index(drop=True)

    # Mostrar top 12 en tabla
    st.subheader("Top departamentos por score de riesgo")
    st.dataframe(df.head(12), use_container_width=True)

    # Gráfico de barras para todos los departamentos (score)
    st.subheader("Distribución de score de riesgo por departamento")
    bar_chart = alt.Chart(df).mark_bar().encode(
        y=alt.Y("Departamento", sort="-x", title="Departamento"),
        x=alt.X("Score", title="Score"),
        color=alt.Color("Score", scale=alt.Scale(domain=[0,6], range=["#059669", "#7F1D1D"]), legend=None),
        tooltip=["Departamento", "Score", "Zona", "Gravedad"]
    ).properties(height=500)
    st.altair_chart(bar_chart, use_container_width=True)


def viaje_page():
    """Página que ofrece un índice de seguridad antes de viajar a un departamento."""
    st.header("✈️ Viaje Seguro")
    st.markdown("Selecciona un departamento para evaluar la seguridad relativa de viajar.")

    dep = st.selectbox("Departamento de destino", DEPARTAMENTOS, index=1)
    if st.button("Analizar destino"):
        data = CRIME_DATA.get(dep, {"score": 2.8, "zona": "BAJO", "gravedad": "BAJO", "municipios": 0})
        score = data["score"]
        # Clasificación de seguridad basada en el score (menor score es mejor)
        if score <= 2.0:
            label, color, stars = "Seguro", C["success"], 5
        elif score <= 3.0:
            label, color, stars = "Precaución", C["warning"], 3
        elif score <= 4.0:
            label, color, stars = "Riesgo Medio", C["danger"], 2
        else:
            label, color, stars = "Alto Riesgo", "#991B1B", 1
        st.markdown(f"### {dep}\n**{label}** — Score: **{score}/6.0**")
        st.markdown("⭐" * stars + "☆" * (5 - stars))
        # Mostrar lista de municipios
        st.subheader("Municipios relevantes")
        st.write(", ".join(get_municipios(dep)))
        # Riesgo por tipo de delito
        st.subheader("Riesgo por tipo de delito")
        delito_scores = []
        for d in DELITOS:
            fac = DELIT_FACTOR.get(d, 1.0)
            sc = round(score * fac, 1)
            delito_scores.append({"Delito": d, "Score": sc})
        delito_df = pd.DataFrame(delito_scores).sort_values("Score", ascending=False)
        alt_chart = alt.Chart(delito_df).mark_bar().encode(
            x=alt.X("Score", title="Score"),
            y=alt.Y("Delito", sort="-x", title="Delito"),
            color=alt.value(C["primary"])
        )
        st.altair_chart(alt_chart, use_container_width=True)
        # Recomendaciones generales (no dependemos de IA)
        st.subheader("Recomendaciones generales")
        st.markdown(
            "- **Mantente informada**: consulta los reportes locales de seguridad.\n"
            "- **Evita zonas solitarias** y sal con amigos/as o familiares cuando sea posible.\n"
            "- **Lleva teléfonos de emergencia** (123, 155) y comparte tu ubicación con alguien de confianza.\n"
            "- **Utiliza transporte seguro** (apps confiables, taxis oficiales).\n"
            "- **Confía en tus instintos** y ante cualquier duda, pide ayuda a las autoridades."
        )


def emergencias_page():
    """Página con información de contacto de emergencia."""
    st.header("🚨 Centro de Emergencias")
    st.markdown(
        "Si estás en peligro, utiliza inmediatamente los números de emergencia. "
        "Haz clic en un contacto para copiarlo o marcar en tu teléfono."
    )

    # Tabla de líneas de emergencia
    emergency_contacts = [
        {"Número": "123", "Descripción": "Policía / Emergencias", "Disponibilidad": "24/7"},
        {"Número": "155", "Descripción": "Línea Mujer", "Disponibilidad": "24/7 (gratuita)"},
        {"Número": "125", "Descripción": "Defensa Civil", "Disponibilidad": "24/7"},
        {"Número": "132", "Descripción": "Cruz Roja", "Disponibilidad": "24/7"},
        {"Número": "137", "Descripción": "Salud Mental", "Disponibilidad": "Apoyo psicológico"},
        {"Número": "106", "Descripción": "Bomberos", "Disponibilidad": "24/7"},
    ]
    df_emerg = pd.DataFrame(emergency_contacts)
    st.table(df_emerg)

    st.markdown("---")
    st.subheader("Consejos en caso de emergencia")
    st.markdown(
        "- **Mantén la calma** y busca un lugar seguro y concurrido.\n"
        "- **Llama al 123** o pide a alguien que llame por ti si no puedes hablar.\n"
        "- **Comparte tu ubicación** con amigos o familiares.\n"
        "- **No confrontes al agresor**; tu prioridad es tu seguridad.\n"
        "- **Recoge evidencia sólo si es seguro** (fotos, audios).\n"
    )


def denuncias_page():
    """Página con un formulario simplificado para registrar una denuncia."""
    st.header("📋 Registro de Denuncia")
    st.markdown(
        "Completa el siguiente formulario para registrar un hecho de forma confidencial. "
        "Esta herramienta es un prototipo académico; para denuncias oficiales acude a las "
        "entidades competentes."
    )
    with st.form("denuncia_form"):
        anon = st.checkbox("Quiero denunciar de forma anónima", value=True)
        delito = st.selectbox("Tipo de delito", [""] + DELITOS)
        dep = st.selectbox("Departamento", DEPARTAMENTOS, index=4)
        lugar = st.text_input("Lugar del hecho (barrio, dirección aproximada)")
        fecha = st.date_input("Fecha aproximada")
        hora = st.time_input("Hora aproximada")
        desc = st.text_area(
            "Descripción de los hechos",
            help="Entre más detallado sea tu relato, mejor podrá orientarte la autoridad competente.",
        )
        opts = st.multiselect(
            "Características y solicitudes (opcional)",
            [
                "Violencia física",
                "Violencia verbal",
                "Violencia psicológica",
                "Violencia económica",
                "Seguimiento / acoso",
                "Violencia digital",
                "Tengo evidencia (fotos/audio/video)",
                "Quiero acompañamiento",
                "Necesito protección urgente",
                "Quiero mantener anonimato total",
            ],
        )
        submitted = st.form_submit_button("📤 Registrar y obtener orientación")

    if submitted:
        if not desc.strip():
            st.error("Por favor escribe una descripción del hecho.")
        else:
            # Mostrar confirmación y ofrecer orientación genérica (no se contacta a IA)
            st.success("Tu denuncia ha sido registrada de manera confidencial.")
            st.markdown(
                "### Orientación Jurídica Básica\n"
                "**⚖️ Tus derechos inmediatos**\n"
                "• Tienes derecho a recibir atención prioritaria y gratuita.\n"
                "• Puedes solicitar medidas de protección inmediatas en una Comisaría de Familia.\n"
                "• Nadie puede obligarte a conciliar con tu agresor.\n"
                "\n"
                "**📋 Pasos a seguir**\n"
                "• Dirígete a la Comisaría de Familia o Fiscalía más cercana.\n"
                "• Presenta tu denuncia con la mayor cantidad de detalles y evidencia posible.\n"
                "• Solicita acompañamiento psicológico o legal si lo necesitas.\n"
                "\n"
                "**🏢 Entidades a contactar**\n"
                "• Comisarías de Familia (para medidas de protección).\n"
                "• Fiscalía General (denuncias penales).\n"
                "• Línea 155 (orientación 24/7).\n"
                "\n"
                "**📱 Evidencia a recolectar**\n"
                "• Fotos, videos o audios que demuestren el hecho.\n"
                "• Mensajes de texto, correos electrónicos, capturas de pantalla.\n"
                "• Datos de testigos (nombres, teléfonos).\n"
                "\n"
                "**⏰ Plazos importantes**\n"
                "• Denuncia lo antes posible para proteger tus derechos.\n"
                "• Algunas medidas de protección se pueden otorgar el mismo día de la denuncia.\n"
            )


def ayuda_page():
    """Página con un directorio de entidades de apoyo."""
    st.header("🚔 Ayuda Cercana")
    st.markdown("Encuentra entidades de apoyo cerca de tu ciudad. Los datos aquí son ejemplos.")
    # Lista de entidades ficticias inspiradas en el prototipo
    entidades = [
        {
            "Tipo": "Policía",
            "Nombre": "CAI Centro",
            "Dirección": "Carrera 45 #54-20, Medellín",
            "Teléfono": "123",
            "Horario": "24/7",
            "Descripción": "Atención inmediata para denuncias y emergencias."
        },
        {
            "Tipo": "Hospital",
            "Nombre": "Hospital General de Medellín",
            "Dirección": "Calle 24 #29-6, Medellín",
            "Teléfono": "4411227",
            "Horario": "24/7 Urgencias",
            "Descripción": "Urgencias, medicina forense y apoyo psicológico para víctimas."
        },
        {
            "Tipo": "Fiscalía",
            "Nombre": "Fiscalía Seccional Medellín",
            "Dirección": "Calle 44 #52-165, Medellín",
            "Teléfono": "01-8000-919-748",
            "Horario": "Lun–Vie 7am–5pm",
            "Descripción": "Recepción de denuncias penales y medidas de protección."
        },
        {
            "Tipo": "Refugio",
            "Nombre": "Casa Refugio Luz y Esperanza",
            "Dirección": "Dirección confidencial — llama al 155",
            "Teléfono": "155",
            "Horario": "24/7",
            "Descripción": "Alojamiento temporal seguro para mujeres y sus hijos."
        },
        {
            "Tipo": "Psicología",
            "Nombre": "Centro Atención Psicosocial",
            "Dirección": "Calle 50 #40-20, Medellín",
            "Teléfono": "137",
            "Horario": "Lun–Sáb 8am–8pm",
            "Descripción": "Atención psicológica gratuita y grupos de apoyo."
        },
    ]
    df_ent = pd.DataFrame(entidades)
    st.dataframe(df_ent, use_container_width=True)
    st.markdown("---")
    st.markdown(
        "**¿Cómo encontrar más ayuda?**\n"
        "- Utiliza Google Maps para buscar 'Comisaría de Familia' más cercana a tu ubicación.\n"
        "- Llama a la Línea 155 para orientación sobre refugios y centros de apoyo.\n"
        "- Acércate a cualquier estación de Policía o Fiscalía para denunciar.\n"
        "- Los hospitales prestan atención de urgencias sin costo para víctimas."
    )


def acerca_page():
    """Página con información sobre el proyecto."""
    st.header("ℹ️ Acerca de SafeHer Colombia")
    st.markdown(
        "**SafeHer** es un proyecto académico diseñado para explorar el uso de técnicas de "
        "analítica de datos, aprendizaje automático e interfaces conversacionales en la "
        "prevención y mitigación de la violencia de género en Colombia.\n\n"
        "Los modelos de predicción están inspirados en algoritmos como XGBoost y "
        "LightGBM. Sin embargo, todos los datos utilizados en esta aplicación son "
        "sintéticos o aproximados y **no representan estadísticas oficiales**."
    )
    st.subheader("Equipo de desarrollo")
    st.write("Laura Sofia Beltrán, Dana Yaray Vargas, Vanessa Mora")
    st.subheader("Stack tecnológico")
    tech_data = pd.DataFrame([
        {"Tecnología": "Streamlit", "Uso": "Frontend interactivo"},
        {"Tecnología": "Pandas + NumPy", "Uso": "Procesamiento de datos"},
        {"Tecnología": "Altair", "Uso": "Visualización de gráficos"},
    ])
    st.table(tech_data)
    st.subheader("Cobertura")
    cov_df = pd.DataFrame(
        [
            {"Concepto": "Departamentos", "Valor": 33},
            {"Concepto": "Municipios", "Valor": 1121},
            {"Concepto": "Tipos de delito", "Valor": 6},
            {"Concepto": "Período analizado", "Valor": "2019–2027"},
        ]
    )
    st.table(cov_df)

###############################################################################
# Configuración principal de la aplicación
###############################################################################

def main():
    st.set_page_config(page_title="SafeHer Colombia", page_icon="🛡️", layout="wide")
    # Navegación lateral
    menu = [
        "Inicio",
        "Predicción ML",
        "Mapa de riesgo",
        "Viaje seguro",
        "Emergencias",
        "Denuncias",
        "Ayuda cercana",
        "Acerca de",
    ]
    choice = st.sidebar.radio("Menú", menu)

    if choice == "Inicio":
        home_page()
    elif choice == "Predicción ML":
        prediccion_page()
    elif choice == "Mapa de riesgo":
        mapa_page()
    elif choice == "Viaje seguro":
        viaje_page()
    elif choice == "Emergencias":
        emergencias_page()
    elif choice == "Denuncias":
        denuncias_page()
    elif choice == "Ayuda cercana":
        ayuda_page()
    elif choice == "Acerca de":
        acerca_page()


if __name__ == "__main__":
    main()
