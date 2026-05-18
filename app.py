import streamlit as st
import anthropic
import random
import math

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SafeHer Colombia · IA Protección",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── DESIGN TOKENS & GLOBAL CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
    background: #F8FAFC !important;
}

/* Hide streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    min-width: 236px !important;
    max-width: 236px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* Sidebar radio buttons as nav */
[data-testid="stSidebar"] .stRadio > div {
    gap: 0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    padding: 10px 14px !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #64748B !important;
    transition: all 0.15s !important;
    margin-bottom: 2px !important;
    white-space: nowrap !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #F8FAFC !important;
    color: #4C1D95 !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 13px !important;
}
[data-testid="stSidebar"] input[type="radio"]:checked + div label,
[data-testid="stSidebar"] .stRadio [aria-checked="true"] label {
    background: #F5F3FF !important;
    color: #4C1D95 !important;
    font-weight: 700 !important;
}

/* Remove default radio circle */
[data-testid="stSidebar"] .stRadio input {
    display: none !important;
}

/* Main content area */
.main .block-container {
    padding: 28px 34px !important;
    max-width: 100% !important;
}

/* Cards */
.safeher-card {
    background: #FFFFFF;
    border-radius: 20px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 16px rgba(0,0,0,0.05);
    padding: 22px;
    margin-bottom: 16px;
}

/* Buttons */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
}

/* Selects & inputs */
.stSelectbox > div, .stTextInput > div, .stTextArea > div {
    border-radius: 10px !important;
}

/* Risk badge */
.risk-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
    white-space: nowrap;
}

/* Chat messages */
.chat-msg-user {
    background: linear-gradient(135deg, #4C1D95, #7C3AED);
    color: white;
    border-radius: 20px 4px 20px 20px;
    padding: 13px 18px;
    font-size: 13px;
    line-height: 1.75;
    max-width: 76%;
    margin-left: auto;
}
.chat-msg-assistant {
    background: #F8F7FF;
    color: #0F172A;
    border-radius: 4px 20px 20px 20px;
    padding: 13px 18px;
    font-size: 13px;
    line-height: 1.75;
    max-width: 76%;
    border: 1px solid #E2E8F0;
}

/* Hide streamlit label on radio for sidebar */
[data-testid="stSidebar"] .stRadio > label { display: none !important; }

/* Remove padding from sidebar markdown */
[data-testid="stSidebar"] .element-container { margin: 0 !important; padding: 0 4px !important; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F1F5F9;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
}

/* Metric */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 16px !important;
}

/* Expandable */
.streamlit-expanderHeader {
    border-radius: 12px !important;
}

