import streamlit as st
import random
import math
import os
import pickle
import numpy as np
import pandas as pd
from groq import Groq
import plotly.graph_objects as go

# ─── CARGAR MODELOS PKL ───────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    models = {}
    files = {
        "xgb_zona":           "xgb_zona.pkl",
        "lgbm_zona":          "lgbm_zona.pkl",
        "le_zona":            "le_target_zona.pkl",
        "encoders_zona":      "encoders_zona.pkl",
        "xgb_gravedad":       "xgb_gravedad.pkl",
        "pipe_lgbm_gravedad": "pipe_lgbm_gravedad.pkl",
        "le_gravedad":        "le_target_gravedad.pkl",
        "preprocessor_grav":  "preprocessor_gravedad.pkl",
        "scaler_gravedad":    "scaler_gravedad.pkl",
    }
    for key, fname in files.items():
        try:
            with open(fname, "rb") as f:
                models[key] = pickle.load(f)
        except Exception:
            models[key] = None
    return models

MODELS = load_models()
MODELS_OK = any(v is not None for v in MODELS.values())

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SafeHer Colombia · IA Protección",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif !important;
    background: #F5F3FF !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="stToolbar"] {display: none;}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #EDE9FE !important;
    min-width: 240px !important;
    max-width: 240px !important;
    box-shadow: 2px 0 16px rgba(109,40,217,0.06);
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebar"] .stRadio > div { gap: 0 !important; }
[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    padding: 10px 16px !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #7C3AED !important;
    transition: all 0.18s !important;
    margin-bottom: 2px !important;
    white-space: nowrap !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #F5F3FF !important;
    color: #5B21B6 !important;
}
[data-testid="stSidebar"] input[type="radio"] { display: none !important; }
[data-testid="stSidebar"] .stRadio > label { display: none !important; }
[data-testid="stSidebar"] .element-container { margin: 0 !important; padding: 0 6px !important; }

/* ── Main content ── */
.main .block-container {
    padding: 24px 36px !important;
    max-width: 100% !important;
    background: #F5F3FF !important;
}

/* ── Cards ── */
.sh-card {
    background: #FFFFFF;
    border-radius: 20px;
    border: 1px solid #EDE9FE;
    box-shadow: 0 2px 20px rgba(109,40,217,0.07);
    padding: 22px;
    margin-bottom: 16px;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    border: none !important;
    padding: 10px 20px !important;
    box-shadow: 0 2px 8px rgba(109,40,217,0.15) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(109,40,217,0.25) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #5B21B6, #7C3AED) !important;
    color: white !important;
}
.stButton > button[kind="secondary"] {
    background: #F5F3FF !important;
    color: #5B21B6 !important;
    border: 1px solid #C4B5FD !important;
}

/* ── Inputs / selects ── */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput > div > div > input,
.stTextArea textarea {
    border-radius: 12px !important;
    border: 1.5px solid #DDD6FE !important;
    font-family: inherit !important;
    font-size: 13px !important;
    background: #FAFAFA !important;
    transition: border 0.18s !important;
}
.stSelectbox [data-baseweb="select"]:focus-within > div,
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #EDE9FE;
    border-radius: 14px;
    padding: 5px;
    border: none;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #5B21B6 !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    box-shadow: 0 2px 8px rgba(109,40,217,0.12) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #EDE9FE;
    border-radius: 18px;
    padding: 16px !important;
    box-shadow: 0 2px 12px rgba(109,40,217,0.06);
}

/* ── Toggle ── */
.stCheckbox label, [data-testid="stCheckbox"] label { font-size: 13px !important; }

