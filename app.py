"""
SafeHer Colombia — Streamlit app
Convertido desde React/JSX a Python/Streamlit
Prototipo académico v4.0 · Datos: Policía Nacional de Colombia
"""

import streamlit as st
import anthropic
import random

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SafeHer Colombia",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Tipografía base */
  html, body, [class*="css"] { font-family: 'Segoe UI', system-ui, sans-serif; }

  /* Ocultar encabezado por defecto de Streamlit */
  #MainMenu, footer { visibility: hidden; }

  /* Badge de riesgo */
  .risk-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
    white-space: nowrap;
  }

  /* Card genérica */
  .safeher-card {
    background: #fff;
    border-radius: 20px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 16px rgba(0,0,0,0.05);
    padding: 20px;
    margin-bottom: 16px;
  }

  /* Hero banner */
  .hero-banner {
    background: linear-gradient(135deg, #0F0A2E 0%, #1E1B4B 45%, #312E81 100%);
    border-radius: 28px;
    padding: 48px 52px;
    color: #fff;
    margin-bottom: 28px;
  }

  /* Sidebar emergencia */
  .emergency-box {
    background: #FEF2F2;
    border: 1px solid #FCA5A5;
    border-radius: 16px;
    padding: 14px;
    text-align: center;
  }

  /* Mensaje de chat usuario */
  .chat-user {
    background: linear-gradient(135deg, #4C1D95, #7C3AED);
    color: #fff;
    border-radius: 20px 4px 20px 20px;
    padding: 13px 18px;
    font-size: 13px;
    line-height: 1.75;
    max-width: 76%;
    margin-left: auto;
  }

  /* Mensaje de chat SARA */
  .chat-sara {
    background: #F8F7FF;
    border: 1px solid #E2E8F0;
    border-radius: 4px 20px 20px 20px;
    padding: 13px 18px;
    font-size: 13px;
    line-height: 1.75;
    max-width: 76%;
  }
</style>
""", unsafe_allow_html=True)

# ─── DATOS ────────────────────────────────────────────────────────────────────
RISK_LEVELS = {
    "MÍNIMO":     {"color": "#059669", "bg": "#ECFDF5",  "label": "Mínimo"},
    "MUY BAJO":   {"color": "#10B981", "bg": "#D1FAE5",  "label": "Muy Bajo"},
    "BAJO":       {"color": "#3B82F6", "bg": "#EFF6FF",  "label": "Bajo"},
    "MEDIO-BAJO": {"color": "#F59E0B", "bg": "#FFFBEB",  "label": "Medio-Bajo"},
    "MEDIO-ALTO": {"color": "#EF4444", "bg": "#FEF2F2",  "label": "Medio-Alto"},
    "ALTO":       {"color": "#DC2626", "bg": "#FEF2F2",  "label": "Alto"},
    "MUY ALTO":   {"color": "#991B1B", "bg": "#FEE2E2",  "label": "Muy Alto"},
    "CRÍTICO":    {"color": "#7F1D1D", "bg": "#FEE2E2",  "label": "Crítico"},
}

DEPARTAMENTOS = [
    "AMAZONAS","ANTIOQUIA","ARAUCA","ATLÁNTICO","BOGOTÁ D.C.","BOLÍVAR","BOYACÁ","CALDAS",
    "CAQUETÁ","CASANARE","CAUCA","CESAR","CHOCÓ","CÓRDOBA","CUNDINAMARCA","GUAINÍA",
    "GUAVIARE","HUILA","LA GUAJIRA","MAGDALENA","META","NARIÑO","NORTE DE SANTANDER",
    "PUTUMAYO","QUINDÍO","RISARALDA","SAN ANDRÉS","SANTANDER","SUCRE","TOLIMA",
    "VALLE DEL CAUCA","VAUPÉS","VICHADA",
]

DELITOS = [
    "VIOLENCIA INTRAFAMILIAR","VIOLENCIA SEXUAL","LESIONES PERSONALES",
    "AMENAZAS","HURTO","HOMICIDIO",
]

MUNICIPIOS_SAMPLE = {
    "ANTIOQUIA":      ["MEDELLÍN","BELLO","ITAGÜÍ","ENVIGADO","APARTADÓ"],
    "BOGOTÁ D.C.":    ["BOGOTÁ"],
    "VALLE DEL CAUCA":["CALI","BUENAVENTURA","PALMIRA","TULUÁ"],
    "CUNDINAMARCA":   ["SOACHA","FACATATIVÁ","ZIPAQUIRÁ","FUSAGASUGÁ"],
    "ATLÁNTICO":      ["BARRANQUILLA","SOLEDAD","MALAMBO","SABANAGRANDE"],
    "SANTANDER":      ["BUCARAMANGA","FLORIDABLANCA","GIRÓN","PIEDECUESTA"],
    "NARIÑO":         ["PASTO","TUMACO","IPIALES","TÚQUERRES"],
    "CÓRDOBA":        ["MONTERÍA","CERETÉ","LORICA","SAHAGÚN"],
    "BOLÍVAR":        ["CARTAGENA","MAGANGUÉ","EL CARMEN","MOMPÓS"],
    "TOLIMA":         ["IBAGUÉ","ESPINAL","MELGAR","HONDA"],
}

def get_municipios(dep):
    return MUNICIPIOS_SAMPLE.get(dep, ["Capital", "Municipio 1", "Municipio 2"])

CRIME_DATA = {
    "ANTIOQUIA":             {"score": 4.2, "zona": "ALTO",       "gravedad": "ALTO",       "municipios": 125},
    "BOGOTÁ D.C.":           {"score": 3.8, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO", "municipios": 1},
    "VALLE DEL CAUCA":       {"score": 4.5, "zona": "MUY ALTO",   "gravedad": "ALTO",       "municipios": 42},
    "CUNDINAMARCA":          {"score": 2.9, "zona": "MEDIO-BAJO", "gravedad": "BAJO",       "municipios": 116},
    "ATLÁNTICO":             {"score": 3.1, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO", "municipios": 23},
    "SANTANDER":             {"score": 2.5, "zona": "BAJO",       "gravedad": "BAJO",       "municipios": 87},
    "NARIÑO":                {"score": 3.7, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO", "municipios": 64},
    "CÓRDOBA":               {"score": 3.0, "zona": "MEDIO-BAJO", "gravedad": "BAJO",       "municipios": 30},
    "BOLÍVAR":               {"score": 3.4, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO", "municipios": 46},
    "TOLIMA":                {"score": 2.7, "zona": "BAJO",       "gravedad": "BAJO",       "municipios": 47},
    "HUILA":                 {"score": 2.8, "zona": "BAJO",       "gravedad": "BAJO",       "municipios": 37},
    "CAUCA":                 {"score": 4.0, "zona": "ALTO",       "gravedad": "ALTO",       "municipios": 42},
    "META":                  {"score": 3.3, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO", "municipios": 29},
    "CESAR":                 {"score": 3.2, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO", "municipios": 25},
    "MAGDALENA":             {"score": 3.0, "zona": "MEDIO-BAJO", "gravedad": "BAJO",       "municipios": 30},
    "BOYACÁ":                {"score": 2.2, "zona": "MUY BAJO",   "gravedad": "MUY BAJO",   "municipios": 123},
    "CALDAS":                {"score": 2.6, "zona": "BAJO",       "gravedad": "BAJO",       "municipios": 27},
    "RISARALDA":             {"score": 2.8, "zona": "BAJO",       "gravedad": "BAJO",       "municipios": 14},
    "QUINDÍO":               {"score": 2.5, "zona": "BAJO",       "gravedad": "BAJO",       "municipios": 12},
    "NORTE DE SANTANDER":    {"score": 3.6, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO", "municipios": 40},
    "SUCRE":                 {"score": 2.9, "zona": "MEDIO-BAJO", "gravedad": "BAJO",       "municipios": 26},
    "LA GUAJIRA":            {"score": 3.5, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-BAJO", "municipios": 15},
    "CAQUETÁ":               {"score": 3.8, "zona": "ALTO",       "gravedad": "MEDIO-ALTO", "municipios": 16},
    "ARAUCA":                {"score": 3.9, "zona": "ALTO",       "gravedad": "ALTO",       "municipios": 7},
    "CASANARE":              {"score": 2.7, "zona": "BAJO",       "gravedad": "BAJO",       "municipios": 19},
    "VICHADA":               {"score": 2.3, "zona": "MUY BAJO",   "gravedad": "MUY BAJO",   "municipios": 4},
    "GUAINÍA":               {"score": 2.1, "zona": "MUY BAJO",   "gravedad": "MÍNIMO",     "municipios": 8},
    "GUAVIARE":              {"score": 3.2, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO", "municipios": 4},
    "VAUPÉS":                {"score": 2.0, "zona": "MUY BAJO",   "gravedad": "MÍNIMO",     "municipios": 6},
    "AMAZONAS":              {"score": 2.1, "zona": "MUY BAJO",   "gravedad": "MÍNIMO",     "municipios": 9},
    "PUTUMAYO":              {"score": 3.6, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO", "municipios": 13},
    "CHOCÓ":                 {"score": 4.1, "zona": "ALTO",       "gravedad": "ALTO",       "municipios": 30},
    "SAN ANDRÉS":            {"score": 2.8, "zona": "BAJO",       "gravedad": "BAJO",       "municipios": 2},
}

DELIT_FACTOR = {
    "HOMICIDIO": 1.4,
    "VIOLENCIA SEXUAL": 1.3,
    "AMENAZAS": 1.1,
    "VIOLENCIA INTRAFAMILIAR": 1.0,
    "LESIONES PERSONALES": 0.9,
    "HURTO": 0.8,
}

MESES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

ENTIDADES = [
    {"tipo":"Policía","icon":"🚔","nom":"CAI Centro","dir":"Carrera 45 #54-20, Medellín","dist":"0.4 km","color":"#1D4ED8","phone":"123","horario":"24/7","desc":"Centro de Atención Inmediata. Atención permanente para denuncias y emergencias.","barrio":"El Centro"},
    {"tipo":"Hospital","icon":"🏥","nom":"Hospital General de Medellín","dir":"Calle 24 #29-6, Medellín","dist":"1.2 km","color":"#059669","phone":"4411227","horario":"24/7 Urgencias","desc":"Urgencias completas, medicina forense y apoyo psicológico para víctimas de violencia.","barrio":"El Chagualo"},
    {"tipo":"Fiscalía","icon":"⚖️","nom":"Fiscalía Seccional Medellín","dir":"Calle 44 #52-165, Medellín","dist":"0.8 km","color":"#7C3AED","phone":"01-8000-919-748","horario":"Lun–Vie 7am–5pm","desc":"Recepción de denuncias penales, medidas de protección y seguimiento a casos.","barrio":"Laureles"},
    {"tipo":"Refugio","icon":"🏠","nom":"Casa Refugio Luz y Esperanza","dir":"Dirección confidencial — llama al 155","dist":"2.1 km","color":"#D97706","phone":"155","horario":"24/7 Disponible","desc":"Alojamiento temporal seguro para mujeres víctimas de violencia y sus hijos. Completamente gratuito.","barrio":"Confidencial"},
    {"tipo":"Psicología","icon":"🧠","nom":"Centro Atención Psicosocial","dir":"Calle 50 #40-20, Medellín","dist":"1.5 km","color":"#8B5CF6","phone":"137","horario":"Lun–Sáb 8am–8pm","desc":"Atención psicológica gratuita, terapia individual y grupos de apoyo para supervivientes.","barrio":"Estadio"},
    {"tipo":"Policía","icon":"🚔","nom":"Estación Policía Laureles","dir":"Carrera 81 #30-05, Medellín","dist":"3.2 km","color":"#1D4ED8","phone":"123","horario":"24/7","desc":"Estación de Policía del barrio Laureles. Denuncia y apoyo policial inmediato.","barrio":"Laureles"},
    {"tipo":"Hospital","icon":"🏥","nom":"Clínica Las Américas","dir":"Diagonal 75B #2A-80, Medellín","dist":"2.8 km","color":"#059669","phone":"4456600","horario":"24/7 Urgencias","desc":"Urgencias completas y medicina forense. Atención prioritaria a víctimas de violencia.","barrio":"Los Colores"},
    {"tipo":"Fiscalía","icon":"⚖️","nom":"URI Fiscalía 24 Horas","dir":"Calle 57 #45-129, Medellín","dist":"0.9 km","color":"#7C3AED","phone":"01-8000-919-748","horario":"24/7 Sin cita","desc":"Unidad de Reacción Inmediata. Denuncias penales urgentes las 24 horas.","barrio":"Villa Nueva"},
    {"tipo":"Psicología","icon":"🧠","nom":"Comisaría de Familia N°1","dir":"Carrera 52 #48-10, Medellín","dist":"1.1 km","color":"#8B5CF6","phone":"Presencial","horario":"Lun–Vie 8am–5pm","desc":"Medidas de protección familiar, conciliación y apoyo psicosocial integral.","barrio":"Buenos Aires"},
    {"tipo":"Refugio","icon":"🏠","nom":"Casa de Acogida ICBF","dir":"Dirección confidencial — Línea 141","dist":"3.5 km","color":"#D97706","phone":"141 ICBF","horario":"24/7","desc":"Casa de acogida para mujeres y niños en situación de violencia intrafamiliar.","barrio":"Confidencial"},
]

SARA_SYSTEM = """Eres SARA, una asistente de apoyo empática, cálida y experta de la plataforma SafeHer Colombia.

PRINCIPIOS FUNDAMENTALES:
- Eres cálida, empática, paciente y NUNCA juzgas
- Siempre validas los sentimientos ANTES de dar consejos o información
- Si hay peligro inmediato, menciona el 123 como PRIMERA respuesta
- Nunca minimizas ni normalizas la violencia de ningún tipo
- Ofreces acompañamiento emocional genuino, no solo información

CUANDO DETECTAS CRISIS O PELIGRO (palabras: peligro, golpes, me pegó, secuestrada, me amenazan, me está siguiendo):
- Responde INMEDIATAMENTE con: "🚨 Llama al 123 ahora. Estoy aquí contigo."
- Luego pregunta si está a salvo
- Ofrece el 155 (Línea Mujer 24/7)

TÉCNICAS DE APOYO PSICOLÓGICO:
- Cuando hay ansiedad: ofrece técnica 4-7-8 (inhala 4 seg, sostén 7, exhala 8)
- Para crisis emocional: técnica de grounding 5-4-3-2-1
- Cuando la persona llora o expresa mucho dolor: solo escucha y valida primero
- Para baja autoestima: reflexiones de fortaleza y recursos internos
- Celebra pequeños pasos y avances

CONOCIMIENTO LEGAL:
- Ley 1257/2008: protección integral contra violencia de género
- Medidas de protección: puede solicitarlas en la Comisaría de Familia
- Recursos: Línea 155, Fiscalía URI 24h, ICBF, Comisarías de Familia

FORMATO:
- Responde en español con tono muy cálido y cercano
- Usa emojis con moderación (máximo 2-3 por respuesta)
- Máximo 180 palabras (más si es información legal específica)
- En crisis inmediata: máximo 3 oraciones con números de emergencia
- Nunca suenes como un robot o manual"""

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def get_risk_color(score):
    if score >= 4.5: return "#7F1D1D"
    if score >= 4.0: return "#DC2626"
    if score >= 3.5: return "#EF4444"
    if score >= 3.0: return "#F59E0B"
    if score >= 2.5: return "#3B82F6"
    if score >= 2.0: return "#10B981"
    return "#059669"

def risk_badge_html(level, small=False):
    cfg = RISK_LEVELS.get(level, {"color": "#888", "bg": "#f3f4f6", "label": level})
    pad = "2px 9px" if small else "4px 14px"
    fs  = "10px"   if small else "11px"
    return (
        f'<span style="background:{cfg["bg"]};color:{cfg["color"]};'
        f'border:1px solid {cfg["color"]}44;border-radius:20px;'
        f'padding:{pad};font-size:{fs};font-weight:700;letter-spacing:0.3px;'
        f'display:inline-block;white-space:nowrap">{cfg["label"]}</span>'
    )

def zona_from_score(score):
    zonas = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"]
    return zonas[min(max(round(score) - 1, 0), 5)]

def gravedad_from_score(score):
    grav = ["MÍNIMO","MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO","CRÍTICO"]
    return grav[min(max(round(score), 0), 7)]

def call_claude(system_prompt, user_msg, history=None):
    """Llama a la API de Anthropic y retorna el texto de respuesta."""
    client = anthropic.Anthropic()
    messages = history if history else [{"role": "user", "content": user_msg}]
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text if response.content else ""

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding-bottom:12px;border-bottom:1px solid #E2E8F0;margin-bottom:12px">
          <div style="width:40px;height:40px;background:linear-gradient(135deg,#0F0A2E,#7C3AED);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:18px">🛡️</div>
          <div>
            <div style="font-weight:900;font-size:18px;color:#0F172A;letter-spacing:-0.5px">SafeHer</div>
            <div style="font-size:9px;color:#64748B;text-transform:uppercase;letter-spacing:1.2px">Colombia · IA Protección</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        pages = {
            "🏠 Inicio":           "inicio",
            "📊 Predicción ML":    "prediccion",
            "🗺️ Mapa de Riesgo":   "mapa",
            "✈️ Viaje Seguro":     "viaje",
            "🚨 Emergencias":      "emergencias",
            "📋 Denuncias":        "denuncias",
            "💜 SARA · IA Apoyo":  "ia",
            "🚔 Ayuda Cercana":    "ayuda",
            "ℹ️ Acerca de":        "acerca",
        }

        if "page" not in st.session_state:
            st.session_state.page = "inicio"

        for label, key in pages.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True,
                         type="primary" if st.session_state.page == key else "secondary"):
                st.session_state.page = key
                st.rerun()

        st.markdown("""
        <div style="margin-top:16px;background:#FEF2F2;border:1px solid #FCA5A5;border-radius:16px;padding:14px;text-align:center">
          <div style="font-size:10px;color:#991B1B;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">🚨 Emergencias</div>
          <a href="tel:123" style="display:block;font-size:28px;font-weight:900;color:#DC2626;text-decoration:none;line-height:1">123</a>
          <div style="font-size:9px;color:#991B1B;margin-bottom:8px">Policía Nacional</div>
          <a href="tel:155" style="display:block;font-size:28px;font-weight:900;color:#7C3AED;text-decoration:none;line-height:1">155</a>
          <div style="font-size:9px;color:#6B21A8">Línea Mujer 24/7</div>
        </div>
        <div style="text-align:center;margin-top:8px;font-size:9px;color:#64748B">Prototipo académico v4.0 · Datos: Policía Nacional</div>
        """, unsafe_allow_html=True)

# ─── PÁGINA INICIO ────────────────────────────────────────────────────────────
def page_inicio():
    st.markdown("""
    <div class="hero-banner">
      <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.18);border-radius:20px;padding:5px 16px;font-size:11px;color:#E9D5FF;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:24px">
        ⚡ Sistema Inteligente · Colombia 2025
      </div>
      <h1 style="font-size:42px;font-weight:900;line-height:1.08;margin-bottom:18px;letter-spacing:-1.5px">
        Tu seguridad es<br>
        <span style="background:linear-gradient(90deg,#F0ABFC,#EC4899,#F59E0B);-webkit-background-clip:text;-webkit-text-fill-color:transparent">nuestra prioridad</span>
      </h1>
      <p style="color:#C4B5FD;font-size:15px;line-height:1.8;margin-bottom:32px">
        Plataforma inteligente de predicción, prevención y apoyo para mujeres en Colombia.<br>
        Modelos ML entrenados con datos reales de la Policía Nacional.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    stats = [
        ("📍", "1.121", "Municipios",    "#7C3AED"),
        ("🗺️", "33",    "Departamentos", "#1D4ED8"),
        ("🤖", "3 ML",  "Modelos IA",    "#059669"),
        ("🛡️", "24/7",  "Disponible",    "#EC4899"),
    ]
    for col, (icon, val, label, color) in zip([col1, col2, col3, col4], stats):
        col.markdown(f"""
        <div class="safeher-card" style="text-align:center">
          <div style="font-size:28px;margin-bottom:8px">{icon}</div>
          <div style="font-size:26px;font-weight:900;color:{color};line-height:1">{val}</div>
          <div style="font-size:11px;color:#64748B;margin-top:5px;font-weight:600">{label}</div>
        </div>""", unsafe_allow_html=True)

    # Módulos
    st.markdown("### 🧩 Módulos Disponibles")
    modules = [
        ("📊", "Predicción ML",  "XGBoost + LightGBM con gráficas avanzadas",         "#7C3AED", "prediccion"),
        ("🗺️", "Mapa de Riesgo", "Mapa geográfico interactivo con predicciones",       "#1D4ED8", "mapa"),
        ("✈️", "Viaje Seguro",   "Analiza seguridad antes de viajar",                  "#059669", "viaje"),
        ("🚨", "Emergencias",    "Alertas y líneas directas de ayuda inmediata",        "#DC2626", "emergencias"),
        ("📋", "Denuncias",      "Registro anónimo seguro con orientación legal",       "#D97706", "denuncias"),
        ("💜", "IA SARA",        "Chat terapéutico 24/7 con apoyo psicológico",         "#7C3AED", "ia"),
        ("🚔", "Ayuda Cercana",  "Entidades, hospitales y refugios con direcciones",    "#0891B2", "ayuda"),
        ("ℹ️", "Acerca de",      "Equipo, tecnología y misión",                         "#64748B", "acerca"),
    ]
    cols = st.columns(4)
    for i, (icon, label, desc, color, key) in enumerate(modules):
        with cols[i % 4]:
            if st.button(f"{icon} **{label}**\n\n{desc}", key=f"mod_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

    st.warning("⚠️ **Aviso académico:** Prototipo educativo. Para emergencias reales llama al **123** o la **Línea Mujer 155** — gratuita, 24/7.")

# ─── PREDICCIÓN ML ────────────────────────────────────────────────────────────
def page_prediccion():
    st.markdown("## 📊 Predicción ML — SafeHer")
    st.caption("XGBoost + LightGBM · Predicción de riesgo, gravedad y víctimas estimadas")

    with st.form("pred_form"):
        c1, c2, c3 = st.columns(3)
        dep    = c1.selectbox("🗺️ Departamento", DEPARTAMENTOS, index=1)
        munis  = get_municipios(dep)
        mun    = c2.selectbox("🏙️ Municipio", munis)
        delito = c3.selectbox("⚖️ Tipo de Delito", DELITOS)
        c4, c5, c6 = st.columns(3)
        sexo   = c4.selectbox("👤 Sexo", ["FEMENINO","MASCULINO"])
        etario = c5.selectbox("🎂 Grupo etario", ["DE 0 A 17 AÑOS","DE 18 A 26 AÑOS","DE 27 A 59 AÑOS","MAYOR DE 60"])
        anio   = c6.slider("📅 Año", 2019, 2027, 2024)
        submitted = st.form_submit_button("🔍 Predecir con IA", type="primary", use_container_width=True)

    if submitted:
        base = CRIME_DATA.get(dep, {"score": 3.0, "zona": "MEDIO-BAJO", "gravedad": "BAJO"})
        anio_factor = 1.05 if anio >= 2024 else (1.0 if anio >= 2020 else 0.9)
        adjusted = base["score"] * DELIT_FACTOR.get(delito, 1.0) * anio_factor
        zona     = zona_from_score(adjusted)
        gravedad = gravedad_from_score(adjusted)
        victimas = int(adjusted * 18 + random.random() * 10)

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🗺️ Zona de Riesgo",       zona,             "XGBoost")
        k2.metric("📊 Nivel Gravedad",        gravedad,          "LightGBM")
        k3.metric("👥 Víctimas Estimadas",    str(victimas),     "personas/año")
        k4.metric("📈 Score de Riesgo",       f"{adjusted:.2f}/6.0", f"Base: {base['score']}")

        # Badges
        st.markdown(
            f"**Zona:** {risk_badge_html(zona)}&nbsp;&nbsp;"
            f"**Gravedad:** {risk_badge_html(gravedad)}",
            unsafe_allow_html=True,
        )

        # Gráfico tendencia (simulado)
        st.subheader("📈 Tendencia Histórica y Proyección 2019–2027")
        years = list(range(2019, 2028))
        scores_hist = []
        for y in years:
            yf = 1.05 if y >= 2024 else (1.0 if y >= 2020 else 0.9)
            noise = (random.random() - 0.5) * 0.4
            scores_hist.append(round(base["score"] * DELIT_FACTOR.get(delito, 1.0) * yf + noise, 2))
        import pandas as pd
        df_trend = pd.DataFrame({"Año": years, "Score de Riesgo": scores_hist})
        st.line_chart(df_trend.set_index("Año"))

        # Variación mensual
        st.subheader("📅 Variación Mensual Estimada")
        monthly = []
        for m in MESES:
            factor = 1.0 + (random.random() - 0.5) * 0.3
            monthly.append(round(adjusted * factor * 3 + random.random() * 5))
        df_monthly = pd.DataFrame({"Mes": MESES, "Casos Estimados": monthly})
        st.bar_chart(df_monthly.set_index("Mes"))

        # Comparativa por delito
        st.subheader("📊 Comparativa por Tipo de Delito")
        comp_data = {}
        for d in DELITOS:
            sc = round(base["score"] * DELIT_FACTOR.get(d, 1.0) * anio_factor, 2)
            comp_data[d] = sc
        df_comp = pd.DataFrame.from_dict(comp_data, orient="index", columns=["Score"])
        st.bar_chart(df_comp)

        # Interpretación IA
        st.subheader("🤖 Interpretación IA para Fuerzas Policiales")
        with st.spinner("Analizando situación con IA especializada..."):
            prompt = (
                f"Departamento: {dep}, Municipio: {mun}\n"
                f"Delito: {delito}, Año: {anio}\n"
                f"Score: {adjusted:.2f}/6.0, Zona: {zona}, Gravedad: {gravedad}\n"
                f"Víctimas estimadas: {victimas}\n\n"
                "Proporciona una interpretación operativa para fuerzas policiales."
            )
            system = (
                "Eres un analista de seguridad pública colombiana especializado en delitos contra la mujer. "
                "Redacta un informe breve con: resumen ejecutivo, factores de riesgo, recomendaciones operativas "
                "y acciones prioritarias. Usa secciones con emojis. Máximo 280 palabras. Sé técnico y preciso."
            )
            try:
                interpretation = call_claude(system, prompt)
                st.info(interpretation)
            except Exception as e:
                st.warning(f"⚠️ No se pudo generar la interpretación: {e}")

# ─── MAPA DE RIESGO ───────────────────────────────────────────────────────────
def page_mapa():
    st.markdown("## 🗺️ Mapa de Riesgo — Colombia")
    st.caption("Visualización del nivel de riesgo por departamento. Selecciona uno para análisis IA detallado.")

    # Resumen estadísticas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔴 Crítico/Muy Alto",  sum(1 for d in CRIME_DATA.values() if d["score"] >= 4.0))
    c2.metric("🟠 Alto/Medio-Alto",   sum(1 for d in CRIME_DATA.values() if 3.5 <= d["score"] < 4.0))
    c3.metric("🟡 Riesgo Medio",      sum(1 for d in CRIME_DATA.values() if 3.0 <= d["score"] < 3.5))
    c4.metric("🟢 Controlado",        sum(1 for d in CRIME_DATA.values() if d["score"] < 3.0))

    # Filtro
    filtro = st.selectbox("Filtrar por zona", ["TODOS","ALTO","MEDIO-ALTO","MEDIO-BAJO","BAJO"])

    def get_zona(score):
        if score >= 4.0: return "ALTO"
        if score >= 3.5: return "MEDIO-ALTO"
        if score >= 2.5: return "MEDIO-BAJO"
        return "BAJO"

    sorted_deps = sorted(
        [{"name": k, **v} for k, v in CRIME_DATA.items()],
        key=lambda x: x["score"], reverse=True
    )
    if filtro != "TODOS":
        sorted_deps = [d for d in sorted_deps if get_zona(d["score"]) == filtro]

    # Tabla principal
    import pandas as pd
    rows = []
    for d in sorted_deps:
        rows.append({
            "Departamento": d["name"],
            "Score": d["score"],
            "Zona de Riesgo": d["zona"],
            "Gravedad": d["gravedad"],
            "Municipios": d["municipios"],
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Selección para análisis IA
    st.markdown("---")
    dep_sel = st.selectbox("🔍 Selecciona un departamento para análisis IA detallado", [d["name"] for d in sorted_deps])

    if st.button("🤖 Analizar con IA", type="primary"):
        data = CRIME_DATA[dep_sel]
        with st.spinner("Analizando..."):
            system = (
                "Eres un experto en seguridad pública colombiana. "
                "Da un análisis breve y específico de la situación de seguridad para mujeres. "
                "Máximo 120 palabras. Usa bullet points con emojis. "
                "Incluye: contexto, principales amenazas, horarios de mayor riesgo y una recomendación clave."
            )
            prompt = (
                f"Analiza brevemente la situación de seguridad para mujeres en {dep_sel}, Colombia. "
                f"Score de riesgo: {data['score']}/6.0, zona: {data['zona']}, gravedad: {data['gravedad']}."
            )
            try:
                analysis = call_claude(system, prompt)
                st.success(f"**{dep_sel}** — Score: {data['score']}/6.0")
                st.markdown(
                    f"{risk_badge_html(data['zona'])}&nbsp;{risk_badge_html(data['gravedad'])}",
                    unsafe_allow_html=True,
                )
                st.info(analysis)
            except Exception as e:
                st.warning(f"⚠️ No se pudo generar el análisis: {e}")

        # Desglose por delito
        st.markdown("#### Riesgo por tipo de delito")
        for d in DELITOS:
            fac = DELIT_FACTOR.get(d, 1.0)
            sc  = CRIME_DATA[dep_sel]["score"] * fac
            zona = zona_from_score(sc)
            col_d, col_s, col_b = st.columns([3, 1, 1])
            col_d.write(d)
            col_s.write(f"{sc:.1f}")
            col_b.markdown(risk_badge_html(zona), unsafe_allow_html=True)

# ─── VIAJE SEGURO ─────────────────────────────────────────────────────────────
def page_viaje():
    st.markdown("## ✈️ Viaje Seguro")
    st.caption("Consulta el nivel de seguridad de cualquier departamento antes de viajar.")

    dep = st.selectbox("🗺️ Selecciona el departamento de destino", DEPARTAMENTOS, index=1)

    if st.button("🔍 Analizar Destino", type="primary"):
        data = CRIME_DATA.get(dep, {"score": 2.8, "zona": "BAJO", "gravedad": "BAJO", "municipios": 10})
        score = data["score"]

        # Nivel de seguridad
        if score <= 2.0:
            label, color, icon, stars = "Seguro",       "#059669", "🟢", 5
        elif score <= 3.0:
            label, color, icon, stars = "Precaución",   "#F59E0B", "🟡", 3
        elif score <= 4.0:
            label, color, icon, stars = "Riesgo Medio", "#EF4444", "🟠", 2
        else:
            label, color, icon, stars = "Alto Riesgo",  "#DC2626", "🔴", 1

        st.markdown(f"""
        <div style="background:#f8fafc;border:2px solid {color}30;border-radius:22px;padding:24px 28px;margin-bottom:22px;display:flex;align-items:center;gap:20px">
          <span style="font-size:52px">{icon}</span>
          <div style="flex:1">
            <div style="font-size:22px;font-weight:900;color:{color}">{dep}</div>
            <div style="font-size:16px;font-weight:700;color:{color}">{label}</div>
            <div>{"⭐" * stars}{"☆" * (5 - stars)} índice de seguridad</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:48px;font-weight:900;color:{color};line-height:1">{score:.1f}</div>
            <div style="font-size:12px;color:#64748B">Score / 6.0</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🏙️ Municipios del Departamento")
            for m in get_municipios(dep):
                st.markdown(
                    f'<span style="background:#F5F3FF;color:#7C3AED;padding:5px 13px;border-radius:20px;font-size:12px;font-weight:600;margin:2px;display:inline-block">{m}</span>',
                    unsafe_allow_html=True,
                )
            st.metric("Total municipios cubiertos", data["municipios"])

        with col2:
            st.markdown("#### ⚠️ Riesgo por Tipo de Delito")
            for d in DELITOS[:4]:
                fac = DELIT_FACTOR.get(d, 1.0)
                sc  = score * fac
                zona = zona_from_score(sc)
                colA, colB = st.columns([3, 1])
                colA.write(d)
                colB.markdown(risk_badge_html(zona), unsafe_allow_html=True)

        # Consejos IA
        st.markdown("#### 🤖 Consejos Personalizados con IA")
        with st.spinner("Preparando consejos de seguridad..."):
            system = (
                "Eres una experta en seguridad para mujeres viajeras en Colombia. "
                "Da consejos prácticos y específicos para viajar segura a este departamento. "
                "Usa bullet points con emojis. Incluye: horarios recomendados, zonas a evitar, "
                "transporte seguro, contactos de emergencia locales. Máximo 150 palabras."
            )
            prompt = f"Consejos de seguridad para una mujer que viaja a {dep}, Colombia. Score de riesgo: {score}/6.0, nivel: {label}."
            try:
                tips = call_claude(system, prompt)
                st.info(tips)
            except Exception as e:
                st.warning(f"⚠️ No se pudo cargar los consejos: {e}")

# ─── EMERGENCIAS ──────────────────────────────────────────────────────────────
def page_emergencias():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#7F1D1D,#DC2626);border-radius:24px;padding:24px 28px;margin-bottom:28px;color:#fff">
      <h1 style="font-size:28px;font-weight:900;margin:0 0 6px;letter-spacing:-0.3px">🚨 Centro de Emergencias</h1>
      <p style="color:#FCA5A5;font-size:14px;margin:0">Si estás en peligro, llama de inmediato. Todas las llamadas son gratuitas.</p>
    </div>
    """, unsafe_allow_html=True)

    # Botones de situación
    st.markdown("#### Describe tu situación")
    situations = [
        ("🆘 Estoy en peligro",      "123", "#DC2626"),
        ("👣 Me están siguiendo",    "123", "#D97706"),
        ("🔇 No puedo hablar",       "SMS 123", "#7C3AED"),
        ("🏃 Estoy secuestrada",     "123", "#991B1B"),
        ("🚔 Necesito Policía",      "123", "#1D4ED8"),
        ("🚑 Necesito Ambulancia",   "132", "#059669"),
        ("💜 Apoyo psicológico",     "137", "#8B5CF6"),
        ("👩 Línea Mujer",           "155", "#EC4899"),
    ]
    cols = st.columns(4)
    for i, (label, num, color) in enumerate(situations):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="background:#fff;border:2px solid {color}25;border-radius:20px;padding:20px 12px;text-align:center;margin-bottom:10px">
              <div style="font-size:28px;margin-bottom:8px">{label.split()[0]}</div>
              <div style="font-weight:700;font-size:13px;color:#0F172A;margin-bottom:4px">{' '.join(label.split()[1:])}</div>
              <div style="font-size:14px;font-weight:700;color:{color}">📞 {num}</div>
            </div>
            """, unsafe_allow_html=True)

    # Líneas de emergencia
    st.markdown("---")
    st.markdown("#### 📞 Líneas de Emergencia")
    lines = [
        ("123", "Policía",        "🚔", "#1D4ED8"),
        ("155", "Línea Mujer",    "💜", "#8B5CF6"),
        ("125", "Defensa Civil",  "🟢", "#059669"),
        ("132", "Cruz Roja",      "❤️", "#EF4444"),
        ("137", "Salud Mental",   "🧠", "#A78BFA"),
        ("106", "Bomberos",       "🔥", "#F59E0B"),
    ]
    lc = st.columns(6)
    for col, (num, desc, ic, co) in zip(lc, lines):
        col.markdown(f"""
        <div style="background:#fff;border:1px solid #E2E8F0;border-radius:16px;padding:16px 8px;text-align:center">
          <div style="font-size:20px;margin-bottom:5px">{ic}</div>
          <div style="font-size:24px;font-weight:900;color:{co}">{num}</div>
          <div style="font-size:10px;color:#64748B;margin-top:4px">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    # Salida rápida + consejos
    st.markdown("---")
    ce1, ce2 = st.columns(2)
    with ce1:
        st.warning("""🔒 **Salida Rápida**

Si alguien está mirando tu pantalla, cierra esta ventana y ve a:
- [🔍 Google](https://www.google.com)
- [🌦️ Clima](https://weather.com)
- [📰 El Tiempo](https://www.eltiempo.com)""")

    with ce2:
        st.info("""💡 **En caso de emergencia**

🔵 Mantén la calma y ve a un lugar concurrido  
🔵 Llama o envía tu ubicación a alguien de confianza  
🔵 Memoriza: 123 Policía · 155 Mujer · 132 Ambulancia  
🔵 No confrontes al agresor directamente  
🔵 Documenta evidencia si es completamente seguro hacerlo""")

# ─── DENUNCIAS ────────────────────────────────────────────────────────────────
def page_denuncias():
    st.markdown("## 📋 Registro de Denuncia")
    st.caption("Registra un hecho de forma segura y confidencial. Recibirás orientación jurídica personalizada.")

    if "denuncia_enviada" not in st.session_state:
        st.session_state.denuncia_enviada = False
    if "orientacion_legal" not in st.session_state:
        st.session_state.orientacion_legal = ""

    if not st.session_state.denuncia_enviada:
        col_form, col_info = st.columns([2, 1])

        with col_form:
            anon = st.toggle("🔒 Denuncia Anónima (Recomendado)", value=True)
            st.markdown("##### 📌 Paso 1: Clasificación del hecho")
            c1, c2 = st.columns(2)
            delito = c1.selectbox("⚖️ Tipo de Delito", [""] + DELITOS)
            dep    = c2.selectbox("🗺️ Departamento", DEPARTAMENTOS)
            c3, c4 = st.columns(2)
            fecha  = c3.date_input("📅 Fecha aproximada")
            hora   = c4.time_input("🕐 Hora aproximada")
            lugar  = st.text_input("📍 Lugar del hecho", placeholder="Ej: Centro Comercial, calle, barrio...")

            st.markdown("##### 📝 Paso 2: Descripción del hecho")
            desc = st.text_area(
                "Descripción",
                placeholder="Describe lo que ocurrió con el mayor detalle posible. Todo es completamente confidencial...",
                height=140,
            )
            st.caption(f"Caracteres: {len(desc)}")

            st.markdown("##### ✅ Paso 3: Características y solicitudes")
            opciones = [
                "Violencia física","Violencia verbal","Violencia psicológica","Violencia económica",
                "Seguimiento / acoso","Violencia digital","Tengo evidencia (fotos/audio/video)",
                "Quiero acompañamiento","Necesito protección urgente","Quiero mantener anonimato total",
            ]
            opts = st.multiselect("Selecciona las que apliquen", opciones)

            st.info("📎 **Evidencia (Opcional):** Si tienes fotos, audios, videos o capturas, guárdalas en un lugar seguro. En una denuncia formal, podrás presentarlas a las autoridades.")

            enviar = st.button("📤 Registrar y Obtener Orientación Legal Gratuita", type="primary", use_container_width=True, disabled=not desc.strip())

            if enviar and desc.strip():
                with st.spinner("Preparando orientación jurídica personalizada..."):
                    system = """Eres una asistente jurídica especializada en derechos de la mujer en Colombia (Ley 1257/2008).
Das orientación clara, empática y práctica. Responde en español.
Usa EXACTAMENTE estas secciones con emojis:
⚖️ TUS DERECHOS INMEDIATOS
📋 PASOS A SEGUIR
🏢 ENTIDADES A CONTACTAR
📱 EVIDENCIA A RECOLECTAR
⏰ PLAZOS IMPORTANTES
Máximo 3 puntos por sección. Total máximo 280 palabras. Sé cálida y empática."""
                    prompt = (
                        f"Una mujer reporta en Colombia:\n"
                        f"Delito: {delito or 'No especificado'}\n"
                        f"Departamento: {dep}\n"
                        f"Lugar: {lugar or 'No especificado'}\n"
                        f"Fecha: {fecha}\nHora: {hora}\n"
                        f"Descripción: {desc}\n"
                        f"Opciones: {', '.join(opts) if opts else 'Ninguna'}\n"
                        "Proporciona orientación jurídica clara, empática y práctica."
                    )
                    try:
                        st.session_state.orientacion_legal = call_claude(system, prompt)
                    except Exception as e:
                        st.session_state.orientacion_legal = (
                            "⚠️ No se pudo generar orientación. Llama a la Línea 155 o dirígete a la Fiscalía para orientación gratuita."
                        )
                st.session_state.denuncia_enviada = True
                st.rerun()

        with col_info:
            st.markdown("""
            **🏢 Entidades Oficiales**

            - ⚖️ [Fiscalía General](https://www.fiscalia.gov.co) — Denuncias penales
            - 🏠 Comisaría de Familia — Violencia intrafamiliar
            - 👨‍👩‍👧 [ICBF](https://www.icbf.gov.co) — Protección familiar
            - 📞 **Línea 155** — Mujer 24/7 Gratis
            - 🚨 URI Fiscalía 24h — Sin cita previa
            """)
            st.warning("⚠️ Esta plataforma es un **prototipo académico**. Para denuncias con validez legal, dirígete a las entidades oficiales.")
            st.markdown("""
            **🧠 ¿Por qué es importante denunciar?**

            ✅ Protege a otras mujeres de la misma persona  
            ✅ Genera registros estadísticos oficiales  
            ✅ Activa medidas de protección inmediata  
            ✅ Accedes a apoyo psicológico gratuito  
            ✅ Rompe el ciclo de la violencia
            """)
    else:
        st.success("✅ **Reporte registrado de forma segura**\n\nTu información es completamente confidencial. Aquí tienes tu orientación jurídica personalizada.")
        st.markdown("#### ⚖️ Orientación Jurídica Personalizada")
        st.markdown("> *Generada con IA especializada en Ley 1257/2008 — Derechos de la Mujer en Colombia*")
        st.info(st.session_state.orientacion_legal)
        if st.button("← Nuevo reporte"):
            st.session_state.denuncia_enviada = False
            st.session_state.orientacion_legal = ""
            st.rerun()

# ─── IA SARA ──────────────────────────────────────────────────────────────────
def page_ia():
    # Estado del chat
    if "sara_messages" not in st.session_state:
        st.session_state.sara_messages = [
            {"role": "assistant", "content": (
                "Hola 💜 Soy SARA, tu asistente de apoyo de SafeHer.\n\n"
                "Estoy aquí para escucharte, orientarte y acompañarte — sin juzgarte, "
                "de forma completamente confidencial. Puedes contarme lo que estás viviendo, "
                "preguntar sobre tus derechos, cómo denunciar, buscar apoyo emocional, "
                "o simplemente desahogarte.\n\n"
                "Estoy aquí 24/7 para ti. ¿Cómo te puedo ayudar hoy? 🌸"
            )}
        ]

    col_left, col_chat = st.columns([1, 3])

    with col_left:
        st.markdown("""
        <div style="background:linear-gradient(160deg,#0F0A2E 0%,#4C1D95 60%,#7C3AED 100%);border-radius:22px;padding:22px;color:#fff;text-align:center;margin-bottom:14px">
          <div style="font-size:34px;margin-bottom:8px">💜</div>
          <div style="font-weight:900;font-size:20px;letter-spacing:-0.5px">SARA</div>
          <div style="font-size:11px;color:#C4B5FD;margin-bottom:12px">Asistente SafeHer · IA Empática</div>
          <div style="font-size:11px;color:#A7F3D0">🟢 En línea · Disponible 24/7</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**¿Cómo te sientes ahora?**")
        moods = ["😰 Asustada","😢 Triste","😡 Enojada","😔 Sola","🙂 Bien","🆘 Urgente"]
        for mood in moods:
            if st.button(mood, key=f"mood_{mood}", use_container_width=True):
                label = mood.split(" ", 1)[1]
                st.session_state._quick_send = f"Me siento {label.lower()}"

        st.markdown("---")
        st.markdown("""
        **💜 SARA puede ayudarte con:**

        🔒 Conversación 100% confidencial  
        ⚡ Respuesta empática inmediata  
        🧠 Ejercicios de calma y bienestar  
        ⚖️ Derechos legales y orientación  
        📍 Recursos de ayuda cercanos  
        💬 Simplemente escucharte sin juzgar  
        """)

        st.error("""🚨 **Emergencia inmediata**

**123** — Policía Nacional  
**155** — Línea Mujer (24/7 Gratis)  
**137** — Salud Mental""")

    with col_chat:
        st.markdown("#### 💜 SARA — Asistente SafeHer")
        st.caption("En línea · Siempre disponible · Completamente confidencial")

        # Mostrar mensajes
        for msg in st.session_state.sara_messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="💜"):
                    st.write(msg["content"])

        # Respuestas rápidas
        st.markdown("**Respuestas rápidas:**")
        quick_replies = [
            "Necesito ayuda urgente 🆘",
            "¿Cómo denuncio?",
            "Me siento sola y asustada",
            "¿Cuáles son mis derechos?",
            "Ejercicio para calmarme",
            "Me están amenazando",
            "Apoyo emocional",
        ]
        qc = st.columns(len(quick_replies))
        for i, qr in enumerate(quick_replies):
            if qc[i].button(qr, key=f"qr_{i}"):
                st.session_state._quick_send = qr

        # Input
        user_input = st.chat_input("Escribe tu mensaje... (Ej: Necesito ayuda, me siento sola, ¿cómo denuncio?)")

        # Procesar quick send o input normal
        to_send = None
        if hasattr(st.session_state, "_quick_send") and st.session_state._quick_send:
            to_send = st.session_state._quick_send
            del st.session_state._quick_send
        elif user_input:
            to_send = user_input

        if to_send:
            st.session_state.sara_messages.append({"role": "user", "content": to_send})
            with st.spinner("SARA está escribiendo..."):
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.sara_messages]
                try:
                    reply = call_claude(SARA_SYSTEM, "", history=history)
                except Exception:
                    reply = "Problema de conexión 💜. Si estás en peligro: **123**. Apoyo: **Línea 155** (24/7, gratuita)."
            st.session_state.sara_messages.append({"role": "assistant", "content": reply})
            st.rerun()

# ─── AYUDA CERCANA ────────────────────────────────────────────────────────────
def page_ayuda():
    st.markdown("## 🚔 Ayuda Cercana")
    st.caption("Entidades de apoyo, hospitales y refugios con información de contacto.")

    city = st.text_input("🏙️ Tu ciudad", value="Medellín")

    tipo_filtro = st.selectbox("Filtrar por tipo", ["Todos","Policía","Hospitales","Fiscalía","Refugios","Psicología"])
    tipo_map    = {"Todos":"Todos","Policía":"Policía","Hospitales":"Hospital","Fiscalía":"Fiscalía","Refugios":"Refugio","Psicología":"Psicología"}
    filtered    = ENTIDADES if tipo_filtro == "Todos" else [e for e in ENTIDADES if e["tipo"] == tipo_map[tipo_filtro]]

    for e in filtered:
        with st.expander(f"{e['icon']} **{e['nom']}** — {e['dist']}", expanded=False):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"""
                **Tipo:** {e['tipo']}  
                **Dirección:** {e['dir']}  
                **Barrio:** {e['barrio']}  
                **Horario:** {e['horario']}  
                **Contacto:** {e['phone']}
                """)
                st.caption(e['desc'])
            with c2:
                maps_url = f"https://maps.google.com/?q={e['dir'].replace(' ', '+')}"
                st.markdown(f"[🗺️ Abrir en Google Maps]({maps_url})")
                if st.button(f"🧭 ¿Cómo llegar desde {city}?", key=f"dir_{e['nom']}"):
                    with st.spinner("Calculando ruta..."):
                        system = "Eres un experto en transporte de Colombia. Da instrucciones claras para llegar a un lugar. Usa bullet points con emojis. Incluye transporte público, taxi y caminando si aplica. Máximo 100 palabras."
                        prompt = f"¿Cómo llego desde el centro de {city} a {e['nom']}, ubicada en {e['dir']}? Distancia: {e['dist']}."
                        try:
                            directions = call_claude(system, prompt)
                            st.info(directions)
                        except Exception as ex:
                            st.warning(f"⚠️ No se pudo cargar. Busca en Google Maps: {e['dir']}")

    st.markdown("---")
    st.info("""🔍 **¿Cómo encontrar más ayuda?**

📱 Google Maps: 'Comisaría de Familia + tu ciudad'  
📞 Línea 155: te orientan al refugio más cercano  
🚔 Estación de Policía más cercana: denuncia inmediata  
🏥 Cualquier hospital: urgencias para víctimas sin costo  
📋 Fiscalía URI: denuncia 24h sin cita previa  
🏠 ICBF (Línea 141): protección familiar emergencia""")

# ─── ACERCA DE ────────────────────────────────────────────────────────────────
def page_acerca():
    st.markdown("## ℹ️ Acerca de SafeHer Colombia")

    col1, col2 = st.columns([3, 2])

    with col1:
        with st.container(border=True):
            st.markdown("### 🎓 Proyecto Académico")
            st.markdown("""
Desarrollado como proyecto de **Analítica y Machine Learning**.
Modelos entrenados con datos del Sistema de Información Estadístico de la
**Policía Nacional de Colombia**. Enfocado en la protección, prevención y apoyo
integral para mujeres.

**👩‍💻 Equipo de Desarrollo:**
""")
            for n in ["Laura Sofia Beltrán","Dana Yaray Vargas","Vanessa Mora"]:
                st.markdown(f"👩‍🎓 {n}")

        with st.container(border=True):
            st.markdown("### 🤖 Modelos de Machine Learning")
            models = [
                ("📊 Nivel de Gravedad",      "XGBoost + LightGBM", "8 clases: MÍNIMO → CRÍTICO",     "#4C1D95"),
                ("🗺️ Zona de Riesgo",          "XGBoost + LightGBM", "6 clases: MUY BAJO → MUY ALTO",  "#1D4ED8"),
                ("👥 Estimación de Víctimas",  "Ensemble de modelos", "Valor numérico estimado",         "#059669"),
                ("🧠 IA de Apoyo (SARA)",      "Claude Sonnet 4",    "Apoyo psicológico y legal",        "#7C3AED"),
            ]
            for ti, al, ta, co in models:
                st.markdown(f"""
                <div style="background:#FAFAFA;border:1px solid {co}18;border-radius:14px;padding:13px 16px;margin-bottom:10px">
                  <div style="font-weight:700;color:#0F172A;font-size:13px">{ti}</div>
                  <div style="font-size:12px;color:{co};margin-top:2px">{al}</div>
                  <div style="font-size:11px;color:#64748B;margin-top:2px">Target: {ta}</div>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.warning("""⚠️ **Limitaciones Importantes**

Plataforma **académica prototipo**. Las predicciones son aproximaciones estadísticas.
Para emergencias reales llama al **123** o **Línea 155**.""")

        with st.container(border=True):
            st.markdown("### 🛠️ Stack Tecnológico")
            techs = [
                ("Streamlit + Python", 95,  "#4C1D95"),
                ("XGBoost",            92,  "#1D4ED8"),
                ("LightGBM",           90,  "#059669"),
                ("Scikit-learn",       88,  "#D97706"),
                ("Claude API (SARA)",  100, "#7C3AED"),
                ("Pandas + NumPy",     90,  "#0891B2"),
            ]
            for tech, pct, color in techs:
                st.markdown(f"**{tech}** — `{pct}%`")
                st.progress(pct / 100)

        with st.container(border=True):
            st.markdown("### 📊 Cobertura")
            coverage = [
                ("Cobertura",         "Colombia completa"),
                ("Departamentos",     "33"),
                ("Municipios",        "1.121"),
                ("Tipos de delito",   "6"),
                ("Fuente de datos",   "Policía Nacional"),
                ("Período análisis",  "2019–2027"),
            ]
            for k, v in coverage:
                st.markdown(f"**{k}:** {v}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    render_sidebar()

    page = st.session_state.get("page", "inicio")

    if page == "inicio":
        page_inicio()
    elif page == "prediccion":
        page_prediccion()
    elif page == "mapa":
        page_mapa()
    elif page == "viaje":
        page_viaje()
    elif page == "emergencias":
        page_emergencias()
    elif page == "denuncias":
        page_denuncias()
    elif page == "ia":
        page_ia()
    elif page == "ayuda":
        page_ayuda()
    elif page == "acerca":
        page_acerca()

if __name__ == "__main__":
    main()