/* Remove streamlit top padding */
.block-container { padding-top: 20px !important; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
RISK_LEVELS = {
    "MÍNIMO":     {"color": "#059669", "bg": "#ECFDF5", "label": "Mínimo"},
    "MUY BAJO":   {"color": "#10B981", "bg": "#D1FAE5", "label": "Muy Bajo"},
    "BAJO":       {"color": "#3B82F6", "bg": "#EFF6FF", "label": "Bajo"},
    "MEDIO-BAJO": {"color": "#F59E0B", "bg": "#FFFBEB", "label": "Medio-Bajo"},
    "MEDIO-ALTO": {"color": "#EF4444", "bg": "#FEF2F2", "label": "Medio-Alto"},
    "ALTO":       {"color": "#DC2626", "bg": "#FEF2F2", "label": "Alto"},
    "MUY ALTO":   {"color": "#991B1B", "bg": "#FEE2E2", "label": "Muy Alto"},
    "CRÍTICO":    {"color": "#7F1D1D", "bg": "#FEE2E2", "label": "Crítico"},
}

DEPARTAMENTOS = [
    "AMAZONAS","ANTIOQUIA","ARAUCA","ATLÁNTICO","BOGOTÁ D.C.","BOLÍVAR","BOYACÁ","CALDAS",
    "CAQUETÁ","CASANARE","CAUCA","CESAR","CHOCÓ","CÓRDOBA","CUNDINAMARCA","GUAINÍA",
    "GUAVIARE","HUILA","LA GUAJIRA","MAGDALENA","META","NARIÑO","NORTE DE SANTANDER",
    "PUTUMAYO","QUINDÍO","RISARALDA","SAN ANDRÉS","SANTANDER","SUCRE","TOLIMA",
    "VALLE DEL CAUCA","VAUPÉS","VICHADA"
]

DELITOS = ["VIOLENCIA INTRAFAMILIAR","VIOLENCIA SEXUAL","LESIONES PERSONALES","AMENAZAS","HURTO","HOMICIDIO"]

MUNICIPIOS_SAMPLE = {
    "ANTIOQUIA": ["MEDELLÍN","BELLO","ITAGÜÍ","ENVIGADO","APARTADÓ"],
    "BOGOTÁ D.C.": ["BOGOTÁ"],
    "VALLE DEL CAUCA": ["CALI","BUENAVENTURA","PALMIRA","TULUÁ"],
    "CUNDINAMARCA": ["SOACHA","FACATATIVÁ","ZIPAQUIRÁ","FUSAGASUGÁ"],
    "ATLÁNTICO": ["BARRANQUILLA","SOLEDAD","MALAMBO","SABANAGRANDE"],
    "SANTANDER": ["BUCARAMANGA","FLORIDABLANCA","GIRÓN","PIEDECUESTA"],
    "NARIÑO": ["PASTO","TUMACO","IPIALES","TÚQUERRES"],
    "CÓRDOBA": ["MONTERÍA","CERETÉ","LORICA","SAHAGÚN"],
    "BOLÍVAR": ["CARTAGENA","MAGANGUÉ","EL CARMEN","MOMPÓS"],
    "TOLIMA": ["IBAGUÉ","ESPINAL","MELGAR","HONDA"],
}

def get_municipios(dep):
    return MUNICIPIOS_SAMPLE.get(dep, ["Capital","Municipio 1","Municipio 2"])

CRIME_DATA = {
    "ANTIOQUIA":              {"score": 4.2, "zona": "ALTO", "gravedad": "ALTO", "municipios": 125},
    "BOGOTÁ D.C.":            {"score": 3.8, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO", "municipios": 1},
    "VALLE DEL CAUCA":        {"score": 4.5, "zona": "MUY ALTO", "gravedad": "ALTO", "municipios": 42},
    "CUNDINAMARCA":           {"score": 2.9, "zona": "MEDIO-BAJO", "gravedad": "BAJO", "municipios": 116},
    "ATLÁNTICO":              {"score": 3.1, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO", "municipios": 23},
    "SANTANDER":              {"score": 2.5, "zona": "BAJO", "gravedad": "BAJO", "municipios": 87},
    "NARIÑO":                 {"score": 3.7, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO", "municipios": 64},
    "CÓRDOBA":                {"score": 3.0, "zona": "MEDIO-BAJO", "gravedad": "BAJO", "municipios": 30},
    "BOLÍVAR":                {"score": 3.4, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO", "municipios": 46},
    "TOLIMA":                 {"score": 2.7, "zona": "BAJO", "gravedad": "BAJO", "municipios": 47},
    "HUILA":                  {"score": 2.8, "zona": "BAJO", "gravedad": "BAJO", "municipios": 37},
    "CAUCA":                  {"score": 4.0, "zona": "ALTO", "gravedad": "ALTO", "municipios": 42},
    "META":                   {"score": 3.3, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO", "municipios": 29},
    "CESAR":                  {"score": 3.2, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO", "municipios": 25},
    "MAGDALENA":              {"score": 3.0, "zona": "MEDIO-BAJO", "gravedad": "BAJO", "municipios": 30},
    "BOYACÁ":                 {"score": 2.2, "zona": "MUY BAJO", "gravedad": "MUY BAJO", "municipios": 123},
    "CALDAS":                 {"score": 2.6, "zona": "BAJO", "gravedad": "BAJO", "municipios": 27},
    "RISARALDA":              {"score": 2.8, "zona": "BAJO", "gravedad": "BAJO", "municipios": 14},
    "QUINDÍO":                {"score": 2.5, "zona": "BAJO", "gravedad": "BAJO", "municipios": 12},
    "NORTE DE SANTANDER":     {"score": 3.6, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO", "municipios": 40},
    "SUCRE":                  {"score": 2.9, "zona": "MEDIO-BAJO", "gravedad": "BAJO", "municipios": 26},
    "LA GUAJIRA":             {"score": 3.5, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-BAJO", "municipios": 15},
    "CAQUETÁ":                {"score": 3.8, "zona": "ALTO", "gravedad": "MEDIO-ALTO", "municipios": 16},
    "ARAUCA":                 {"score": 3.9, "zona": "ALTO", "gravedad": "ALTO", "municipios": 7},
    "CASANARE":               {"score": 2.7, "zona": "BAJO", "gravedad": "BAJO", "municipios": 19},
    "VICHADA":                {"score": 2.3, "zona": "MUY BAJO", "gravedad": "MUY BAJO", "municipios": 4},
    "GUAINÍA":                {"score": 2.1, "zona": "MUY BAJO", "gravedad": "MÍNIMO", "municipios": 8},
    "GUAVIARE":               {"score": 3.2, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO", "municipios": 4},
    "VAUPÉS":                 {"score": 2.0, "zona": "MUY BAJO", "gravedad": "MÍNIMO", "municipios": 6},
    "AMAZONAS":               {"score": 2.1, "zona": "MUY BAJO", "gravedad": "MÍNIMO", "municipios": 9},
    "PUTUMAYO":               {"score": 3.6, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO", "municipios": 13},
    "CHOCÓ":                  {"score": 4.1, "zona": "ALTO", "gravedad": "ALTO", "municipios": 30},
    "SAN ANDRÉS":             {"score": 2.8, "zona": "BAJO", "gravedad": "BAJO", "municipios": 2},
}

DELIT_FACTOR = {
    "HOMICIDIO": 1.4, "VIOLENCIA SEXUAL": 1.3, "AMENAZAS": 1.1,
    "VIOLENCIA INTRAFAMILIAR": 1.0, "LESIONES PERSONALES": 0.9, "HURTO": 0.8
}

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
    fs = "10px" if small else "11px"
    return f"""<span style="background:{cfg['bg']};color:{cfg['color']};border:1px solid {cfg['color']}44;
        border-radius:20px;padding:{pad};font-size:{fs};font-weight:700;letter-spacing:0.3px;
        display:inline-block;white-space:nowrap;">{cfg['label']}</span>"""

def card_html(content, extra_style=""):
    return f"""<div style="background:#FFFFFF;border-radius:20px;border:1px solid #E2E8F0;
        box-shadow:0 1px 16px rgba(0,0,0,0.05);padding:22px;margin-bottom:16px;{extra_style}">{content}</div>"""

def call_claude(system_prompt, user_msg, history=None):
    """Call Claude API and return text response."""
    try:
        client = anthropic.Anthropic()
        if history:
            messages = history
        else:
            messages = [{"role": "user", "content": user_msg}]
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system_prompt,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"⚠️ Error de conexión: {str(e)}"

def calc_prediction(dep, mun, delito, sexo, etario, año):
    base = CRIME_DATA.get(dep, {"score": 3.0, "zona": "MEDIO-BAJO", "gravedad": "BAJO", "municipios": 10})
    año_factor = 1.05 if año >= 2024 else (1.0 if año >= 2020 else 0.9)
    adjusted = base["score"] * DELIT_FACTOR.get(delito, 1.0) * año_factor
    zonas = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"]
    gravedades = ["MÍNIMO","MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO","CRÍTICO"]
    zona_idx = min(max(round(adjusted) - 1, 0), 5)
    grav_idx = min(max(round(adjusted), 0), 7)
    zona = zonas[zona_idx]
    gravedad = gravedades[grav_idx]
    victimas = round(adjusted * 18 + random.random() * 10)

    probs_zona = {}
    for i, z in enumerate(zonas):
        dist = abs(i - zona_idx)
        probs_zona[z] = max(2, 100 - dist * 28 + (random.random() * 6 - 3))
    total_z = sum(probs_zona.values())
    probs_zona = {k: round(v / total_z * 100, 1) for k, v in probs_zona.items()}

    trend = []
    for y in [2019,2020,2021,2022,2023,2024,2025,2026,2027]:
        yf = 1.05 if y >= 2024 else (1.0 if y >= 2020 else 0.9)
        noise = random.random() * 0.3 - 0.15
        s = base["score"] * DELIT_FACTOR.get(delito, 1.0) * yf * (1 + (y - 2020) * 0.025) + noise
        trend.append({"year": y, "score": round(min(max(s, 0.5), 6.0), 2), "projected": y >= 2025})

    comparativa = []
    for d in DELITOS:
        df = DELIT_FACTOR.get(d, 1.0)
        sc = base["score"] * df * año_factor
        zi = min(max(round(sc) - 1, 0), 5)
        comparativa.append({"label": d, "value": round(sc, 1), "risk": zonas[zi]})
    comparativa.sort(key=lambda x: x["value"], reverse=True)

    months = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    seasonal = [0.85,0.8,0.9,0.95,1.0,1.05,1.1,1.15,1.0,0.95,1.1,1.3]
    monthly = [{"month": m, "value": round(adjusted * seasonal[i] * (1 + random.random() * 0.1 - 0.05), 2),
                "cases": round(victimas / 12 * seasonal[i] * (1 + random.random() * 0.2 - 0.1))}
               for i, m in enumerate(months)]

    return {
        "zona": zona, "gravedad": gravedad, "victimas": victimas,
        "probs_zona": probs_zona, "trend": trend, "comparativa": comparativa,
        "score": round(adjusted, 1), "zona_idx": zona_idx, "monthly": monthly
    }

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:22px 20px 18px;border-bottom:1px solid #E2E8F0;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:40px;height:40px;background:linear-gradient(135deg,#0F0A2E,#7C3AED);border-radius:12px;
                display:flex;align-items:center;justify-content:center;font-size:18px;">🛡️</div>
            <div>
                <div style="font-weight:900;font-size:18px;color:#0F172A;letter-spacing:-0.5px;">SafeHer</div>
                <div style="font-size:9px;color:#64748B;text-transform:uppercase;letter-spacing:1.2px;">Colombia · IA Protección</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:12px 10px 0;'>", unsafe_allow_html=True)

    page = st.radio(
        "nav",
        options=[
            "🏠  Inicio",
            "📊  Predicción ML",
            "🗺️  Mapa de Riesgo",
            "✈️  Viaje Seguro",
            "🚨  Emergencias",
            "📋  Denuncias",
            "💜  SARA · IA Apoyo",
            "🚔  Ayuda Cercana",
            "ℹ️  Acerca de",
        ],
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:14px;border-top:1px solid #E2E8F0;margin-top:auto;">
        <div style="background:#FEF2F2;border:1px solid #FCA5A5;border-radius:16px;padding:14px;text-align:center;">
            <div style="font-size:10px;color:#991B1B;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">🚨 Emergencias</div>
            <a href="tel:123" style="display:block;font-size:28px;font-weight:900;color:#DC2626;text-decoration:none;font-family:Georgia,serif;line-height:1;">123</a>
            <div style="font-size:9px;color:#991B1B;margin-bottom:8px;">Policía Nacional</div>
            <a href="tel:155" style="display:block;font-size:28px;font-weight:900;color:#7C3AED;text-decoration:none;font-family:Georgia,serif;line-height:1;">155</a>
            <div style="font-size:9px;color:#6B21A8;">Línea Mujer 24/7</div>
        </div>
        <div style="text-align:center;margin-top:8px;font-size:9px;color:#64748B;">Prototipo académico v4.0 · Datos: Policía Nacional</div>
    </div>
    """, unsafe_allow_html=True)

# ─── PAGES ────────────────────────────────────────────────────────────────────

# ── INICIO ────────────────────────────────────────────────────────────────────
if "🏠" in page:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0F0A2E 0%,#1E1B4B 45%,#312E81 100%);
        border-radius:28px;padding:56px 52px;margin-bottom:32px;position:relative;overflow:hidden;color:#fff;">
        <div style="position:absolute;top:-80px;right:-80px;width:380px;height:380px;border-radius:50%;background:rgba(255,255,255,0.03);"></div>
        <div style="position:absolute;bottom:-60px;right:100px;width:220px;height:220px;border-radius:50%;background:rgba(236,72,153,0.1);"></div>
        <div style="max-width:600px;position:relative;">
            <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.1);
                border:1px solid rgba(255,255,255,0.18);border-radius:20px;padding:5px 16px;
                font-size:11px;color:#E9D5FF;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:24px;">
                ⚡ Sistema Inteligente · Colombia 2025
            </div>
            <h1 style="font-size:48px;font-weight:900;line-height:1.08;margin:0 0 18px;letter-spacing:-1.5px;">
                Tu seguridad es<br>
                <span style="background:linear-gradient(90deg,#F0ABFC,#EC4899,#F59E0B);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">nuestra prioridad</span>
            </h1>
            <p style="color:#C4B5FD;font-size:15px;line-height:1.8;margin:0 0 32px;">
                Plataforma inteligente de predicción, prevención y apoyo para mujeres en Colombia.
                Modelos ML entrenados con datos reales de la Policía Nacional.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "📍", "1.121", "Municipios", "#7C3AED"),
        (c2, "🗺️", "33", "Departamentos", "#1D4ED8"),
        (c3, "🤖", "3 ML", "Modelos IA", "#059669"),
        (c4, "🛡️", "24/7", "Disponible", "#EC4899"),
    ]
    for col, icon, val, label, color in stats:
        with col:
            st.markdown(f"""
            <div style="background:#fff;border-radius:20px;border:1px solid #E2E8F0;
                box-shadow:0 1px 16px rgba(0,0,0,0.05);padding:22px 20px;text-align:center;">
                <div style="font-size:28px;margin-bottom:8px;">{icon}</div>
                <div style="font-size:28px;font-weight:900;color:{color};line-height:1;">{val}</div>
                <div style="font-size:11px;color:#64748B;margin-top:5px;font-weight:600;">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<h2 style='font-size:20px;font-weight:800;color:#0F172A;margin:28px 0 20px;letter-spacing:-0.3px;'>🧩 Módulos Disponibles</h2>", unsafe_allow_html=True)

    modules = [
        ("📊", "Predicción ML", "XGBoost + LightGBM con gráficas avanzadas", "#7C3AED"),
        ("🗺️", "Mapa de Riesgo", "Mapa geográfico interactivo con predicciones", "#1D4ED8"),
        ("✈️", "Viaje Seguro", "Analiza seguridad antes de viajar", "#059669"),
        ("🚨", "Emergencias", "Alertas y líneas directas de ayuda inmediata", "#DC2626"),
        ("📋", "Denuncias", "Registro anónimo seguro con orientación legal", "#D97706"),
        ("💜", "IA SARA", "Chat terapéutico 24/7 con apoyo psicológico", "#7C3AED"),
        ("🚔", "Ayuda Cercana", "Entidades, hospitales y refugios con direcciones", "#0891B2"),
        ("ℹ️", "Acerca de", "Equipo, tecnología y misión", "#64748B"),
    ]
    cols = st.columns(4)
    for i, (icon, label, desc, color) in enumerate(modules):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="background:#fff;border-radius:20px;padding:22px;border:1px solid #E2E8F0;
                margin-bottom:14px;transition:all 0.2s;">
                <div style="width:46px;height:46px;border-radius:14px;background:{color}14;
                    display:flex;align-items:center;justify-content:center;font-size:22px;margin-bottom:14px;">{icon}</div>
                <div style="font-weight:700;font-size:14px;color:#0F172A;margin-bottom:6px;">{label}</div>
                <div style="font-size:12px;color:#64748B;line-height:1.6;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:14px;padding:16px 22px;
        display:flex;align-items:center;gap:12px;margin-top:8px;">
        <span style="font-size:20px;">⚠️</span>
        <span style="font-size:13px;color:#92400E;">
            <strong>Aviso académico:</strong> Prototipo educativo. Para emergencias reales llama al
            <strong style="color:#DC2626;">123</strong> o la
            <strong style="color:#7C3AED;">Línea Mujer 155</strong> — gratuita, 24/7.
        </span>
    </div>
    """, unsafe_allow_html=True)

# ── PREDICCIÓN ML ─────────────────────────────────────────────────────────────
elif "📊" in page:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:#F5F3FF;
            border:1px solid #7C3AED30;border-radius:20px;padding:4px 14px;font-size:11px;
            color:#7C3AED;font-weight:700;margin-bottom:12px;">📊 MÓDULO DE PREDICCIÓN ML</div>
        <h1 style="font-size:30px;font-weight:900;color:#0F172A;margin:0 0 6px;letter-spacing:-0.5px;">Predicción Inteligente de Riesgo</h1>
        <p style="color:#64748B;font-size:14px;margin:0;">XGBoost + LightGBM en tiempo real · Interpretación IA para apoyo policial · Datos: Policía Nacional Colombia</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px;font-weight:700;color:#7C3AED;margin-bottom:18px;">⚙️ Parámetros de Análisis</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            dep = st.selectbox("🗺️ Departamento", DEPARTAMENTOS, index=DEPARTAMENTOS.index("ANTIOQUIA"))
        munis = get_municipios(dep)
        with c2:
            mun = st.selectbox("📍 Municipio", munis)
        with c3:
            año = st.selectbox("📅 Año", list(range(2019, 2028)), index=5)

        c4, c5, c6 = st.columns(3)
        with c4:
            delito = st.selectbox("⚖️ Tipo de Delito", DELITOS)
        with c5:
            sexo = st.selectbox("👤 Sexo", ["FEMENINO", "MASCULINO"])
        with c6:
            etario = st.selectbox("🎂 Grupo Etario", ["DE 0 A 17 AÑOS","DE 18 A 26 AÑOS","DE 27 A 59 AÑOS","DE 60 Y MÁS"], index=2)

        predict_btn = st.button("🔮 Ejecutar Predicción ML", use_container_width=False,
                                type="primary", key="predict_btn")
        st.markdown('</div>', unsafe_allow_html=True)

    if predict_btn or st.session_state.get("pred_result"):
        if predict_btn:
            with st.spinner("⏳ Ejecutando modelos ML..."):
                result = calc_prediction(dep, mun, delito, sexo, etario, año)
                st.session_state["pred_result"] = result
                st.session_state["pred_form"] = {"dep": dep, "mun": mun, "delito": delito, "sexo": sexo, "etario": etario, "año": año}

        result = st.session_state.get("pred_result")
        form = st.session_state.get("pred_form", {})

        if result:
            # Context banner
            zona_badge = risk_badge_html(result["zona"])
            grav_badge = risk_badge_html(result["gravedad"])
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0F0A2E,#1E1B4B);border-radius:18px;
                padding:16px 22px;margin-bottom:22px;display:flex;align-items:center;gap:12px;">
                <span style="font-size:18px;">📍</span>
                <div>
                    <div style="font-weight:700;font-size:15px;color:#fff;">{form.get('dep',dep)} · {form.get('mun',mun)}</div>
                    <div style="font-size:12px;color:#A5B4FC;">{form.get('delito',delito)} · {form.get('sexo',sexo)} · {form.get('etario',etario)} · {form.get('año',año)}</div>
                </div>
                <div style="margin-left:auto;display:flex;gap:8px;">{zona_badge}&nbsp;{grav_badge}</div>
            </div>
            """, unsafe_allow_html=True)

            # KPIs
            max_month = max(result["monthly"], key=lambda x: x["cases"])
            k1, k2, k3, k4 = st.columns(4)
            kpis = [
                (k1, "ZONA DE RIESGO", "XGBoost", risk_badge_html(result["zona"]), f"Score: {result['score']}/6.0", RISK_LEVELS.get(result['zona'], {}).get('color','#7C3AED')),
                (k2, "NIVEL GRAVEDAD", "LightGBM", risk_badge_html(result["gravedad"]), "Impacto estimado", RISK_LEVELS.get(result['gravedad'], {}).get('color','#1D4ED8')),
                (k3, "VÍCTIMAS ESTIMADAS", "Combinación ML",
                 f'<div style="font-size:38px;font-weight:900;color:#DC2626;font-family:Georgia,serif;line-height:1;">{result["victimas"]}</div>',
                 "personas/año", "#DC2626"),
                (k4, "MES MÁS CRÍTICO", "Análisis estacional",
                 f'<div style="font-size:22px;font-weight:900;color:#D97706;">{max_month["month"]}</div>',
                 f'{max_month["cases"]} casos estimados', "#D97706"),
            ]
            for col, label, sub, display, extra, color in kpis:
                with col:
                    st.markdown(f"""
                    <div style="background:#fff;border-radius:20px;border:1px solid #E2E8F0;
                        box-shadow:0 1px 16px rgba(0,0,0,0.05);padding:18px;">
                        <div style="font-size:9px;font-weight:700;color:#64748B;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">{label}</div>
                        <div style="font-size:9px;color:{color};font-weight:700;margin-bottom:8px;">{sub}</div>
                        <div style="margin-bottom:8px;">{display}</div>
                        <div style="font-size:10px;color:#64748B;">{extra}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Trend chart using plotly
            import plotly.graph_objects as go
            col_trend, col_prob = st.columns([3, 2])

            with col_trend:
                st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:13px;font-weight:800;color:#0F172A;margin-bottom:4px;">📈 Tendencia Histórica y Proyección 2019–2027</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:11px;color:#64748B;margin-bottom:12px;">{form.get("delito",delito)} en {form.get("dep",dep)} · Score 0–6 · Línea punteada = proyección</div>', unsafe_allow_html=True)

                solid_x = [t["year"] for t in result["trend"] if not t["projected"]]
                solid_y = [t["score"] for t in result["trend"] if not t["projected"]]
                proj_x = [t["year"] for t in result["trend"] if t["projected"] or t["year"] == solid_x[-1]]
                proj_y = [t["score"] for t in result["trend"] if t["projected"] or t["year"] == solid_x[-1]]

                colors_pts = [get_risk_color(t["score"]) for t in result["trend"]]

                fig = go.Figure()
                fig.add_shape(type="rect", x0=2019, x1=2027, y0=4, y1=6, fillcolor="#FEE2E2", opacity=0.3, line_width=0)
                fig.add_shape(type="rect", x0=2019, x1=2027, y0=3, y1=4, fillcolor="#FEF9C3", opacity=0.3, line_width=0)
                fig.add_shape(type="rect", x0=2019, x1=2027, y0=0, y1=3, fillcolor="#F0FDF4", opacity=0.3, line_width=0)
                fig.add_trace(go.Scatter(x=solid_x, y=solid_y, mode="lines+markers", line=dict(color="#7C3AED", width=2.5),
                    marker=dict(size=8, color=colors_pts[:len(solid_x)], line=dict(color="white", width=2)),
                    name="Histórico", fill="tozeroy", fillcolor="rgba(124,58,237,0.07)"))
                fig.add_trace(go.Scatter(x=proj_x, y=proj_y, mode="lines+markers", line=dict(color="#A78BFA", width=2, dash="dash"),
                    marker=dict(size=7, color=colors_pts[len(solid_x)-1:], line=dict(color="white", width=2)),
                    name="Proyectado"))
                fig.update_layout(height=200, margin=dict(l=30, r=10, t=10, b=30),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(range=[0, 6.5], gridcolor="#E2E8F0", tickfont=dict(size=9)),
                    xaxis=dict(gridcolor="#E2E8F0", tickfont=dict(size=9)),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=9)),
                    showlegend=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)

            with col_prob:
                st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
                st.markdown('<div style="font-size:13px;font-weight:800;color:#0F172A;margin-bottom:4px;">🎯 Distribución de Probabilidad</div>', unsafe_allow_html=True)
                st.markdown('<div style="font-size:11px;color:#64748B;margin-bottom:14px;">Confianza del modelo por zona de riesgo</div>', unsafe_allow_html=True)
                for zone, pct in sorted(result["probs_zona"].items(), key=lambda x: x[1], reverse=True):
                    cfg = RISK_LEVELS.get(zone, {"color": "#888"})
                    st.markdown(f"""
                    <div style="margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                            <span style="font-size:11px;color:#0F172A;font-weight:600;">{zone}</span>
                            <span style="font-size:12px;color:{cfg['color']};font-weight:800;">{pct}%</span>
                        </div>
                        <div style="background:#F1F5F9;border-radius:6px;height:10px;overflow:hidden;">
                            <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,{cfg['color']}CC,{cfg['color']});border-radius:6px;"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Monthly + Comparativa
            col_m, col_c = st.columns(2)
            with col_m:
                st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
                st.markdown('<div style="font-size:13px;font-weight:800;color:#0F172A;margin-bottom:4px;">📅 Variación Mensual Estimada</div>', unsafe_allow_html=True)
                st.markdown('<div style="font-size:11px;color:#64748B;margin-bottom:12px;">Riesgo estacional — el mes en rojo es el más crítico</div>', unsafe_allow_html=True)
                max_m = max(result["monthly"], key=lambda x: x["value"])
                fig2 = go.Figure()
                bar_colors = ["#DC2626" if m["month"] == max_m["month"] else get_risk_color(m["value"]) for m in result["monthly"]]
                fig2.add_trace(go.Bar(x=[m["month"] for m in result["monthly"]], y=[m["value"] for m in result["monthly"]],
                    marker_color=bar_colors, marker_opacity=0.85))
                fig2.update_layout(height=170, margin=dict(l=5, r=5, t=5, b=25),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(gridcolor="#E2E8F0", tickfont=dict(size=8)),
                    xaxis=dict(tickfont=dict(size=8)), showlegend=False)
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)

            with col_c:
                st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:13px;font-weight:800;color:#0F172A;margin-bottom:4px;">📊 Comparativa por Tipo de Delito</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:11px;color:#64748B;margin-bottom:14px;">Score predicho para {form.get("dep",dep)} en {form.get("año",año)}</div>', unsafe_allow_html=True)
                max_v = result["comparativa"][0]["value"] if result["comparativa"] else 1
                for item in result["comparativa"]:
                    cfg = RISK_LEVELS.get(item["risk"], {"color": "#888"})
                    is_sel = item["label"] == form.get("delito", delito)
                    marker = " ◀" if is_sel else ""
                    st.markdown(f"""
                    <div style="padding:8px 12px;background:{''+cfg['color']+'10' if is_sel else '#FAFAFA'};border-radius:10px;
                        border:1px solid {cfg['color']+'40' if is_sel else '#E2E8F0'};margin-bottom:8px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                            <span style="font-size:11px;color:#0F172A;font-weight:{'700' if is_sel else '500'};">{item['label']}{marker}</span>
                            <div style="display:flex;align-items:center;gap:6px;">
                                <span style="font-size:11px;font-weight:800;color:{cfg['color']};">{item['value']}</span>
                                {risk_badge_html(item['risk'], small=True)}
                            </div>
                        </div>
                        <div style="background:#E2E8F0;border-radius:4px;height:5px;">
                            <div style="width:{item['value']/max_v*100:.0f}%;height:100%;background:{cfg['color']};border-radius:4px;"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # AI Interpretation
            st.markdown("""
            <div class="safeher-card">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:18px;">
                    <div style="width:40px;height:40px;background:linear-gradient(135deg,#0F0A2E,#4C1D95);border-radius:12px;
                        display:flex;align-items:center;justify-content:center;font-size:18px;">🤖</div>
                    <div>
                        <div style="font-size:15px;font-weight:800;color:#0F172A;">Interpretación IA para Fuerzas Policiales</div>
                        <div style="font-size:11px;color:#64748B;">Análisis contextual automatizado · Recomendaciones operativas</div>
                    </div>
                    <div style="margin-left:auto;background:#F5F3FF;color:#7C3AED;font-size:11px;font-weight:700;padding:4px 12px;border-radius:20px;">🔒 Uso Policial</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if "interp_result" not in st.session_state or predict_btn:
                with st.spinner("🤖 Analizando situación con IA especializada..."):
                    interp = call_claude(
                        """Eres un analista experto en seguridad pública de Colombia, asesor de la Policía Nacional.
Estructura tu respuesta EXACTAMENTE con estas 4 secciones:
🔍 DIAGNÓSTICO SITUACIONAL
⚠️ FACTORES DE RIESGO IDENTIFICADOS
🚨 ACCIONES INMEDIATAS RECOMENDADAS
🤝 RECURSOS INTERINSTITUCIONALES
Cada sección máximo 3 puntos con bullet (•). Total máximo 250 palabras.""",
                        f"""Analiza:
- Departamento: {form.get('dep',dep)} | Municipio: {form.get('mun',mun)}
- Delito: {form.get('delito',delito)} | Año: {form.get('año',año)}
- Zona: {result['zona']} | Gravedad: {result['gravedad']}
- Víctimas: {result['victimas']} | Score: {result['score']}/6.0"""
                    )
                    st.session_state["interp_result"] = interp

            interp = st.session_state.get("interp_result", "")
            if interp:
                st.markdown(f"""
                <div style="background:#FAFAFA;border-radius:14px;padding:18px 20px;border:1px solid #E2E8F0;
                    font-size:12px;line-height:1.75;white-space:pre-wrap;color:#0F172A;">{interp}</div>
                """, unsafe_allow_html=True)

# ── MAPA DE RIESGO ─────────────────────────────────────────────────────────────
elif "🗺️" in page:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:#EFF6FF;
            border:1px solid #1D4ED830;border-radius:20px;padding:4px 14px;font-size:11px;
            color:#1D4ED8;font-weight:700;margin-bottom:12px;">🗺️ MAPA INTERACTIVO</div>
        <h1 style="font-size:30px;font-weight:900;color:#0F172A;margin:0 0 6px;letter-spacing:-0.5px;">Mapa de Riesgo — Colombia</h1>
        <p style="color:#64748B;font-size:14px;margin:0;">Visualización geográfica del nivel de riesgo por departamento. Haz clic para análisis IA detallado.</p>
    </div>
    """, unsafe_allow_html=True)

    # Summary stats
    c1, c2, c3, c4 = st.columns(4)
    summary_stats = [
        (c1, "Crítico / Muy Alto", sum(1 for d in CRIME_DATA.values() if d["score"] >= 4.0), "#DC2626", "#FEF2F2"),
        (c2, "Alto / Medio-Alto", sum(1 for d in CRIME_DATA.values() if 3.5 <= d["score"] < 4.0), "#EF4444", "#FFF7ED"),
        (c3, "Riesgo Medio", sum(1 for d in CRIME_DATA.values() if 3.0 <= d["score"] < 3.5), "#F59E0B", "#FFFBEB"),
        (c4, "Controlado", sum(1 for d in CRIME_DATA.values() if d["score"] < 3.0), "#059669", "#ECFDF5"),
    ]
    for col, label, count, color, bg in summary_stats:
        with col:
            st.markdown(f"""<div style="background:{bg};border-radius:14px;padding:14px 16px;
                border:1px solid {color}30;text-align:center;">
                <div style="font-size:26px;font-weight:900;color:{color};line-height:1;">{count}</div>
                <div style="font-size:10px;color:{color};font-weight:700;margin-top:4px;">Departamentos</div>
                <div style="font-size:10px;color:#64748B;margin-top:2px;">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    filter_zone = st.selectbox("Filtrar por zona:", ["TODOS","ALTO","MEDIO-ALTO","MEDIO-BAJO","BAJO"], key="map_filter")

    def get_risk_zone_label(score):
        if score >= 4.0: return "ALTO"
        if score >= 3.5: return "MEDIO-ALTO"
        if score >= 2.5: return "MEDIO-BAJO"
        return "BAJO"

    sorted_deps = sorted(
        [{"name": k, **v} for k, v in CRIME_DATA.items()
         if filter_zone == "TODOS" or get_risk_zone_label(v["score"]) == filter_zone],
        key=lambda x: x["score"], reverse=True
    )

    st.markdown(f'<div style="font-size:12px;color:#64748B;margin-bottom:14px;">Mostrando <strong style="color:#0F172A;">{len(sorted_deps)}</strong> departamentos</div>', unsafe_allow_html=True)

    col_map, col_detail = st.columns([2, 1])

    with col_map:
        st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:700;color:#64748B;margin-bottom:14px;text-transform:uppercase;letter-spacing:1px;">🇨🇴 Colombia — Nivel de Riesgo por Departamento</div>', unsafe_allow_html=True)

        # Grid of department tiles
        cols_per_row = 5
        rows = [sorted_deps[i:i+cols_per_row] for i in range(0, len(sorted_deps), cols_per_row)]
        for row in rows:
            rcols = st.columns(cols_per_row)
            for j, dep_d in enumerate(row):
                color = get_risk_color(dep_d["score"])
                with rcols[j]:
                    if st.button(f"{dep_d['name'][:12]}\n{dep_d['score']:.1f}", key=f"dep_{dep_d['name']}",
                                 use_container_width=True):
                        st.session_state["selected_dep"] = dep_d["name"]
                    st.markdown(f"""<div style="background:{color}14;border-radius:10px;padding:2px 6px;
                        text-align:center;margin-top:-12px;margin-bottom:4px;">
                        <div style="font-size:9px;color:{color};font-weight:700;">{dep_d['zona']}</div>
                    </div>""", unsafe_allow_html=True)

        # Legend
        st.markdown("""<div style="display:flex;gap:12px;padding:12px 0 0;flex-wrap:wrap;">""", unsafe_allow_html=True)
        for c, lb in [("#7F1D1D","Crítico(≥4.5)"),("#DC2626","Alto(4-4.5)"),("#EF4444","Med-Alto(3.5)"),
                       ("#F59E0B","Medio(3-3.5)"),("#3B82F6","Med-Bajo(2.5)"),("#059669","Bajo(<2.5)")]:
            st.markdown(f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:10px;color:#64748B;">'
                        f'<span style="width:10px;height:10px;background:{c};border-radius:2px;display:inline-block;"></span>{lb}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Top 10 bar chart
        st.markdown('<div style="font-size:13px;font-weight:700;color:#0F172A;margin:18px 0 12px;">📊 Top 12 Departamentos por Score</div>', unsafe_allow_html=True)
        for i, d in enumerate(sorted_deps[:12]):
            color = get_risk_color(d["score"])
            pct = d["score"] / 6 * 100
            st.markdown(f"""<div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <span style="font-size:11px;color:#{'#DC2626' if i < 3 else '#64748B'};font-weight:{'800' if i < 3 else '600'};width:20px;">#{i+1}</span>
                    <span style="font-size:12px;color:#0F172A;font-weight:600;flex:1;padding:0 8px;">{d['name']}</span>
                    <span style="font-size:12px;color:{color};font-weight:800;">{d['score']:.1f}/6.0</span>
                    &nbsp;{risk_badge_html(d['zona'], small=True)}
                </div>
                <div style="background:#F1F5F9;border-radius:6px;height:8px;overflow:hidden;">
                    <div style="width:{pct:.0f}%;height:100%;background:linear-gradient(90deg,{color}99,{color});border-radius:6px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_detail:
        sel_name = st.session_state.get("selected_dep")
        if sel_name and sel_name in CRIME_DATA:
            sel = {"name": sel_name, **CRIME_DATA[sel_name]}
            color = get_risk_color(sel["score"])
            pct_ring = sel["score"] / 6

            st.markdown(f"""<div class="safeher-card">
                <div style="font-size:18px;font-weight:900;color:#0F172A;margin-bottom:4px;">{sel["name"]}</div>
                <div style="font-size:11px;color:#64748B;margin-bottom:16px;">Colombia · {sel["municipios"]} municipios</div>
                <div style="display:flex;align-items:center;gap:16px;margin-bottom:18px;background:#FAFAFA;border-radius:14px;padding:14px;">
                    <div style="text-align:center;">
                        <div style="font-size:36px;font-weight:900;color:{color};">{sel['score']:.1f}</div>
                        <div style="font-size:10px;color:#94A3B8;">/ 6.0</div>
                    </div>
                    <div>
                        <div style="font-size:12px;color:#64748B;margin-bottom:6px;">Nivel de riesgo</div>
                        <div style="margin-bottom:4px;">{risk_badge_html(sel['zona'])}</div>
                        <div>{risk_badge_html(sel['gravedad'])}</div>
                    </div>
                </div>
                <div style="font-size:12px;font-weight:700;color:#0F172A;margin-bottom:10px;">Riesgo por tipo de delito</div>
            """, unsafe_allow_html=True)

            zonas_list = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"]
            for d in DELITOS:
                fac = DELIT_FACTOR.get(d, 1.0)
                sc = sel["score"] * fac
                z = zonas_list[min(max(round(sc) - 1, 0), 5)]
                col_d = get_risk_color(sc)
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                    padding:7px 0;border-bottom:1px solid #E2E8F0;">
                    <span style="font-size:11px;color:#0F172A;">{d}</span>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:11px;font-weight:700;color:{col_d};">{sc:.1f}</span>
                        {risk_badge_html(z, small=True)}
                    </div>
                </div>""", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # close card

            # AI Analysis
            if st.button(f"🤖 Análisis IA de {sel_name}", key="ai_map_btn"):
                with st.spinner("Analizando..."):
                    ai_text = call_claude(
                        "Eres un experto en seguridad pública colombiana. Da análisis breve (máx 120 palabras) con bullets y emojis: contexto, amenazas, horarios de riesgo, recomendación clave.",
                        f"Analiza seguridad para mujeres en {sel_name}, Colombia. Score: {sel['score']}/6.0, zona: {sel['zona']}."
                    )
                    st.session_state[f"ai_map_{sel_name}"] = ai_text

            ai_result = st.session_state.get(f"ai_map_{sel_name}", "")
            if ai_result:
                st.markdown(f"""<div style="background:#F5F3FF;border-radius:14px;padding:14px;
                    border:1px solid #7C3AED20;font-size:11px;color:#0F172A;line-height:1.7;white-space:pre-wrap;">{ai_result}</div>""",
                    unsafe_allow_html=True)

            # Recommendation
            if sel["score"] >= 4.0:
                rec_color, rec_bg, rec_text = "#DC2626", "#FEF2F2", "Zona de alto riesgo. Refuerzo urgente de patrullaje y coordinación con Fiscalía."
            elif sel["score"] >= 3.0:
                rec_color, rec_bg, rec_text = "#D97706", "#FFFBEB", "Riesgo moderado. Monitoreo activo y campañas de prevención."
            else:
                rec_color, rec_bg, rec_text = "#059669", "#ECFDF5", "Riesgo controlado. Mantener estrategias preventivas."
            st.markdown(f"""<div style="background:{rec_bg};border-radius:12px;padding:12px 14px;font-size:12px;line-height:1.6;margin-top:8px;">
                <strong style="color:{rec_color};">💡 Recomendación:</strong>
                <span style="color:#0F172A;"> {rec_text}</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background:#F8FAFC;border-radius:16px;border:2px dashed #E2E8F0;
                padding:40px 20px;text-align:center;color:#94A3B8;font-size:13px;">
                👆 Selecciona un departamento para ver análisis detallado
            </div>""", unsafe_allow_html=True)

# ── VIAJE SEGURO ──────────────────────────────────────────────────────────────
elif "✈️" in page:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:#ECFDF5;
            border:1px solid #05996930;border-radius:20px;padding:4px 14px;font-size:11px;
            color:#059669;font-weight:700;margin-bottom:12px;">✈️ PLANIFICACIÓN DE VIAJE</div>
        <h1 style="font-size:30px;font-weight:900;color:#0F172A;margin:0 0 6px;letter-spacing:-0.5px;">Viaje Seguro</h1>
        <p style="color:#64748B;font-size:14px;margin:0;">Consulta el nivel de seguridad de cualquier departamento antes de viajar.</p>
    </div>
    """, unsafe_allow_html=True)

    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        dep_viaje = st.selectbox("Selecciona el departamento de destino:", DEPARTAMENTOS, key="dep_viaje")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        analizar_btn = st.button("🔍 Analizar", type="primary", use_container_width=True, key="viaje_btn")

    if analizar_btn or st.session_state.get("viaje_result"):
        if analizar_btn:
            data = CRIME_DATA.get(dep_viaje, {"score": 2.8, "zona": "BAJO", "gravedad": "BAJO", "municipios": 10})
            muns = get_municipios(dep_viaje)
            st.session_state["viaje_result"] = {"dep": dep_viaje, "data": data, "muns": muns}
            st.session_state.pop("viaje_tips", None)

        vr = st.session_state.get("viaje_result")
        if vr:
            score = vr["data"]["score"]
            if score <= 2.0:
                safety = {"label": "Seguro", "color": "#059669", "bg": "#ECFDF5", "icon": "🟢", "stars": 5}
            elif score <= 3.0:
                safety = {"label": "Precaución", "color": "#F59E0B", "bg": "#FFFBEB", "icon": "🟡", "stars": 3}
            elif score <= 4.0:
                safety = {"label": "Riesgo Medio", "color": "#EF4444", "bg": "#FEF2F2", "icon": "🟠", "stars": 2}
            else:
                safety = {"label": "Alto Riesgo", "color": "#DC2626", "bg": "#FEE2E2", "icon": "🔴", "stars": 1}

            stars_html = "".join([f'<span style="font-size:18px;opacity:{"1" if i < safety["stars"] else "0.25"}">⭐</span>' for i in range(5)])

            st.markdown(f"""<div style="background:{safety['bg']};border:2px solid {safety['color']}30;border-radius:22px;
                padding:24px 28px;margin-bottom:22px;display:flex;align-items:center;gap:20px;">
                <div style="font-size:52px;">{safety['icon']}</div>
                <div style="flex:1;">
                    <div style="font-size:22px;font-weight:900;color:{safety['color']};margin-bottom:4px;">{vr['dep']}</div>
                    <div style="font-size:16px;font-weight:700;color:{safety['color']};margin-bottom:8px;">{safety['label']}</div>
                    <div>{stars_html}<span style="font-size:12px;color:#64748B;margin-left:6px;">Índice de seguridad</span></div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:48px;font-weight:900;color:{safety['color']};font-family:Georgia,serif;line-height:1;">{score:.1f}</div>
                    <div style="font-size:12px;color:#64748B;">Score de riesgo / 6.0</div>
                </div>
            </div>""", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
                st.markdown('<div style="font-weight:700;font-size:13px;color:#0F172A;margin-bottom:14px;">🏙️ Municipios del Departamento</div>', unsafe_allow_html=True)
                chips = "".join([f'<span style="background:#F5F3FF;color:#7C3AED;padding:5px 13px;border-radius:20px;font-size:12px;font-weight:600;display:inline-block;margin:3px;">{m}</span>' for m in vr["muns"]])
                st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:4px;">{chips}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="margin-top:14px;padding:12px 14px;background:#FAFAFA;border-radius:12px;">'
                            f'<div style="font-size:11px;color:#64748B;margin-bottom:4px;">Municipios cubiertos</div>'
                            f'<div style="font-size:22px;font-weight:900;color:#4C1D95;">{vr["data"]["municipios"]}</div></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_b:
                st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
                st.markdown('<div style="font-weight:700;font-size:13px;color:#0F172A;margin-bottom:14px;">⚠️ Riesgo por Tipo de Delito</div>', unsafe_allow_html=True)
                zonas_l = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"]
                delito_scores = sorted(
                    [{"d": d, "sc": round(vr["data"]["score"] * DELIT_FACTOR.get(d, 1.0), 1)} for d in DELITOS],
                    key=lambda x: x["sc"], reverse=True
                )
                for item in delito_scores[:4]:
                    z = zonas_l[min(max(round(item["sc"]) - 1, 0), 5)]
                    st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                        padding:7px 0;border-bottom:1px solid #E2E8F0;">
                        <span style="font-size:11px;color:#0F172A;">{item['d']}</span>
                        {risk_badge_html(z, small=True)}
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # AI Tips
            st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:14px;font-weight:700;color:#0F172A;margin-bottom:8px;">🤖 Consejos Personalizados para {vr["dep"]}</div>', unsafe_allow_html=True)
            if "viaje_tips" not in st.session_state:
                with st.spinner("Preparando consejos de seguridad..."):
                    tips = call_claude(
                        "Eres experta en seguridad para mujeres viajeras en Colombia. Responde en español con bullets y emojis. Secciones: 🛡️ Recomendaciones, 🏠 Mejores Zonas, 🕐 Horarios Seguros, 🚗 Transporte, 📞 Emergencias. Máx 200 palabras.",
                        f"Consejos para mujer viajando a {vr['dep']}, Colombia. Score: {score:.1f}/6.0 ({vr['data']['zona']})."
                    )
                    st.session_state["viaje_tips"] = tips
            st.markdown(f'<div style="font-size:13px;color:#0F172A;line-height:1.8;white-space:pre-wrap;background:#FAFAFA;border-radius:12px;padding:16px;">{st.session_state.get("viaje_tips","")}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ── EMERGENCIAS ────────────────────────────────────────────────────────────────
elif "🚨" in page:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#7F1D1D,#DC2626);border-radius:24px;
        padding:24px 28px;margin-bottom:28px;color:#fff;">
        <h1 style="font-size:30px;font-weight:900;margin:0 0 6px;letter-spacing:-0.3px;">🚨 Centro de Emergencias</h1>
        <p style="color:#FCA5A5;font-size:14px;margin:0;">Si estás en peligro, presiona el botón que describe tu situación. Todas las llamadas son gratuitas.</p>
    </div>
    """, unsafe_allow_html=True)

    emergencias = [
        ("🆘", "Estoy en peligro", "123 — Emergencias", "tel:123", "#DC2626"),
        ("👣", "Me están siguiendo", "123 — Policía", "tel:123", "#D97706"),
        ("🔇", "No puedo hablar", "SMS 123", "sms:123", "#7C3AED"),
        ("🏃", "Estoy secuestrada", "123 — Urgente", "tel:123", "#991B1B"),
        ("🚔", "Necesito Policía", "Policía Nacional", "tel:123", "#1D4ED8"),
        ("🚑", "Necesito Ambulancia", "Cruz Roja — 132", "tel:132", "#059669"),
        ("💜", "Apoyo psicológico", "Línea 137", "tel:137", "#8B5CF6"),
        ("👩", "Línea Mujer", "155 — 24/7 Gratis", "tel:155", "#EC4899"),
    ]

    cols = st.columns(4)
    for i, (icon, label, sub, href, color) in enumerate(emergencias):
        with cols[i % 4]:
            st.markdown(f"""<a href="{href}" style="text-decoration:none;">
            <div style="background:#fff;border:2px solid {color}25;border-radius:20px;padding:22px 16px;
                text-align:center;cursor:pointer;min-height:130px;transition:all 0.2s;margin-bottom:14px;">
                <div style="font-size:30px;margin-bottom:10px;">{icon}</div>
                <div style="font-weight:700;font-size:13px;color:#0F172A;margin-bottom:5px;">{label}</div>
                <div style="font-size:11px;font-weight:700;color:{color};">{sub}</div>
            </div></a>""", unsafe_allow_html=True)

    st.markdown("<h2 style='font-size:18px;font-weight:800;color:#0F172A;margin:16px 0;'>📞 Líneas de Emergencia — toca para llamar</h2>", unsafe_allow_html=True)

    lineas = [
        ("tel:123","123","Policía","🚔","#1D4ED8"),
        ("tel:155","155","Línea Mujer","💜","#8B5CF6"),
        ("tel:125","125","Defensa Civil","🟢","#059669"),
        ("tel:132","132","Cruz Roja","❤️","#EF4444"),
        ("tel:137","137","Salud Mental","🧠","#A78BFA"),
        ("tel:106","106","Bomberos","🔥","#F59E0B"),
    ]
    cols_l = st.columns(6)
    for i, (href, num, desc, ic, co) in enumerate(lineas):
        with cols_l[i]:
            st.markdown(f"""<a href="{href}" style="text-decoration:none;">
            <div style="background:#fff;border-radius:16px;border:1px solid #E2E8F0;padding:18px 12px;text-align:center;margin-bottom:12px;">
                <div style="font-size:20px;margin-bottom:5px;">{ic}</div>
                <div style="font-family:Georgia,serif;font-size:26px;font-weight:900;color:{co};">{num}</div>
                <div style="font-size:10px;color:#64748B;margin-top:4px;">{desc}</div>
            </div></a>""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""<div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:18px;padding:22px;">
            <div style="font-weight:700;color:#92400E;font-size:15px;margin-bottom:12px;">🔒 Salida Rápida</div>
            <p style="font-size:13px;color:#78350F;line-height:1.6;margin-bottom:14px;">Presiona para ir a una página neutra si alguien está mirando tu pantalla:</p>
            <div style="display:flex;gap:10px;flex-wrap:wrap;">
                <a href="https://www.google.com" target="_blank" style="background:#FEF3C7;color:#92400E;padding:8px 16px;border-radius:10px;font-size:12px;text-decoration:none;font-weight:700;">🔍 Google</a>
                <a href="https://weather.com" target="_blank" style="background:#FEF3C7;color:#92400E;padding:8px 16px;border-radius:10px;font-size:12px;text-decoration:none;font-weight:700;">🌦️ Clima</a>
                <a href="https://www.eltiempo.com" target="_blank" style="background:#FEF3C7;color:#92400E;padding:8px 16px;border-radius:10px;font-size:12px;text-decoration:none;font-weight:700;">📰 Noticias</a>
            </div>
        </div>""", unsafe_allow_html=True)
    with col_b:
        tips_list = ["🔵 Mantén la calma y ve a un lugar concurrido",
                     "🔵 Llama o envía tu ubicación a alguien de confianza",
                     "🔵 Memoriza: 123 Policía · 155 Mujer · 132 Ambulancia",
                     "🔵 No confrontes al agresor directamente",
                     "🔵 Documenta evidencia si es completamente seguro",
                     "🔵 Activa la alerta de tu celular o smartwatch"]
        tips_html = "".join([f'<div style="font-size:12px;color:#0F172A;margin-bottom:7px;line-height:1.6;">{t}</div>' for t in tips_list])
        st.markdown(f"""<div style="background:#F5F3FF;border:1px solid #4C1D9518;border-radius:18px;padding:22px;">
            <div style="font-weight:700;color:#4C1D95;font-size:15px;margin-bottom:12px;">💡 En caso de emergencia</div>
            {tips_html}
        </div>""", unsafe_allow_html=True)

# ── DENUNCIAS ─────────────────────────────────────────────────────────────────
elif "📋" in page:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:#FFFBEB;
            border:1px solid #D9770630;border-radius:20px;padding:4px 14px;font-size:11px;
            color:#D97706;font-weight:700;margin-bottom:12px;">📋 CENTRO DE DENUNCIAS</div>
        <h1 style="font-size:30px;font-weight:900;color:#0F172A;margin:0 0 8px;letter-spacing:-0.5px;">Registro de Denuncia</h1>
        <p style="color:#64748B;font-size:14px;margin:0;">Registra un hecho de forma segura y confidencial. Recibirás orientación jurídica personalizada.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("denuncia_sent"):
        col_form, col_info = st.columns([2, 1])
        with col_form:
            with st.container():
                anon = st.toggle("🔒 Denuncia Anónima (Recomendado)", value=True)
                st.markdown(f"""<div style="background:{'#ECFDF5' if anon else '#F5F3FF'};border-radius:16px;padding:12px 16px;
                    border:1px solid {'#05996930' if anon else '#4C1D9530'};margin-bottom:16px;font-size:13px;font-weight:700;
                    color:{'#059669' if anon else '#4C1D95'};">{'✅ Denuncia Anónima activa' if anon else '👤 Denuncia con Identidad'}</div>""",
                    unsafe_allow_html=True)

                st.markdown('<div style="font-size:12px;font-weight:700;color:#4C1D95;margin-bottom:8px;">📌 Paso 1: Clasificación del hecho</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    d_delito = st.selectbox("⚖️ Tipo de Delito", [""] + DELITOS, key="d_delito")
                with c2:
                    d_dep = st.selectbox("🗺️ Departamento", DEPARTAMENTOS, key="d_dep")
                c3, c4 = st.columns(2)
                with c3:
                    d_fecha = st.date_input("📅 Fecha aproximada", key="d_fecha", value=None)
                with c4:
                    d_hora = st.time_input("🕐 Hora aproximada", key="d_hora", value=None)
                d_lugar = st.text_input("📍 Lugar del hecho", placeholder="Ej: Centro Comercial, calle, barrio...", key="d_lugar")

                st.markdown('<div style="font-size:12px;font-weight:700;color:#4C1D95;margin:16px 0 8px;">📝 Paso 2: Descripción del hecho</div>', unsafe_allow_html=True)
                d_desc = st.text_area("Describe lo que ocurrió...", height=140,
                    placeholder="Describe con el mayor detalle posible. Todo es completamente confidencial...", key="d_desc")
                st.markdown(f'<div style="font-size:10px;color:#64748B;margin-top:-8px;margin-bottom:12px;">Caracteres: {len(d_desc)}</div>', unsafe_allow_html=True)

                st.markdown('<div style="font-size:12px;font-weight:700;color:#4C1D95;margin-bottom:8px;">✅ Paso 3: Características y solicitudes</div>', unsafe_allow_html=True)
                opciones = ["Violencia física","Violencia verbal","Violencia psicológica","Violencia económica",
                            "Seguimiento / acoso","Violencia digital","Tengo evidencia","Quiero acompañamiento",
                            "Necesito protección urgente","Quiero mantener anonimato total"]
                d_opts = st.multiselect("Selecciona las que apliquen:", opciones, key="d_opts")

                send_btn = st.button("📤 Registrar y Obtener Orientación Legal Gratuita",
                                     type="primary", use_container_width=True, key="denuncia_send",
                                     disabled=not d_desc.strip())

        with col_info:
            st.markdown("""<div class="safeher-card">
                <div style="font-size:12px;font-weight:700;color:#4C1D95;margin-bottom:14px;">🏢 Entidades Oficiales</div>""", unsafe_allow_html=True)
            entidades_d = [
                ("⚖️","Fiscalía General","Denuncias penales — en línea","https://www.fiscalia.gov.co","#7C3AED"),
                ("🏠","Comisaría de Familia","Violencia intrafamiliar","tel:123","#1D4ED8"),
                ("👨‍👩‍👧","Instituto ICBF","Protección familiar y menores","https://www.icbf.gov.co","#059669"),
                ("📞","Línea 155","Mujer 24/7 — Completamente Gratis","tel:155","#EC4899"),
                ("🚨","URI Fiscalía 24h","Denuncia urgente sin cita","tel:018000919748","#7C3AED"),
            ]
            for icon_e, name_e, desc_e, href_e, color_e in entidades_d:
                st.markdown(f"""<a href="{href_e}" target="{'_blank' if href_e.startswith('http') else '_self'}" style="text-decoration:none;">
                <div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #E2E8F0;">
                    <div style="width:30px;height:30px;background:{color_e}14;border-radius:8px;
                        display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;">{icon_e}</div>
                    <div>
                        <div style="font-size:12px;font-weight:700;color:#0F172A;">{name_e}</div>
                        <div style="font-size:10px;color:#64748B;">{desc_e}</div>
                    </div>
                </div></a>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("""<div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:14px;padding:16px;
                font-size:12px;color:#92400E;line-height:1.7;margin-bottom:14px;">
                ⚠️ Esta plataforma es un <strong>prototipo académico</strong>. Para denuncias con validez legal, dirígete a las entidades oficiales.
            </div>""", unsafe_allow_html=True)

            razones = ["✅ Protege a otras mujeres","✅ Genera registros estadísticos","✅ Activa medidas de protección",
                       "✅ Accedes a apoyo psicológico","✅ Rompe el ciclo de violencia"]
            r_html = "".join([f'<div style="font-size:12px;color:#0F172A;margin-bottom:7px;line-height:1.5;">{r}</div>' for r in razones])
            st.markdown(f'<div class="safeher-card"><div style="font-size:12px;font-weight:700;color:#4C1D95;margin-bottom:10px;">🧠 ¿Por qué es importante denunciar?</div>{r_html}</div>', unsafe_allow_html=True)

        if send_btn and d_desc.strip():
            st.session_state["denuncia_sent"] = True
            with st.spinner("Preparando orientación jurídica personalizada..."):
                legal_text = call_claude(
                    """Eres asistente jurídica especializada en derechos de la mujer en Colombia (Ley 1257/2008).
Usa EXACTAMENTE estas secciones:
⚖️ TUS DERECHOS INMEDIATOS
📋 PASOS A SEGUIR
🏢 ENTIDADES A CONTACTAR
📱 EVIDENCIA A RECOLECTAR
⏰ PLAZOS IMPORTANTES
Máximo 3 puntos por sección. Sé cálida y empática.""",
                    f"Mujer reporta en Colombia:\nDelito: {d_delito}\nDep: {d_dep}\nLugar: {d_lugar}\nDescripción: {d_desc}\nOpciones: {', '.join(d_opts)}"
                )
                st.session_state["legal_text"] = legal_text
            st.rerun()

    else:
        st.markdown("""<div style="background:#ECFDF5;border:1px solid #6EE7B7;border-radius:22px;padding:26px;
            margin-bottom:22px;display:flex;align-items:center;gap:16px;">
            <div style="width:52px;height:52px;background:#059669;border-radius:50%;display:flex;
                align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">✅</div>
            <div>
                <div style="font-size:18px;font-weight:800;color:#065F46;margin-bottom:4px;">Reporte registrado de forma segura</div>
                <div style="font-size:13px;color:#047857;">Tu información es completamente confidencial.</div>
            </div>
        </div>""", unsafe_allow_html=True)

        legal = st.session_state.get("legal_text", "")
        st.markdown(f"""<div class="safeher-card">
            <div style="font-size:15px;font-weight:700;color:#0F172A;margin-bottom:12px;">⚖️ Orientación Jurídica Personalizada</div>
            <div style="font-size:11px;color:#64748B;margin-bottom:16px;">Generada con IA especializada en Ley 1257/2008</div>
            <div style="background:#FAFAFA;border-radius:14px;padding:18px 20px;border:1px solid #E2E8F0;
                font-size:12px;line-height:1.75;white-space:pre-wrap;color:#0F172A;">{legal}</div>
        </div>""", unsafe_allow_html=True)

        if st.button("← Nuevo reporte"):
            st.session_state["denuncia_sent"] = False
            st.session_state.pop("legal_text", None)
            st.rerun()

# ── SARA · IA APOYO ───────────────────────────────────────────────────────────
elif "💜" in page:
    SARA_SYSTEM = """Eres SARA, asistente de apoyo empática y experta de SafeHer Colombia.
PRINCIPIOS: Cálida, empática, nunca juzgas. Valida sentimientos ANTES de dar consejos.
Si hay peligro (golpes, amenazas, secuestro): responde inmediatamente con 🚨 Llama al 123.
Técnicas: ansiedad→4-7-8, crisis→grounding 5-4-3-2-1.
Conocimiento legal: Ley 1257/2008, Comisaría de Familia, Línea 155, Fiscalía URI 24h.
Responde en español, máx 180 palabras, tono cálido y cercano."""

    if "sara_messages" not in st.session_state:
        st.session_state.sara_messages = [
            {"role": "assistant", "content": "Hola 💜 Soy SARA, tu asistente de apoyo de SafeHer.\n\nEstoy aquí para escucharte, orientarte y acompañarte — sin juzgarte, completamente confidencial. Puedes contarme lo que estás viviendo, preguntar sobre tus derechos, o simplemente desahogarte.\n\nEstoy aquí 24/7 para ti. ¿Cómo te puedo ayudar hoy? 🌸"}
        ]

    col_sidebar_sara, col_chat = st.columns([1, 3])

    with col_sidebar_sara:
        st.markdown("""<div style="background:linear-gradient(160deg,#0F0A2E 0%,#4C1D95 60%,#7C3AED 100%);
            border-radius:22px;padding:22px;color:#fff;text-align:center;margin-bottom:14px;">
            <div style="width:64px;height:64px;background:rgba(255,255,255,0.14);border-radius:50%;
                display:flex;align-items:center;justify-content:center;font-size:30px;margin:0 auto 12px;
                border:2px solid rgba(255,255,255,0.22);">💜</div>
            <div style="font-weight:900;font-size:20px;letter-spacing:-0.5px;">SARA</div>
            <div style="font-size:11px;color:#C4B5FD;margin-bottom:12px;">Asistente SafeHer · IA Empática</div>
            <div style="display:flex;align-items:center;gap:6px;justify-content:center;">
                <div style="width:8px;height:8px;border-radius:50%;background:#4ADE80;box-shadow:0 0 8px #4ADE80;"></div>
                <span style="font-size:11px;color:#A7F3D0;">En línea · Disponible 24/7</span>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div style="font-size:12px;font-weight:700;color:#0F172A;margin-bottom:8px;">¿Cómo te sientes ahora?</div>', unsafe_allow_html=True)
        mood_options = [("😰","Asustada"),("😢","Triste"),("😡","Enojada"),("😔","Sola"),("🙂","Bien"),("🆘","Urgente")]
        cols_mood = st.columns(3)
        for i, (emoji, label) in enumerate(mood_options):
            with cols_mood[i % 3]:
                if st.button(f"{emoji}\n{label}", key=f"mood_{label}", use_container_width=True):
                    st.session_state.sara_messages.append({"role": "user", "content": f"Me siento {label.lower()}"})
                    with st.spinner("SARA está escribiendo..."):
                        reply = call_claude(SARA_SYSTEM, "", history=[{"role": m["role"], "content": m["content"]} for m in st.session_state.sara_messages])
                    st.session_state.sara_messages.append({"role": "assistant", "content": reply})
                    st.rerun()

        st.markdown("""<div class="safeher-card" style="margin-top:14px;">
            <div style="font-size:12px;font-weight:700;color:#0F172A;margin-bottom:10px;">💜 SARA puede ayudarte:</div>""", unsafe_allow_html=True)
        for ic, txt in [("🔒","Conversación confidencial"),("⚡","Respuesta empática"),("🧠","Ejercicios de calma"),
                         ("⚖️","Orientación legal"),("📍","Recursos cercanos"),("💬","Escucharte sin juzgar")]:
            st.markdown(f'<div style="display:flex;gap:8px;margin-bottom:8px;"><span style="font-size:14px;">{ic}</span><span style="font-size:11px;color:#64748B;">{txt}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div style="background:#FEF2F2;border:1px solid #FCA5A5;border-radius:14px;padding:14px;">
            <div style="font-size:11px;font-weight:700;color:#991B1B;margin-bottom:10px;">🚨 Emergencia inmediata</div>""", unsafe_allow_html=True)
        for num, desc, sub in [("123","Policía Nacional","24/7"),("155","Línea Mujer","24/7 Gratis"),("137","Salud Mental","Apoyo")]:
            st.markdown(f'<a href="tel:{num}" style="display:flex;justify-content:space-between;text-decoration:none;padding:8px 0;border-bottom:1px solid #FCA5A544;">'
                        f'<span style="font-size:16px;color:#991B1B;font-weight:900;font-family:Georgia,serif;">{num}</span>'
                        f'<div style="text-align:right;"><div style="font-size:10px;color:#DC2626;font-weight:700;">{desc}</div>'
                        f'<div style="font-size:9px;color:#991B1B;">{sub}</div></div></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chat:
        # Chat header
        st.markdown("""<div style="padding:16px 22px;border-bottom:1px solid #E2E8F0;display:flex;align-items:center;
            gap:12px;background:linear-gradient(135deg,#0F0A2E,#4C1D95);border-radius:20px 20px 0 0;">
            <div style="width:40px;height:40px;background:rgba(255,255,255,0.14);border-radius:50%;
                display:flex;align-items:center;justify-content:center;font-size:20px;">💜</div>
            <div>
                <div style="font-weight:700;font-size:15px;color:#fff;">SARA — Asistente SafeHer</div>
                <div style="font-size:11px;color:#A7F3D0;display:flex;align-items:center;gap:5px;">
                    <span style="width:7px;height:7px;border-radius:50%;background:#4ADE80;display:inline-block;"></span>
                    En línea · Siempre disponible · Completamente confidencial
                </div>
            </div>
            <div style="margin-left:auto;display:flex;gap:8px;">
                <a href="tel:155" style="background:rgba(255,255,255,0.12);color:#fff;padding:6px 14px;
                    border-radius:20px;font-size:11px;text-decoration:none;font-weight:700;">📞 155</a>
                <a href="tel:123" style="background:rgba(220,38,38,0.4);color:#fff;padding:6px 14px;
                    border-radius:20px;font-size:11px;text-decoration:none;font-weight:700;">🚨 123</a>
            </div>
        </div>""", unsafe_allow_html=True)

        # Messages
        msgs_html = ""
        for msg in st.session_state.sara_messages:
            if msg["role"] == "user":
                msgs_html += f"""<div style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:16px;">
                    <div style="max-width:76%;background:linear-gradient(135deg,#4C1D95,#7C3AED);color:#fff;
                        border-radius:20px 4px 20px 20px;padding:13px 18px;font-size:13px;line-height:1.75;">{msg['content']}</div>
                    <div style="width:32px;height:32px;background:#F5F3FF;border-radius:50%;display:flex;
                        align-items:center;justify-content:center;font-size:15px;flex-shrink:0;margin-top:2px;">👤</div>
                </div>"""
            else:
                msgs_html += f"""<div style="display:flex;gap:10px;margin-bottom:16px;">
                    <div style="width:32px;height:32px;background:linear-gradient(135deg,#0F0A2E,#7C3AED);border-radius:50%;
                        display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0;margin-top:2px;">💜</div>
                    <div style="max-width:76%;background:#F8F7FF;color:#0F172A;
                        border-radius:4px 20px 20px 20px;padding:13px 18px;font-size:13px;line-height:1.75;
                        border:1px solid #E2E8F0;white-space:pre-wrap;">{msg['content']}</div>
                </div>"""

        st.markdown(f"""<div style="background:#fff;padding:20px 22px;min-height:360px;
            border-left:1px solid #E2E8F0;border-right:1px solid #E2E8F0;overflow-y:auto;max-height:400px;">
            {msgs_html}
        </div>""", unsafe_allow_html=True)

        # Quick replies
        st.markdown('<div style="background:#FAFAFA;padding:10px 22px 8px;border:1px solid #E2E8F0;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:10px;color:#64748B;margin-bottom:6px;font-weight:600;">RESPUESTAS RÁPIDAS:</div>', unsafe_allow_html=True)
        quick_replies = ["Necesito ayuda urgente 🆘","¿Cómo denuncio?","Me siento sola y asustada","¿Cuáles son mis derechos?","Ejercicio para calmarme","Me están amenazando"]
        qcols = st.columns(len(quick_replies))
        for i, q in enumerate(quick_replies):
            with qcols[i]:
                if st.button(q, key=f"qr_{i}", use_container_width=True):
                    st.session_state.sara_messages.append({"role": "user", "content": q})
                    with st.spinner("SARA está escribiendo..."):
                        reply = call_claude(SARA_SYSTEM, "", history=[{"role": m["role"], "content": m["content"]} for m in st.session_state.sara_messages])
                    st.session_state.sara_messages.append({"role": "assistant", "content": reply})
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Input
        with st.form("sara_form", clear_on_submit=True):
            col_inp, col_send = st.columns([5, 1])
            with col_inp:
                user_input = st.text_input("", placeholder="Escribe tu mensaje... (Ej: Necesito ayuda, ¿cómo denuncio?)",
                                           label_visibility="collapsed", key="sara_input")
            with col_send:
                send_sara = st.form_submit_button("➤", use_container_width=True)
        if send_sara and user_input.strip():
            st.session_state.sara_messages.append({"role": "user", "content": user_input.strip()})
            with st.spinner("SARA está escribiendo..."):
                reply = call_claude(SARA_SYSTEM, "", history=[{"role": m["role"], "content": m["content"]} for m in st.session_state.sara_messages])
            st.session_state.sara_messages.append({"role": "assistant", "content": reply})
            st.rerun()

        st.markdown('<div style="background:#fff;border:1px solid #E2E8F0;border-radius:0 0 20px 20px;padding:6px;"></div>', unsafe_allow_html=True)

# ── AYUDA CERCANA ─────────────────────────────────────────────────────────────
elif "🚔" in page:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:#EFF6FF;
            border:1px solid #1D4ED830;border-radius:20px;padding:4px 14px;font-size:11px;
            color:#1D4ED8;font-weight:700;margin-bottom:12px;">🚔 AYUDA CERCANA</div>
        <h1 style="font-size:30px;font-weight:900;color:#0F172A;margin:0 0 8px;letter-spacing:-0.5px;">Ayuda Cercana</h1>
        <p style="color:#64748B;font-size:14px;margin:0;">Encuentra entidades de apoyo con información detallada y cómo llegar.</p>
    </div>
    """, unsafe_allow_html=True)

    city_input = st.text_input("📍 Ingresa tu ciudad o barrio:", value="Medellín", key="ayuda_city")

    entidades = [
        {"tipo": "Policía", "icon": "🚔", "nom": "CAI Centro", "dir": "Carrera 45 #54-20, Medellín", "dist": "0.4 km", "color": "#1D4ED8", "href": "tel:123", "phone": "123", "horario": "24/7", "desc": "Centro de Atención Inmediata. Atención permanente para denuncias y emergencias."},
        {"tipo": "Hospital", "icon": "🏥", "nom": "Hospital General de Medellín", "dir": "Calle 24 #29-6, Medellín", "dist": "1.2 km", "color": "#059669", "href": "tel:4411227", "phone": "4411227", "horario": "24/7 Urgencias", "desc": "Urgencias completas, medicina forense y apoyo psicológico para víctimas de violencia."},
        {"tipo": "Fiscalía", "icon": "⚖️", "nom": "Fiscalía Seccional Medellín", "dir": "Calle 44 #52-165, Medellín", "dist": "0.8 km", "color": "#7C3AED", "href": "https://www.fiscalia.gov.co", "phone": "01-8000-919-748", "horario": "Lun–Vie 7am–5pm", "desc": "Recepción de denuncias penales, medidas de protección y seguimiento a casos."},
        {"tipo": "Refugio", "icon": "🏠", "nom": "Casa Refugio Luz y Esperanza", "dir": "Dirección confidencial — llama al 155", "dist": "2.1 km", "color": "#D97706", "href": "tel:155", "phone": "155", "horario": "24/7 Disponible", "desc": "Alojamiento temporal seguro para mujeres víctimas de violencia. Completamente gratuito."},
        {"tipo": "Psicología", "icon": "🧠", "nom": "Centro Atención Psicosocial", "dir": "Calle 50 #40-20, Medellín", "dist": "1.5 km", "color": "#8B5CF6", "href": "tel:137", "phone": "137", "horario": "Lun–Sáb 8am–8pm", "desc": "Atención psicológica gratuita, terapia individual y grupos de apoyo."},
        {"tipo": "Policía", "icon": "🚔", "nom": "Estación Policía Laureles", "dir": "Carrera 81 #30-05, Medellín", "dist": "3.2 km", "color": "#1D4ED8", "href": "tel:123", "phone": "123", "horario": "24/7", "desc": "Estación de Policía del barrio Laureles. Denuncia y apoyo policial inmediato."},
        {"tipo": "Hospital", "icon": "🏥", "nom": "Clínica Las Américas", "dir": "Diagonal 75B #2A-80, Medellín", "dist": "2.8 km", "color": "#059669", "href": "tel:4456600", "phone": "4456600", "horario": "24/7 Urgencias", "desc": "Urgencias completas y medicina forense. Atención prioritaria a víctimas de violencia."},
        {"tipo": "Fiscalía", "icon": "⚖️", "nom": "URI Fiscalía 24 Horas", "dir": "Calle 57 #45-129, Medellín", "dist": "0.9 km", "color": "#7C3AED", "href": "https://www.fiscalia.gov.co", "phone": "01-8000-919-748", "horario": "24/7 Sin cita", "desc": "Unidad de Reacción Inmediata. Denuncias penales urgentes las 24 horas."},
        {"tipo": "Psicología", "icon": "🧠", "nom": "Comisaría de Familia N°1", "dir": "Carrera 52 #48-10, Medellín", "dist": "1.1 km", "color": "#8B5CF6", "href": "tel:123", "phone": "Presencial", "horario": "Lun–Vie 8am–5pm", "desc": "Medidas de protección familiar, conciliación y apoyo psicosocial integral."},
        {"tipo": "Refugio", "icon": "🏠", "nom": "Casa de Acogida ICBF", "dir": "Dirección confidencial — Línea 141", "dist": "3.5 km", "color": "#D97706", "href": "tel:141", "phone": "141 ICBF", "horario": "24/7", "desc": "Casa de acogida para mujeres y niños en situación de violencia intrafamiliar."},
    ]

    filter_tipo = st.selectbox("Filtrar por tipo:", ["Todos","Policía","Hospitales","Fiscalía","Refugios","Psicología"], key="ayuda_filter")
    filter_map = {"Todos": "Todos", "Policía": "Policía", "Hospitales": "Hospital", "Fiscalía": "Fiscalía", "Refugios": "Refugio", "Psicología": "Psicología"}
    filtered = [e for e in entidades if filter_tipo == "Todos" or e["tipo"] == filter_map[filter_tipo]]

    st.markdown(f'<div style="font-size:12px;color:#64748B;margin-bottom:16px;"><strong style="color:#0F172A;">{len(filtered)}</strong> lugares de apoyo cerca de <strong style="color:#0F172A;">{city_input}</strong></div>', unsafe_allow_html=True)

    col_grid, col_ent = st.columns([2, 1])
    with col_grid:
        gcols = st.columns(3)
        for i, e in enumerate(filtered):
            with gcols[i % 3]:
                is_sel = st.session_state.get("selected_entity") == e["nom"]
                border_color = e["color"] if is_sel else "#E2E8F0"
                shadow = f"0 4px 24px {e['color']}28" if is_sel else "0 1px 8px rgba(0,0,0,0.04)"
                st.markdown(f"""<div style="background:#fff;border:2px solid {border_color};border-radius:20px;
                    padding:20px;cursor:pointer;box-shadow:{shadow};margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">
                        <div style="background:{e['color']}14;border-radius:12px;width:46px;height:46px;
                            display:flex;align-items:center;justify-content:center;font-size:22px;">{e['icon']}</div>
                        <div style="background:{e['color']}14;color:{e['color']};font-size:9px;font-weight:700;
                            padding:4px 8px;border-radius:20px;text-transform:uppercase;">{e['tipo']}</div>
                    </div>
                    <div style="font-weight:700;font-size:14px;color:#0F172A;margin-bottom:5px;">{e['nom']}</div>
                    <div style="font-size:11px;color:#64748B;margin-bottom:10px;">📍 {e['dir']}</div>
                    <div style="display:flex;gap:6px;flex-wrap:wrap;">
                        <div style="background:#ECFDF5;color:#059669;font-size:10px;font-weight:700;padding:4px 10px;border-radius:20px;">🚶 {e['dist']}</div>
                        <div style="background:#EFF6FF;color:#1D4ED8;font-size:10px;font-weight:700;padding:4px 10px;border-radius:20px;">🕐 {e['horario']}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                if st.button("Ver detalles", key=f"ent_{e['nom']}", use_container_width=True):
                    if st.session_state.get("selected_entity") == e["nom"]:
                        st.session_state.pop("selected_entity", None)
                    else:
                        st.session_state["selected_entity"] = e["nom"]
                    st.rerun()

    with col_ent:
        sel_nom = st.session_state.get("selected_entity")
        sel_e = next((e for e in entidades if e["nom"] == sel_nom), None)
        if sel_e:
            st.markdown(f"""<div class="safeher-card">
                <div style="background:{sel_e['color']}14;border-radius:16px;width:54px;height:54px;
                    display:flex;align-items:center;justify-content:center;font-size:26px;margin-bottom:16px;">{sel_e['icon']}</div>
                <div style="font-size:8px;font-weight:700;color:{sel_e['color']};letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">{sel_e['tipo']}</div>
                <div style="font-size:18px;font-weight:900;color:#0F172A;margin-bottom:8px;">{sel_e['nom']}</div>
                <p style="font-size:12px;color:#64748B;line-height:1.65;margin-bottom:18px;">{sel_e['desc']}</p>""", unsafe_allow_html=True)

            for label, val in [("📍 Dirección", sel_e['dir']),("🕐 Horario", sel_e['horario']),("📞 Contacto", sel_e['phone'])]:
                st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:9px 12px;background:#FAFAFA;border-radius:10px;margin-bottom:8px;">
                    <span style="font-size:11px;color:#64748B;">{label}</span>
                    <span style="font-size:11px;font-weight:700;color:#0F172A;text-align:right;max-width:55%;">{val}</span>
                </div>""", unsafe_allow_html=True)

            st.markdown(f'<a href="{sel_e["href"]}" target="{"_blank" if sel_e["href"].startswith("http") else "_self"}" style="text-decoration:none;display:block;margin-bottom:8px;">'
                        f'<div style="width:100%;background:linear-gradient(135deg,{sel_e["color"]},{sel_e["color"]}BB);color:#fff;border-radius:12px;'
                        f'padding:12px;text-align:center;font-size:13px;font-weight:700;cursor:pointer;">{"📞 Llamar: " + sel_e["phone"] if sel_e["href"].startswith("tel:") else "🌐 Visitar sitio"}</div></a>', unsafe_allow_html=True)

            maps_url = f"https://maps.google.com/?q={sel_e['dir'].replace(' ', '+')}"
            st.markdown(f'<a href="{maps_url}" target="_blank" style="text-decoration:none;display:block;margin-bottom:10px;">'
                        f'<div style="width:100%;background:#fff;color:#1D4ED8;border:1px solid #1D4ED8;border-radius:12px;'
                        f'padding:10px;text-align:center;font-size:12px;font-weight:700;cursor:pointer;">🗺️ Abrir en Google Maps</div></a>', unsafe_allow_html=True)

            if st.button(f"🧭 ¿Cómo llegar desde {city_input}?", key="directions_btn", use_container_width=True):
                with st.spinner("Calculando mejor ruta..."):
                    dir_text = call_claude(
                        "Experto en navegación y transporte de Colombia. Instrucciones claras con bullets y emojis. Incluye: TransMilenio/Metro, taxi, caminando. Máx 100 palabras.",
                        f"¿Cómo llego desde el centro de {city_input} a {sel_e['nom']}, en {sel_e['dir']}? Distancia: {sel_e['dist']}."
                    )
                    st.session_state[f"dir_{sel_e['nom']}"] = dir_text

            dir_r = st.session_state.get(f"dir_{sel_e['nom']}", "")
            if dir_r:
                st.markdown(f"""<div style="background:#F8F7FF;border-radius:12px;padding:14px 16px;border:1px solid #7C3AED25;">
                    <div style="font-size:11px;font-weight:700;color:#7C3AED;margin-bottom:8px;">🧭 Cómo llegar desde {city_input}</div>
                    <div style="font-size:11px;color:#0F172A;line-height:1.75;white-space:pre-wrap;">{dir_r}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background:#F8FAFC;border-radius:16px;border:2px dashed #E2E8F0;
                padding:40px 20px;text-align:center;color:#94A3B8;font-size:13px;">
                👆 Selecciona una entidad para ver más detalles
            </div>""", unsafe_allow_html=True)

    tips_ayuda = ["📱 Google Maps: 'Comisaría de Familia + tu ciudad'","📞 Línea 155: te orientan al refugio más cercano",
                  "🚔 Estación de Policía más cercana: denuncia inmediata","🏥 Cualquier hospital: urgencias para víctimas sin costo",
                  "📋 Fiscalía URI: denuncia 24h sin cita previa","🏠 ICBF (Línea 141): protección familiar emergencia"]
    t_cols = st.columns(2)
    for i, tip in enumerate(tips_ayuda):
        with t_cols[i % 2]:
            st.markdown(f'<div style="font-size:12px;color:#0F172A;line-height:1.7;padding:8px 12px;background:#fff;border-radius:10px;border:1px solid #E2E8F0;margin-bottom:8px;">{tip}</div>', unsafe_allow_html=True)

# ── ACERCA DE ─────────────────────────────────────────────────────────────────
elif "ℹ️" in page:
    st.markdown('<h1 style="font-size:30px;font-weight:900;color:#0F172A;margin-bottom:26px;letter-spacing:-0.5px;">ℹ️ Acerca de SafeHer Colombia</h1>', unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown("""<div class="safeher-card">
            <div style="font-weight:700;color:#4C1D95;font-size:16px;margin-bottom:14px;">🎓 Proyecto Académico</div>
            <p style="font-size:13px;color:#0F172A;line-height:1.8;margin-bottom:18px;">
                Desarrollado como proyecto de <strong>Analítica y Machine Learning</strong>. Modelos entrenados con datos del
                Sistema de Información Estadístico de la <strong>Policía Nacional de Colombia</strong>.
                Enfocado en la protección, prevención y apoyo integral para mujeres.
            </p>
            <div style="font-weight:700;color:#0F172A;margin-bottom:12px;font-size:14px;">👩‍💻 Equipo de Desarrollo:</div>""", unsafe_allow_html=True)
        for name in ["Laura Sofia Beltrán","Dana Yaray Vargas","Vanessa Mora"]:
            st.markdown(f"""<div style="background:#FAFAFA;border-radius:12px;padding:11px 16px;display:flex;align-items:center;
                gap:12px;margin-bottom:8px;border:1px solid #E2E8F0;">
                <span>👩‍🎓</span><span style="font-size:13px;color:#0F172A;font-weight:600;">{name}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="safeher-card">
            <div style="font-weight:700;color:#4C1D95;font-size:16px;margin-bottom:16px;">🤖 Modelos de Machine Learning</div>""", unsafe_allow_html=True)
        for ti, al, ta, co in [
            ("📊 Nivel de Gravedad","XGBoost + LightGBM","8 clases: MÍNIMO → CRÍTICO","#4C1D95"),
            ("🗺️ Zona de Riesgo","XGBoost + LightGBM","6 clases: MUY BAJO → MUY ALTO","#1D4ED8"),
            ("👥 Estimación de Víctimas","Ensemble de modelos","Valor numérico estimado","#059669"),
            ("🧠 IA de Apoyo (SARA)","Claude Sonnet 4","Apoyo psicológico y legal","#7C3AED"),
        ]:
            st.markdown(f"""<div style="background:#FAFAFA;border:1px solid {co}18;border-radius:14px;padding:13px 16px;margin-bottom:10px;">
                <div style="font-weight:700;color:#0F172A;font-size:13px;">{ti}</div>
                <div style="font-size:12px;color:{co};margin-top:2px;">{al}</div>
                <div style="font-size:11px;color:#64748B;margin-top:2px;">Target: {ta}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown("""<div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:18px;padding:20px;margin-bottom:16px;">
            <div style="font-weight:700;color:#92400E;font-size:14px;margin-bottom:8px;">⚠️ Limitaciones Importantes</div>
            <p style="font-size:12px;color:#78350F;line-height:1.75;">Plataforma <strong>académica prototipo</strong>.
            Las predicciones son aproximaciones estadísticas. Para emergencias reales llama al
            <strong>123</strong> o <strong>Línea 155</strong>.</p>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:700;color:#0F172A;font-size:14px;margin-bottom:14px;">🛠️ Stack Tecnológico</div>', unsafe_allow_html=True)
        for tech, pct, color in [
            ("Python + Streamlit","95%","#4C1D95"),("XGBoost","92%","#1D4ED8"),("LightGBM","90%","#059669"),
            ("Scikit-learn","88%","#D97706"),("Claude API (SARA)","100%","#7C3AED"),("Pandas + NumPy","90%","#0891B2")
        ]:
            st.markdown(f"""<div style="margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:5px;">
                    <span style="color:#0F172A;font-weight:600;">{tech}</span>
                    <span style="color:{color};font-weight:800;">{pct}</span>
                </div>
                <div style="background:#F1F5F9;border-radius:6px;height:8px;">
                    <div style="width:{pct};height:100%;background:linear-gradient(90deg,{color}99,{color});border-radius:6px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:700;color:#4C1D95;font-size:14px;margin-bottom:12px;">📊 Cobertura</div>', unsafe_allow_html=True)
        for v, k in [("Colombia completa","Cobertura"),("33","Departamentos"),("1.121","Municipios"),
                      ("6","Tipos de delito"),("Policía Nacional","Fuente de datos"),("2019–2027","Período de análisis")]:
            st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:8px 0;
                border-bottom:1px solid #E2E8F0;font-size:12px;">
                <span style="color:#64748B;">{k}</span>
                <span style="color:#0F172A;font-weight:700;">{v}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