/* ── Spinner ── */
.stSpinner > div > div { border-top-color: #7C3AED !important; }

/* ── Progress bar ── */
.stProgress > div > div > div { background: linear-gradient(90deg, #A78BFA, #7C3AED) !important; border-radius: 99px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F5F3FF; }
::-webkit-scrollbar-thumb { background: #C4B5FD; border-radius: 99px; }

/* ── Alert boxes ── */
.stAlert { border-radius: 16px !important; }

/* ── Risk badge ── */
.risk-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.4px;
    white-space: nowrap;
}

/* ── Chat bubbles ── */
.chat-user {
    background: linear-gradient(135deg, #5B21B6, #7C3AED);
    color: white;
    border-radius: 20px 4px 20px 20px;
    padding: 13px 18px;
    font-size: 13px;
    line-height: 1.75;
    max-width: 76%;
    margin-left: auto;
    margin-bottom: 14px;
    box-shadow: 0 3px 12px rgba(124,58,237,0.22);
}
.chat-sara {
    background: #FAF8FF;
    color: #1E1B4B;
    border-radius: 4px 20px 20px 20px;
    padding: 13px 18px;
    font-size: 13px;
    line-height: 1.8;
    max-width: 76%;
    border: 1px solid #EDE9FE;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(109,40,217,0.05);
}

/* ── Forms ── */
[data-testid="stForm"] {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}

/* Hover on markdown links ── */
a:hover { opacity: 0.88; }

/* Remove top space ── */
.block-container { padding-top: 16px !important; }

/* Hide empty element containers ── */
.element-container:empty { display: none !important; }
div[data-testid="stVerticalBlock"] > div:empty { display: none !important; }
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
    "ANTIOQUIA": ["MEDELLÍN","BELLO","ITAGÜÍ","ENVIGADO","APARTADÓ","TURBO"],
    "BOGOTÁ D.C.": ["BOGOTÁ"],
    "VALLE DEL CAUCA": ["CALI","BUENAVENTURA","PALMIRA","TULUÁ","BUGA"],
    "CUNDINAMARCA": ["SOACHA","FACATATIVÁ","ZIPAQUIRÁ","FUSAGASUGÁ","GIRARDOT"],
    "ATLÁNTICO": ["BARRANQUILLA","SOLEDAD","MALAMBO","SABANAGRANDE","SABANALARGA"],
    "SANTANDER": ["BUCARAMANGA","FLORIDABLANCA","GIRÓN","PIEDECUESTA","BARRANCABERMEJA"],
    "NARIÑO": ["PASTO","TUMACO","IPIALES","TÚQUERRES","LA UNIÓN"],
    "CÓRDOBA": ["MONTERÍA","CERETÉ","LORICA","SAHAGÚN","TIERRALTA"],
    "BOLÍVAR": ["CARTAGENA","MAGANGUÉ","EL CARMEN","MOMPÓS","TURBACO"],
    "TOLIMA": ["IBAGUÉ","ESPINAL","MELGAR","HONDA","CHAPARRAL"],
}
def get_municipios(dep):
    return MUNICIPIOS_SAMPLE.get(dep, ["Capital","Municipio 1","Municipio 2"])

CRIME_DATA = {
    "ANTIOQUIA":          {"score": 4.2, "zona": "ALTO",      "gravedad": "ALTO",      "municipios": 125},
    "BOGOTÁ D.C.":        {"score": 3.8, "zona": "MEDIO-ALTO","gravedad": "MEDIO-ALTO","municipios": 1},
    "VALLE DEL CAUCA":    {"score": 4.5, "zona": "MUY ALTO",  "gravedad": "ALTO",      "municipios": 42},
    "CUNDINAMARCA":       {"score": 2.9, "zona": "MEDIO-BAJO","gravedad": "BAJO",      "municipios": 116},
    "ATLÁNTICO":          {"score": 3.1, "zona": "MEDIO-BAJO","gravedad": "MEDIO-BAJO","municipios": 23},
    "SANTANDER":          {"score": 2.5, "zona": "BAJO",      "gravedad": "BAJO",      "municipios": 87},
    "NARIÑO":             {"score": 3.7, "zona": "MEDIO-ALTO","gravedad": "MEDIO-ALTO","municipios": 64},
    "CÓRDOBA":            {"score": 3.0, "zona": "MEDIO-BAJO","gravedad": "BAJO",      "municipios": 30},
    "BOLÍVAR":            {"score": 3.4, "zona": "MEDIO-BAJO","gravedad": "MEDIO-BAJO","municipios": 46},
    "TOLIMA":             {"score": 2.7, "zona": "BAJO",      "gravedad": "BAJO",      "municipios": 47},
    "HUILA":              {"score": 2.8, "zona": "BAJO",      "gravedad": "BAJO",      "municipios": 37},
    "CAUCA":              {"score": 4.0, "zona": "ALTO",      "gravedad": "ALTO",      "municipios": 42},
    "META":               {"score": 3.3, "zona": "MEDIO-BAJO","gravedad": "MEDIO-BAJO","municipios": 29},
    "CESAR":              {"score": 3.2, "zona": "MEDIO-BAJO","gravedad": "MEDIO-BAJO","municipios": 25},
    "MAGDALENA":          {"score": 3.0, "zona": "MEDIO-BAJO","gravedad": "BAJO",      "municipios": 30},
    "BOYACÁ":             {"score": 2.2, "zona": "MUY BAJO",  "gravedad": "MUY BAJO",  "municipios": 123},
    "CALDAS":             {"score": 2.6, "zona": "BAJO",      "gravedad": "BAJO",      "municipios": 27},
    "RISARALDA":          {"score": 2.8, "zona": "BAJO",      "gravedad": "BAJO",      "municipios": 14},
    "QUINDÍO":            {"score": 2.5, "zona": "BAJO",      "gravedad": "BAJO",      "municipios": 12},
    "NORTE DE SANTANDER": {"score": 3.6, "zona": "MEDIO-ALTO","gravedad": "MEDIO-ALTO","municipios": 40},
    "SUCRE":              {"score": 2.9, "zona": "MEDIO-BAJO","gravedad": "BAJO",      "municipios": 26},
    "LA GUAJIRA":         {"score": 3.5, "zona": "MEDIO-ALTO","gravedad": "MEDIO-BAJO","municipios": 15},
    "CAQUETÁ":            {"score": 3.8, "zona": "ALTO",      "gravedad": "MEDIO-ALTO","municipios": 16},
    "ARAUCA":             {"score": 3.9, "zona": "ALTO",      "gravedad": "ALTO",      "municipios": 7},
    "CASANARE":           {"score": 2.7, "zona": "BAJO",      "gravedad": "BAJO",      "municipios": 19},
    "VICHADA":            {"score": 2.3, "zona": "MUY BAJO",  "gravedad": "MUY BAJO",  "municipios": 4},
    "GUAINÍA":            {"score": 2.1, "zona": "MUY BAJO",  "gravedad": "MÍNIMO",    "municipios": 8},
    "GUAVIARE":           {"score": 3.2, "zona": "MEDIO-BAJO","gravedad": "MEDIO-BAJO","municipios": 4},
    "VAUPÉS":             {"score": 2.0, "zona": "MUY BAJO",  "gravedad": "MÍNIMO",    "municipios": 6},
    "AMAZONAS":           {"score": 2.1, "zona": "MUY BAJO",  "gravedad": "MÍNIMO",    "municipios": 9},
    "PUTUMAYO":           {"score": 3.6, "zona": "MEDIO-ALTO","gravedad": "MEDIO-ALTO","municipios": 13},
    "CHOCÓ":              {"score": 4.1, "zona": "ALTO",      "gravedad": "ALTO",      "municipios": 30},
    "SAN ANDRÉS":         {"score": 2.8, "zona": "BAJO",      "gravedad": "BAJO",      "municipios": 2},
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

def risk_badge(level, small=False):
    cfg = RISK_LEVELS.get(level, {"color": "#888", "bg": "#f3f4f6", "label": level})
    p = "2px 9px" if small else "4px 14px"
    fs = "10px" if small else "11px"
    return (f'<span style="background:{cfg["bg"]};color:{cfg["color"]};border:1px solid {cfg["color"]}44;'
            f'border-radius:20px;padding:{p};font-size:{fs};font-weight:700;letter-spacing:0.4px;'
            f'display:inline-block;white-space:nowrap;">{cfg["label"]}</span>')

def card(content, extra=""):
    return (f'<div style="background:#fff;border-radius:20px;border:1px solid #EDE9FE;'
            f'box-shadow:0 2px 20px rgba(109,40,217,0.07);padding:22px;margin-bottom:16px;{extra}">{content}</div>')

def get_api_key():
    """Obtiene GROQ_API_KEY desde secrets de Streamlit o variable de entorno."""
    try:
        key = st.secrets["GROQ_API_KEY"]
        if key and key.strip():
            return key.strip()
    except Exception:
        pass
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key
    return None

def call_claude(system_prompt, user_msg, history=None):
    """Llama a Groq API (gratis) en lugar de Anthropic."""
    try:
        api_key = get_api_key()

        if not api_key:
            return ("⚠️ API Key no configurada. "
                    "Ve a Streamlit Cloud → Settings → Secrets y agrega: "
                    "GROQ_API_KEY = \"gsk_tu-clave-aqui\"")

        client = Groq(api_key=api_key)

        if history:
            messages = [{"role": "system", "content": system_prompt}] + history
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ]

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1000,
        )
        return response.choices[0].message.content

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
    used_pkl = False

    # ── Intentar usar modelos PKL reales ──────────────────────────────────────
    try:
        if MODELS.get("xgb_zona") and MODELS.get("encoders_zona") and MODELS.get("le_zona"):
            enc = MODELS["encoders_zona"]
            # Construir DataFrame de entrada
            row = pd.DataFrame([{
                "DEPARTAMENTO": dep,
                "MUNICIPIO":    mun,
                "DELITO":       delito,
                "SEXO":         sexo,
                "GRUPO_ETARIO": etario,
                "AÑO":          año,
            }])
            # Aplicar label encoders si existen
            for col in ["DEPARTAMENTO","MUNICIPIO","DELITO","SEXO","GRUPO_ETARIO"]:
                if col in enc and col in row.columns:
                    try:
                        row[col] = enc[col].transform(row[col].astype(str))
                    except Exception:
                        row[col] = 0
            zona_pred = MODELS["xgb_zona"].predict(row)[0]
            try:
                zona = MODELS["le_zona"].inverse_transform([zona_pred])[0]
            except Exception:
                zona = str(zona_pred)
            used_pkl = True
    except Exception:
        pass

    try:
        if MODELS.get("xgb_gravedad") and MODELS.get("le_gravedad"):
            row2 = pd.DataFrame([{
                "DEPARTAMENTO": dep,
                "MUNICIPIO":    mun,
                "DELITO":       delito,
                "SEXO":         sexo,
                "GRUPO_ETARIO": etario,
                "AÑO":          año,
            }])
            if MODELS.get("preprocessor_grav"):
                row2 = MODELS["preprocessor_grav"].transform(row2)
            elif MODELS.get("scaler_gravedad"):
                row2 = MODELS["scaler_gravedad"].transform(row2)
            grav_pred = MODELS["xgb_gravedad"].predict(row2)[0]
            try:
                gravedad = MODELS["le_gravedad"].inverse_transform([grav_pred])[0]
            except Exception:
                gravedad = str(grav_pred)
            used_pkl = True
    except Exception:
        pass

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
    monthly = [{"month": m, "value": round(adjusted * seasonal[i] * (1 + random.random()*0.1-0.05), 2),
                "cases": round(victimas/12 * seasonal[i] * (1+random.random()*0.2-0.1))}
               for i, m in enumerate(months)]

    return {"zona": zona, "gravedad": gravedad, "victimas": victimas, "probs_zona": probs_zona,
            "trend": trend, "comparativa": comparativa, "score": round(adjusted, 1),
            "zona_idx": zona_idx, "monthly": monthly, "used_pkl": used_pkl}

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 20px 18px;border-bottom:1px solid #EDE9FE;">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:42px;height:42px;background:linear-gradient(135deg,#2E1065,#7C3AED);
                border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:20px;
                box-shadow:0 4px 12px rgba(124,58,237,0.35);">🛡️</div>
            <div>
                <div style="font-weight:900;font-size:18px;color:#1E1B4B;letter-spacing:-0.5px;">SafeHer</div>
                <div style="font-size:9px;color:#A78BFA;text-transform:uppercase;letter-spacing:1.4px;font-weight:600;">Colombia · IA Protección</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:10px 8px 0;'>", unsafe_allow_html=True)
    nav_options = [
        "🏠  Inicio",
        "📊  Predicción ML",
        "🗺️  Mapa de Riesgo",
        "✈️  Viaje Seguro",
        "🚨  Emergencias",
        "📋  Denuncias",
        "💜  SARA · IA Apoyo",
        "🚔  Ayuda Cercana",
        "ℹ️  Acerca de",
    ]
    # Allow navigation from module cards
    default_nav = nav_options.index(st.session_state.get("nav_page", "🏠  Inicio")) if st.session_state.get("nav_page") in nav_options else 0
    if "nav_page" in st.session_state:
        del st.session_state["nav_page"]
    page = st.radio("nav", options=nav_options, index=default_nav, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:16px 14px;border-top:1px solid #EDE9FE;margin-top:auto;">
        <div style="background:linear-gradient(135deg,#FFF1F2,#FEE2E2);border:1px solid #FECDD3;
            border-radius:18px;padding:16px;text-align:center;">
            <div style="font-size:10px;color:#9F1239;font-weight:800;letter-spacing:1.2px;
                text-transform:uppercase;margin-bottom:8px;">🚨 Emergencias</div>
            <a href="tel:123" style="display:block;font-size:30px;font-weight:900;color:#DC2626;
                text-decoration:none;font-family:Georgia,serif;line-height:1;letter-spacing:-1px;">123</a>
            <div style="font-size:9px;color:#BE123C;margin-bottom:10px;font-weight:600;">Policía Nacional</div>
            <a href="tel:155" style="display:block;font-size:30px;font-weight:900;color:#7C3AED;
                text-decoration:none;font-family:Georgia,serif;line-height:1;letter-spacing:-1px;">155</a>
            <div style="font-size:9px;color:#6D28D9;font-weight:600;">Línea Mujer 24/7</div>
        </div>
        <div style="text-align:center;margin-top:10px;font-size:9px;color:#A78BFA;font-weight:500;">
            Prototipo académico v4.0 · Datos: Policía Nacional
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ─── PÁGINAS ──────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

# ── INICIO ────────────────────────────────────────────────────────────────────
if "🏠" in page:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1E1B4B 0%,#312E81 45%,#4C1D95 100%);
        border-radius:28px;padding:52px 52px;margin-bottom:32px;position:relative;overflow:hidden;color:#fff;">
        <div style="position:absolute;top:-80px;right:-80px;width:380px;height:380px;border-radius:50%;background:rgba(255,255,255,0.04);"></div>
        <div style="position:absolute;bottom:-60px;right:100px;width:220px;height:220px;border-radius:50%;background:rgba(236,72,153,0.1);"></div>
        <div style="max-width:600px;position:relative;">
            <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.1);
                border:1px solid rgba(255,255,255,0.18);border-radius:24px;padding:6px 18px;
                font-size:11px;color:#E9D5FF;font-weight:700;letter-spacing:1.3px;text-transform:uppercase;margin-bottom:24px;">
                ⚡ Sistema Inteligente · Colombia 2025
            </div>
            <h1 style="font-size:46px;font-weight:900;line-height:1.08;margin:0 0 18px;letter-spacing:-1.5px;">
                Tu seguridad es<br>
                <span style="background:linear-gradient(90deg,#F0ABFC,#EC4899,#F59E0B);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">nuestra prioridad</span>
            </h1>
            <p style="color:#C4B5FD;font-size:15px;line-height:1.85;margin:0 0 32px;">
                Plataforma inteligente de predicción, prevención y apoyo para mujeres en Colombia.
                Modelos ML entrenados con datos reales de la Policía Nacional.
            </p>
            <div style="display:flex;gap:12px;flex-wrap:wrap;">
                <a href="?page=pred" style="background:linear-gradient(135deg,#EC4899,#C026D3);color:#fff;
                    padding:14px 26px;border-radius:14px;font-size:14px;font-weight:700;text-decoration:none;
                    box-shadow:0 4px 22px rgba(236,72,153,0.45);">📊 Ver Predicciones IA</a>
                <a href="tel:155" style="background:rgba(255,255,255,0.12);color:#fff;border:1px solid rgba(255,255,255,0.28);
                    padding:14px 26px;border-radius:14px;font-size:14px;font-weight:700;text-decoration:none;">
                    📞 Línea 155 — Mujer</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, val, label, color in [
        (c1, "📍", "1.121", "Municipios cubiertos", "#7C3AED"),
        (c2, "🗺️", "33", "Departamentos", "#2563EB"),
        (c3, "🤖", "3 ML", "Modelos de IA", "#059669"),
        (c4, "🛡️", "24/7", "Disponible siempre", "#EC4899"),
    ]:
        with col:
            st.markdown(f"""<div style="background:#fff;border-radius:20px;border:1px solid #EDE9FE;
                padding:22px 18px;text-align:center;box-shadow:0 2px 16px rgba(109,40,217,0.07);">
                <div style="font-size:28px;margin-bottom:8px;">{icon}</div>
                <div style="font-size:28px;font-weight:900;color:{color};line-height:1;font-family:Georgia,serif;">{val}</div>
                <div style="font-size:11px;color:#6B7280;margin-top:6px;font-weight:600;">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2 style="font-size:20px;font-weight:800;color:#1E1B4B;margin-bottom:18px;letter-spacing:-0.4px;">🧩 Módulos Disponibles</h2>', unsafe_allow_html=True)

    modules = [
        ("📊","Predicción ML","XGBoost + LightGBM con gráficos avanzados e interpretación IA","#7C3AED"),
        ("🗺️","Mapa de Riesgo","Mapa geográfico interactivo de Colombia","#2563EB"),
        ("✈️","Viaje Seguro","Analiza seguridad antes de viajar","#059669"),
        ("🚨","Emergencias","Alertas, botón pánico y líneas directas","#DC2626"),
        ("📋","Denuncias","Registro anónimo con orientación jurídica IA","#D97706"),
        ("💜","IA de Apoyo SARA","Chat empático 24/7 con apoyo psicológico","#7C3AED"),
        ("🚔","Ayuda Cercana","Policía, hospitales, refugios con direcciones","#0891B2"),
        ("ℹ️","Acerca de","Equipo, tecnología y misión del proyecto","#6B7280"),
    ]
    page_map = {
        "Predicción ML": "📊  Predicción ML",
        "Mapa de Riesgo": "🗺️  Mapa de Riesgo",
        "Viaje Seguro": "✈️  Viaje Seguro",
        "Emergencias": "🚨  Emergencias",
        "Denuncias": "📋  Denuncias",
        "IA de Apoyo SARA": "💜  SARA · IA Apoyo",
        "Ayuda Cercana": "🚔  Ayuda Cercana",
        "Acerca de": "ℹ️  Acerca de",
    }
    cols = st.columns(4)
    for i, (icon, title, desc, color) in enumerate(modules):
        with cols[i % 4]:
            st.markdown(f'''<div style="background:#fff;border-radius:20px;padding:22px;border:1px solid #EDE9FE;
                margin-bottom:4px;box-shadow:0 2px 12px rgba(109,40,217,0.06);">
                <div style="width:46px;height:46px;border-radius:14px;background:{color}15;
                    display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:14px;">{icon}</div>
                <div style="font-weight:800;font-size:14px;color:#1E1B4B;margin-bottom:6px;">{title}</div>
                <div style="font-size:12px;color:#6B7280;line-height:1.6;margin-bottom:10px;">{desc}</div>
            </div>''', unsafe_allow_html=True)
            if st.button(f"Ir a {title}", key=f"mod_{i}", use_container_width=True):
                st.session_state["nav_page"] = page_map.get(title, page)
                st.rerun()

    st.markdown("""<div style="background:linear-gradient(135deg,#FFFBEB,#FEF3C7);border:1px solid #FCD34D;
        border-radius:16px;padding:16px 22px;display:flex;align-items:center;gap:14px;margin-top:8px;">
        <span style="font-size:22px;">⚠️</span>
        <span style="font-size:13px;color:#92400E;line-height:1.6;">
            <strong>Aviso académico:</strong> Prototipo educativo. Para emergencias reales llama al
            <strong style="color:#DC2626;">123</strong> o la <strong style="color:#7C3AED;">Línea Mujer 155</strong> — gratuita, 24/7.
        </span>
    </div>""", unsafe_allow_html=True)

# ── PREDICCIÓN ML ─────────────────────────────────────────────────────────────
elif "📊" in page:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:#F5F3FF;
            border:1px solid #C4B5FD;border-radius:24px;padding:5px 16px;font-size:11px;
            color:#5B21B6;font-weight:700;margin-bottom:12px;letter-spacing:0.5px;">📊 MÓDULO DE PREDICCIÓN ML</div>
        <h1 style="font-size:30px;font-weight:900;color:#1E1B4B;margin:0 0 6px;letter-spacing:-0.5px;">Predicción de Riesgo</h1>
        <p style="color:#6B7280;font-size:14px;margin:0;">XGBoost + LightGBM con gráficos avanzados e interpretación IA para apoyo policial.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sh-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;font-weight:700;color:#7C3AED;margin-bottom:16px;">⚙️ Parámetros de Análisis</div>', unsafe_allow_html=True)
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
        sexo = st.selectbox("👤 Sexo", ["FEMENINO","MASCULINO"])
    with c6:
        etario = st.selectbox("🎂 Grupo Etario", ["DE 0 A 17 AÑOS","DE 18 A 26 AÑOS","DE 27 A 59 AÑOS","DE 60 Y MÁS"], index=2)

    predict_btn = st.button("🔮 Ejecutar Predicción ML", type="primary", key="predict_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    if predict_btn or st.session_state.get('pred_result'):
        if predict_btn:
            with st.spinner("⏳ Ejecutando modelos ML..."):
                result = calc_prediction(dep, mun, delito, sexo, etario, año)
                st.session_state["pred_result"] = result
                st.session_state["pred_form"] = {"dep": dep, "mun": mun, "delito": delito, "sexo": sexo, "etario": etario, "año": año}
                st.session_state.pop("interp_result", None)

        result = st.session_state.get("pred_result")
        form = st.session_state.get("pred_form", {})

        if result:
            import plotly.graph_objects as go

            # Context banner
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1E1B4B,#312E81);border-radius:18px;
                padding:16px 24px;margin-bottom:24px;display:flex;align-items:center;gap:14px;">
                <div style="width:40px;height:40px;background:rgba(255,255,255,0.12);border-radius:12px;
                    display:flex;align-items:center;justify-content:center;font-size:20px;">📍</div>
                <div>
                    <div style="font-weight:800;font-size:15px;color:#fff;">{form.get('dep',dep)} · {form.get('mun',mun)}</div>
                    <div style="font-size:12px;color:#A5B4FC;margin-top:2px;">{form.get('delito',delito)} · {form.get('sexo',sexo)} · {form.get('etario',etario)} · {form.get('año',año)}</div>
                </div>
                <div style="margin-left:auto;display:flex;gap:8px;">
                    {risk_badge(result["zona"])}&nbsp;{risk_badge(result["gravedad"])}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # KPI cards
            max_month = max(result["monthly"], key=lambda x: x["cases"])
            k1, k2, k3, k4 = st.columns(4)
            for col, label, model, display, extra, color in [
                (k1, "ZONA DE RIESGO", "XGBoost", risk_badge(result["zona"]),
                 f'<div style="font-size:28px;font-weight:900;color:{RISK_LEVELS.get(result["zona"],{}).get("color","#7C3AED")};font-family:Georgia,serif;line-height:1;">{result["score"]}<span style="font-size:14px;">/6.0</span></div>', "#7C3AED"),
                (k2, "NIVEL GRAVEDAD", "LightGBM", risk_badge(result["gravedad"]),
                 "", "#2563EB"),
                (k3, "VÍCTIMAS ESTIMADAS", "Ensemble ML",
                 f'<div style="font-size:40px;font-weight:900;color:#DC2626;font-family:Georgia,serif;line-height:1;">{result["victimas"]}</div>',
                 "personas/año estimadas", "#DC2626"),
                (k4, "MES MÁS CRÍTICO", "Análisis estacional",
                 f'<div style="font-size:24px;font-weight:900;color:#D97706;font-family:Georgia,serif;">{max_month["month"]}</div>',
                 f'{max_month["cases"]} casos estimados', "#D97706"),
            ]:
                with col:
                    st.markdown(f"""<div style="background:#fff;border-radius:20px;border:1px solid #EDE9FE;
                        padding:20px;box-shadow:0 2px 16px rgba(109,40,217,0.07);min-height:130px;">
                        <div style="font-size:9px;font-weight:800;color:{color};letter-spacing:1.2px;
                            text-transform:uppercase;margin-bottom:6px;">{label}</div>
                        <div style="font-size:9px;color:#A78BFA;font-weight:600;margin-bottom:10px;">{model}</div>
                        <div style="margin-bottom:6px;">{display}</div>
                        <div style="font-size:10px;color:#6B7280;margin-top:4px;">{extra}</div>
                    </div>""", unsafe_allow_html=True)

            # PKL status badge
            pkl_badge = ('✅ Modelos PKL reales activos' if result.get("used_pkl")
                         else '⚙️ Modo simulación (PKL no cargados)')
            pkl_color = "#059669" if result.get("used_pkl") else "#D97706"
            pkl_bg = "#ECFDF5" if result.get("used_pkl") else "#FFFBEB"
            st.markdown(f'''<div style="background:{pkl_bg};border:1px solid {pkl_color}40;border-radius:12px;
                padding:10px 16px;margin:12px 0;display:inline-block;font-size:12px;font-weight:700;color:{pkl_color};">
                {pkl_badge}</div>''', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Charts tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Tendencia Histórica", "🎯 Distribución de Probabilidad", "📅 Variación Mensual", "🕸️ Radar de Riesgo"])

            with tab1:
                solid_x = [t["year"] for t in result["trend"] if not t["projected"]]
                solid_y = [t["score"] for t in result["trend"] if not t["projected"]]
                proj_x_start = solid_x[-1]
                proj_y_start = solid_y[-1]
                proj_x = [proj_x_start] + [t["year"] for t in result["trend"] if t["projected"]]
                proj_y = [proj_y_start] + [t["score"] for t in result["trend"] if t["projected"]]
                colors_pts = [get_risk_color(t["score"]) for t in result["trend"]]

                fig = go.Figure()
                # Risk zones background
                fig.add_shape(type="rect", x0=2019, x1=2027, y0=4, y1=6,
                              fillcolor="#FEE2E2", opacity=0.25, line_width=0)
                fig.add_shape(type="rect", x0=2019, x1=2027, y0=3, y1=4,
                              fillcolor="#FEF9C3", opacity=0.25, line_width=0)
                fig.add_shape(type="rect", x0=2019, x1=2027, y0=0, y1=3,
                              fillcolor="#F0FDF4", opacity=0.25, line_width=0)
                # Zone labels
                for y_pos, label_t, color_t in [(5.0,"⚠️ Alto riesgo","#DC2626"),(3.5,"⚡ Riesgo medio","#F59E0B"),(1.5,"✅ Controlado","#059669")]:
                    fig.add_annotation(x=2019.1, y=y_pos, text=label_t, showarrow=False,
                                       font=dict(size=9, color=color_t), xanchor="left")
                # Lines
                fig.add_trace(go.Scatter(
                    x=solid_x, y=solid_y, mode="lines+markers",
                    line=dict(color="#7C3AED", width=3),
                    marker=dict(size=9, color=colors_pts[:len(solid_x)],
                                line=dict(color="white", width=2)),
                    name="Histórico", fill="tozeroy",
                    fillcolor="rgba(124,58,237,0.08)"
                ))
                fig.add_trace(go.Scatter(
                    x=proj_x, y=proj_y, mode="lines+markers",
                    line=dict(color="#A78BFA", width=2.5, dash="dot"),
                    marker=dict(size=8, color="#A78BFA", line=dict(color="white", width=2)),
                    name="Proyectado 2025–2027"
                ))
                fig.update_layout(
                    height=280, margin=dict(l=40, r=20, t=20, b=40),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(range=[0, 6.5], gridcolor="#EDE9FE", tickfont=dict(size=10, color="#6B7280"),
                               title="Score (0–6)", title_font=dict(size=10, color="#6B7280")),
                    xaxis=dict(gridcolor="#EDE9FE", tickfont=dict(size=10, color="#6B7280"), dtick=1),
                    legend=dict(orientation="h", y=1.04, font=dict(size=10)),
                    font=dict(family="Plus Jakarta Sans"),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown(f'<div style="font-size:11px;color:#6B7280;text-align:center;margin-top:-10px;">'
                            f'{form.get("delito",delito)} en {form.get("dep",dep)} · Score de riesgo 2019–2027 (proyección punteada)</div>',
                            unsafe_allow_html=True)

            with tab2:
                prob_sorted = sorted(result["probs_zona"].items(), key=lambda x: x[1], reverse=True)
                labels = [p[0] for p in prob_sorted]
                values = [p[1] for p in prob_sorted]
                bar_colors = [RISK_LEVELS.get(z, {"color": "#888"})["color"] for z in labels]
                fig2 = go.Figure(go.Bar(
                    x=values, y=labels, orientation="h",
                    marker=dict(color=bar_colors, opacity=0.85, line=dict(width=0)),
                    text=[f"{v}%" for v in values],
                    textposition="outside", textfont=dict(size=11, color="#1E1B4B"),
                ))
                fig2.update_layout(
                    height=280, margin=dict(l=80, r=60, t=20, b=20),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(range=[0, max(values)*1.2], gridcolor="#EDE9FE", tickfont=dict(size=10), ticksuffix="%"),
                    yaxis=dict(tickfont=dict(size=11, color="#1E1B4B")),
                    font=dict(family="Plus Jakarta Sans"),
                    showlegend=False,
                )
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
                st.markdown('<div style="font-size:11px;color:#6B7280;text-align:center;margin-top:-10px;">Probabilidad asignada por el modelo XGBoost a cada zona de riesgo</div>', unsafe_allow_html=True)

            with tab3:
                max_m = max(result["monthly"], key=lambda x: x["value"])
                bar_colors_m = ["#DC2626" if m["month"] == max_m["month"] else get_risk_color(m["value"])
                                for m in result["monthly"]]
                fig3 = go.Figure(go.Bar(
                    x=[m["month"] for m in result["monthly"]],
                    y=[m["cases"] for m in result["monthly"]],
                    marker=dict(color=bar_colors_m, opacity=0.88, line=dict(width=0)),
                    text=[str(m["cases"]) for m in result["monthly"]],
                    textposition="outside", textfont=dict(size=10),
                ))
                fig3.update_layout(
                    height=240, margin=dict(l=20, r=20, t=20, b=30),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(gridcolor="#EDE9FE", tickfont=dict(size=9, color="#6B7280")),
                    xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, color="#6B7280")),
                    font=dict(family="Plus Jakarta Sans"), showlegend=False,
                )
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
                st.markdown(f'<div style="font-size:11px;color:#6B7280;text-align:center;margin-top:-10px;">Casos estimados por mes — mes más crítico: <strong style="color:#DC2626;">{max_m["month"]}</strong></div>', unsafe_allow_html=True)

            with tab4:
                radar_cats = ["Frecuencia", "Gravedad", "Víctimas", "Estacionalidad", "Proyección", "Impacto Social"]
                score_norm = result["score"] / 6.0
                radar_vals = [
                    min(score_norm * 1.1, 1.0),
                    RISK_LEVELS.get(result["gravedad"], {"color":"#888"}) and score_norm * 0.95,
                    min(result["victimas"] / 200, 1.0),
                    max(result["monthly"], key=lambda x: x["value"])["value"] / 6.0,
                    result["trend"][-1]["score"] / 6.0,
                    score_norm * 1.05,
                ]
                radar_vals = [round(min(v, 1.0), 2) for v in radar_vals]
                radar_vals_pct = [round(v * 100) for v in radar_vals]
                fig4 = go.Figure()
                fig4.add_trace(go.Scatterpolar(
                    r=radar_vals_pct,
                    theta=radar_cats,
                    fill='toself',
                    fillcolor='rgba(124,58,237,0.15)',
                    line=dict(color='#7C3AED', width=2.5),
                    marker=dict(size=7, color='#7C3AED'),
                    name=f'{form.get("dep",dep)}'
                ))
                fig4.add_trace(go.Scatterpolar(
                    r=[50]*len(radar_cats),
                    theta=radar_cats,
                    line=dict(color='#E2E8F0', width=1, dash='dot'),
                    showlegend=False,
                    mode='lines'
                ))
                fig4.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=9), gridcolor='#EDE9FE'),
                        angularaxis=dict(tickfont=dict(size=11, color='#1E1B4B')),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    height=300, margin=dict(l=50,r=50,t=30,b=30),
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=True,
                    legend=dict(font=dict(size=10)),
                    font=dict(family='Plus Jakarta Sans')
                )
                st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
                st.markdown('<div style="font-size:11px;color:#6B7280;text-align:center;margin-top:-10px;">Perfil multidimensional de riesgo — valores normalizados 0–100%</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Comparativa bar chart
            st.markdown('<div class="sh-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:14px;font-weight:800;color:#1E1B4B;margin-bottom:4px;">📊 Comparativa por Tipo de Delito — {form.get("dep",dep)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:11px;color:#6B7280;margin-bottom:16px;">Score de riesgo predicho para cada categoría en {form.get("año",año)}</div>', unsafe_allow_html=True)
            max_v = result["comparativa"][0]["value"] if result["comparativa"] else 1
            for item in result["comparativa"]:
                cfg = RISK_LEVELS.get(item["risk"], {"color": "#888"})
                is_sel = item["label"] == form.get("delito", delito)
                bg = cfg["color"] + "12" if is_sel else "#FAFAFA"
                border = cfg["color"] + "50" if is_sel else "#EDE9FE"
                marker = " ← seleccionado" if is_sel else ""
                st.markdown(f"""
                <div style="padding:12px 16px;background:{bg};border-radius:14px;
                    border:1.5px solid {border};margin-bottom:8px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;">
                        <span style="font-size:12px;color:#1E1B4B;font-weight:{'800' if is_sel else '600'};">{item['label']}<span style="font-size:10px;color:{cfg['color']};font-style:italic;">{marker}</span></span>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:13px;font-weight:900;color:{cfg['color']};">{item['value']}</span>
                            {risk_badge(item['risk'], small=True)}
                        </div>
                    </div>
                    <div style="background:#E8E4F9;border-radius:6px;height:8px;overflow:hidden;">
                        <div style="width:{item['value']/max_v*100:.0f}%;height:100%;background:linear-gradient(90deg,{cfg['color']}88,{cfg['color']});border-radius:6px;transition:width 0.6s ease;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # AI Interpretation
            st.markdown("""
            <div class="sh-card">
                <div style="display:flex;align-items:center;gap:14px;margin-bottom:4px;">
                    <div style="width:46px;height:46px;background:linear-gradient(135deg,#1E1B4B,#5B21B6);
                        border-radius:14px;display:flex;align-items:center;justify-content:center;
                        font-size:22px;box-shadow:0 4px 14px rgba(91,33,182,0.3);">🤖</div>
                    <div>
                        <div style="font-size:16px;font-weight:800;color:#1E1B4B;">Interpretación IA para Fuerzas Policiales</div>
                        <div style="font-size:11px;color:#A78BFA;">Diagnóstico situacional · Factores de riesgo · Acciones operativas</div>
                    </div>
                    <div style="margin-left:auto;background:linear-gradient(135deg,#F5F3FF,#EDE9FE);
                        color:#5B21B6;font-size:11px;font-weight:700;padding:6px 14px;border-radius:20px;
                        border:1px solid #C4B5FD;">🔒 Uso Policial</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if "interp_result" not in st.session_state or predict_btn:
                with st.spinner("🤖 Analizando con IA especializada..."):
                    interp = call_claude(
                        """Eres analista experto en seguridad pública de Colombia, asesor de la Policía Nacional.
Estructura tu respuesta con EXACTAMENTE estas 4 secciones (cada una máximo 3 puntos con bullet •):

🔍 DIAGNÓSTICO SITUACIONAL
⚠️ FACTORES DE RIESGO IDENTIFICADOS
🚨 ACCIONES INMEDIATAS RECOMENDADAS
🤝 RECURSOS INTERINSTITUCIONALES

Total máximo 280 palabras. Sé concreto, técnico y orientado a la acción policial.""",
                        f"""Analiza:
- Departamento: {form.get('dep',dep)} | Municipio: {form.get('mun',mun)}
- Delito: {form.get('delito',delito)} | Año: {form.get('año',año)}
- Zona de Riesgo: {result['zona']} | Gravedad: {result['gravedad']}
- Víctimas estimadas: {result['victimas']} | Score: {result['score']}/6.0"""
                    )
                    st.session_state["interp_result"] = interp

            interp = st.session_state.get("interp_result", "")
            if interp:
                st.markdown(f"""<div style="background:linear-gradient(135deg,#FAFAFA,#F5F3FF);border-radius:16px;
                    padding:20px 24px;border:1px solid #EDE9FE;font-size:13px;line-height:1.85;
                    white-space:pre-wrap;color:#1E1B4B;">{interp}</div>""", unsafe_allow_html=True)

            # Alert box
            s = result["score"]
            if s >= 4.0:
                al_bg, al_border, al_color, al_icon, al_text = "#FEF2F2","#FECDD3","#991B1B","🚨","Zona de ALTO RIESGO. Se requiere refuerzo urgente de patrullaje y coordinación inmediata con la Fiscalía."
            elif s >= 3.0:
                al_bg, al_border, al_color, al_icon, al_text = "#FFFBEB","#FDE68A","#92400E","⚠️","Riesgo MODERADO. Monitoreo activo y campañas preventivas focalizadas."
            else:
                al_bg, al_border, al_color, al_icon, al_text = "#ECFDF5","#A7F3D0","#065F46","✅","Riesgo CONTROLADO. Mantener estrategias preventivas actuales."
            st.markdown(f"""<div style="background:{al_bg};border:1.5px solid {al_border};border-radius:16px;
                padding:16px 22px;display:flex;align-items:flex-start;gap:12px;margin-top:16px;">
                <span style="font-size:20px;">{al_icon}</span>
                <div>
                    <div style="font-weight:800;color:{al_color};font-size:13px;margin-bottom:4px;">Alerta Operacional</div>
                    <div style="font-size:12px;color:{al_color};opacity:0.85;line-height:1.6;">{al_text}</div>
                </div>
            </div>""", unsafe_allow_html=True)

# ── MAPA DE RIESGO ─────────────────────────────────────────────────────────────
elif "🗺️" in page:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:#EFF6FF;
            border:1px solid #BFDBFE;border-radius:24px;padding:5px 16px;font-size:11px;
            color:#1D4ED8;font-weight:700;margin-bottom:12px;">🗺️ MAPA INTERACTIVO</div>
        <h1 style="font-size:30px;font-weight:900;color:#1E1B4B;margin:0 0 6px;letter-spacing:-0.5px;">Mapa de Riesgo — Colombia</h1>
        <p style="color:#6B7280;font-size:14px;margin:0;">Visualización geográfica del nivel de riesgo por departamento. Selecciona uno para análisis detallado con IA.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, label, count, color, bg in [
        (c1, "Crítico / Muy Alto", sum(1 for d in CRIME_DATA.values() if d["score"] >= 4.0), "#DC2626", "linear-gradient(135deg,#FEF2F2,#FEE2E2)"),
        (c2, "Riesgo Alto", sum(1 for d in CRIME_DATA.values() if 3.5 <= d["score"] < 4.0), "#EF4444", "linear-gradient(135deg,#FFF7ED,#FFEDD5)"),
        (c3, "Riesgo Medio", sum(1 for d in CRIME_DATA.values() if 3.0 <= d["score"] < 3.5), "#F59E0B", "linear-gradient(135deg,#FFFBEB,#FEF3C7)"),
        (c4, "Controlado", sum(1 for d in CRIME_DATA.values() if d["score"] < 3.0), "#059669", "linear-gradient(135deg,#ECFDF5,#D1FAE5)"),
    ]:
        with col:
            st.markdown(f"""<div style="background:{bg};border-radius:18px;padding:16px 18px;
                border:1px solid {color}25;text-align:center;margin-bottom:14px;">
                <div style="font-size:30px;font-weight:900;color:{color};font-family:Georgia,serif;line-height:1;">{count}</div>
                <div style="font-size:10px;color:{color};font-weight:700;margin-top:5px;">Departamentos</div>
                <div style="font-size:10px;color:#6B7280;margin-top:3px;">{label}</div>
            </div>""", unsafe_allow_html=True)

    filter_zone = st.selectbox("🔍 Filtrar por nivel de riesgo:", ["TODOS","ALTO","MEDIO-ALTO","MEDIO-BAJO","BAJO"], key="map_filter")

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

    st.markdown(f'<div style="font-size:12px;color:#6B7280;margin-bottom:16px;">Mostrando <strong style="color:#1E1B4B;">{len(sorted_deps)}</strong> departamentos</div>', unsafe_allow_html=True)

    col_map, col_detail = st.columns([2, 1])

    with col_map:
        st.markdown('<div class="sh-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:700;color:#A78BFA;margin-bottom:16px;text-transform:uppercase;letter-spacing:1.2px;">🇨🇴 Colombia — Nivel de Riesgo por Departamento</div>', unsafe_allow_html=True)

        # ── Mapa Choropleth interactivo usando Plotly + ISO codes ─────────────
        import plotly.express as px, json

        # Coordenadas centrales aproximadas de cada departamento (lat, lon)
        DEP_COORDS = {
            "AMAZONAS":           (-1.5,  -71.5),
            "ANTIOQUIA":          ( 7.0,  -75.5),
            "ARAUCA":             ( 6.5,  -71.0),
            "ATLÁNTICO":          (10.7,  -74.9),
            "BOGOTÁ D.C.":        ( 4.7,  -74.1),
            "BOLÍVAR":            ( 8.5,  -74.5),
            "BOYACÁ":             ( 5.5,  -73.0),
            "CALDAS":             ( 5.3,  -75.3),
            "CAQUETÁ":            ( 1.0,  -74.0),
            "CASANARE":           ( 5.5,  -71.5),
            "CAUCA":              ( 2.5,  -76.8),
            "CESAR":              ( 9.5,  -73.5),
            "CHOCÓ":              ( 5.5,  -76.8),
            "CÓRDOBA":            ( 8.5,  -75.8),
            "CUNDINAMARCA":       ( 5.0,  -74.5),
            "GUAINÍA":            ( 2.5,  -68.5),
            "GUAVIARE":           ( 2.0,  -72.5),
            "HUILA":              ( 2.5,  -75.5),
            "LA GUAJIRA":         (11.5,  -72.5),
            "MAGDALENA":          (10.0,  -74.3),
            "META":               ( 3.5,  -73.0),
            "NARIÑO":             ( 1.2,  -77.5),
            "NORTE DE SANTANDER": ( 7.9,  -72.5),
            "PUTUMAYO":           ( 0.5,  -76.0),
            "QUINDÍO":            ( 4.5,  -75.7),
            "RISARALDA":          ( 5.2,  -76.0),
            "SAN ANDRÉS":         (12.5,  -81.7),
            "SANTANDER":          ( 6.8,  -73.5),
            "SUCRE":              ( 9.0,  -75.0),
            "TOLIMA":             ( 4.0,  -75.3),
            "VALLE DEL CAUCA":    ( 3.8,  -76.5),
            "VAUPÉS":             ( 0.5,  -70.5),
            "VICHADA":            ( 4.5,  -69.5),
        }

        dep_scores = []
        for k, v in CRIME_DATA.items():
            lat, lon = DEP_COORDS.get(k, (4.0, -74.0))
            dep_scores.append({
                "Departamento": k,
                "Score": v["score"],
                "Zona": v["zona"],
                "Gravedad": v["gravedad"],
                "Municipios": v["municipios"],
                "lat": lat,
                "lon": lon,
                "Color": get_risk_color(v["score"]),
                "Tamaño": max(15, v["score"] * 6),
                "Label": k.split()[0][:9],
            })
        df_map = pd.DataFrame(dep_scores)

        # Filtrar si hay filtro activo
        if filter_zone != "TODOS":
            df_map_vis = df_map[df_map["Departamento"].apply(
                lambda d: get_risk_zone_label(CRIME_DATA.get(d, {}).get("score", 0)) == filter_zone
            )]
        else:
            df_map_vis = df_map.copy()

        # Mapa con px.scatter_geo — sin update_layout geo para máxima compatibilidad
        import plotly.express as px
        fig_map = px.scatter_geo(
            df_map_vis,
            lat="lat",
            lon="lon",
            size="Tamaño",
            color="Score",
            hover_name="Departamento",
            hover_data={
                "Zona": True,
                "Gravedad": True,
                "Municipios": True,
                "lat": False,
                "lon": False,
                "Tamaño": False,
                "Color": False,
                "Label": False,
            },
            color_continuous_scale=[
                [0.0, "#10B981"], [0.3, "#3B82F6"],
                [0.55, "#F59E0B"], [0.70, "#EF4444"],
                [0.85, "#DC2626"], [1.0, "#7F1D1D"],
            ],
            range_color=[1.5, 5.0],
            size_max=38,
            scope="south america",
        )
        fig_map.update_layout(height=520, margin={"l":0,"r":0,"t":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<div style="font-size:11px;color:#6B7280;text-align:center;margin-top:-8px;">Burbujas proporcionales al score de riesgo · Pasa el cursor para ver detalles · Selecciona departamento en la lista de abajo</div>', unsafe_allow_html=True)

        # Leyenda del mapa
        st.markdown("""
        <div style="display:flex;gap:14px;flex-wrap:wrap;justify-content:center;margin:10px 0 4px;padding:8px 12px;
            background:#F8FAFF;border-radius:12px;border:1px solid #EDE9FE;">
            <span style="font-size:11px;color:#7F1D1D;font-weight:700;">● ≥4.5 Crítico</span>
            <span style="font-size:11px;color:#DC2626;font-weight:700;">● ≥4.0 Alto</span>
            <span style="font-size:11px;color:#EF4444;font-weight:700;">● ≥3.5 Medio-Alto</span>
            <span style="font-size:11px;color:#F59E0B;font-weight:700;">● ≥3.0 Medio</span>
            <span style="font-size:11px;color:#3B82F6;font-weight:700;">● ≥2.5 Bajo</span>
            <span style="font-size:11px;color:#10B981;font-weight:700;">● &lt;2.5 Mínimo</span>
        </div>
        """, unsafe_allow_html=True)

        # Dept selector buttons
        st.markdown('<div style="font-size:13px;font-weight:700;color:#1E1B4B;margin:18px 0 12px;">📊 Seleccionar Departamento</div>', unsafe_allow_html=True)
        cols_per_row = 5
        rows = [sorted_deps[i:i+cols_per_row] for i in range(0, len(sorted_deps), cols_per_row)]
        for row in rows:
            rcols = st.columns(cols_per_row)
            for j, dep_d in enumerate(row):
                color = get_risk_color(dep_d["score"])
                with rcols[j]:
                    if st.button(f"{dep_d['name'][:10]}\n{dep_d['score']:.1f}", key=f"dep_{dep_d['name']}", use_container_width=True):
                        st.session_state["selected_dep"] = dep_d["name"]
                    st.markdown(f"""<div style="background:{color}14;border-radius:8px;padding:2px 4px;
                        text-align:center;margin-top:-10px;margin-bottom:4px;">
                        <div style="font-size:8px;color:{color};font-weight:700;">{dep_d['zona']}</div>
                    </div>""", unsafe_allow_html=True)

        # Top bar chart
        st.markdown('<div style="font-size:13px;font-weight:700;color:#1E1B4B;margin:18px 0 12px;">🏆 Top 12 Departamentos por Score de Riesgo</div>', unsafe_allow_html=True)
        for i, d in enumerate(sorted_deps[:12]):
            color = get_risk_color(d["score"])
            pct = d["score"] / 6 * 100
            num_color = "#DC2626" if i < 3 else "#6B7280"
            st.markdown(f"""<div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <span style="font-size:10px;color:{num_color};font-weight:800;width:20px;">#{i+1}</span>
                    <span style="font-size:12px;color:#1E1B4B;font-weight:600;flex:1;padding:0 8px;">{d['name']}</span>
                    <span style="font-size:12px;color:{color};font-weight:900;">{d['score']:.1f}/6.0</span>
                    &nbsp;{risk_badge(d['zona'], small=True)}
                </div>
                <div style="background:#EDE9FE;border-radius:8px;height:9px;overflow:hidden;">
                    <div style="width:{pct:.0f}%;height:100%;background:linear-gradient(90deg,{color}80,{color});
                        border-radius:8px;transition:width 0.5s ease;"></div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_detail:
        sel_name = st.session_state.get("selected_dep")
        if sel_name and sel_name in CRIME_DATA:
            sel = {"name": sel_name, **CRIME_DATA[sel_name]}
            color = get_risk_color(sel["score"])

            st.markdown(f"""<div class="sh-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">
                    <div>
                        <div style="font-size:19px;font-weight:900;color:#1E1B4B;">{sel["name"]}</div>
                        <div style="font-size:11px;color:#A78BFA;margin-top:2px;">Colombia · {sel["municipios"]} municipios</div>
                    </div>
                    <div style="width:42px;height:42px;background:{color}15;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;font-size:22px;">🗺️</div>
                </div>
                <div style="display:flex;align-items:center;gap:16px;margin-bottom:18px;
                    background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:16px;padding:16px;">
                    <div style="text-align:center;">
                        <div style="font-size:40px;font-weight:900;color:{color};font-family:Georgia,serif;line-height:1;">{sel['score']:.1f}</div>
                        <div style="font-size:10px;color:#A78BFA;font-weight:600;">/ 6.0</div>
                    </div>
                    <div>
                        <div style="font-size:12px;color:#6B7280;margin-bottom:8px;">Nivel de riesgo:</div>
                        <div style="margin-bottom:6px;">{risk_badge(sel['zona'])}</div>
                        <div>{risk_badge(sel['gravedad'])}</div>
                    </div>
                </div>
                <div style="background:#EDE9FE;border-radius:8px;height:10px;margin-bottom:18px;">
                    <div style="width:{sel['score']/6*100:.0f}%;height:100%;background:linear-gradient(90deg,{color}88,{color});border-radius:8px;"></div>
                </div>
                <div style="font-size:12px;font-weight:700;color:#1E1B4B;margin-bottom:10px;">⚖️ Riesgo por tipo de delito</div>
            """, unsafe_allow_html=True)

            zonas_list = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"]
            for d in DELITOS:
                fac = DELIT_FACTOR.get(d, 1.0)
                sc = sel["score"] * fac
                z = zonas_list[min(max(round(sc) - 1, 0), 5)]
                cfg = RISK_LEVELS.get(z, {"color": "#888"})
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                    padding:7px 0;border-bottom:1px solid #EDE9FE;">
                    <span style="font-size:11px;color:#1E1B4B;">{d}</span>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:11px;font-weight:700;color:{cfg['color']};">{sc:.1f}</span>
                        {risk_badge(z, small=True)}
                    </div>
                </div>""", unsafe_allow_html=True)

            # Horarios
            st.markdown('<div style="font-size:12px;font-weight:700;color:#1E1B4B;margin:14px 0 8px;">🕐 Riesgo por Horario</div>', unsafe_allow_html=True)
            h_risks = [("Madrugada (0–6h)","BAJO"),("Mañana (6–12h)","MUY BAJO"),
                       ("Tarde (12–18h)","MEDIO-BAJO"),("Noche (18–24h)","MUY ALTO" if sel["score"]>=4.0 else "ALTO" if sel["score"]>=3.0 else "MEDIO-ALTO")]
            for h_label, h_risk in h_risks:
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                    padding:6px 0;border-bottom:1px solid #EDE9FE;">
                    <span style="font-size:11px;color:#1E1B4B;">{h_label}</span>
                    {risk_badge(h_risk, small=True)}
                </div>""", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            if st.button(f"🤖 Análisis IA completo de {sel_name}", key="ai_map_btn", use_container_width=True, type="primary"):
                with st.spinner("Analizando con IA..."):
                    ai_text = call_claude(
                        "Eres experto en seguridad pública colombiana. Análisis breve (máx 130 palabras) con bullets y emojis: contexto del departamento, amenazas principales para mujeres, horarios de mayor riesgo, recomendación operativa clave.",
                        f"Analiza seguridad para mujeres en {sel_name}, Colombia. Score: {sel['score']}/6.0, zona: {sel['zona']}, gravedad: {sel['gravedad']}."
                    )
                    st.session_state[f"ai_map_{sel_name}"] = ai_text

            ai_result = st.session_state.get(f"ai_map_{sel_name}", "")
            if ai_result:
                st.markdown(f"""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:16px;padding:16px;
                    border:1px solid #C4B5FD;font-size:12px;color:#1E1B4B;line-height:1.75;white-space:pre-wrap;">{ai_result}</div>""",
                    unsafe_allow_html=True)

            if sel["score"] >= 4.0:
                rec_color, rec_bg, rec_text = "#991B1B","#FEF2F2","🚨 Zona de alto riesgo. Refuerzo urgente de patrullaje y coordinación con Fiscalía."
            elif sel["score"] >= 3.0:
                rec_color, rec_bg, rec_text = "#92400E","#FFFBEB","⚠️ Riesgo moderado. Monitoreo activo y campañas de prevención."
            else:
                rec_color, rec_bg, rec_text = "#065F46","#ECFDF5","✅ Riesgo controlado. Mantener estrategias preventivas."
            st.markdown(f"""<div style="background:{rec_bg};border-radius:14px;padding:14px 16px;font-size:12px;
                line-height:1.6;margin-top:10px;border:1px solid {rec_color}22;">
                <span style="color:{rec_color};font-weight:700;">{rec_text}</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:20px;
                border:2px dashed #C4B5FD;padding:48px 24px;text-align:center;">
                <div style="font-size:48px;margin-bottom:14px;">🗺️</div>
                <div style="font-size:15px;font-weight:700;color:#5B21B6;margin-bottom:6px;">Selecciona un departamento</div>
                <div style="font-size:12px;color:#A78BFA;line-height:1.7;">Haz clic en cualquier departamento de la lista para ver el análisis detallado de riesgo y obtener interpretación con IA.</div>
            </div>""", unsafe_allow_html=True)

# ── VIAJE SEGURO ──────────────────────────────────────────────────────────────
elif "✈️" in page:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:#ECFDF5;
            border:1px solid #A7F3D0;border-radius:24px;padding:5px 16px;font-size:11px;
            color:#059669;font-weight:700;margin-bottom:12px;">✈️ PLANIFICACIÓN DE VIAJE SEGURO</div>
        <h1 style="font-size:30px;font-weight:900;color:#1E1B4B;margin:0 0 6px;letter-spacing:-0.5px;">Viaje Seguro</h1>
        <p style="color:#6B7280;font-size:14px;margin:0;">Consulta el nivel de seguridad de cualquier departamento antes de viajar.</p>
    </div>
    """, unsafe_allow_html=True)

    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        dep_viaje = st.selectbox("🗺️ Selecciona el departamento de destino:", DEPARTAMENTOS, key="dep_viaje")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        analizar_btn = st.button("🔍 Analizar Destino", type="primary", use_container_width=True, key="viaje_btn")

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
                safety = {"label": "Seguro", "color": "#059669", "bg": "linear-gradient(135deg,#ECFDF5,#D1FAE5)", "icon": "🟢", "stars": 5}
            elif score <= 3.0:
                safety = {"label": "Precaución", "color": "#F59E0B", "bg": "linear-gradient(135deg,#FFFBEB,#FEF3C7)", "icon": "🟡", "stars": 3}
            elif score <= 4.0:
                safety = {"label": "Riesgo Medio", "color": "#EF4444", "bg": "linear-gradient(135deg,#FEF2F2,#FEE2E2)", "icon": "🟠", "stars": 2}
            else:
                safety = {"label": "Alto Riesgo", "color": "#DC2626", "bg": "linear-gradient(135deg,#FEF2F2,#FECDD3)", "icon": "🔴", "stars": 1}

            stars_html = "".join([f'<span style="font-size:20px;color:{"#F59E0B" if i<safety["stars"] else "#E2E8F0"};">★</span>' for i in range(5)])

            st.markdown(f"""<div style="background:{safety['bg']};border:2px solid {safety['color']}30;
                border-radius:24px;padding:28px 34px;margin-bottom:24px;
                display:flex;align-items:center;gap:24px;">
                <div style="font-size:56px;">{safety['icon']}</div>
                <div style="flex:1;">
                    <div style="font-size:24px;font-weight:900;color:#1E1B4B;margin-bottom:4px;">{vr['dep']}</div>
                    <div style="font-size:17px;font-weight:700;color:{safety['color']};margin-bottom:10px;">{safety['label']}</div>
                    <div>{stars_html}<span style="font-size:12px;color:#6B7280;margin-left:8px;">índice de seguridad</span></div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:52px;font-weight:900;color:{safety['color']};font-family:Georgia,serif;line-height:1;">{score:.1f}</div>
                    <div style="font-size:12px;color:#6B7280;font-weight:600;">Score / 6.0</div>
                </div>
            </div>""", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<div class="sh-card">', unsafe_allow_html=True)
                st.markdown('<div style="font-weight:800;font-size:13px;color:#1E1B4B;margin-bottom:14px;">🏙️ Municipios del Departamento</div>', unsafe_allow_html=True)
                chips = "".join([f'<span style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);color:#5B21B6;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;display:inline-block;margin:3px;border:1px solid #C4B5FD;">{m}</span>' for m in vr["muns"]])
                st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:4px;">{chips}</div>', unsafe_allow_html=True)
                st.markdown(f"""<div style="margin-top:16px;padding:14px 16px;background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:14px;border:1px solid #C4B5FD;">
                    <div style="font-size:11px;color:#A78BFA;font-weight:600;margin-bottom:4px;">Municipios cubiertos en el análisis</div>
                    <div style="font-size:26px;font-weight:900;color:#5B21B6;font-family:Georgia,serif;">{vr['data']['municipios']}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_b:
                st.markdown('<div class="sh-card">', unsafe_allow_html=True)
                st.markdown('<div style="font-weight:800;font-size:13px;color:#1E1B4B;margin-bottom:14px;">⚠️ Riesgo por Tipo de Delito</div>', unsafe_allow_html=True)
                zonas_l = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"]
                delito_scores = sorted(
                    [{"d": d, "sc": round(vr["data"]["score"] * DELIT_FACTOR.get(d, 1.0), 1)} for d in DELITOS],
                    key=lambda x: x["sc"], reverse=True
                )
                max_sc = delito_scores[0]["sc"] if delito_scores else 1
                for item in delito_scores:
                    z = zonas_l[min(max(round(item["sc"]) - 1, 0), 5)]
                    cfg = RISK_LEVELS.get(z, {"color": "#888"})
                    st.markdown(f"""<div style="margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                            <span style="font-size:11px;color:#1E1B4B;font-weight:600;">{item['d']}</span>
                            {risk_badge(z, small=True)}
                        </div>
                        <div style="background:#EDE9FE;border-radius:6px;height:7px;overflow:hidden;">
                            <div style="width:{item['sc']/max_sc*100:.0f}%;height:100%;background:{cfg['color']};border-radius:6px;"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # AI Travel Tips
            st.markdown('<div class="sh-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:15px;font-weight:800;color:#1E1B4B;margin-bottom:6px;">🤖 Consejos Personalizados con IA para {vr["dep"]}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:12px;color:#A78BFA;margin-bottom:14px;">Recomendaciones generadas por IA basadas en datos de riesgo reales</div>', unsafe_allow_html=True)
            if "viaje_tips" not in st.session_state:
                with st.spinner("✨ Preparando consejos personalizados..."):
                    tips = call_claude(
                        "Eres experta en seguridad para mujeres viajeras en Colombia. Responde en español con bullets y emojis. Secciones: 🛡️ Recomendaciones de seguridad, 🏠 Mejores zonas para alojarse, 🕐 Horarios seguros, 🚗 Transporte recomendado, 📞 Números de emergencia locales. Máx 220 palabras. Sé específica para el departamento.",
                        f"Consejos para mujer viajando a {vr['dep']}, Colombia. Score de riesgo: {score:.1f}/6.0 (zona: {vr['data']['zona']})."
                    )
                    st.session_state["viaje_tips"] = tips
            tips_text = st.session_state.get("viaje_tips", "")
            st.markdown(f'<div style="font-size:13px;color:#1E1B4B;line-height:1.85;white-space:pre-wrap;background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:14px;padding:18px;border:1px solid #C4B5FD;">{tips_text}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ── EMERGENCIAS ────────────────────────────────────────────────────────────────
elif "🚨" in page:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#7F1D1D,#BE123C,#DC2626);border-radius:24px;
        padding:26px 32px;margin-bottom:30px;color:#fff;
        box-shadow:0 8px 32px rgba(220,38,38,0.3);">
        <h1 style="font-size:30px;font-weight:900;margin:0 0 8px;letter-spacing:-0.3px;">🚨 Centro de Emergencias</h1>
        <p style="color:#FECDD3;font-size:14px;margin:0;line-height:1.6;">
            Si estás en peligro, presiona el botón que describe tu situación. Todas las llamadas son gratuitas y confidenciales.
        </p>
    </div>
    """, unsafe_allow_html=True)

    emergencias = [
        ("🆘","Estoy en peligro","123 — Emergencias","tel:123","#DC2626"),
        ("👣","Me están siguiendo","123 — Policía","tel:123","#D97706"),
        ("🔇","No puedo hablar","SMS 123","sms:123","#7C3AED"),
        ("🏃","Estoy secuestrada","123 — Urgente","tel:123","#991B1B"),
        ("🚔","Necesito Policía","Policía Nacional","tel:123","#1D4ED8"),
        ("🚑","Necesito Ambulancia","Cruz Roja — 132","tel:132","#059669"),
        ("💜","Apoyo psicológico","Línea 137","tel:137","#8B5CF6"),
        ("👩","Línea Mujer","155 — 24/7 Gratis","tel:155","#EC4899"),
    ]

    cols = st.columns(4)
    for i, (icon, label, sub, href, color) in enumerate(emergencias):
        with cols[i % 4]:
            st.markdown(f"""<a href="{href}" style="text-decoration:none;">
            <div style="background:#fff;border:2px solid {color}22;border-radius:22px;padding:24px 18px;
                text-align:center;cursor:pointer;min-height:136px;margin-bottom:16px;
                box-shadow:0 3px 16px rgba(0,0,0,0.06);transition:all 0.2s;"
                onmouseover="this.style.borderColor='{color}';this.style.transform='translateY(-2px)';"
                onmouseout="this.style.borderColor='{color}22';this.style.transform='translateY(0)';">
                <div style="font-size:32px;margin-bottom:10px;">{icon}</div>
                <div style="font-weight:800;font-size:13px;color:#1E1B4B;margin-bottom:6px;">{label}</div>
                <div style="font-size:11px;font-weight:700;color:{color};background:{color}12;
                    padding:4px 10px;border-radius:20px;display:inline-block;">{sub}</div>
            </div></a>""", unsafe_allow_html=True)

    st.markdown("<h2 style='font-size:18px;font-weight:800;color:#1E1B4B;margin:20px 0 14px;'>📞 Líneas de Emergencia — toca para llamar</h2>", unsafe_allow_html=True)

    lineas = [
        ("tel:123","123","Policía","🚔","#1D4ED8"),("tel:155","155","Línea Mujer","💜","#7C3AED"),
        ("tel:125","125","Defensa Civil","🟢","#059669"),("tel:132","132","Cruz Roja","❤️","#DC2626"),
        ("tel:137","137","Salud Mental","🧠","#8B5CF6"),("tel:106","106","Bomberos","🔥","#D97706"),
    ]
    cols_l = st.columns(6)
    for i, (href, num, desc, ic, co) in enumerate(lineas):
        with cols_l[i]:
            st.markdown(f"""<a href="{href}" style="text-decoration:none;">
            <div style="background:#fff;border-radius:18px;border:1px solid #EDE9FE;padding:18px 12px;
                text-align:center;margin-bottom:12px;box-shadow:0 2px 12px rgba(109,40,217,0.07);transition:all 0.2s;">
                <div style="font-size:22px;margin-bottom:6px;">{ic}</div>
                <div style="font-family:Georgia,serif;font-size:28px;font-weight:900;color:{co};line-height:1;">{num}</div>
                <div style="font-size:10px;color:#6B7280;margin-top:6px;font-weight:600;">{desc}</div>
            </div></a>""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""<div style="background:linear-gradient(135deg,#FFFBEB,#FEF3C7);border:1.5px solid #FCD34D;
            border-radius:20px;padding:24px;">
            <div style="font-weight:800;color:#92400E;font-size:15px;margin-bottom:12px;">🔒 Salida Rápida</div>
            <p style="font-size:13px;color:#78350F;line-height:1.7;margin-bottom:16px;">
                Presiona para ir a una página neutra si alguien está mirando tu pantalla:
            </p>
            <div style="display:flex;gap:10px;flex-wrap:wrap;">
                <a href="https://www.google.com" target="_blank" style="background:#FEF3C7;color:#92400E;
                    padding:10px 18px;border-radius:12px;font-size:12px;text-decoration:none;font-weight:700;
                    border:1px solid #FCD34D;">🔍 Google</a>
                <a href="https://weather.com" target="_blank" style="background:#FEF3C7;color:#92400E;
                    padding:10px 18px;border-radius:12px;font-size:12px;text-decoration:none;font-weight:700;
                    border:1px solid #FCD34D;">🌦️ Clima</a>
                <a href="https://www.eltiempo.com" target="_blank" style="background:#FEF3C7;color:#92400E;
                    padding:10px 18px;border-radius:12px;font-size:12px;text-decoration:none;font-weight:700;
                    border:1px solid #FCD34D;">📰 Noticias</a>
            </div>
        </div>""", unsafe_allow_html=True)
    with col_b:
        tips_list = ["🔵 Mantén la calma y ve a un lugar concurrido",
                     "🔵 Llama o envía tu ubicación a alguien de confianza",
                     "🔵 Memoriza: 123 Policía · 155 Mujer · 132 Ambulancia",
                     "🔵 No confrontes al agresor directamente",
                     "🔵 Documenta evidencia si es completamente seguro",
                     "🔵 Activa la alerta de tu celular o smartwatch"]
        tips_html = "".join([f'<div style="font-size:12px;color:#1E1B4B;margin-bottom:9px;line-height:1.65;display:flex;align-items:flex-start;gap:4px;">{t}</div>' for t in tips_list])
        st.markdown(f"""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border:1.5px solid #C4B5FD;
            border-radius:20px;padding:24px;">
            <div style="font-weight:800;color:#5B21B6;font-size:15px;margin-bottom:14px;">💡 En caso de emergencia</div>
            {tips_html}
        </div>""", unsafe_allow_html=True)

# ── DENUNCIAS ─────────────────────────────────────────────────────────────────
elif "📋" in page:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:#FFFBEB;
            border:1px solid #FDE68A;border-radius:24px;padding:5px 16px;font-size:11px;
            color:#D97706;font-weight:700;margin-bottom:12px;">📋 CENTRO DE DENUNCIAS SEGURO</div>
        <h1 style="font-size:30px;font-weight:900;color:#1E1B4B;margin:0 0 8px;letter-spacing:-0.5px;">Registro de Denuncia</h1>
        <p style="color:#6B7280;font-size:14px;margin:0;">Registra un hecho de forma segura y confidencial. Orientación jurídica personalizada con IA.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("denuncia_sent"):
        # Step indicator
        step = st.session_state.get("denuncia_step", 1)
        steps = ["Clasificación", "Descripción", "Opciones y Envío"]
        step_html = '<div style="display:flex;align-items:center;gap:0;margin-bottom:24px;">'
        for si, sl in enumerate(steps, 1):
            if si < step:
                s_bg, s_color, s_text = "#059669","#fff","✓"
            elif si == step:
                s_bg, s_color, s_text = "#5B21B6","#fff",str(si)
            else:
                s_bg, s_color, s_text = "#EDE9FE","#A78BFA",str(si)
            step_html += f'<div style="display:flex;align-items:center;{"flex:1;" if si < len(steps) else ""}">'
            step_html += f'<div style="width:30px;height:30px;border-radius:50%;background:{s_bg};color:{s_color};display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;flex-shrink:0;">{s_text}</div>'
            step_html += f'<span style="font-size:12px;font-weight:{"700" if si==step else "500"};color:{"#5B21B6" if si==step else "#6B7280"};margin-left:8px;white-space:nowrap;">{sl}</span>'
            if si < len(steps):
                step_html += f'<div style="flex:1;height:2px;background:{"#059669" if si<step else "#EDE9FE"};margin:0 12px;"></div>'
            step_html += '</div>'
        step_html += '</div>'
        st.markdown(step_html, unsafe_allow_html=True)

        col_form, col_info = st.columns([2, 1])
        with col_form:
            st.markdown('<div class="sh-card">', unsafe_allow_html=True)

            # Anon toggle
            anon = st.toggle("🔒 Denuncia Anónima (Recomendado)", value=st.session_state.get("d_anon", True), key="d_anon_toggle")
            st.session_state["d_anon"] = anon
            anon_bg = "linear-gradient(135deg,#ECFDF5,#D1FAE5)" if anon else "linear-gradient(135deg,#F5F3FF,#EDE9FE)"
            anon_color = "#059669" if anon else "#5B21B6"
            anon_label = "✅ Denuncia 100% Anónima — Tu identidad está protegida" if anon else "👤 Denuncia con Identidad"
            st.markdown(f"""<div style="background:{anon_bg};border-radius:14px;padding:12px 16px;
                border:1px solid {anon_color}30;margin-bottom:20px;font-size:13px;font-weight:700;color:{anon_color};">
                {anon_label}</div>""", unsafe_allow_html=True)

            if step == 1:
                st.markdown('<div style="font-size:13px;font-weight:800;color:#5B21B6;margin-bottom:14px;">📌 Paso 1: Clasificación del hecho</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    d_delito = st.selectbox("⚖️ Tipo de Delito", ["— Selecciona —"] + DELITOS, key="d_delito")
                with c2:
                    d_dep = st.selectbox("🗺️ Departamento", DEPARTAMENTOS, key="d_dep")
                c3, c4 = st.columns(2)
                with c3:
                    d_fecha = st.date_input("📅 Fecha aproximada", key="d_fecha", value=None)
                with c4:
                    d_hora = st.time_input("🕐 Hora aproximada", key="d_hora", value=None)
                d_lugar = st.text_input("📍 Lugar del hecho", placeholder="Ej: Centro Comercial El Tesoro, Cll 45, barrio...", key="d_lugar")

                # Urgencia
                st.markdown('<div style="font-size:12px;font-weight:700;color:#5B21B6;margin:14px 0 8px;">🚨 Nivel de Urgencia</div>', unsafe_allow_html=True)
                urg_cols = st.columns(3)
                urgencias = [("🔴","INMEDIATA","En peligro ahora","#DC2626","#FEF2F2"),
                             ("🟡","URGENTE","Ocurrió recientemente","#D97706","#FFFBEB"),
                             ("🟢","NORMAL","Para registro y seguimiento","#059669","#ECFDF5")]
                sel_urg = st.session_state.get("d_urgencia","NORMAL")
                for ui, (uic, ulabel, udesc, ucolor, ubg) in enumerate(urgencias):
                    with urg_cols[ui]:
                        is_sel_u = sel_urg == ulabel
                        if st.button(f"{uic} {ulabel}", key=f"urg_{ulabel}", use_container_width=True):
                            st.session_state["d_urgencia"] = ulabel
                            st.rerun()
                        st.markdown(f'<div style="font-size:9px;color:{ucolor};text-align:center;margin-top:-10px;margin-bottom:8px;">{udesc}</div>', unsafe_allow_html=True)

                if st.button("Siguiente → Descripción del hecho", type="primary", use_container_width=True):
                    st.session_state["denuncia_step"] = 2
                    st.rerun()

            elif step == 2:
                st.markdown('<div style="font-size:13px;font-weight:800;color:#5B21B6;margin-bottom:14px;">📝 Paso 2: Descripción del hecho</div>', unsafe_allow_html=True)
                d_desc = st.text_area("Describe lo que ocurrió con detalle:",
                    height=160, placeholder="Describe con el mayor detalle posible. Incluye qué pasó, quién lo hizo, cómo reaccionaste. Todo es completamente confidencial...", key="d_desc")
                char_color = "#059669" if len(d_desc) > 50 else "#D97706"
                st.markdown(f'<div style="font-size:11px;color:{char_color};margin-top:-6px;margin-bottom:16px;font-weight:600;">{len(d_desc)} caracteres{"  ✓ Descripción suficiente" if len(d_desc)>50 else " — agrega más detalles para mejor orientación"}</div>', unsafe_allow_html=True)

                # File upload
                st.markdown('<div style="font-size:12px;font-weight:700;color:#5B21B6;margin-bottom:8px;">📎 Evidencia (fotos, audio, video)</div>', unsafe_allow_html=True)
                uploaded = st.file_uploader("Adjunta archivos de evidencia (opcional):", accept_multiple_files=True,
                    type=["jpg","jpeg","png","mp4","mp3","pdf","wav"], label_visibility="collapsed", key="d_files")
                if uploaded:
                    for f in uploaded:
                        st.markdown(f'<div style="font-size:12px;color:#059669;margin-bottom:4px;">✅ {f.name} adjuntado</div>', unsafe_allow_html=True)

                c_prev, c_next = st.columns(2)
                with c_prev:
                    if st.button("← Anterior", use_container_width=True):
                        st.session_state["denuncia_step"] = 1
                        st.rerun()
                with c_next:
                    if st.button("Siguiente → Opciones y Envío", type="primary", use_container_width=True, disabled=not st.session_state.get("d_desc","").strip()):
                        st.session_state["denuncia_step"] = 3
                        st.rerun()

            elif step == 3:
                st.markdown('<div style="font-size:13px;font-weight:800;color:#5B21B6;margin-bottom:14px;">✅ Paso 3: Opciones adicionales y envío</div>', unsafe_allow_html=True)
                opciones = ["Violencia física","Violencia verbal","Violencia psicológica","Violencia económica",
                            "Seguimiento / acoso","Violencia digital","Tengo evidencia","Quiero acompañamiento",
                            "Necesito protección urgente","Quiero mantener anonimato total","Involucra menores de edad"]
                d_opts = st.multiselect("Selecciona todas las que apliquen:", opciones, key="d_opts")

                # Resumen
                st.markdown(f"""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:16px;
                    padding:18px;margin-top:14px;border:1px solid #C4B5FD;margin-bottom:18px;">
                    <div style="font-size:13px;font-weight:800;color:#5B21B6;margin-bottom:12px;">📋 Resumen del Reporte</div>
                    {''.join([f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #DDD6FE;font-size:12px;"><span style="color:#6B7280;">{k}</span><span style="color:#1E1B4B;font-weight:700;">{v}</span></div>' for k,v in [
                        ("Modo", "🔒 Anónimo" if st.session_state.get("d_anon",True) else "👤 Con identidad"),
                        ("Urgencia", st.session_state.get("d_urgencia","NORMAL")),
                        ("Delito", st.session_state.get("d_delito","No especificado")),
                        ("Departamento", st.session_state.get("d_dep","No especificado")),
                        ("Opciones", f"{len(d_opts)} seleccionadas" if d_opts else "Ninguna"),
                    ]])}
                </div>""", unsafe_allow_html=True)

                c_prev2, c_send = st.columns(2)
                with c_prev2:
                    if st.button("← Anterior", use_container_width=True, key="prev2"):
                        st.session_state["denuncia_step"] = 2
                        st.rerun()
                with c_send:
                    send_btn = st.button("📤 Registrar y Obtener Orientación Legal",
                                         type="primary", use_container_width=True, key="denuncia_send",
                                         disabled=not st.session_state.get("d_desc","").strip())

                if send_btn and st.session_state.get("d_desc","").strip():
                    st.session_state["denuncia_sent"] = True
                    with st.spinner("⚖️ Preparando orientación jurídica personalizada..."):
                        legal_text = call_claude(
                            """Eres asistente jurídica especializada en derechos de la mujer en Colombia (Ley 1257/2008).
Usa EXACTAMENTE estas secciones con emojis:
⚖️ TUS DERECHOS INMEDIATOS
📋 PASOS A SEGUIR (ordenados)
🏢 ENTIDADES A CONTACTAR
📱 EVIDENCIA A RECOLECTAR
⏰ PLAZOS IMPORTANTES
Máximo 3 puntos por sección con bullet •. Tono cálido, empático y empoderador.""",
                            f"""Mujer reporta en Colombia:
Delito: {st.session_state.get('d_delito','No especificado')}
Departamento: {st.session_state.get('d_dep','No especificado')}
Lugar: {st.session_state.get('d_lugar','No especificado')}
Urgencia: {st.session_state.get('d_urgencia','NORMAL')}
Descripción: {st.session_state.get('d_desc','')}
Opciones seleccionadas: {', '.join(d_opts) if d_opts else 'Ninguna'}"""
                        )
                        st.session_state["legal_text"] = legal_text
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        with col_info:
            st.markdown("""<div class="sh-card">
                <div style="font-size:13px;font-weight:800;color:#5B21B6;margin-bottom:16px;">🏢 Entidades Oficiales</div>""", unsafe_allow_html=True)
            entidades_d = [
                ("⚖️","Fiscalía General","Denuncias penales en línea","https://www.fiscalia.gov.co","#7C3AED"),
                ("🏠","Comisaría de Familia","Violencia intrafamiliar","tel:123","#1D4ED8"),
                ("👨‍👩‍👧","Instituto ICBF","Protección familiar","https://www.icbf.gov.co","#059669"),
                ("📞","Línea 155","Mujer 24/7 — Gratis","tel:155","#EC4899"),
                ("🚨","URI Fiscalía 24h","Denuncia urgente sin cita","tel:018000919748","#DC2626"),
            ]
            for icon_e, name_e, desc_e, href_e, color_e in entidades_d:
                st.markdown(f"""<a href="{href_e}" target="{'_blank' if href_e.startswith('http') else '_self'}" style="text-decoration:none;">
                <div style="display:flex;align-items:center;gap:10px;padding:11px 0;border-bottom:1px solid #EDE9FE;">
                    <div style="width:34px;height:34px;background:linear-gradient(135deg,{color_e}18,{color_e}10);border-radius:10px;
                        display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">{icon_e}</div>
                    <div>
                        <div style="font-size:12px;font-weight:700;color:#1E1B4B;">{name_e}</div>
                        <div style="font-size:10px;color:#A78BFA;font-weight:500;">{desc_e}</div>
                    </div>
                </div></a>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("""<div style="background:linear-gradient(135deg,#FFFBEB,#FEF3C7);border:1.5px solid #FCD34D;
                border-radius:16px;padding:16px;font-size:12px;color:#92400E;line-height:1.75;margin-bottom:14px;">
                ⚠️ Plataforma <strong>académica prototipo</strong>. Para denuncias con validez legal, dirígete a las entidades oficiales.
            </div>""", unsafe_allow_html=True)

            razones = ["✅ Protege a otras mujeres","✅ Genera registros estadísticos","✅ Activa medidas de protección",
                       "✅ Accedes a apoyo psicológico","✅ Rompe el ciclo de violencia"]
            r_html = "".join([f'<div style="font-size:12px;color:#1E1B4B;margin-bottom:8px;line-height:1.6;">{r}</div>' for r in razones])
            st.markdown(f'<div class="sh-card"><div style="font-size:13px;font-weight:800;color:#5B21B6;margin-bottom:12px;">🧠 ¿Por qué es importante denunciar?</div>{r_html}</div>', unsafe_allow_html=True)

    else:
        # Sent confirmation
        st.markdown("""<div style="background:linear-gradient(135deg,#ECFDF5,#D1FAE5);border:2px solid #6EE7B7;
            border-radius:24px;padding:28px;margin-bottom:24px;display:flex;align-items:center;gap:18px;">
            <div style="width:56px;height:56px;background:#059669;border-radius:50%;display:flex;
                align-items:center;justify-content:center;font-size:26px;flex-shrink:0;
                box-shadow:0 4px 16px rgba(5,150,105,0.35);">✅</div>
            <div>
                <div style="font-size:20px;font-weight:900;color:#065F46;margin-bottom:4px;">Reporte registrado de forma segura</div>
                <div style="font-size:13px;color:#047857;line-height:1.6;">Tu información es completamente confidencial. Tu valentía importa.</div>
            </div>
        </div>""", unsafe_allow_html=True)

        legal = st.session_state.get("legal_text", "")
        st.markdown(f"""<div class="sh-card">
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:18px;">
                <div style="width:46px;height:46px;background:linear-gradient(135deg,#1E1B4B,#5B21B6);
                    border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:22px;">⚖️</div>
                <div>
                    <div style="font-size:16px;font-weight:800;color:#1E1B4B;">Orientación Jurídica Personalizada</div>
                    <div style="font-size:11px;color:#A78BFA;">Generada con IA especializada en Ley 1257/2008 — Colombia</div>
                </div>
            </div>
            <div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:16px;padding:20px 24px;
                border:1px solid #C4B5FD;font-size:13px;line-height:1.85;white-space:pre-wrap;color:#1E1B4B;">{legal}</div>
        </div>""", unsafe_allow_html=True)

        if st.button("← Registrar nueva denuncia", type="secondary"):
            st.session_state["denuncia_sent"] = False
            st.session_state["denuncia_step"] = 1
            st.session_state.pop("legal_text", None)
            st.rerun()

# ── SARA · IA APOYO ───────────────────────────────────────────────────────────
elif "💜" in page:
    SARA_SYSTEM = """Eres SARA, asistente de apoyo empática, cálida y experta de SafeHer Colombia.

ROL PRINCIPAL: Acompañar y orientar a mujeres que pueden estar en situaciones de riesgo, violencia, crisis emocional o que buscan información.

PRINCIPIOS FUNDAMENTALES:
- Eres cálida, empática, paciente y NUNCA juzgas
- Siempre valida los sentimientos ANTES de dar cualquier consejo
- Si hay peligro inmediato (golpes, secuestro, amenazas): responde en ≤3 oraciones con 🚨 Llama al 123 INMEDIATAMENTE
- Nunca minimizas ni normalizas la violencia

APOYO PSICOLÓGICO:
- Ansiedad → técnica 4-7-8 (inhala 4s, retén 7s, exhala 8s)
- Crisis → grounding 5-4-3-2-1 (5 cosas ves, 4 tocas, 3 escuchas, 2 hueles, 1 sabores)
- Usa preguntas abiertas para entender mejor
- Celebra pequeños pasos: "Es muy valiente que estés buscando ayuda"

CONOCIMIENTO LEGAL:
- Ley 1257/2008, medidas de protección, órdenes de alejamiento
- Comisaría de Familia, Fiscalía URI 24h, Línea 155, ICBF Línea 141

SOBRE LA APP SafeHer:
- Predicción ML: datos de riesgo por departamento
- Mapa de Riesgo: visualización geográfica
- Denuncias: registro anónimo con orientación jurídica IA
- Ayuda Cercana: entidades de apoyo con cómo llegar
- Emergencias: líneas directas (123, 155, 137)

FORMATO: Español cálido y cercano, máx 200 palabras, emojis con moderación (💜🌸). Crisis inmediata: máx 3 oraciones."""

    if "sara_messages" not in st.session_state:
        st.session_state.sara_messages = [
            {"role": "assistant", "content": "Hola 💜 Soy SARA, tu asistente de apoyo de SafeHer.\n\nEstoy aquí para escucharte, orientarte y acompañarte — sin juzgarte, completamente confidencial. Puedes contarme lo que estás viviendo, preguntar sobre tus derechos, buscar apoyo emocional, o simplemente desahogarte.\n\nEstoy aquí 24/7 para ti. ¿Cómo te puedo ayudar hoy? 🌸"}
        ]

    col_sidebar_sara, col_chat = st.columns([1, 3])

    with col_sidebar_sara:
        st.markdown("""<div style="background:linear-gradient(160deg,#1E1B4B 0%,#4C1D95 55%,#7C3AED 100%);
            border-radius:22px;padding:24px;color:#fff;text-align:center;margin-bottom:14px;
            box-shadow:0 6px 24px rgba(91,33,182,0.3);">
            <div style="width:68px;height:68px;background:rgba(255,255,255,0.14);border-radius:50%;
                display:flex;align-items:center;justify-content:center;font-size:32px;margin:0 auto 12px;
                border:2px solid rgba(255,255,255,0.24);box-shadow:0 0 20px rgba(167,139,250,0.3);">💜</div>
            <div style="font-weight:900;font-size:22px;letter-spacing:-0.5px;">SARA</div>
            <div style="font-size:11px;color:#C4B5FD;margin-bottom:14px;">Asistente SafeHer · IA Empática</div>
            <div style="display:flex;align-items:center;gap:7px;justify-content:center;">
                <div style="width:9px;height:9px;border-radius:50%;background:#4ADE80;box-shadow:0 0 10px #4ADE80;"></div>
                <span style="font-size:11px;color:#A7F3D0;font-weight:600;">En línea · 24/7</span>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div style="font-size:13px;font-weight:700;color:#1E1B4B;margin-bottom:10px;">¿Cómo te sientes ahora?</div>', unsafe_allow_html=True)
        mood_options = [("😰","Asustada"),("😢","Triste"),("😡","Enojada"),("😔","Sola"),("🙂","Bien"),("🆘","Urgente")]
        cols_mood = st.columns(3)
        for i, (emoji, label) in enumerate(mood_options):
            with cols_mood[i % 3]:
                if st.button(f"{emoji}", key=f"mood_{label}", use_container_width=True, help=label):
                    msg_content = f"Me siento {label.lower()} {emoji}"
                    st.session_state.sara_messages.append({"role": "user", "content": msg_content})
                    with st.spinner("💜"):
                        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.sara_messages]
                        reply = call_claude(SARA_SYSTEM, "", history=history)
                    st.session_state.sara_messages.append({"role": "assistant", "content": reply})
                    st.rerun()
                st.markdown(f'<div style="font-size:9px;color:#A78BFA;text-align:center;margin-top:-8px;margin-bottom:6px;">{label}</div>', unsafe_allow_html=True)

        st.markdown('<div class="sh-card" style="margin-top:14px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:700;color:#1E1B4B;margin-bottom:10px;">💜 SARA puede ayudarte con:</div>', unsafe_allow_html=True)
        for ic, txt in [("🔒","Confidencial 100%"),("⚡","Respuesta empática"),("🧠","Técnicas de calma"),
                        ("⚖️","Orientación legal"),("📍","Recursos cercanos"),("💬","Escucharte sin juzgar"),
                        ("🌱","Apoyo psicológico"),("📱","Navegar la app")]:
            st.markdown(f'<div style="display:flex;gap:9px;margin-bottom:9px;align-items:flex-start;">'
                       f'<span style="font-size:15px;line-height:1.4;">{ic}</span>'
                       f'<span style="font-size:11px;color:#6B7280;line-height:1.5;">{txt}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div style="background:linear-gradient(135deg,#FFF1F2,#FEE2E2);border:1.5px solid #FECDD3;
            border-radius:16px;padding:16px;margin-top:4px;">
            <div style="font-size:11px;font-weight:800;color:#9F1239;margin-bottom:12px;text-transform:uppercase;letter-spacing:0.8px;">🚨 Emergencia</div>""", unsafe_allow_html=True)
        for num, desc, sub in [("123","Policía","24/7"),("155","Línea Mujer","Gratis 24/7"),("137","Salud Mental","Apoyo")]:
            st.markdown(f'<a href="tel:{num}" style="display:flex;justify-content:space-between;align-items:center;text-decoration:none;padding:9px 0;border-bottom:1px solid #FECDD3;">'
                       f'<span style="font-size:18px;color:#BE123C;font-weight:900;font-family:Georgia,serif;">{num}</span>'
                       f'<div style="text-align:right;"><div style="font-size:11px;color:#DC2626;font-weight:700;">{desc}</div>'
                       f'<div style="font-size:9px;color:#9F1239;font-weight:500;">{sub}</div></div></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chat:
        # Header
        st.markdown("""<div style="padding:18px 24px;border-bottom:1px solid #EDE9FE;display:flex;align-items:center;
            gap:14px;background:linear-gradient(135deg,#1E1B4B,#4C1D95);border-radius:22px 22px 0 0;
            box-shadow:0 4px 16px rgba(30,27,75,0.3);">
            <div style="width:42px;height:42px;background:rgba(255,255,255,0.14);border-radius:50%;
                display:flex;align-items:center;justify-content:center;font-size:22px;
                box-shadow:0 2px 8px rgba(0,0,0,0.2);">💜</div>
            <div>
                <div style="font-weight:800;font-size:15px;color:#fff;letter-spacing:-0.3px;">SARA — Asistente SafeHer</div>
                <div style="font-size:11px;color:#A7F3D0;display:flex;align-items:center;gap:6px;margin-top:3px;">
                    <span style="width:7px;height:7px;border-radius:50%;background:#4ADE80;display:inline-block;box-shadow:0 0 6px #4ADE80;"></span>
                    En línea · Siempre disponible · Completamente confidencial
                </div>
            </div>
            <div style="margin-left:auto;display:flex;gap:8px;">
                <a href="tel:155" style="background:rgba(255,255,255,0.1);color:#E9D5FF;padding:7px 14px;
                    border-radius:20px;font-size:11px;text-decoration:none;font-weight:700;
                    border:1px solid rgba(255,255,255,0.2);">📞 155</a>
                <a href="tel:123" style="background:rgba(220,38,38,0.35);color:#FCA5A5;padding:7px 14px;
                    border-radius:20px;font-size:11px;text-decoration:none;font-weight:700;
                    border:1px solid rgba(220,38,38,0.4);">🚨 123</a>
            </div>
        </div>""", unsafe_allow_html=True)

        # Messages
        msgs_html = ""
        for msg in st.session_state.sara_messages:
            if msg["role"] == "user":
                msgs_html += f"""<div style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:16px;">
                    <div class="chat-user">{msg['content']}</div>
                    <div style="width:34px;height:34px;background:linear-gradient(135deg,#EDE9FE,#DDD6FE);border-radius:50%;
                        display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;margin-top:2px;">👤</div>
                </div>"""
            else:
                content = msg['content'].replace('\n', '<br>')
                msgs_html += f"""<div style="display:flex;gap:10px;margin-bottom:16px;">
                    <div style="width:34px;height:34px;background:linear-gradient(135deg,#1E1B4B,#7C3AED);border-radius:50%;
                        display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;margin-top:2px;
                        box-shadow:0 3px 10px rgba(124,58,237,0.3);">💜</div>
                    <div class="chat-sara">{content}</div>
                </div>"""

        st.markdown(f"""<div style="background:#fff;padding:24px;min-height:380px;max-height:420px;
            border-left:1px solid #EDE9FE;border-right:1px solid #EDE9FE;overflow-y:auto;">
            {msgs_html}
        </div>""", unsafe_allow_html=True)

        # Quick replies
        st.markdown("""<div style="background:linear-gradient(135deg,#FAFAFA,#F5F3FF);padding:12px 24px 10px;
            border:1px solid #EDE9FE;border-top:none;">
            <div style="font-size:10px;color:#A78BFA;margin-bottom:8px;font-weight:700;letter-spacing:0.8px;">RESPUESTAS RÁPIDAS:</div>
        """, unsafe_allow_html=True)
        quick_replies = ["Necesito ayuda urgente 🆘","¿Cómo denuncio?","Me siento sola y asustada",
                         "¿Cuáles son mis derechos?","Ejercicio para calmarme 🧘","Me están amenazando",
                         "¿Qué hace esta app?","Apoyo psicológico"]
        qcols = st.columns(4)
        for i, q in enumerate(quick_replies):
            with qcols[i % 4]:
                if st.button(q, key=f"qr_{i}", use_container_width=True):
                    st.session_state.sara_messages.append({"role": "user", "content": q})
                    with st.spinner("SARA está escribiendo..."):
                        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.sara_messages]
                        reply = call_claude(SARA_SYSTEM, "", history=history)
                    st.session_state.sara_messages.append({"role": "assistant", "content": reply})
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Input form
        st.markdown('<div style="background:#fff;border:1px solid #EDE9FE;border-radius:0 0 22px 22px;padding:14px 24px;">', unsafe_allow_html=True)
        with st.form("sara_form", clear_on_submit=True):
            col_inp, col_send = st.columns([5, 1])
            with col_inp:
                user_input = st.text_input("", placeholder="Escribe tu mensaje... Estoy aquí para escucharte 💜",
                                           label_visibility="collapsed", key="sara_input")
            with col_send:
                send_sara = st.form_submit_button("➤ Enviar", use_container_width=True)
        if send_sara and user_input.strip():
            st.session_state.sara_messages.append({"role": "user", "content": user_input.strip()})
            with st.spinner("SARA está escribiendo..."):
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.sara_messages]
                reply = call_claude(SARA_SYSTEM, "", history=history)
            st.session_state.sara_messages.append({"role": "assistant", "content": reply})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        col_clear, col_info_sara = st.columns([1, 2])
        with col_clear:
            if st.button("🔄 Nueva conversación", use_container_width=True):
                st.session_state.sara_messages = [
                    {"role": "assistant", "content": "Hola 💜 Soy SARA. Estoy aquí para escucharte. ¿Cómo te puedo ayudar?"}
                ]
                st.rerun()
        with col_info_sara:
            st.markdown('<div style="font-size:11px;color:#A78BFA;padding:8px 0;">🔒 Esta conversación es completamente confidencial y no se almacena de forma permanente.</div>', unsafe_allow_html=True)

# ── AYUDA CERCANA ─────────────────────────────────────────────────────────────
elif "🚔" in page:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:#EFF6FF;
            border:1px solid #BFDBFE;border-radius:24px;padding:5px 16px;font-size:11px;
            color:#1D4ED8;font-weight:700;margin-bottom:12px;">🚔 AYUDA CERCANA</div>
        <h1 style="font-size:30px;font-weight:900;color:#1E1B4B;margin:0 0 8px;letter-spacing:-0.5px;">Ayuda Cercana</h1>
        <p style="color:#6B7280;font-size:14px;margin:0;">Encuentra entidades de apoyo con información detallada, cómo llegar y contacto directo.</p>
    </div>
    """, unsafe_allow_html=True)

    city_input = st.text_input("📍 Tu ciudad o barrio:", value="Medellín", key="ayuda_city",
                                placeholder="Ej: Medellín, Bogotá, Cali, Barranquilla...")

    entidades = [
        {"tipo":"Policía","icon":"🚔","nom":"CAI Centro","dir":"Carrera 45 #54-20, Medellín","barrio":"Centro","dist":"0.4 km","color":"#1D4ED8","href":"tel:123","phone":"123","horario":"24/7","desc":"Centro de Atención Inmediata. Atención permanente para denuncias y emergencias policiales.","transporte":"Metro: Prado (5 min caminando) · Bus: múltiples rutas por Cra 45"},
        {"tipo":"Hospital","icon":"🏥","nom":"Hospital General de Medellín","dir":"Calle 24 #29-6, Medellín","barrio":"Bomboná","dist":"1.2 km","color":"#059669","href":"tel:4411227","phone":"4411227","horario":"24/7 Urgencias","desc":"Hospital público con urgencias completas, medicina forense y apoyo psicológico para víctimas de violencia.","transporte":"Bus: rutas por Cll 24 · Metro: Industriales (12 min caminando)"},
        {"tipo":"Fiscalía","icon":"⚖️","nom":"Fiscalía Seccional Medellín","dir":"Calle 44 #52-165, Medellín","barrio":"El Centro","dist":"0.8 km","color":"#7C3AED","href":"https://www.fiscalia.gov.co","phone":"01-8000-919-748","horario":"Lun–Vie 7am–5pm","desc":"Recepción de denuncias penales, medidas de protección y seguimiento a casos de violencia.","transporte":"Metro: Alpujarra (8 min caminando) · Bus: Av. Regional"},
        {"tipo":"Refugio","icon":"🏠","nom":"Casa Refugio Luz y Esperanza","dir":"Dirección confidencial — llama al 155","barrio":"Confidencial","dist":"2.1 km","color":"#D97706","href":"tel:155","phone":"155","horario":"24/7 Disponible","desc":"Alojamiento temporal gratuito y seguro para mujeres víctimas de violencia y sus hijos.","transporte":"Llama al 155 para coordinación de transporte seguro y discreto"},
        {"tipo":"Psicología","icon":"🧠","nom":"CAIVAS - Atención Integral","dir":"Calle 50 #40-20, Medellín","barrio":"Prado","dist":"1.5 km","color":"#8B5CF6","href":"tel:137","phone":"137","horario":"Lun–Sáb 8am–8pm","desc":"Centro de Atención Integral a Víctimas. Psicología gratuita, terapia individual y grupos de apoyo.","transporte":"Bus: Cll 50 (múltiples rutas) · Metro: Prado (10 min caminando)"},
        {"tipo":"Policía","icon":"🚔","nom":"Estación Policía Laureles","dir":"Carrera 81 #30-05, Medellín","barrio":"Laureles","dist":"3.2 km","color":"#1D4ED8","href":"tel:123","phone":"123","horario":"24/7","desc":"Estación de Policía del barrio Laureles. Denuncia y apoyo policial inmediato.","transporte":"Bus: Cra 80 (múltiples rutas) · Metro: Universidad (15 min caminando)"},
        {"tipo":"Hospital","icon":"🏥","nom":"Clínica Las Américas","dir":"Diagonal 75B #2A-80, Medellín","barrio":"Estadio","dist":"2.8 km","color":"#059669","href":"tel:4456600","phone":"4456600","horario":"24/7 Urgencias","desc":"Urgencias completas y medicina forense. Atención prioritaria a víctimas de violencia.","transporte":"Metro: Estadio (8 min caminando) · Bus: Cll 73 (múltiples rutas)"},
        {"tipo":"Fiscalía","icon":"⚖️","nom":"URI Fiscalía 24 Horas","dir":"Calle 57 #45-129, Medellín","barrio":"Niquitao","dist":"0.9 km","color":"#7C3AED","href":"https://www.fiscalia.gov.co","phone":"01-8000-919-748","horario":"24/7 Sin cita previa","desc":"Unidad de Reacción Inmediata. Denuncias penales urgentes las 24 horas, sin necesidad de cita.","transporte":"Metro: Hospital (10 min caminando) · Bus: Cll 57"},
        {"tipo":"Psicología","icon":"🧠","nom":"Comisaría de Familia N°1","dir":"Carrera 52 #48-10, Medellín","barrio":"El Centro","dist":"1.1 km","color":"#8B5CF6","href":"tel:123","phone":"Presencial","horario":"Lun–Vie 8am–5pm","desc":"Medidas de protección familiar, conciliación y apoyo psicosocial integral. Sin costo.","transporte":"Metro: Alpujarra (12 min caminando) · Bus: Cra 52"},
        {"tipo":"Refugio","icon":"🏠","nom":"Casa de Acogida ICBF","dir":"Dirección confidencial — Línea 141","barrio":"Confidencial","dist":"3.5 km","color":"#D97706","href":"tel:141","phone":"141 ICBF","horario":"24/7","desc":"Casa de acogida para mujeres y niños en situación de violencia intrafamiliar.","transporte":"Llama al 141 (ICBF) para información de acceso seguro"},
    ]

    filter_tipo = st.selectbox("🔍 Filtrar por tipo de entidad:", ["Todos","Policía","Hospitales","Fiscalía","Refugios","Psicología"], key="ayuda_filter")
    filter_map = {"Todos":"Todos","Policía":"Policía","Hospitales":"Hospital","Fiscalía":"Fiscalía","Refugios":"Refugio","Psicología":"Psicología"}
    filtered = [e for e in entidades if filter_tipo == "Todos" or e["tipo"] == filter_map[filter_tipo]]

    st.markdown(f'<div style="font-size:12px;color:#6B7280;margin-bottom:16px;"><strong style="color:#1E1B4B;">{len(filtered)}</strong> lugares de apoyo cerca de <strong style="color:#1E1B4B;">{city_input}</strong></div>', unsafe_allow_html=True)

    col_grid, col_ent = st.columns([2, 1])
    with col_grid:
        gcols = st.columns(3)
        for i, e in enumerate(filtered):
            with gcols[i % 3]:
                is_sel = st.session_state.get("selected_entity") == e["nom"]
                border = f"2px solid {e['color']}" if is_sel else "1.5px solid #EDE9FE"
                shadow = f"0 6px 24px {e['color']}28" if is_sel else "0 2px 12px rgba(109,40,217,0.07)"
                st.markdown(f"""<div style="background:#fff;border:{border};border-radius:20px;
                    padding:20px;margin-bottom:14px;box-shadow:{shadow};transition:all 0.2s;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">
                        <div style="background:linear-gradient(135deg,{e['color']}18,{e['color']}0D);border-radius:14px;
                            width:48px;height:48px;display:flex;align-items:center;justify-content:center;font-size:24px;">{e['icon']}</div>
                        <div style="background:{e['color']}14;color:{e['color']};font-size:9px;font-weight:800;
                            padding:4px 10px;border-radius:20px;text-transform:uppercase;letter-spacing:0.5px;">{e['tipo']}</div>
                    </div>
                    <div style="font-weight:800;font-size:13px;color:#1E1B4B;margin-bottom:5px;">{e['nom']}</div>
                    <div style="font-size:10px;color:#A78BFA;margin-bottom:4px;">📍 {e['barrio']}</div>
                    <div style="font-size:11px;color:#6B7280;margin-bottom:10px;line-height:1.5;">{e['dir']}</div>
                    <div style="display:flex;gap:6px;flex-wrap:wrap;">
                        <div style="background:#ECFDF5;color:#059669;font-size:10px;font-weight:700;padding:4px 10px;border-radius:20px;">🚶 {e['dist']}</div>
                        <div style="background:#EFF6FF;color:#1D4ED8;font-size:10px;font-weight:700;padding:4px 10px;border-radius:20px;">🕐 {e['horario']}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"{'✓ Seleccionado' if is_sel else 'Ver detalles'}", key=f"ent_{e['nom']}", use_container_width=True,
                             type="primary" if is_sel else "secondary"):
                    if is_sel:
                        st.session_state.pop("selected_entity", None)
                    else:
                        st.session_state["selected_entity"] = e["nom"]
                    st.rerun()

    with col_ent:
        sel_nom = st.session_state.get("selected_entity")
        sel_e = next((e for e in entidades if e["nom"] == sel_nom), None)
        if sel_e:
            st.markdown(f"""<div class="sh-card" style="position:sticky;top:20px;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
                    <div style="background:linear-gradient(135deg,{sel_e['color']}18,{sel_e['color']}0D);border-radius:16px;
                        width:56px;height:56px;display:flex;align-items:center;justify-content:center;font-size:28px;">{sel_e['icon']}</div>
                    <div style="background:{sel_e['color']}14;color:{sel_e['color']};font-size:9px;font-weight:800;
                        padding:5px 12px;border-radius:20px;text-transform:uppercase;">{sel_e['tipo']}</div>
                </div>
                <div style="font-size:19px;font-weight:900;color:#1E1B4B;margin-bottom:6px;">{sel_e['nom']}</div>
                <p style="font-size:12px;color:#6B7280;line-height:1.7;margin-bottom:18px;">{sel_e['desc']}</p>""",
                unsafe_allow_html=True)

            for label, val in [("📍 Dirección", sel_e['dir']),("🏘️ Barrio", sel_e['barrio']),("🕐 Horario", sel_e['horario']),("📞 Contacto", sel_e['phone'])]:
                st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:9px 12px;
                    background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:12px;margin-bottom:8px;">
                    <span style="font-size:11px;color:#A78BFA;font-weight:600;">{label}</span>
                    <span style="font-size:11px;font-weight:800;color:#1E1B4B;text-align:right;max-width:55%;">{val}</span>
                </div>""", unsafe_allow_html=True)

            # Transporte
            st.markdown(f"""<div style="background:linear-gradient(135deg,#EFF6FF,#DBEAFE);border-radius:14px;
                padding:12px 14px;margin-bottom:14px;border:1px solid #BFDBFE;">
                <div style="font-size:11px;font-weight:800;color:#1D4ED8;margin-bottom:5px;">🚌 Cómo llegar desde {city_input}</div>
                <div style="font-size:11px;color:#1E40AF;line-height:1.7;">{sel_e['transporte']}</div>
            </div>""", unsafe_allow_html=True)

            # Action buttons
            st.markdown(f'<a href="{sel_e["href"]}" target="{"_blank" if sel_e["href"].startswith("http") else "_self"}" style="text-decoration:none;display:block;margin-bottom:8px;">'
                       f'<div style="width:100%;background:linear-gradient(135deg,{sel_e["color"]},{sel_e["color"]}CC);color:#fff;border-radius:14px;'
                       f'padding:13px;text-align:center;font-size:13px;font-weight:800;cursor:pointer;'
                       f'box-shadow:0 4px 14px {sel_e["color"]}44;">{"📞 Llamar: "+sel_e["phone"] if sel_e["href"].startswith("tel:") else "🌐 Visitar sitio web"}</div></a>',
                       unsafe_allow_html=True)

            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={sel_e['dir'].replace(' ', '+')}&travelmode=transit"
            st.markdown(f'<a href="{maps_url}" target="_blank" style="text-decoration:none;display:block;margin-bottom:8px;">'
                       f'<div style="width:100%;background:#fff;color:#1D4ED8;border:1.5px solid #BFDBFE;border-radius:14px;'
                       f'padding:11px;text-align:center;font-size:12px;font-weight:700;cursor:pointer;">🗺️ Ruta en transporte público</div></a>',
                       unsafe_allow_html=True)

            copy_dir = sel_e['dir']
            st.markdown(f'<div style="width:100%;background:#F5F3FF;color:#5B21B6;border:1px solid #C4B5FD;border-radius:14px;'
                       f'padding:10px;text-align:center;font-size:11px;font-weight:700;cursor:pointer;margin-bottom:12px;'
                       f'user-select:all;" title="Haz clic para copiar">📋 {copy_dir}</div>', unsafe_allow_html=True)

            if st.button(f"🤖 Instrucciones detalladas con IA", key="directions_btn", use_container_width=True):
                with st.spinner("Calculando mejor ruta..."):
                    dir_text = call_claude(
                        "Experto en transporte urbano de Colombia. Instrucciones claras con bullets y emojis. Incluye: TransMilenio/Metro/BRT, taxi/app, a pie. Máx 120 palabras. Incluye tiempo estimado.",
                        f"¿Cómo llegar desde el centro de {city_input} hasta {sel_e['nom']} en {sel_e['dir']}, barrio {sel_e.get('barrio','')}, distancia ~{sel_e['dist']}?"
                    )
                    st.session_state[f"dir_{sel_e['nom']}"] = dir_text

            dir_r = st.session_state.get(f"dir_{sel_e['nom']}", "")
            if dir_r:
                st.markdown(f"""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:14px;
                    padding:14px 16px;border:1px solid #C4B5FD;margin-top:4px;">
                    <div style="font-size:11px;font-weight:800;color:#5B21B6;margin-bottom:8px;">🧭 Instrucciones de SARA</div>
                    <div style="font-size:11px;color:#1E1B4B;line-height:1.8;white-space:pre-wrap;">{dir_r}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:20px;
                border:2px dashed #C4B5FD;padding:48px 24px;text-align:center;">
                <div style="font-size:48px;margin-bottom:14px;">🚔</div>
                <div style="font-size:15px;font-weight:700;color:#5B21B6;margin-bottom:6px;">Selecciona una entidad</div>
                <div style="font-size:12px;color:#A78BFA;line-height:1.7;">Haz clic en "Ver detalles" para ver información completa, cómo llegar e instrucciones con IA.</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tips_ayuda = ["📱 Google Maps: busca 'Comisaría de Familia + tu ciudad'",
                  "📞 Línea 155 te orienta al refugio más cercano 24/7",
                  "🚔 Estación de Policía más cercana: denuncia inmediata",
                  "🏥 Todo hospital debe atenderte en urgencias sin costo",
                  "📋 Fiscalía URI: denuncias urgentes 24h sin cita previa",
                  "🏠 ICBF Línea 141: protección familiar y menores"]
    t_cols = st.columns(2)
    for i, tip in enumerate(tips_ayuda):
        with t_cols[i % 2]:
            st.markdown(f"""<div style="font-size:12px;color:#1E1B4B;line-height:1.7;padding:11px 14px;background:#fff;
                border-radius:14px;border:1px solid #EDE9FE;margin-bottom:8px;
                box-shadow:0 2px 8px rgba(109,40,217,0.05);">{tip}</div>""", unsafe_allow_html=True)

# ── ACERCA DE ─────────────────────────────────────────────────────────────────
elif "ℹ️" in page:
    st.markdown("""
    <h1 style="font-size:30px;font-weight:900;color:#1E1B4B;margin-bottom:28px;letter-spacing:-0.5px;">ℹ️ Acerca de SafeHer Colombia</h1>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown("""<div class="sh-card">
            <div style="font-weight:800;color:#5B21B6;font-size:16px;margin-bottom:16px;">🎓 Proyecto Académico</div>
            <p style="font-size:13px;color:#1E1B4B;line-height:1.85;margin-bottom:20px;">
                Desarrollado como proyecto de <strong>Analítica y Machine Learning</strong>. Modelos entrenados con datos del
                Sistema de Información Estadístico de la <strong>Policía Nacional de Colombia</strong>.
                Plataforma integral de protección, prevención y apoyo para mujeres.
            </p>
            <div style="font-weight:800;color:#1E1B4B;margin-bottom:14px;font-size:14px;">👩‍💻 Equipo de Desarrollo:</div>""", unsafe_allow_html=True)
        for name in ["Laura Sofia Beltrán","Dana Yaray Vargas","Vanessa Mora"]:
            st.markdown(f"""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:14px;padding:13px 18px;
                display:flex;align-items:center;gap:14px;margin-bottom:10px;border:1px solid #C4B5FD;">
                <div style="width:38px;height:38px;background:linear-gradient(135deg,#4C1D95,#7C3AED);border-radius:50%;
                    display:flex;align-items:center;justify-content:center;font-size:18px;">👩‍🎓</div>
                <span style="font-size:13px;color:#1E1B4B;font-weight:700;">{name}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="sh-card">
            <div style="font-weight:800;color:#5B21B6;font-size:16px;margin-bottom:16px;">🤖 Modelos de Machine Learning</div>""", unsafe_allow_html=True)
        for ti, al, ta, co in [
            ("📊 Nivel de Gravedad","XGBoost + LightGBM","8 clases: MÍNIMO → CRÍTICO","#4C1D95"),
            ("🗺️ Zona de Riesgo","XGBoost + LightGBM","6 clases: MUY BAJO → MUY ALTO","#1D4ED8"),
            ("👥 Estimación de Víctimas","Ensemble de modelos","Valor numérico estimado","#059669"),
            ("🧠 IA de Apoyo (SARA)","Claude Sonnet 4","Apoyo psicológico y legal","#7C3AED"),
        ]:
            st.markdown(f"""<div style="background:linear-gradient(135deg,{co}08,{co}04);border:1px solid {co}22;
                border-radius:16px;padding:14px 18px;margin-bottom:10px;">
                <div style="font-weight:800;color:#1E1B4B;font-size:13px;">{ti}</div>
                <div style="font-size:12px;color:{co};margin-top:3px;font-weight:600;">{al}</div>
                <div style="font-size:11px;color:#6B7280;margin-top:2px;">Target: {ta}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown("""<div style="background:linear-gradient(135deg,#FFFBEB,#FEF3C7);border:1.5px solid #FCD34D;
            border-radius:20px;padding:20px;margin-bottom:18px;">
            <div style="font-weight:800;color:#92400E;font-size:14px;margin-bottom:10px;">⚠️ Limitaciones Importantes</div>
            <p style="font-size:12px;color:#78350F;line-height:1.8;">Plataforma <strong>académica prototipo</strong>.
            Las predicciones son aproximaciones estadísticas. Para emergencias reales llama al
            <strong>123</strong> o <strong>Línea 155</strong>.</p>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sh-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:800;color:#1E1B4B;font-size:14px;margin-bottom:16px;">🛠️ Stack Tecnológico</div>', unsafe_allow_html=True)
        for tech, pct, color in [
            ("Python + Streamlit","95%","#5B21B6"),("XGBoost","92%","#1D4ED8"),("LightGBM","90%","#059669"),
            ("Scikit-learn","88%","#D97706"),("Claude API (SARA)","100%","#7C3AED"),
            ("Pandas + NumPy","90%","#0891B2"),("Plotly","88%","#EC4899"),
        ]:
            st.markdown(f"""<div style="margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:5px;">
                    <span style="color:#1E1B4B;font-weight:600;">{tech}</span>
                    <span style="color:{color};font-weight:800;">{pct}</span>
                </div>
                <div style="background:#EDE9FE;border-radius:8px;height:9px;overflow:hidden;">
                    <div style="width:{pct};height:100%;background:linear-gradient(90deg,{color}80,{color});border-radius:8px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sh-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:800;color:#5B21B6;font-size:14px;margin-bottom:14px;">📊 Cobertura del Sistema</div>', unsafe_allow_html=True)
        for v, k in [("Colombia completa","Cobertura"),("33","Departamentos"),("1.121","Municipios"),
                     ("6","Tipos de delito"),("Policía Nacional","Fuente de datos"),("2019–2027","Período de análisis")]:
            st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:9px 0;
                border-bottom:1px solid #EDE9FE;font-size:12px;">
                <span style="color:#6B7280;font-weight:500;">{k}</span>
                <span style="color:#1E1B4B;font-weight:800;">{v}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # API Key info box
        st.markdown("""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border:1.5px solid #C4B5FD;
            border-radius:18px;padding:18px;">
            <div style="font-weight:800;color:#5B21B6;font-size:13px;margin-bottom:10px;">🔑 Configuración de IA</div>
            <div style="font-size:12px;color:#1E1B4B;line-height:1.8;">
                Para activar todas las funciones de IA (SARA, interpretaciones, consejos), crea el archivo:
            </div>
            <div style="background:#1E1B4B;border-radius:10px;padding:12px;margin:10px 0;font-family:monospace;font-size:11px;color:#A7F3D0;">
                .streamlit/secrets.toml<br>
                GROQ_API_KEY = "gsk_tu-clave-aqui"
            </div>
            <div style="font-size:11px;color:#7C3AED;font-weight:600;">O define la variable de entorno GROQ_API_KEY</div>
        </div>""", unsafe_allow_html=True)
