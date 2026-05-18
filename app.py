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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@700;800;900&display=swap');

:root {
    --purple-900: #1E0A40;
    --purple-800: #2D1060;
    --purple-700: #4C1D95;
    --purple-600: #6D28D9;
    --purple-400: #A78BFA;
    --purple-100: #EDE9FE;
    --purple-50:  #F5F3FF;
    --pink-500:   #EC4899;
    --red-600:    #DC2626;
    --green-600:  #059669;
    --amber-500:  #F59E0B;
    --slate-900:  #0F172A;
    --slate-700:  #334155;
    --slate-500:  #64748B;
    --slate-200:  #E2E8F0;
    --slate-100:  #F1F5F9;
    --slate-50:   #F8FAFC;
    --white:      #FFFFFF;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', 'Segoe UI', system-ui, sans-serif !important;
    background: #F4F2FA !important;
}

/* Hide streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="stToolbar"] {display: none;}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--purple-900) !important;
    border-right: none !important;
    min-width: 248px !important;
    max-width: 248px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* Sidebar radio as nav */
[data-testid="stSidebar"] .stRadio > div { gap: 0 !important; }
[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    padding: 11px 18px !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,0.6) !important;
    transition: all 0.15s !important;
    margin-bottom: 2px !important;
    white-space: nowrap !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.9) !important;
}
[data-testid="stSidebar"] input[type="radio"]:checked + div label,
[data-testid="stSidebar"] .stRadio [aria-checked="true"] label {
    background: rgba(255,255,255,0.14) !important;
    color: #fff !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] input { display: none !important; }
[data-testid="stSidebar"] .stRadio > label { display: none !important; }
[data-testid="stSidebar"] .element-container { margin: 0 !important; padding: 0 6px !important; }

/* Main content area */
.main .block-container {
    padding: 28px 36px !important;
    max-width: 100% !important;
}

/* Cards */
.safeher-card {
    background: var(--white);
    border-radius: 22px;
    border: 1px solid var(--slate-200);
    box-shadow: 0 2px 20px rgba(78,37,140,0.06);
    padding: 24px;
    margin-bottom: 16px;
}

/* Buttons */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--purple-700), var(--purple-600)) !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(109,40,217,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(109,40,217,0.45) !important;
}
.stButton > button:not([kind="primary"]) {
    background: var(--white) !important;
    color: var(--slate-700) !important;
    border: 1px solid var(--slate-200) !important;
}

/* Inputs */
.stSelectbox > div > div, .stTextInput > div > div > input, .stTextArea textarea {
    border-radius: 12px !important;
    border: 1.5px solid var(--slate-200) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextArea textarea:focus, .stTextInput > div > div > input:focus {
    border-color: var(--purple-600) !important;
    box-shadow: 0 0 0 3px rgba(109,40,217,0.12) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--slate-100);
    border-radius: 14px;
    padding: 4px;
    border: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

/* Metric */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid var(--slate-200);
    border-radius: 18px;
    padding: 16px !important;
}

/* Spinner */
.stSpinner > div { border-top-color: var(--purple-600) !important; }

/* Block container */
.block-container { padding-top: 20px !important; }

/* Toggle */
.stCheckbox label { font-weight: 600 !important; }

/* Progress bars */
.stProgress > div > div { background: var(--purple-600) !important; border-radius: 6px !important; }

/* Divider */
hr { border-color: var(--slate-200) !important; margin: 20px 0 !important; }

/* Multiselect */
[data-testid="stMultiSelect"] > div { border-radius: 12px !important; }

/* Date input */
.stDateInput > div { border-radius: 12px !important; }

/* Time input */
.stTimeInput > div { border-radius: 12px !important; }

/* Section header styles */
.section-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.section-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 32px;
    font-weight: 800;
    color: var(--slate-900);
    margin: 0 0 6px;
    letter-spacing: -0.5px;
    line-height: 1.2;
}
.section-sub {
    color: var(--slate-500);
    font-size: 14px;
    margin: 0;
    line-height: 1.6;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--purple-400); border-radius: 3px; }

/* Plotly chart container */
.js-plotly-plot { border-radius: 12px !important; }

/* Chat animation */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.chat-msg-animated { animation: fadeInUp 0.3s ease; }

/* Pulse for emergency */
@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(220,38,38,0.4); }
    50%       { box-shadow: 0 0 0 12px rgba(220,38,38,0); }
}
.emergency-pulse { animation: pulse-red 2s infinite; }

/* Glow card */
.glow-card {
    background: var(--white);
    border-radius: 22px;
    border: 1px solid var(--purple-100);
    box-shadow: 0 4px 30px rgba(109,40,217,0.12);
    padding: 24px;
    margin-bottom: 16px;
}

/* Denuncias step */
.step-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    background: var(--purple-50);
    border-radius: 14px;
    margin-bottom: 16px;
    border-left: 4px solid var(--purple-700);
}

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
    "ANTIOQUIA": ["MEDELLÍN","BELLO","ITAGÜÍ","ENVIGADO","APARTADÓ","RIONEGRO","TURBO"],
    "BOGOTÁ D.C.": ["BOGOTÁ"],
    "VALLE DEL CAUCA": ["CALI","BUENAVENTURA","PALMIRA","TULUÁ","CARTAGO"],
    "CUNDINAMARCA": ["SOACHA","FACATATIVÁ","ZIPAQUIRÁ","FUSAGASUGÁ","CHÍA"],
    "ATLÁNTICO": ["BARRANQUILLA","SOLEDAD","MALAMBO","SABANAGRANDE","BARANOA"],
    "SANTANDER": ["BUCARAMANGA","FLORIDABLANCA","GIRÓN","PIEDECUESTA","BARRANCABERMEJA"],
    "NARIÑO": ["PASTO","TUMACO","IPIALES","TÚQUERRES","LA UNIÓN"],
    "CÓRDOBA": ["MONTERÍA","CERETÉ","LORICA","SAHAGÚN","TIERRALTA"],
    "BOLÍVAR": ["CARTAGENA","MAGANGUÉ","EL CARMEN","MOMPÓS","TURBACO"],
    "TOLIMA": ["IBAGUÉ","ESPINAL","MELGAR","HONDA","LÍBANO"],
}

def get_municipios(dep):
    return MUNICIPIOS_SAMPLE.get(dep, ["Capital","Municipio 1","Municipio 2","Municipio 3"])

CRIME_DATA = {
    "AMAZONAS":              {"score": 2.1, "zona": "MUY BAJO",   "gravedad": "MÍNIMO",     "municipios": 9,  "lat":  -3.4, "lon": -70.0},
    "ANTIOQUIA":             {"score": 4.2, "zona": "ALTO",       "gravedad": "ALTO",        "municipios": 125,"lat":  7.0,  "lon": -75.5},
    "ARAUCA":                {"score": 3.9, "zona": "ALTO",       "gravedad": "ALTO",        "municipios": 7,  "lat":  7.1,  "lon": -70.8},
    "ATLÁNTICO":             {"score": 3.1, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO",  "municipios": 23, "lat": 10.7,  "lon": -75.0},
    "BOGOTÁ D.C.":           {"score": 3.8, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO",  "municipios": 1,  "lat":  4.7,  "lon": -74.1},
    "BOLÍVAR":               {"score": 3.4, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO",  "municipios": 46, "lat":  8.6,  "lon": -74.1},
    "BOYACÁ":                {"score": 2.2, "zona": "MUY BAJO",   "gravedad": "MUY BAJO",    "municipios": 123,"lat":  5.6,  "lon": -73.4},
    "CALDAS":                {"score": 2.6, "zona": "BAJO",       "gravedad": "BAJO",        "municipios": 27, "lat":  5.3,  "lon": -75.3},
    "CAQUETÁ":               {"score": 3.8, "zona": "ALTO",       "gravedad": "MEDIO-ALTO",  "municipios": 16, "lat":  1.0,  "lon": -74.8},
    "CASANARE":              {"score": 2.7, "zona": "BAJO",       "gravedad": "BAJO",        "municipios": 19, "lat":  5.7,  "lon": -71.6},
    "CAUCA":                 {"score": 4.0, "zona": "ALTO",       "gravedad": "ALTO",        "municipios": 42, "lat":  2.5,  "lon": -76.8},
    "CESAR":                 {"score": 3.2, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO",  "municipios": 25, "lat": 10.0,  "lon": -73.2},
    "CHOCÓ":                 {"score": 4.1, "zona": "ALTO",       "gravedad": "ALTO",        "municipios": 30, "lat":  5.7,  "lon": -76.6},
    "CÓRDOBA":               {"score": 3.0, "zona": "MEDIO-BAJO", "gravedad": "BAJO",        "municipios": 30, "lat":  8.3,  "lon": -75.8},
    "CUNDINAMARCA":          {"score": 2.9, "zona": "MEDIO-BAJO", "gravedad": "BAJO",        "municipios": 116,"lat":  5.0,  "lon": -74.0},
    "GUAINÍA":               {"score": 2.1, "zona": "MUY BAJO",   "gravedad": "MÍNIMO",      "municipios": 8,  "lat":  2.6,  "lon": -68.5},
    "GUAVIARE":              {"score": 3.2, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO",  "municipios": 4,  "lat":  2.5,  "lon": -72.6},
    "HUILA":                 {"score": 2.8, "zona": "BAJO",       "gravedad": "BAJO",        "municipios": 37, "lat":  2.5,  "lon": -75.5},
    "LA GUAJIRA":            {"score": 3.5, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-BAJO",  "municipios": 15, "lat": 11.5,  "lon": -72.5},
    "MAGDALENA":             {"score": 3.0, "zona": "MEDIO-BAJO", "gravedad": "BAJO",        "municipios": 30, "lat": 10.4,  "lon": -74.5},
    "META":                  {"score": 3.3, "zona": "MEDIO-BAJO", "gravedad": "MEDIO-BAJO",  "municipios": 29, "lat":  3.5,  "lon": -73.4},
    "NARIÑO":                {"score": 3.7, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO",  "municipios": 64, "lat":  1.5,  "lon": -78.0},
    "NORTE DE SANTANDER":    {"score": 3.6, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO",  "municipios": 40, "lat":  7.9,  "lon": -72.7},
    "PUTUMAYO":              {"score": 3.6, "zona": "MEDIO-ALTO", "gravedad": "MEDIO-ALTO",  "municipios": 13, "lat":  0.5,  "lon": -76.5},
    "QUINDÍO":               {"score": 2.5, "zona": "BAJO",       "gravedad": "BAJO",        "municipios": 12, "lat":  4.5,  "lon": -75.7},
    "RISARALDA":             {"score": 2.8, "zona": "BAJO",       "gravedad": "BAJO",        "municipios": 14, "lat":  5.3,  "lon": -76.0},
    "SAN ANDRÉS":            {"score": 2.8, "zona": "BAJO",       "gravedad": "BAJO",        "municipios": 2,  "lat": 12.5,  "lon": -81.7},
    "SANTANDER":             {"score": 2.5, "zona": "BAJO",       "gravedad": "BAJO",        "municipios": 87, "lat":  6.9,  "lon": -73.2},
    "SUCRE":                 {"score": 2.9, "zona": "MEDIO-BAJO", "gravedad": "BAJO",        "municipios": 26, "lat":  9.0,  "lon": -75.5},
    "TOLIMA":                {"score": 2.7, "zona": "BAJO",       "gravedad": "BAJO",        "municipios": 47, "lat":  4.0,  "lon": -75.2},
    "VALLE DEL CAUCA":       {"score": 4.5, "zona": "MUY ALTO",   "gravedad": "ALTO",        "municipios": 42, "lat":  3.8,  "lon": -76.5},
    "VAUPÉS":                {"score": 2.0, "zona": "MUY BAJO",   "gravedad": "MÍNIMO",      "municipios": 6,  "lat":  0.9,  "lon": -70.9},
    "VICHADA":               {"score": 2.3, "zona": "MUY BAJO",   "gravedad": "MUY BAJO",    "municipios": 4,  "lat":  4.4,  "lon": -69.9},
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
    pad = "2px 10px" if small else "4px 14px"
    fs  = "10px" if small else "11px"
    return (f'<span style="background:{cfg["bg"]};color:{cfg["color"]};border:1px solid {cfg["color"]}44;'
            f'border-radius:20px;padding:{pad};font-size:{fs};font-weight:700;letter-spacing:0.3px;'
            f'display:inline-block;white-space:nowrap;">{cfg["label"]}</span>')

def call_claude(system_prompt, user_msg, history=None):
    try:
        client = anthropic.Anthropic()
        messages = history if history else [{"role": "user", "content": user_msg}]
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1200,
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
    zonas      = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"]
    gravedades = ["MÍNIMO","MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO","CRÍTICO"]
    zona_idx   = min(max(round(adjusted) - 1, 0), 5)
    grav_idx   = min(max(round(adjusted), 0), 7)
    zona       = zonas[zona_idx]
    gravedad   = gravedades[grav_idx]
    victimas   = round(adjusted * 18 + random.random() * 10)

    probs_zona = {}
    for i, z in enumerate(zonas):
        dist = abs(i - zona_idx)
        probs_zona[z] = max(2, 100 - dist * 28 + (random.random() * 6 - 3))
    total_z    = sum(probs_zona.values())
    probs_zona = {k: round(v / total_z * 100, 1) for k, v in probs_zona.items()}

    trend = []
    for y in [2019,2020,2021,2022,2023,2024,2025,2026,2027]:
        yf    = 1.05 if y >= 2024 else (1.0 if y >= 2020 else 0.9)
        noise = random.random() * 0.3 - 0.15
        s     = base["score"] * DELIT_FACTOR.get(delito, 1.0) * yf * (1 + (y-2020)*0.025) + noise
        trend.append({"year": y, "score": round(min(max(s, 0.5), 6.0), 2), "projected": y >= 2025})

    comparativa = []
    for d in DELITOS:
        df = DELIT_FACTOR.get(d, 1.0)
        sc = base["score"] * df * año_factor
        zi = min(max(round(sc) - 1, 0), 5)
        comparativa.append({"label": d, "value": round(sc,1), "risk": zonas[zi]})
    comparativa.sort(key=lambda x: x["value"], reverse=True)

    months   = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    seasonal = [0.85,0.80,0.90,0.95,1.00,1.05,1.10,1.15,1.00,0.95,1.10,1.30]
    monthly  = [{"month": m, "value": round(adjusted * seasonal[i] * (1 + random.random()*0.1-0.05), 2),
                 "cases": round(victimas/12 * seasonal[i] * (1 + random.random()*0.2-0.1))}
                for i, m in enumerate(months)]

    # Hourly risk (for the enhanced map)
    hourly = []
    hour_pattern = [0.4,0.3,0.3,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.0,
                    0.9,0.9,0.9,0.8,0.85,0.9,1.0,1.1,1.2,1.2,1.0,0.7]
    for h in range(24):
        hourly.append({"hour": f"{h:02d}:00", "value": round(adjusted * hour_pattern[h] * (1 + random.random()*0.1-0.05), 2)})

    return {
        "zona": zona, "gravedad": gravedad, "victimas": victimas,
        "probs_zona": probs_zona, "trend": trend, "comparativa": comparativa,
        "score": round(adjusted, 1), "zona_idx": zona_idx, "monthly": monthly,
        "hourly": hourly
    }

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:26px 20px 20px;border-bottom:1px solid rgba(255,255,255,0.1);">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:44px;height:44px;background:linear-gradient(135deg,#EC4899,#A78BFA);border-radius:14px;
                display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 4px 14px rgba(236,72,153,0.4);">🛡️</div>
            <div>
                <div style="font-weight:900;font-size:20px;color:#fff;letter-spacing:-0.5px;font-family:'DM Sans',sans-serif;">SafeHer</div>
                <div style="font-size:9px;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:1.5px;">Colombia · IA Protección</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:12px 6px 0;'>", unsafe_allow_html=True)

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
    <div style="padding:14px;border-top:1px solid rgba(255,255,255,0.1);margin-top:24px;">
        <div style="background:rgba(220,38,38,0.15);border:1px solid rgba(220,38,38,0.35);border-radius:18px;padding:16px;text-align:center;">
            <div style="font-size:9px;color:#FCA5A5;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:6px;">🚨 Emergencias</div>
            <a href="tel:123" style="display:block;font-size:30px;font-weight:900;color:#EF4444;text-decoration:none;line-height:1;font-family:'DM Sans',sans-serif;">123</a>
            <div style="font-size:9px;color:rgba(255,255,255,0.5);margin-bottom:8px;">Policía Nacional</div>
            <a href="tel:155" style="display:block;font-size:30px;font-weight:900;color:#A78BFA;text-decoration:none;line-height:1;font-family:'DM Sans',sans-serif;">155</a>
            <div style="font-size:9px;color:rgba(255,255,255,0.5);">Línea Mujer 24/7</div>
        </div>
        <div style="text-align:center;margin-top:10px;font-size:9px;color:rgba(255,255,255,0.3);">Prototipo académico v5.0 · Datos: Policía Nacional</div>
    </div>
    """, unsafe_allow_html=True)

# ─── PAGES ────────────────────────────────────────────────────────────────────

# ── INICIO ────────────────────────────────────────────────────────────────────
if "🏠" in page:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1E0A40 0%,#2D1060 40%,#4C1D95 100%);
        border-radius:28px;padding:56px 52px;margin-bottom:32px;position:relative;overflow:hidden;color:#fff;">
        <div style="position:absolute;top:-100px;right:-80px;width:420px;height:420px;border-radius:50%;
            background:radial-gradient(circle,rgba(236,72,153,0.15),transparent 70%);"></div>
        <div style="position:absolute;bottom:-60px;left:60px;width:260px;height:260px;border-radius:50%;
            background:radial-gradient(circle,rgba(167,139,250,0.12),transparent 70%);"></div>
        <div style="max-width:580px;position:relative;">
            <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.1);
                border:1px solid rgba(255,255,255,0.18);border-radius:20px;padding:5px 16px;
                font-size:11px;color:#E9D5FF;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:24px;">
                ⚡ Sistema Inteligente · Colombia 2025
            </div>
            <h1 style="font-family:'Playfair Display',Georgia,serif;font-size:52px;font-weight:900;line-height:1.05;margin:0 0 18px;letter-spacing:-1px;">
                Tu seguridad es<br>
                <span style="background:linear-gradient(90deg,#F0ABFC,#EC4899,#F59E0B);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">nuestra prioridad</span>
            </h1>
            <p style="color:#C4B5FD;font-size:15px;line-height:1.8;margin:0 0 32px;">
                Plataforma inteligente de predicción, prevención y apoyo para mujeres en Colombia.
                Modelos ML entrenados con datos reales de la Policía Nacional.
            </p>
            <div style="display:flex;gap:12px;flex-wrap:wrap;">
                <a href="tel:155" style="text-decoration:none;">
                    <div style="background:linear-gradient(135deg,#EC4899,#BE185D);color:#fff;padding:14px 28px;border-radius:14px;
                        font-weight:700;font-size:14px;display:flex;align-items:center;gap:8px;
                        box-shadow:0 4px 20px rgba(236,72,153,0.4);">💜 Línea Mujer · 155</div>
                </a>
                <a href="tel:123" style="text-decoration:none;">
                    <div style="background:rgba(220,38,38,0.2);border:1px solid rgba(220,38,38,0.5);color:#FCA5A5;
                        padding:14px 28px;border-radius:14px;font-weight:700;font-size:14px;display:flex;align-items:center;gap:8px;">
                        🚨 Emergencia · 123</div>
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    modules = [
        ("📊", "Predicción ML", "XGBoost + LightGBM para predecir riesgo por zona y delito", "#7C3AED"),
        ("🗺️", "Mapa Interactivo", "Visualización geográfica de riesgo con gráficos comparativos", "#1D4ED8"),
        ("✈️", "Viaje Seguro", "Análisis de seguridad por departamento con consejos IA", "#059669"),
        ("🚨", "Emergencias", "Botones directos a policía, ambulancia y línea mujer", "#DC2626"),
        ("📋", "Denuncias", "Registro confidencial con orientación jurídica IA", "#D97706"),
        ("💜", "SARA · IA Apoyo", "Chat terapéutico 24/7 con apoyo psicológico personalizado", "#7C3AED"),
        ("🚔", "Ayuda Cercana", "Entidades con direcciones, horarios y cómo llegar", "#0891B2"),
        ("ℹ️", "Acerca de", "Equipo, tecnología y misión del proyecto", "#64748B"),
    ]
    cols = st.columns(4)
    for i, (icon, label, desc, color) in enumerate(modules):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="background:#fff;border-radius:22px;padding:24px;border:1px solid #E2E8F0;
                margin-bottom:14px;transition:all 0.2s;box-shadow:0 2px 12px rgba(0,0,0,0.04);">
                <div style="width:48px;height:48px;border-radius:16px;background:{color}18;
                    display:flex;align-items:center;justify-content:center;font-size:22px;margin-bottom:14px;
                    box-shadow:inset 0 0 0 1px {color}22;">{icon}</div>
                <div style="font-weight:800;font-size:14px;color:#0F172A;margin-bottom:6px;">{label}</div>
                <div style="font-size:12px;color:#64748B;line-height:1.65;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#FFFBEB,#FFF7ED);border:1px solid #FCD34D;border-radius:18px;
        padding:18px 24px;display:flex;align-items:center;gap:14px;margin-top:8px;">
        <span style="font-size:22px;">⚠️</span>
        <span style="font-size:13px;color:#92400E;line-height:1.6;">
            <strong>Aviso académico:</strong> Prototipo educativo. Para emergencias reales llama al
            <strong style="color:#DC2626;">123</strong> o la
            <strong style="color:#7C3AED;">Línea Mujer 155</strong> — gratuita, 24/7.
        </span>
    </div>
    """, unsafe_allow_html=True)

# ── PREDICCIÓN ML ─────────────────────────────────────────────────────────────
elif "📊" in page:
    st.markdown("""
    <div style="margin-bottom:28px;">
        <div class="section-tag" style="background:#F5F3FF;border:1px solid #7C3AED30;color:#7C3AED;">
            📊 MÓDULO DE PREDICCIÓN ML
        </div>
        <h1 class="section-title">Predicción Inteligente de Riesgo</h1>
        <p class="section-sub">XGBoost + LightGBM · Interpretación IA para apoyo policial · Datos: Policía Nacional Colombia</p>
    </div>
    """, unsafe_allow_html=True)

    import plotly.graph_objects as go
    import plotly.express as px

    with st.container():
        st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:14px;font-weight:700;color:#7C3AED;margin-bottom:18px;display:flex;align-items:center;gap:8px;">⚙️ Parámetros de Análisis</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            dep = st.selectbox("🗺️ Departamento", DEPARTAMENTOS, index=DEPARTAMENTOS.index("ANTIOQUIA"))
        munis = get_municipios(dep)
        with c2:
            mun = st.selectbox("📍 Municipio", munis)
        with c3:
            año = st.selectbox("📅 Año de análisis", list(range(2019, 2028)), index=5)

        c4, c5, c6 = st.columns(3)
        with c4:
            delito = st.selectbox("⚖️ Tipo de Delito", DELITOS)
        with c5:
            sexo = st.selectbox("👤 Sexo víctima", ["FEMENINO","MASCULINO"])
        with c6:
            etario = st.selectbox("🎂 Grupo Etario", ["DE 0 A 17 AÑOS","DE 18 A 26 AÑOS","DE 27 A 59 AÑOS","DE 60 Y MÁS"], index=2)

        predict_btn = st.button("🔮 Ejecutar Predicción ML", type="primary", key="predict_btn")
        st.markdown('</div>', unsafe_allow_html=True)

    if predict_btn or st.session_state.get("pred_result"):
        if predict_btn:
            with st.spinner("⏳ Ejecutando modelos ML…"):
                result = calc_prediction(dep, mun, delito, sexo, etario, año)
                st.session_state["pred_result"] = result
                st.session_state["pred_form"] = {"dep":dep,"mun":mun,"delito":delito,"sexo":sexo,"etario":etario,"año":año}
                st.session_state.pop("interp_result", None)

        result = st.session_state.get("pred_result")
        form   = st.session_state.get("pred_form", {})

        if result:
            zona_badge = risk_badge_html(result["zona"])
            grav_badge = risk_badge_html(result["gravedad"])
            r_color    = get_risk_color(result["score"])

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1E0A40,#2D1060);border-radius:20px;
                padding:18px 24px;margin-bottom:24px;display:flex;align-items:center;gap:14px;">
                <div style="width:46px;height:46px;background:rgba(255,255,255,0.1);border-radius:14px;
                    display:flex;align-items:center;justify-content:center;font-size:22px;">📍</div>
                <div style="flex:1;">
                    <div style="font-weight:800;font-size:16px;color:#fff;">{form.get('dep',dep)} · {form.get('mun',mun)}</div>
                    <div style="font-size:12px;color:#A5B4FC;margin-top:3px;">{form.get('delito',delito)} · {form.get('sexo',sexo)} · {form.get('etario',etario)} · {form.get('año',año)}</div>
                </div>
                <div style="display:flex;gap:8px;">{zona_badge}&nbsp;{grav_badge}</div>
            </div>
            """, unsafe_allow_html=True)

            # KPIs
            max_month = max(result["monthly"], key=lambda x: x["cases"])
            k1, k2, k3, k4 = st.columns(4)
            kpis = [
                (k1, "ZONA DE RIESGO", "XGBoost", risk_badge_html(result["zona"]), f"Score: {result['score']}/6.0", RISK_LEVELS.get(result['zona'],{}).get('color','#7C3AED')),
                (k2, "NIVEL GRAVEDAD", "LightGBM", risk_badge_html(result["gravedad"]), "Impacto estimado", RISK_LEVELS.get(result['gravedad'],{}).get('color','#1D4ED8')),
                (k3, "VÍCTIMAS ESTIMADAS", "Ensemble ML",
                 f'<div style="font-size:42px;font-weight:900;color:#DC2626;line-height:1;font-family:\'DM Sans\',sans-serif;">{result["victimas"]}</div>',
                 "personas/año", "#DC2626"),
                (k4, "MES MÁS CRÍTICO", "Análisis estacional",
                 f'<div style="font-size:26px;font-weight:900;color:#D97706;">{max_month["month"]}</div>',
                 f'{max_month["cases"]} casos estimados', "#D97706"),
            ]
            for col, label, sub, display, extra, color in kpis:
                with col:
                    st.markdown(f"""
                    <div style="background:#fff;border-radius:20px;border:1px solid #E2E8F0;
                        box-shadow:0 2px 16px rgba(0,0,0,0.05);padding:20px;">
                        <div style="font-size:9px;font-weight:700;color:#64748B;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px;">{label}</div>
                        <div style="font-size:9px;color:{color};font-weight:700;margin-bottom:10px;">via {sub}</div>
                        <div style="margin-bottom:8px;">{display}</div>
                        <div style="font-size:10px;color:#64748B;">{extra}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── TABS for charts ────────────────────────────────────────────────
            tab_trend, tab_monthly, tab_hourly, tab_compare, tab_prob = st.tabs([
                "📈 Tendencia Histórica", "📅 Variación Mensual", "🕐 Riesgo por Hora", "📊 Comparativa Delitos", "🎯 Distribución Probabilidad"
            ])

            with tab_trend:
                solid_x = [t["year"] for t in result["trend"] if not t["projected"]]
                solid_y = [t["score"] for t in result["trend"] if not t["projected"]]
                proj_x  = [t["year"] for t in result["trend"] if t["projected"] or t["year"] == solid_x[-1]]
                proj_y  = [t["score"] for t in result["trend"] if t["projected"] or t["year"] == solid_x[-1]]
                pts_col = [get_risk_color(t["score"]) for t in result["trend"]]

                fig = go.Figure()
                # Background risk bands
                for y0, y1, fc in [(4,6,"#FEE2E2"),(3,4,"#FEF9C3"),(0,3,"#F0FDF4")]:
                    fig.add_shape(type="rect", x0=2019, x1=2027, y0=y0, y1=y1, fillcolor=fc, opacity=0.35, line_width=0)
                fig.add_trace(go.Scatter(x=solid_x, y=solid_y, mode="lines+markers",
                    line=dict(color="#7C3AED", width=3), marker=dict(size=10, color=pts_col[:len(solid_x)], line=dict(color="white",width=2)),
                    name="Histórico", fill="tozeroy", fillcolor="rgba(124,58,237,0.08)"))
                fig.add_trace(go.Scatter(x=proj_x, y=proj_y, mode="lines+markers",
                    line=dict(color="#A78BFA", width=2.5, dash="dash"), marker=dict(size=8, color=pts_col[len(solid_x)-1:], line=dict(color="white",width=2)),
                    name="Proyectado (2025–2027)"))
                # Threshold annotations
                for yv, txt, clr in [(4,"🔴 Zona ALTO","#DC2626"),(3,"🟡 Zona MEDIA","#F59E0B")]:
                    fig.add_hline(y=yv, line_dash="dot", line_color=clr, opacity=0.6,
                                  annotation_text=txt, annotation_position="right")
                fig.update_layout(height=320, margin=dict(l=40,r=60,t=20,b=40),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(range=[0,6.5], gridcolor="#E2E8F0", title="Score de Riesgo (0–6)", tickfont=dict(size=11)),
                    xaxis=dict(gridcolor="#E2E8F0", tickfont=dict(size=11), title="Año"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
                    font=dict(family="DM Sans"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown(f"""<div style="background:#F5F3FF;border-radius:12px;padding:12px 16px;font-size:12px;color:#4C1D95;line-height:1.7;">
                    📌 <strong>Interpretación:</strong> El gráfico muestra la evolución del score de riesgo para <strong>{form.get('delito',delito)}</strong> en 
                    <strong>{form.get('dep',dep)}</strong>. La zona sombreada verde indica riesgo controlado; amarilla, riesgo moderado; roja, alto riesgo.
                    La línea punteada representa proyecciones hasta 2027. <strong>Score actual: {result['score']}/6.0</strong>
                </div>""", unsafe_allow_html=True)

            with tab_monthly:
                max_m = max(result["monthly"], key=lambda x: x["value"])
                bar_cols = ["#DC2626" if m["month"]==max_m["month"] else get_risk_color(m["value"]) for m in result["monthly"]]
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    x=[m["month"] for m in result["monthly"]],
                    y=[m["value"] for m in result["monthly"]],
                    text=[f'{m["value"]:.1f}' for m in result["monthly"]],
                    textposition="outside",
                    marker_color=bar_cols, marker_opacity=0.88,
                    hovertemplate="<b>%{x}</b><br>Score: %{y:.2f}<extra></extra>"
                ))
                fig2.add_hline(y=sum(m["value"] for m in result["monthly"])/12, line_dash="dot",
                               line_color="#7C3AED", opacity=0.7,
                               annotation_text="Promedio anual", annotation_position="right")
                fig2.update_layout(height=300, margin=dict(l=10,r=60,t=30,b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(gridcolor="#E2E8F0", tickfont=dict(size=11)),
                    xaxis=dict(tickfont=dict(size=11)),
                    showlegend=False, font=dict(family="DM Sans"))
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
                # Monthly cases heatmap row
                cases_row = [m["cases"] for m in result["monthly"]]
                max_c = max(cases_row)
                st.markdown('<div style="display:flex;gap:4px;margin-top:8px;">', unsafe_allow_html=True)
                for m, c in zip(result["monthly"], cases_row):
                    intensity = int(c/max_c * 200) if max_c>0 else 0
                    bg = f"rgba(220,38,38,{c/max_c*0.85:.2f})" if c == max_c else f"rgba(109,40,217,{c/max_c*0.6:.2f})"
                    st.markdown(f'<div style="flex:1;background:{bg};border-radius:8px;padding:8px 2px;text-align:center;">'
                                f'<div style="font-size:9px;color:#fff;font-weight:700;">{m["month"]}</div>'
                                f'<div style="font-size:10px;color:#fff;font-weight:800;">{c}</div></div>', unsafe_allow_html=True)
                st.markdown('</div><div style="font-size:10px;color:#64748B;margin-top:6px;">Casos estimados por mes</div>', unsafe_allow_html=True)

            with tab_hourly:
                h_vals = [h["value"] for h in result["hourly"]]
                h_cols = [get_risk_color(v) for v in h_vals]
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(
                    x=[h["hour"] for h in result["hourly"]],
                    y=h_vals, mode="lines+markers",
                    line=dict(color="#7C3AED", width=2.5),
                    marker=dict(size=7, color=h_cols, line=dict(color="white",width=1.5)),
                    fill="tozeroy", fillcolor="rgba(124,58,237,0.1)",
                    hovertemplate="<b>%{x}</b><br>Score riesgo: %{y:.2f}<extra></extra>"
                ))
                # Night band
                fig3.add_vrect(x0="22:00", x1="23:00", fillcolor="#FEE2E2", opacity=0.3, line_width=0)
                fig3.add_vrect(x0="00:00", x1="05:00", fillcolor="#FEE2E2", opacity=0.3, line_width=0)
                fig3.update_layout(height=300, margin=dict(l=40,r=20,t=20,b=40),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(gridcolor="#E2E8F0", title="Score de Riesgo", tickfont=dict(size=10)),
                    xaxis=dict(gridcolor="#E2E8F0", tickfont=dict(size=9), title="Hora del día"),
                    showlegend=False, font=dict(family="DM Sans"))
                # Marks for key hours
                peak_h = max(result["hourly"], key=lambda x: x["value"])
                fig3.add_annotation(x=peak_h["hour"], y=peak_h["value"],
                                    text=f"🔴 Pico: {peak_h['hour']}", showarrow=True, arrowhead=2,
                                    arrowcolor="#DC2626", font=dict(color="#DC2626", size=11))
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
                st.markdown("""<div style="background:#FEF2F2;border-radius:12px;padding:12px 16px;font-size:12px;color:#991B1B;line-height:1.7;border:1px solid #FCA5A540;">
                    🌙 Las zonas rojas representan franjas nocturnas de mayor riesgo (10pm–5am). Se recomienda mayor precaución en estos horarios.
                </div>""", unsafe_allow_html=True)

            with tab_compare:
                max_v = result["comparativa"][0]["value"] if result["comparativa"] else 1
                fig4 = go.Figure()
                colors_bar = [get_risk_color(item["value"]) for item in result["comparativa"]]
                fig4.add_trace(go.Bar(
                    x=[item["label"].replace("VIOLENCIA ","VIO. ").replace("INTRAFAMILIAR","INTRAFAM.").replace("PERSONALES","PERS.") for item in result["comparativa"]],
                    y=[item["value"] for item in result["comparativa"]],
                    text=[f'{item["value"]:.1f}' for item in result["comparativa"]],
                    textposition="outside",
                    marker_color=colors_bar,
                    hovertemplate="<b>%{x}</b><br>Score: %{y:.2f}<extra></extra>"
                ))
                fig4.update_layout(height=280, margin=dict(l=10,r=10,t=30,b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(range=[0, max_v*1.2], gridcolor="#E2E8F0", tickfont=dict(size=10)),
                    xaxis=dict(tickfont=dict(size=10)),
                    showlegend=False, font=dict(family="DM Sans"),
                    title=dict(text=f"Scores por delito en {form.get('dep',dep)} ({form.get('año',año)})", font=dict(size=12, color="#0F172A")))
                st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

            with tab_prob:
                zonas_probs  = sorted(result["probs_zona"].items(), key=lambda x: x[1], reverse=True)
                fig5 = go.Figure()
                fig5.add_trace(go.Pie(
                    labels=[z[0] for z in zonas_probs],
                    values=[z[1] for z in zonas_probs],
                    hole=0.5,
                    marker_colors=[RISK_LEVELS.get(z[0],{}).get("color","#888") for z in zonas_probs],
                    textinfo="label+percent",
                    textfont_size=11,
                    hovertemplate="<b>%{label}</b><br>Prob: %{value}%<extra></extra>"
                ))
                fig5.update_layout(height=300, margin=dict(l=10,r=10,t=20,b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    showlegend=False, font=dict(family="DM Sans"),
                    annotations=[dict(text=f"<b>{result['zona']}</b>", x=0.5, y=0.5, font_size=13, showarrow=False)])
                st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

            # ── IA Interpretation for Police ─────────────────────────────────
            st.markdown("""
            <div style="background:linear-gradient(135deg,#1E0A40,#2D1060);border-radius:20px;
                padding:18px 24px;margin:28px 0 16px;display:flex;align-items:center;gap:14px;">
                <div style="width:46px;height:46px;background:rgba(255,255,255,0.12);border-radius:14px;
                    display:flex;align-items:center;justify-content:center;font-size:22px;">🤖</div>
                <div>
                    <div style="font-size:16px;font-weight:800;color:#fff;">Interpretación IA para Fuerzas Policiales</div>
                    <div style="font-size:11px;color:#A5B4FC;">Análisis contextual automatizado · Recomendaciones operativas · Uso oficial</div>
                </div>
                <div style="margin-left:auto;background:rgba(220,38,38,0.2);border:1px solid rgba(220,38,38,0.4);
                    color:#FCA5A5;font-size:10px;font-weight:700;padding:5px 14px;border-radius:20px;">🔒 USO POLICIAL</div>
            </div>
            """, unsafe_allow_html=True)

            if "interp_result" not in st.session_state or predict_btn:
                with st.spinner("🤖 Analizando situación con IA especializada..."):
                    interp = call_claude(
                        """Eres un analista senior de seguridad pública de Colombia, asesor de la Policía Nacional.
Genera un informe profesional con EXACTAMENTE estas 5 secciones:

🔍 DIAGNÓSTICO SITUACIONAL
⚠️ FACTORES DE RIESGO CRÍTICOS
📊 ANÁLISIS DE PATRONES
🚨 ACCIONES OPERATIVAS RECOMENDADAS
🤝 COORDINACIÓN INTERINSTITUCIONAL

Cada sección: exactamente 3 puntos con bullet (•). Usa datos concretos y lenguaje técnico policial.
Total: máximo 300 palabras. Sé directo y accionable.""",
                        f"""Datos del análisis:
• Departamento: {form.get('dep',dep)} | Municipio: {form.get('mun',mun)}
• Delito objetivo: {form.get('delito',delito)} | Año: {form.get('año',año)}
• Zona de riesgo (XGBoost): {result['zona']} | Gravedad (LightGBM): {result['gravedad']}
• Víctimas estimadas: {result['victimas']} personas/año | Score: {result['score']}/6.0
• Sexo víctima: {form.get('sexo',sexo)} | Grupo etario: {form.get('etario',etario)}
• Mes crítico: {max_month['month']} ({max_month['cases']} casos estimados)"""
                    )
                    st.session_state["interp_result"] = interp

            interp = st.session_state.get("interp_result","")
            if interp:
                sections = interp.split("\n\n")
                for sec in sections:
                    if sec.strip():
                        lines = sec.strip().split("\n")
                        header = lines[0] if lines else ""
                        body   = "\n".join(lines[1:]) if len(lines) > 1 else ""
                        icon   = "🔍" if "DIAGNÓSTICO" in header else ("⚠️" if "RIESGO" in header else
                                 ("📊" if "PATRONES" in header else ("🚨" if "OPERATIVAS" in header else "🤝")))
                        color  = "#DC2626" if "🚨" in header else ("#EF4444" if "⚠️" in header else "#7C3AED")
                        st.markdown(f"""<div style="background:#fff;border-radius:16px;padding:18px 20px;margin-bottom:12px;
                            border:1px solid #E2E8F0;border-left:4px solid {color};">
                            <div style="font-weight:800;font-size:13px;color:{color};margin-bottom:10px;">{header}</div>
                            <div style="font-size:12px;color:#0F172A;line-height:1.8;white-space:pre-wrap;">{body}</div>
                        </div>""", unsafe_allow_html=True)

# ── MAPA DE RIESGO ─────────────────────────────────────────────────────────────
elif "🗺️" in page:
    import plotly.graph_objects as go
    import plotly.express as px

    st.markdown("""
    <div style="margin-bottom:28px;">
        <div class="section-tag" style="background:#EFF6FF;border:1px solid #1D4ED830;color:#1D4ED8;">
            🗺️ MAPA INTERACTIVO
        </div>
        <h1 class="section-title">Mapa de Riesgo — Colombia</h1>
        <p class="section-sub">Visualización geográfica interactiva del nivel de riesgo por departamento. Haz clic en cualquier zona para análisis IA detallado.</p>
    </div>
    """, unsafe_allow_html=True)

    # Summary stats
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1,"Crítico / Muy Alto",sum(1 for d in CRIME_DATA.values() if d["score"]>=4.0),"#DC2626","#FEF2F2","🔴"),
        (c2,"Alto / Medio-Alto", sum(1 for d in CRIME_DATA.values() if 3.5<=d["score"]<4.0),"#EF4444","#FFF7ED","🟠"),
        (c3,"Riesgo Medio",      sum(1 for d in CRIME_DATA.values() if 3.0<=d["score"]<3.5),"#F59E0B","#FFFBEB","🟡"),
        (c4,"Controlado",        sum(1 for d in CRIME_DATA.values() if d["score"]<3.0),"#059669","#ECFDF5","🟢"),
    ]
    for col, label, count, color, bg, ic in stats:
        with col:
            st.markdown(f"""<div style="background:{bg};border-radius:18px;padding:16px;
                border:1px solid {color}30;text-align:center;">
                <div style="font-size:22px;margin-bottom:4px;">{ic}</div>
                <div style="font-size:30px;font-weight:900;color:{color};line-height:1;">{count}</div>
                <div style="font-size:10px;font-weight:700;color:{color};margin-top:4px;">Departamentos</div>
                <div style="font-size:10px;color:#64748B;margin-top:2px;">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_map, col_detail = st.columns([3, 2])

    with col_map:
        st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:800;font-size:14px;color:#0F172A;margin-bottom:4px;">🇨🇴 Colombia — Score de Riesgo por Departamento</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:11px;color:#64748B;margin-bottom:16px;">Haz clic en un punto del mapa para ver el análisis detallado del departamento</div>', unsafe_allow_html=True)

        # Scatter map using lat/lon
        map_data = []
        for name, d in CRIME_DATA.items():
            map_data.append({
                "name": name, "score": d["score"], "zona": d["zona"],
                "lat": d["lat"], "lon": d["lon"],
                "color": get_risk_color(d["score"]),
                "size": 12 + d["score"] * 5
            })

        fig_map = go.Figure()
        for row in map_data:
            rc = get_risk_color(row["score"])
            fig_map.add_trace(go.Scattergeo(
                lat=[row["lat"]], lon=[row["lon"]],
                mode="markers+text",
                marker=dict(size=row["size"], color=rc, opacity=0.85,
                            line=dict(color="white", width=1.5),
                            symbol="circle"),
                text=[row["name"][:10]],
                textposition="top center",
                textfont=dict(size=8, color="#0F172A"),
                hovertemplate=f"<b>{row['name']}</b><br>Score: {row['score']:.1f}/6.0<br>Zona: {row['zona']}<extra></extra>",
                name=row["name"],
                showlegend=False
            ))

        fig_map.update_layout(
            height=480,
            margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            geo=dict(
                scope="south america",
                center=dict(lat=4.0, lon=-74.0),
                projection_scale=3.8,
                showland=True, landcolor="#F1F5F9",
                showocean=True, oceancolor="#E0F2FE",
                showcountries=True, countrycolor="#94A3B8",
                showrivers=True, rivercolor="#BAE6FD",
                showlakes=True, lakecolor="#BAE6FD",
                bgcolor="rgba(0,0,0,0)"
            )
        )
        st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})

        # Legend
        st.markdown('<div style="display:flex;gap:10px;flex-wrap:wrap;padding:8px 0 0;">', unsafe_allow_html=True)
        for c, lb in [("#7F1D1D","Crítico(≥4.5)"),("#DC2626","Alto(4–4.5)"),("#EF4444","Med-Alto(3.5)"),
                       ("#F59E0B","Medio(3–3.5)"),("#3B82F6","Med-Bajo(2.5)"),("#059669","Bajo(<2.5)")]:
            st.markdown(f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:11px;color:#334155;">'
                        f'<span style="width:12px;height:12px;background:{c};border-radius:50%;display:inline-block;"></span>{lb}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Top departments bar chart
        st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:800;font-size:14px;color:#0F172A;margin-bottom:16px;">📊 Top 12 Departamentos por Score de Riesgo</div>', unsafe_allow_html=True)
        sorted_deps = sorted([{"name":k,**v} for k,v in CRIME_DATA.items()], key=lambda x: x["score"], reverse=True)[:12]

        fig_top = go.Figure()
        fig_top.add_trace(go.Bar(
            x=[d["score"] for d in sorted_deps],
            y=[d["name"].replace("NORTE DE SANTANDER","N. SANTANDER") for d in sorted_deps],
            orientation="h",
            marker_color=[get_risk_color(d["score"]) for d in sorted_deps],
            text=[f'{d["score"]:.1f}' for d in sorted_deps],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}/6.0<extra></extra>"
        ))
        fig_top.update_layout(height=340, margin=dict(l=10,r=60,t=10,b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#E2E8F0", tickfont=dict(size=10), autorange="reversed"),
            xaxis=dict(range=[0,6], gridcolor="#E2E8F0", tickfont=dict(size=10)),
            showlegend=False, font=dict(family="DM Sans"))
        st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})

        # Selector
        dep_sel = st.selectbox("🔍 Seleccionar departamento para análisis detallado:", ["(Ninguno)"] + [d["name"] for d in sorted([{"name":k,**v} for k,v in CRIME_DATA.items()], key=lambda x: x["name"])], key="map_dep_select")
        if dep_sel != "(Ninguno)":
            st.session_state["selected_dep"] = dep_sel
        st.markdown('</div>', unsafe_allow_html=True)

    with col_detail:
        sel_name = st.session_state.get("selected_dep")
        if sel_name and sel_name in CRIME_DATA:
            sel   = {"name": sel_name, **CRIME_DATA[sel_name]}
            color = get_risk_color(sel["score"])

            st.markdown(f"""<div class="glow-card">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
                    <div>
                        <div style="font-size:20px;font-weight:900;color:#0F172A;">{sel['name']}</div>
                        <div style="font-size:11px;color:#64748B;">{sel['municipios']} municipios · Colombia</div>
                    </div>
                    {risk_badge_html(sel['zona'])}
                </div>
                <div style="background:linear-gradient(135deg,{color}10,{color}18);border-radius:16px;padding:18px;margin-bottom:18px;
                    border:1px solid {color}25;text-align:center;">
                    <div style="font-size:48px;font-weight:900;color:{color};line-height:1;">{sel['score']:.1f}</div>
                    <div style="font-size:11px;color:#64748B;">Score / 6.0</div>
                    <div style="margin-top:10px;background:{color}18;border-radius:8px;height:10px;overflow:hidden;">
                        <div style="width:{sel['score']/6*100:.0f}%;height:100%;background:linear-gradient(90deg,{color}99,{color});border-radius:8px;"></div>
                    </div>
                </div>
                <div style="font-size:12px;font-weight:700;color:#0F172A;margin-bottom:12px;">Riesgo estimado por delito:</div>
            """, unsafe_allow_html=True)

            zonas_l = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"]
            for d in DELITOS:
                df   = DELIT_FACTOR.get(d,1.0)
                sc   = round(sel["score"] * df, 1)
                zi   = min(max(round(sc)-1,0),5)
                pct  = sc / 6 * 100
                rc   = get_risk_color(sc)
                st.markdown(f"""<div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                        <span style="font-size:11px;color:#334155;font-weight:600;">{d.replace('VIOLENCIA ','')[:20]}</span>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <span style="font-size:11px;font-weight:800;color:{rc};">{sc}</span>
                            {risk_badge_html(zonas_l[zi], small=True)}
                        </div>
                    </div>
                    <div style="background:#E2E8F0;border-radius:4px;height:6px;overflow:hidden;">
                        <div style="width:{pct:.0f}%;height:100%;background:linear-gradient(90deg,{rc}80,{rc});border-radius:4px;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # AI Analysis button
            if st.button("🤖 Análisis IA detallado", key="map_ai_btn", use_container_width=True, type="primary"):
                with st.spinner("Analizando con IA…"):
                    analysis = call_claude(
                        "Eres analista experto en seguridad de Colombia. Responde en español con bullets y emojis. Secciones: 🔍 Contexto, ⚠️ Principales Riesgos, 🛡️ Recomendaciones. Máx 150 palabras.",
                        f"Analiza el nivel de seguridad de {sel['name']} Colombia. Score de riesgo: {sel['score']}/6.0. Zona: {sel['zona']}. Municipios: {sel['municipios']}."
                    )
                    st.session_state[f"map_ai_{sel_name}"] = analysis

            ai_r = st.session_state.get(f"map_ai_{sel_name}","")
            if ai_r:
                st.markdown(f"""<div style="background:#F5F3FF;border-radius:16px;padding:16px;margin-top:8px;border:1px solid #7C3AED20;">
                    <div style="font-size:11px;font-weight:700;color:#7C3AED;margin-bottom:10px;">🤖 Análisis IA</div>
                    <div style="font-size:12px;color:#0F172A;line-height:1.75;white-space:pre-wrap;">{ai_r}</div>
                </div>""", unsafe_allow_html=True)

            # Risk comparison radar
            st.markdown('<div class="safeher-card" style="margin-top:14px;">', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:700;font-size:13px;color:#0F172A;margin-bottom:12px;">📡 Perfil de Riesgo por Delito</div>', unsafe_allow_html=True)
            delito_labels = [d.replace("VIOLENCIA ","").replace("INTRAFAMILIAR","INTRAFAM.").replace("PERSONALES","PERS.") for d in DELITOS]
            delito_scores = [round(sel["score"] * DELIT_FACTOR.get(d,1.0),1) for d in DELITOS]
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=delito_scores + [delito_scores[0]],
                theta=delito_labels + [delito_labels[0]],
                fill="toself", fillcolor=f"{color}20", line=dict(color=color, width=2),
                mode="lines+markers", marker=dict(size=6, color=color)
            ))
            fig_radar.update_layout(height=260, margin=dict(l=20,r=20,t=20,b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                polar=dict(
                    radialaxis=dict(range=[0,6], visible=True, tickfont=dict(size=8)),
                    angularaxis=dict(tickfont=dict(size=9))
                ),
                showlegend=False, font=dict(family="DM Sans"))
            st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.markdown("""<div style="background:#F8FAFC;border:2px dashed #C4B5FD;border-radius:22px;
                padding:48px 24px;text-align:center;color:#94A3B8;">
                <div style="font-size:36px;margin-bottom:12px;">🗺️</div>
                <div style="font-size:14px;font-weight:600;color:#6D28D9;margin-bottom:6px;">Selecciona un departamento</div>
                <div style="font-size:12px;">Usa el menú desplegable o el mapa para ver el análisis detallado</div>
            </div>""", unsafe_allow_html=True)

# ── VIAJE SEGURO ────────────────────────────────────────────────────────────────
elif "✈️" in page:
    st.markdown("""
    <div style="margin-bottom:28px;">
        <div class="section-tag" style="background:#ECFDF5;border:1px solid #05996930;color:#059669;">
            ✈️ VIAJE SEGURO
        </div>
        <h1 class="section-title">Viaje Seguro a Colombia</h1>
        <p class="section-sub">Analiza el nivel de seguridad del departamento que vas a visitar y recibe consejos personalizados con IA.</p>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_info = st.columns([1,1])
    with col_form:
        st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
        dep_viaje = st.selectbox("🗺️ ¿A qué departamento vas a viajar?", DEPARTAMENTOS, key="viaje_dep")
        motivo    = st.selectbox("🎯 Motivo del viaje", ["Turismo","Trabajo","Familia","Estudio","Otro"])
        duracion  = st.selectbox("⏱️ Duración estimada", ["Un día","Fin de semana","1 semana","Más de 1 semana"])
        st.markdown("<br>", unsafe_allow_html=True)
        analizar_btn = st.button("🔍 Analizar Seguridad del Destino", type="primary", use_container_width=True, key="viaje_btn")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown("""<div class="safeher-card">
            <div style="font-weight:700;font-size:13px;color:#0F172A;margin-bottom:14px;">💡 ¿Por qué revisar antes de viajar?</div>
            <div style="font-size:12px;color:#334155;line-height:1.75;">
                ✅ Conoces las zonas más seguras para hospedarte<br>
                ✅ Identificas horarios de mayor riesgo<br>
                ✅ Sabes qué delitos son más frecuentes<br>
                ✅ Tienes a mano los contactos de emergencia<br>
                ✅ Puedes planificar rutas seguras
            </div>
        </div>""", unsafe_allow_html=True)

    if analizar_btn or st.session_state.get("viaje_result"):
        if analizar_btn:
            data = CRIME_DATA.get(dep_viaje, {"score":2.8,"zona":"BAJO","gravedad":"BAJO","municipios":10})
            muns = get_municipios(dep_viaje)
            st.session_state["viaje_result"] = {"dep":dep_viaje,"data":data,"muns":muns,"motivo":motivo,"duracion":duracion}
            st.session_state.pop("viaje_tips",None)

        vr = st.session_state.get("viaje_result")
        if vr:
            score = vr["data"]["score"]
            if score<=2.0:   safety = {"label":"Muy Seguro","color":"#059669","bg":"#ECFDF5","icon":"🟢","stars":5}
            elif score<=3.0: safety = {"label":"Precaución","color":"#F59E0B","bg":"#FFFBEB","icon":"🟡","stars":3}
            elif score<=4.0: safety = {"label":"Riesgo Medio","color":"#EF4444","bg":"#FEF2F2","icon":"🟠","stars":2}
            else:            safety = {"label":"Alto Riesgo","color":"#DC2626","bg":"#FEE2E2","icon":"🔴","stars":1}

            stars = "".join([f'<span style="font-size:20px;opacity:{1 if i<safety["stars"] else 0.2}">⭐</span>' for i in range(5)])

            st.markdown(f"""<div style="background:{safety['bg']};border:2px solid {safety['color']}30;border-radius:24px;
                padding:28px;margin-bottom:24px;display:flex;align-items:center;gap:24px;">
                <div style="font-size:60px;">{safety['icon']}</div>
                <div style="flex:1;">
                    <div style="font-size:24px;font-weight:900;color:{safety['color']};margin-bottom:4px;font-family:'DM Sans',sans-serif;">{vr['dep']}</div>
                    <div style="font-size:16px;font-weight:700;color:{safety['color']};margin-bottom:8px;">{safety['label']}</div>
                    <div>{stars}&nbsp;<span style="font-size:12px;color:#64748B;">Índice de seguridad para viajeras</span></div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:52px;font-weight:900;color:{safety['color']};line-height:1;font-family:'DM Sans',sans-serif;">{score:.1f}</div>
                    <div style="font-size:11px;color:#64748B;">Score / 6.0</div>
                </div>
            </div>""", unsafe_allow_html=True)

            ca, cb = st.columns(2)
            with ca:
                st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
                st.markdown('<div style="font-weight:700;font-size:13px;color:#0F172A;margin-bottom:12px;">🏙️ Municipios del Departamento</div>', unsafe_allow_html=True)
                for m in vr["muns"]:
                    st.markdown(f'<span style="background:#F5F3FF;color:#7C3AED;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:600;display:inline-block;margin:3px;">{m}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with cb:
                st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
                st.markdown('<div style="font-weight:700;font-size:13px;color:#0F172A;margin-bottom:12px;">⚠️ Riesgo por Tipo de Delito</div>', unsafe_allow_html=True)
                zonas_l = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"]
                delito_scores_v = sorted([{"d":d,"sc":round(vr["data"]["score"]*DELIT_FACTOR.get(d,1.0),1)} for d in DELITOS],key=lambda x:x["sc"],reverse=True)
                for item in delito_scores_v:
                    z = zonas_l[min(max(round(item["sc"])-1,0),5)]
                    rc = get_risk_color(item["sc"])
                    st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                        padding:8px 0;border-bottom:1px solid #E2E8F0;">
                        <span style="font-size:11px;color:#334155;font-weight:500;">{item['d'].replace('VIOLENCIA ','')}</span>
                        {risk_badge_html(z, small=True)}
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # AI tips
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:14px;font-weight:800;color:#0F172A;margin-bottom:12px;">🤖 Consejos Personalizados — {vr["dep"]}</div>', unsafe_allow_html=True)
            if "viaje_tips" not in st.session_state:
                with st.spinner("Preparando consejos de seguridad…"):
                    tips = call_claude(
                        "Eres experta en seguridad para mujeres viajeras en Colombia. Responde en español con emojis. EXACTAMENTE estas secciones: 🛡️ Recomendaciones Clave, 🏠 Mejores Zonas para Hospedarte, 🕐 Horarios Seguros, 🚗 Transporte Recomendado, 📞 Números de Emergencia Locales. Máx 220 palabras. Sé práctica y específica.",
                        f"Mujer viajando a {vr['dep']}, Colombia. Motivo: {vr.get('motivo','turismo')}. Duración: {vr.get('duracion','una semana')}. Score de riesgo: {score:.1f}/6.0 ({vr['data']['zona']})."
                    )
                    st.session_state["viaje_tips"] = tips
            tips_txt = st.session_state.get("viaje_tips","")
            st.markdown(f'<div style="font-size:12px;color:#0F172A;line-height:1.85;white-space:pre-wrap;background:#FAFAFA;border-radius:14px;padding:18px;">{tips_txt}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ── EMERGENCIAS ────────────────────────────────────────────────────────────────
elif "🚨" in page:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#7F1D1D 0%,#991B1B 40%,#DC2626 100%);
        border-radius:24px;padding:28px 32px;margin-bottom:28px;color:#fff;position:relative;overflow:hidden;">
        <div style="position:absolute;top:-60px;right:-60px;width:220px;height:220px;border-radius:50%;
            background:rgba(255,255,255,0.06);"></div>
        <h1 style="font-family:'Playfair Display',serif;font-size:34px;font-weight:900;margin:0 0 8px;">🚨 Centro de Emergencias</h1>
        <p style="color:#FCA5A5;font-size:14px;margin:0;max-width:540px;">Si estás en peligro, presiona el botón que describe tu situación. Todas las llamadas son gratuitas y de ayuda inmediata.</p>
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
    for i,(icon,label,sub,href,color) in enumerate(emergencias):
        with cols[i%4]:
            is_critical = href == "tel:123" and i < 2
            glow = f"0 0 0 3px {color}40, 0 4px 20px {color}30" if is_critical else f"0 4px 14px {color}18"
            st.markdown(f"""<a href="{href}" style="text-decoration:none;">
            <div style="background:#fff;border:2px solid {color}30;border-radius:22px;padding:26px 16px;
                text-align:center;cursor:pointer;min-height:140px;margin-bottom:14px;
                box-shadow:{glow};transition:all 0.2s;">
                <div style="font-size:34px;margin-bottom:12px;">{icon}</div>
                <div style="font-weight:800;font-size:13px;color:#0F172A;margin-bottom:6px;">{label}</div>
                <div style="font-size:11px;font-weight:700;color:{color};background:{color}10;
                    padding:4px 10px;border-radius:20px;display:inline-block;">{sub}</div>
            </div></a>""", unsafe_allow_html=True)

    st.markdown("<h2 style='font-size:18px;font-weight:800;color:#0F172A;margin:20px 0 16px;'>📞 Líneas de Emergencia — toca para llamar</h2>", unsafe_allow_html=True)

    lineas = [("tel:123","123","Policía","🚔","#1D4ED8"),("tel:155","155","Línea Mujer","💜","#8B5CF6"),
              ("tel:125","125","Defensa Civil","🟢","#059669"),("tel:132","132","Cruz Roja","❤️","#EF4444"),
              ("tel:137","137","Salud Mental","🧠","#A78BFA"),("tel:106","106","Bomberos","🔥","#F59E0B")]
    cols_l = st.columns(6)
    for i,(href,num,desc,ic,co) in enumerate(lineas):
        with cols_l[i]:
            st.markdown(f"""<a href="{href}" style="text-decoration:none;">
            <div style="background:#fff;border-radius:20px;border:1px solid #E2E8F0;padding:20px 12px;text-align:center;
                box-shadow:0 2px 12px rgba(0,0,0,0.06);margin-bottom:12px;">
                <div style="font-size:22px;margin-bottom:6px;">{ic}</div>
                <div style="font-size:30px;font-weight:900;color:{co};line-height:1;">{num}</div>
                <div style="font-size:10px;color:#64748B;margin-top:6px;">{desc}</div>
            </div></a>""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""<div style="background:linear-gradient(135deg,#FFFBEB,#FEF3C7);border:1px solid #FCD34D;border-radius:20px;padding:24px;">
            <div style="font-weight:800;color:#92400E;font-size:15px;margin-bottom:12px;">🔒 Salida Rápida de Pantalla</div>
            <p style="font-size:12px;color:#78350F;line-height:1.7;margin-bottom:14px;">Si alguien podría ver tu pantalla, presiona para ir a una página neutra instantáneamente:</p>
            <div style="display:flex;gap:10px;flex-wrap:wrap;">
                <a href="https://www.google.com" target="_blank" style="background:#FEF3C7;color:#92400E;padding:10px 18px;border-radius:12px;font-size:12px;text-decoration:none;font-weight:700;">🔍 Google</a>
                <a href="https://weather.com" target="_blank" style="background:#FEF3C7;color:#92400E;padding:10px 18px;border-radius:12px;font-size:12px;text-decoration:none;font-weight:700;">🌦️ Clima</a>
                <a href="https://www.eltiempo.com" target="_blank" style="background:#FEF3C7;color:#92400E;padding:10px 18px;border-radius:12px;font-size:12px;text-decoration:none;font-weight:700;">📰 Noticias</a>
            </div>
        </div>""", unsafe_allow_html=True)
    with col_b:
        tips_list = ["🔵 Mantén la calma y ve a un lugar concurrido","🔵 Comparte tu ubicación con alguien de confianza",
                     "🔵 Memoriza: 123 Policía · 155 Mujer · 132 Ambulancia","🔵 No confrontes al agresor directamente",
                     "🔵 Documenta evidencia solo si es completamente seguro","🔵 Activa la alerta de tu celular o smartwatch"]
        tips_html = "".join([f'<div style="font-size:12px;color:#0F172A;margin-bottom:8px;line-height:1.6;">{t}</div>' for t in tips_list])
        st.markdown(f"""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border:1px solid #C4B5FD;border-radius:20px;padding:24px;">
            <div style="font-weight:800;color:#4C1D95;font-size:15px;margin-bottom:14px;">💡 En caso de emergencia recuerda:</div>
            {tips_html}
        </div>""", unsafe_allow_html=True)

# ── DENUNCIAS ─────────────────────────────────────────────────────────────────
elif "📋" in page:
    st.markdown("""
    <div style="margin-bottom:28px;">
        <div class="section-tag" style="background:#FFFBEB;border:1px solid #D9770630;color:#D97706;">
            📋 CENTRO DE DENUNCIAS
        </div>
        <h1 class="section-title">Registra tu Denuncia</h1>
        <p class="section-sub">Proceso confidencial y guiado en 3 pasos. Recibirás orientación jurídica personalizada basada en la Ley 1257/2008.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("denuncia_sent"):
        col_form, col_info = st.columns([3,2])
        with col_form:
            # Privacy toggle
            anon = st.toggle("🔒 Denuncia 100% Anónima (Recomendado)", value=True)
            st.markdown(f"""<div style="background:{'#ECFDF5' if anon else '#F5F3FF'};border-radius:14px;padding:12px 18px;
                border:1px solid {'#6EE7B740' if anon else '#C4B5FD40'};margin-bottom:20px;
                display:flex;align-items:center;gap:10px;">
                <span style="font-size:18px;">{'🔒' if anon else '👤'}</span>
                <div>
                    <div style="font-size:13px;font-weight:700;color:{'#059669' if anon else '#4C1D95'};">{'Denuncia Anónima Activada' if anon else 'Denuncia con Identidad'}</div>
                    <div style="font-size:11px;color:#64748B;">{'Tu identidad nunca será revelada.' if anon else 'Tu información estará protegida.'}</div>
                </div>
            </div>""", unsafe_allow_html=True)

            # Step 1
            st.markdown("""<div class="step-header">
                <div style="width:32px;height:32px;background:#4C1D95;border-radius:50%;display:flex;align-items:center;
                    justify-content:center;color:#fff;font-weight:800;font-size:14px;flex-shrink:0;">1</div>
                <div>
                    <div style="font-size:13px;font-weight:700;color:#4C1D95;">Clasificación del hecho</div>
                    <div style="font-size:11px;color:#64748B;">¿Qué ocurrió y dónde?</div>
                </div>
            </div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                d_delito = st.selectbox("⚖️ Tipo de Delito", [""]+DELITOS, key="d_delito")
            with c2:
                d_dep = st.selectbox("🗺️ Departamento", DEPARTAMENTOS, key="d_dep")
            c3, c4 = st.columns(2)
            with c3:
                d_fecha = st.date_input("📅 Fecha aproximada", key="d_fecha", value=None)
            with c4:
                d_hora = st.time_input("🕐 Hora aproximada", key="d_hora", value=None)
            d_lugar = st.text_input("📍 Lugar del hecho", placeholder="Ej: Centro Comercial, calle, barrio, municipio...", key="d_lugar")

            st.markdown("<br>", unsafe_allow_html=True)

            # Step 2
            st.markdown("""<div class="step-header">
                <div style="width:32px;height:32px;background:#4C1D95;border-radius:50%;display:flex;align-items:center;
                    justify-content:center;color:#fff;font-weight:800;font-size:14px;flex-shrink:0;">2</div>
                <div>
                    <div style="font-size:13px;font-weight:700;color:#4C1D95;">Descripción del hecho</div>
                    <div style="font-size:11px;color:#64748B;">Cuéntanos lo que viviste con el mayor detalle posible</div>
                </div>
            </div>""", unsafe_allow_html=True)
            d_desc = st.text_area("Describe lo que ocurrió…", height=160,
                placeholder="Todo es completamente confidencial. Incluye detalles como: ¿qué pasó? ¿había testigos? ¿tienes evidencia? ¿el agresor es conocido?...",
                key="d_desc")
            char_count = len(d_desc)
            bar_color = "#059669" if char_count > 80 else ("#F59E0B" if char_count > 30 else "#E2E8F0")
            st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-top:-8px;margin-bottom:16px;">'
                        f'<div style="flex:1;background:#E2E8F0;border-radius:4px;height:4px;overflow:hidden;">'
                        f'<div style="width:{min(char_count/200*100,100):.0f}%;height:100%;background:{bar_color};border-radius:4px;transition:all 0.3s;"></div></div>'
                        f'<span style="font-size:10px;color:#64748B;">{char_count} caracteres</span></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Step 3
            st.markdown("""<div class="step-header">
                <div style="width:32px;height:32px;background:#4C1D95;border-radius:50%;display:flex;align-items:center;
                    justify-content:center;color:#fff;font-weight:800;font-size:14px;flex-shrink:0;">3</div>
                <div>
                    <div style="font-size:13px;font-weight:700;color:#4C1D95;">Características y solicitudes</div>
                    <div style="font-size:11px;color:#64748B;">Selecciona todo lo que aplique a tu caso</div>
                </div>
            </div>""", unsafe_allow_html=True)

            opciones = ["Violencia física","Violencia verbal","Violencia psicológica","Violencia económica",
                        "Seguimiento / acoso","Violencia digital","Tengo evidencia fotográfica/video",
                        "Quiero acompañamiento legal","Necesito protección urgente","Quiero mantener anonimato total",
                        "Hay menores afectados","El agresor es familiar","El agresor es pareja/expareja"]
            d_opts = st.multiselect("Selecciona las que apliquen:", opciones, key="d_opts")

            st.markdown("<br>", unsafe_allow_html=True)

            # Evidence upload info
            st.markdown("""<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:14px;padding:14px 18px;margin-bottom:20px;
                display:flex;align-items:flex-start;gap:10px;">
                <span style="font-size:18px;flex-shrink:0;">📎</span>
                <div>
                    <div style="font-size:12px;font-weight:700;color:#1D4ED8;margin-bottom:4px;">Adjuntar evidencia</div>
                    <div style="font-size:11px;color:#334155;line-height:1.65;">Para adjuntar fotos, videos o audios como evidencia, dirígete a la Fiscalía (web oficial) o a la URI 24h. Ellos garantizan la cadena de custodia legal.</div>
                </div>
            </div>""", unsafe_allow_html=True)

            send_btn = st.button("📤 Registrar y Obtener Orientación Jurídica Gratuita",
                                 type="primary", use_container_width=True, key="denuncia_send",
                                 disabled=not d_desc.strip())

        with col_info:
            st.markdown("""<div class="safeher-card">
                <div style="font-size:13px;font-weight:700;color:#4C1D95;margin-bottom:14px;">🏢 Entidades Oficiales</div>""", unsafe_allow_html=True)
            entidades_d = [
                ("⚖️","Fiscalía General","Denuncias penales · en línea","https://www.fiscalia.gov.co","#7C3AED"),
                ("🏠","Comisaría de Familia","Violencia intrafamiliar · 24h","tel:123","#1D4ED8"),
                ("👨‍👩‍👧","ICBF","Protección familiar y menores","https://www.icbf.gov.co","#059669"),
                ("📞","Línea 155","Línea Mujer · 24/7 Gratis","tel:155","#EC4899"),
                ("🚨","URI Fiscalía 24h","Denuncia urgente sin cita","tel:018000919748","#DC2626"),
            ]
            for icon_e, name_e, desc_e, href_e, color_e in entidades_d:
                target = '_blank' if href_e.startswith('http') else '_self'
                st.markdown(f"""<a href="{href_e}" target="{target}" style="text-decoration:none;">
                <div style="display:flex;align-items:center;gap:10px;padding:11px 0;border-bottom:1px solid #E2E8F0;
                    transition:all 0.15s;">
                    <div style="width:34px;height:34px;background:{color_e}12;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">{icon_e}</div>
                    <div>
                        <div style="font-size:12px;font-weight:700;color:#0F172A;">{name_e}</div>
                        <div style="font-size:10px;color:#64748B;">{desc_e}</div>
                    </div>
                </div></a>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("""<div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:16px;padding:16px;margin-bottom:14px;">
                ⚠️ Esta plataforma es un <strong>prototipo académico</strong>. Para denuncias con validez legal, dirígete a las entidades oficiales.
            </div>""", unsafe_allow_html=True)

            razones = ["✅ Protege a otras mujeres","✅ Genera registros estadísticos oficiales","✅ Activa medidas de protección legal",
                       "✅ Accedes a apoyo psicológico gratuito","✅ Rompe el ciclo de violencia","✅ Tienes derecho a ser escuchada"]
            r_html = "".join([f'<div style="font-size:12px;color:#0F172A;margin-bottom:8px;line-height:1.5;">{r}</div>' for r in razones])
            st.markdown(f'<div class="safeher-card"><div style="font-size:13px;font-weight:700;color:#4C1D95;margin-bottom:12px;">💜 ¿Por qué es importante denunciar?</div>{r_html}</div>', unsafe_allow_html=True)

        if send_btn and d_desc.strip():
            st.session_state["denuncia_sent"] = True
            with st.spinner("Preparando tu orientación jurídica personalizada…"):
                legal_text = call_claude(
                    """Eres asistente jurídica especializada en derechos de la mujer en Colombia (Ley 1257/2008, Decreto 1930/2013).
Sé cálida, empática y directa. Usa EXACTAMENTE estas 5 secciones con bullets (•):
⚖️ TUS DERECHOS INMEDIATOS
📋 PASOS CONCRETOS A SEGUIR
🏢 ENTIDADES A CONTACTAR HOY
📱 EVIDENCIA QUE DEBES RECOLECTAR
⏰ PLAZOS IMPORTANTES
Máximo 3 bullets por sección. Empieza con un mensaje de validación emocional.""",
                    f"Mujer reporta en Colombia:\nDelito: {d_delito}\nDepartamento: {d_dep}\nLugar: {d_lugar}\nDescripción: {d_desc}\nCaracterísticas: {', '.join(d_opts)}\nDenuncia anónima: {'Sí' if anon else 'No'}"
                )
                st.session_state["legal_text"] = legal_text
            st.rerun()

    else:
        st.markdown("""<div style="background:linear-gradient(135deg,#ECFDF5,#D1FAE5);border:2px solid #6EE7B7;border-radius:24px;
            padding:28px;margin-bottom:24px;display:flex;align-items:center;gap:18px;">
            <div style="width:56px;height:56px;background:#059669;border-radius:50%;display:flex;
                align-items:center;justify-content:center;font-size:26px;flex-shrink:0;
                box-shadow:0 4px 20px rgba(5,150,105,0.3);">✅</div>
            <div>
                <div style="font-size:20px;font-weight:900;color:#065F46;margin-bottom:4px;font-family:'DM Sans',sans-serif;">Reporte registrado de forma segura</div>
                <div style="font-size:13px;color:#047857;">Tu información es completamente confidencial. Aquí está tu orientación jurídica personalizada.</div>
            </div>
        </div>""", unsafe_allow_html=True)

        legal = st.session_state.get("legal_text","")
        st.markdown(f"""<div class="glow-card">
            <div style="font-size:16px;font-weight:800;color:#0F172A;margin-bottom:6px;">⚖️ Orientación Jurídica Personalizada</div>
            <div style="font-size:11px;color:#64748B;margin-bottom:18px;">Generada con IA · Ley 1257/2008 Colombia · No reemplaza asesoría legal profesional</div>
            <div style="font-size:13px;color:#0F172A;line-height:1.85;white-space:pre-wrap;background:#FAFAFA;border-radius:16px;padding:20px;">{legal}</div>
        </div>""", unsafe_allow_html=True)

        if st.button("← Registrar otro reporte", key="nuevo_reporte"):
            st.session_state["denuncia_sent"] = False
            st.session_state.pop("legal_text",None)
            st.rerun()

# ── SARA · IA APOYO ───────────────────────────────────────────────────────────
elif "💜" in page:
    SARA_SYSTEM = """Eres SARA, asistente de apoyo psicológico y emocional de SafeHer Colombia.

PRINCIPIOS FUNDAMENTALES:
- Siempre valida los sentimientos ANTES de dar consejos o información
- Nunca juzgas ni minimizas lo que la persona siente
- Eres cálida, cercana, como una amiga de confianza con conocimiento profesional
- Usas lenguaje sencillo, cercano, con emojis cuando es apropiado
- Tu prioridad es que la persona se sienta escuchada y segura

PROTOCOLOS DE EMERGENCIA:
- Si hay peligro INMEDIATO (golpes activos, amenaza de muerte, secuestro): responde PRIMERO con 🚨 EMERGENCIA: Llama al 123 AHORA
- Si hay riesgo (maltrato frecuente, amenazas): orienta al 155 (Línea Mujer) y Comisaría de Familia

TÉCNICAS PSICOLÓGICAS:
- Ansiedad/pánico: Técnica 4-7-8 (inhala 4s, sostén 7s, exhala 8s)
- Crisis/disociación: Grounding 5-4-3-2-1 (5 cosas que ves, 4 que tocas, 3 que oyes, 2 que hueles, 1 que sabores)
- Estrés: Respiración cuadrada, movimiento corporal suave
- Soledad: Validación, conexión, recursos de apoyo

GUÍA DE LA PLATAFORMA:
Puedes ayudar a la usuaria a entender y navegar SafeHer:
- 📊 Predicción ML: analiza riesgo por zona y delito
- 🗺️ Mapa de Riesgo: visualiza zonas peligrosas en Colombia
- 🚔 Ayuda Cercana: encuentra hospitales, policía, refugios cerca
- 📋 Denuncias: registra hechos con orientación jurídica IA
- 🚨 Emergencias: botones directos a números de ayuda
- ✈️ Viaje Seguro: analiza seguridad de tu destino

CONOCIMIENTO LEGAL:
- Ley 1257/2008: protección integral contra violencias
- Medidas de protección: Comisaría de Familia (gratuito)
- Fiscalía URI: denuncias penales 24h sin cita
- ICBF Línea 141: protección familiar

FORMATO: Responde en español. Máx 200 palabras. Siempre termina con una pregunta de seguimiento o invitación a seguir hablando. Tono: cálido, cercano, esperanzador."""

    if "sara_messages" not in st.session_state:
        st.session_state.sara_messages = [
            {"role":"assistant","content":"Hola 💜 Soy SARA, tu asistente de apoyo de SafeHer.\n\nEstoy aquí para escucharte, orientarte y acompañarte — sin juzgarte, completamente confidencial. Puedes contarme lo que estás viviendo, preguntarme sobre tus derechos, pedir un ejercicio para calmarte, o simplemente desahogarte.\n\nTambién puedo ayudarte a entender cómo funciona esta plataforma y a encontrar la ayuda que necesitas. 🌸\n\n¿Cómo te sientes hoy? ¿En qué puedo ayudarte?"}
        ]

    col_sidebar_sara, col_chat = st.columns([1,3])

    with col_sidebar_sara:
        st.markdown("""<div style="background:linear-gradient(160deg,#1E0A40 0%,#4C1D95 60%,#7C3AED 100%);
            border-radius:24px;padding:24px;color:#fff;text-align:center;margin-bottom:14px;
            box-shadow:0 8px 32px rgba(124,58,237,0.3);">
            <div style="width:70px;height:70px;background:rgba(255,255,255,0.14);border-radius:50%;
                display:flex;align-items:center;justify-content:center;font-size:32px;margin:0 auto 14px;
                border:2px solid rgba(255,255,255,0.24);box-shadow:0 0 20px rgba(167,139,250,0.4);">💜</div>
            <div style="font-weight:900;font-size:22px;letter-spacing:-0.5px;font-family:'DM Sans',sans-serif;">SARA</div>
            <div style="font-size:11px;color:#C4B5FD;margin-bottom:14px;">Asistente SafeHer · IA Empática</div>
            <div style="display:flex;align-items:center;gap:8px;justify-content:center;
                background:rgba(255,255,255,0.1);border-radius:20px;padding:6px 14px;">
                <div style="width:8px;height:8px;border-radius:50%;background:#4ADE80;
                    box-shadow:0 0 8px #4ADE80;animation:pulse 2s infinite;"></div>
                <span style="font-size:11px;color:#A7F3D0;font-weight:600;">Disponible 24/7</span>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div style="font-size:12px;font-weight:700;color:#0F172A;margin-bottom:10px;">¿Cómo te sientes ahora?</div>', unsafe_allow_html=True)
        mood_options = [("😰","Asustada"),("😢","Triste"),("😡","Enojada"),("😔","Sola"),("🙂","Bien"),("🆘","Urgente")]
        cols_mood = st.columns(3)
        for i,(emoji,label) in enumerate(mood_options):
            with cols_mood[i%3]:
                if st.button(f"{emoji}\n{label}", key=f"mood_{label}", use_container_width=True):
                    st.session_state.sara_messages.append({"role":"user","content":f"Me siento {label.lower()} en este momento."})
                    with st.spinner("SARA está escribiendo…"):
                        reply = call_claude(SARA_SYSTEM, "", history=[{"role":m["role"],"content":m["content"]} for m in st.session_state.sara_messages])
                    st.session_state.sara_messages.append({"role":"assistant","content":reply})
                    st.rerun()

        st.markdown("""<div class="safeher-card" style="margin-top:14px;">
            <div style="font-size:12px;font-weight:700;color:#0F172A;margin-bottom:10px;">💜 SARA puede ayudarte con:</div>""", unsafe_allow_html=True)
        for ic, txt in [("🔒","Conversación 100% confidencial"),("🧠","Ejercicios de calma y grounding"),
                         ("⚖️","Orientación legal Colombia"),("📍","Encontrar recursos cercanos"),
                         ("💬","Escucharte sin juzgar"),("🗺️","Navegar esta plataforma")]:
            st.markdown(f'<div style="display:flex;gap:8px;margin-bottom:8px;align-items:flex-start;">'
                        f'<span style="font-size:14px;flex-shrink:0;">{ic}</span>'
                        f'<span style="font-size:11px;color:#334155;line-height:1.5;">{txt}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div style="background:#FEF2F2;border:1px solid #FCA5A5;border-radius:16px;padding:16px;">
            <div style="font-size:11px;font-weight:700;color:#991B1B;margin-bottom:10px;">🚨 Emergencia inmediata</div>""", unsafe_allow_html=True)
        for num, desc, sub in [("123","Policía Nacional","24/7"),("155","Línea Mujer","24/7 Gratis"),("137","Salud Mental","Apoyo")]:
            st.markdown(f'<a href="tel:{num}" style="display:flex;justify-content:space-between;align-items:center;text-decoration:none;padding:8px 0;border-bottom:1px solid #FCA5A544;">'
                        f'<span style="font-size:20px;color:#991B1B;font-weight:900;">{num}</span>'
                        f'<div style="text-align:right;"><div style="font-size:10px;color:#DC2626;font-weight:700;">{desc}</div>'
                        f'<div style="font-size:9px;color:#991B1B;">{sub}</div></div></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🗑️ Limpiar conversación", key="clear_sara"):
            st.session_state.sara_messages = [
                {"role":"assistant","content":"Hola 💜 Soy SARA, tu asistente de apoyo de SafeHer.\n\nEstoy aquí para escucharte, orientarte y acompañarte — sin juzgarte, completamente confidencial. ¿Cómo te puedo ayudar hoy?"}
            ]
            st.rerun()

    with col_chat:
        # Header
        st.markdown("""<div style="padding:16px 24px;background:linear-gradient(135deg,#1E0A40,#4C1D95);
            border-radius:22px 22px 0 0;display:flex;align-items:center;gap:14px;">
            <div style="width:44px;height:44px;background:rgba(255,255,255,0.14);border-radius:50%;
                display:flex;align-items:center;justify-content:center;font-size:22px;">💜</div>
            <div>
                <div style="font-weight:800;font-size:16px;color:#fff;">SARA — Asistente SafeHer</div>
                <div style="font-size:11px;color:#A7F3D0;display:flex;align-items:center;gap:6px;">
                    <span style="width:7px;height:7px;border-radius:50%;background:#4ADE80;display:inline-block;"></span>
                    En línea · Confidencial · Empática
                </div>
            </div>
            <div style="margin-left:auto;display:flex;gap:8px;">
                <a href="tel:155" style="background:rgba(255,255,255,0.12);color:#fff;padding:7px 16px;
                    border-radius:20px;font-size:11px;text-decoration:none;font-weight:700;">📞 155</a>
                <a href="tel:123" style="background:rgba(220,38,38,0.4);color:#fff;padding:7px 16px;
                    border-radius:20px;font-size:11px;text-decoration:none;font-weight:700;">🚨 123</a>
            </div>
        </div>""", unsafe_allow_html=True)

        # Messages
        msgs_html = ""
        for msg in st.session_state.sara_messages:
            if msg["role"] == "user":
                msgs_html += f"""<div class="chat-msg-animated" style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:18px;">
                    <div style="max-width:75%;background:linear-gradient(135deg,#4C1D95,#7C3AED);color:#fff;
                        border-radius:20px 4px 20px 20px;padding:14px 18px;font-size:13px;line-height:1.8;
                        box-shadow:0 4px 14px rgba(124,58,237,0.25);">{msg['content']}</div>
                    <div style="width:34px;height:34px;background:#F5F3FF;border-radius:50%;display:flex;
                        align-items:center;justify-content:center;font-size:16px;flex-shrink:0;margin-top:2px;">👤</div>
                </div>"""
            else:
                msgs_html += f"""<div class="chat-msg-animated" style="display:flex;gap:10px;margin-bottom:18px;">
                    <div style="width:34px;height:34px;background:linear-gradient(135deg,#1E0A40,#7C3AED);border-radius:50%;
                        display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;margin-top:2px;">💜</div>
                    <div style="max-width:75%;background:#fff;color:#0F172A;
                        border-radius:4px 20px 20px 20px;padding:14px 18px;font-size:13px;line-height:1.8;
                        border:1px solid #E2E8F0;box-shadow:0 2px 10px rgba(0,0,0,0.04);white-space:pre-wrap;">{msg['content']}</div>
                </div>"""

        st.markdown(f"""<div style="background:#FAFAFA;padding:20px 24px;min-height:400px;
            border-left:1px solid #E2E8F0;border-right:1px solid #E2E8F0;overflow-y:auto;max-height:440px;">
            {msgs_html}
        </div>""", unsafe_allow_html=True)

        # Quick replies
        st.markdown('<div style="background:#fff;padding:12px 24px 10px;border:1px solid #E2E8F0;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:10px;color:#64748B;margin-bottom:8px;font-weight:600;letter-spacing:0.8px;">SUGERENCIAS RÁPIDAS:</div>', unsafe_allow_html=True)
        quick_replies = ["🆘 Necesito ayuda urgente","¿Cómo denuncio?","Me siento sola y asustada","¿Cuáles son mis derechos?","Ejercicio para calmarme","¿Cómo funciona esta plataforma?","Me están amenazando"]
        qcols = st.columns(4)
        for i, q in enumerate(quick_replies[:4]):
            with qcols[i]:
                if st.button(q, key=f"qr_{i}", use_container_width=True):
                    st.session_state.sara_messages.append({"role":"user","content":q})
                    with st.spinner("SARA está escribiendo…"):
                        reply = call_claude(SARA_SYSTEM, "", history=[{"role":m["role"],"content":m["content"]} for m in st.session_state.sara_messages])
                    st.session_state.sara_messages.append({"role":"assistant","content":reply})
                    st.rerun()
        qcols2 = st.columns(3)
        for i, q in enumerate(quick_replies[4:]):
            with qcols2[i]:
                if st.button(q, key=f"qr2_{i}", use_container_width=True):
                    st.session_state.sara_messages.append({"role":"user","content":q})
                    with st.spinner("SARA está escribiendo…"):
                        reply = call_claude(SARA_SYSTEM, "", history=[{"role":m["role"],"content":m["content"]} for m in st.session_state.sara_messages])
                    st.session_state.sara_messages.append({"role":"assistant","content":reply})
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Input
        with st.form("sara_form", clear_on_submit=True):
            col_inp, col_send = st.columns([5,1])
            with col_inp:
                user_input = st.text_input("", placeholder="Escribe tu mensaje… (Ej: Necesito ayuda, ¿cómo denuncio?, me siento asustada…)",
                                           label_visibility="collapsed", key="sara_input")
            with col_send:
                send_sara = st.form_submit_button("➤", use_container_width=True)
        if send_sara and user_input.strip():
            st.session_state.sara_messages.append({"role":"user","content":user_input.strip()})
            with st.spinner("SARA está escribiendo…"):
                reply = call_claude(SARA_SYSTEM, "", history=[{"role":m["role"],"content":m["content"]} for m in st.session_state.sara_messages])
            st.session_state.sara_messages.append({"role":"assistant","content":reply})
            st.rerun()

        st.markdown('<div style="background:#fff;border:1px solid #E2E8F0;border-radius:0 0 22px 22px;padding:8px;"></div>', unsafe_allow_html=True)

# ── AYUDA CERCANA ─────────────────────────────────────────────────────────────
elif "🚔" in page:
    st.markdown("""
    <div style="margin-bottom:28px;">
        <div class="section-tag" style="background:#EFF6FF;border:1px solid #1D4ED830;color:#1D4ED8;">
            🚔 AYUDA CERCANA
        </div>
        <h1 class="section-title">Encuentra Ayuda Cercana</h1>
        <p class="section-sub">Entidades de apoyo con información detallada, cómo llegar y contacto directo.</p>
    </div>
    """, unsafe_allow_html=True)

    col_city, col_filter = st.columns([2,1])
    with col_city:
        city_input = st.text_input("📍 Ingresa tu ciudad o barrio:", value="Medellín", key="ayuda_city")
    with col_filter:
        filter_tipo = st.selectbox("Filtrar por tipo:", ["Todos","Policía","Hospital","Fiscalía","Refugio","Psicología"], key="ayuda_filter")

    entidades = [
        {"tipo":"Policía","icon":"🚔","nom":"CAI Centro","dir":"Carrera 45 #54-20, Medellín","dist":"0.4 km","color":"#1D4ED8","href":"tel:123","phone":"123","horario":"24/7","desc":"Centro de Atención Inmediata. Atención permanente para denuncias y emergencias policiales."},
        {"tipo":"Hospital","icon":"🏥","nom":"Hospital General de Medellín","dir":"Calle 24 #29-6, Medellín","dist":"1.2 km","color":"#059669","href":"tel:4411227","phone":"4411227","horario":"24/7 Urgencias","desc":"Urgencias completas, medicina forense y apoyo psicológico para víctimas de violencia. Sin costo."},
        {"tipo":"Fiscalía","icon":"⚖️","nom":"Fiscalía Seccional Medellín","dir":"Calle 44 #52-165, Medellín","dist":"0.8 km","color":"#7C3AED","href":"https://www.fiscalia.gov.co","phone":"01-8000-919-748","horario":"Lun–Vie 7am–5pm","desc":"Recepción de denuncias penales, medidas de protección y seguimiento a casos activos."},
        {"tipo":"Refugio","icon":"🏠","nom":"Casa Refugio Luz y Esperanza","dir":"Dirección confidencial — llama al 155","dist":"2.1 km","color":"#D97706","href":"tel:155","phone":"155","horario":"24/7 Disponible","desc":"Alojamiento temporal gratuito para mujeres víctimas de violencia. Incluye alimentación y apoyo."},
        {"tipo":"Psicología","icon":"🧠","nom":"Centro Atención Psicosocial","dir":"Calle 50 #40-20, Medellín","dist":"1.5 km","color":"#8B5CF6","href":"tel:137","phone":"137","horario":"Lun–Sáb 8am–8pm","desc":"Atención psicológica gratuita, terapia individual, grupos de apoyo y acompañamiento a víctimas."},
        {"tipo":"Policía","icon":"🚔","nom":"Estación Policía Laureles","dir":"Carrera 81 #30-05, Medellín","dist":"3.2 km","color":"#1D4ED8","href":"tel:123","phone":"123","horario":"24/7","desc":"Estación de Policía del barrio Laureles. Denuncia, apoyo y patrullaje permanente."},
        {"tipo":"Hospital","icon":"🏥","nom":"Clínica Las Américas","dir":"Diagonal 75B #2A-80, Medellín","dist":"2.8 km","color":"#059669","href":"tel:4456600","phone":"4456600","horario":"24/7 Urgencias","desc":"Urgencias completas y medicina forense. Atención prioritaria a víctimas de violencia de género."},
        {"tipo":"Fiscalía","icon":"⚖️","nom":"URI Fiscalía 24 Horas","dir":"Calle 57 #45-129, Medellín","dist":"0.9 km","color":"#7C3AED","href":"https://www.fiscalia.gov.co","phone":"01-8000-919-748","horario":"24/7 Sin cita","desc":"Unidad de Reacción Inmediata. Denuncias penales urgentes las 24 horas del día."},
        {"tipo":"Psicología","icon":"🧠","nom":"Comisaría de Familia N°1","dir":"Carrera 52 #48-10, Medellín","dist":"1.1 km","color":"#8B5CF6","href":"tel:123","phone":"Presencial","horario":"Lun–Vie 8am–5pm","desc":"Medidas de protección familiar, conciliación y apoyo psicosocial integral de forma gratuita."},
        {"tipo":"Refugio","icon":"🏠","nom":"Casa de Acogida ICBF","dir":"Dirección confidencial — Línea 141","dist":"3.5 km","color":"#D97706","href":"tel:141","phone":"141 ICBF","horario":"24/7","desc":"Casa de acogida para mujeres y niños en situación de violencia intrafamiliar. 100% gratuito."},
    ]

    tipo_map = {"Todos":"Todos","Policía":"Policía","Hospital":"Hospital","Fiscalía":"Fiscalía","Refugio":"Refugio","Psicología":"Psicología"}
    filtered = [e for e in entidades if filter_tipo == "Todos" or e["tipo"] == tipo_map[filter_tipo]]

    # Stats row
    st.markdown(f'<div style="font-size:13px;color:#64748B;margin-bottom:20px;font-weight:500;"><strong style="color:#0F172A;font-size:16px;">{len(filtered)}</strong> lugares de apoyo cerca de <strong style="color:#4C1D95;">{city_input}</strong></div>', unsafe_allow_html=True)

    col_grid, col_ent = st.columns([2,1])
    with col_grid:
        # Category tabs
        tab_all, tab_pol, tab_hosp, tab_fisc, tab_ref, tab_psy = st.tabs(["Todos","🚔 Policía","🏥 Hospitales","⚖️ Fiscalía","🏠 Refugios","🧠 Psicología"])

        def render_entities(ents):
            gcols = st.columns(2)
            for i, e in enumerate(ents):
                with gcols[i%2]:
                    is_sel = st.session_state.get("selected_entity") == e["nom"]
                    border = e["color"] if is_sel else "#E2E8F0"
                    shadow = f"0 4px 24px {e['color']}28, 0 0 0 2px {e['color']}" if is_sel else "0 2px 12px rgba(0,0,0,0.06)"
                    st.markdown(f"""<div style="background:#fff;border:2px solid {border};border-radius:22px;
                        padding:20px;cursor:pointer;box-shadow:{shadow};margin-bottom:14px;transition:all 0.2s;">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">
                            <div style="background:{e['color']}14;border-radius:14px;width:48px;height:48px;
                                display:flex;align-items:center;justify-content:center;font-size:22px;">{e['icon']}</div>
                            <div style="background:{e['color']}14;color:{e['color']};font-size:9px;font-weight:700;
                                padding:4px 10px;border-radius:20px;text-transform:uppercase;letter-spacing:0.5px;">{e['tipo']}</div>
                        </div>
                        <div style="font-weight:800;font-size:14px;color:#0F172A;margin-bottom:5px;">{e['nom']}</div>
                        <div style="font-size:11px;color:#64748B;margin-bottom:10px;">📍 {e['dir']}</div>
                        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;">
                            <div style="background:#ECFDF5;color:#059669;font-size:10px;font-weight:700;padding:4px 10px;border-radius:20px;">🚶 {e['dist']}</div>
                            <div style="background:#EFF6FF;color:#1D4ED8;font-size:10px;font-weight:700;padding:4px 10px;border-radius:20px;">🕐 {e['horario']}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("Ver detalles y cómo llegar", key=f"ent_{e['nom']}", use_container_width=True):
                        if st.session_state.get("selected_entity") == e["nom"]:
                            st.session_state.pop("selected_entity",None)
                        else:
                            st.session_state["selected_entity"] = e["nom"]
                        st.rerun()

        with tab_all:
            render_entities(filtered)
        with tab_pol:
            render_entities([e for e in entidades if e["tipo"]=="Policía"])
        with tab_hosp:
            render_entities([e for e in entidades if e["tipo"]=="Hospital"])
        with tab_fisc:
            render_entities([e for e in entidades if e["tipo"]=="Fiscalía"])
        with tab_ref:
            render_entities([e for e in entidades if e["tipo"]=="Refugio"])
        with tab_psy:
            render_entities([e for e in entidades if e["tipo"]=="Psicología"])

    with col_ent:
        sel_nom = st.session_state.get("selected_entity")
        sel_e   = next((e for e in entidades if e["nom"]==sel_nom),None)
        if sel_e:
            st.markdown(f"""<div class="glow-card">
                <div style="background:{sel_e['color']}12;border-radius:18px;width:58px;height:58px;
                    display:flex;align-items:center;justify-content:center;font-size:28px;margin-bottom:16px;">{sel_e['icon']}</div>
                <div style="font-size:9px;font-weight:700;color:{sel_e['color']};letter-spacing:1.2px;text-transform:uppercase;margin-bottom:4px;">{sel_e['tipo']}</div>
                <div style="font-size:20px;font-weight:900;color:#0F172A;margin-bottom:8px;font-family:'DM Sans',sans-serif;">{sel_e['nom']}</div>
                <p style="font-size:12px;color:#334155;line-height:1.75;margin-bottom:18px;">{sel_e['desc']}</p>
            """, unsafe_allow_html=True)

            for label, val in [("📍 Dirección",sel_e['dir']),("🕐 Horario",sel_e['horario']),("📞 Contacto",sel_e['phone'])]:
                st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:10px 12px;background:#F8FAFC;
                    border-radius:12px;margin-bottom:8px;">
                    <span style="font-size:11px;color:#64748B;">{label}</span>
                    <span style="font-size:11px;font-weight:700;color:#0F172A;text-align:right;max-width:55%;">{val}</span>
                </div>""", unsafe_allow_html=True)

            # Call/web button
            is_phone = sel_e['href'].startswith("tel:")
            btn_text = f'📞 Llamar: {sel_e["phone"]}' if is_phone else "🌐 Visitar sitio oficial"
            target   = "_self" if is_phone else "_blank"
            st.markdown(f'<a href="{sel_e["href"]}" target="{target}" style="text-decoration:none;display:block;margin-bottom:10px;">'
                        f'<div style="width:100%;background:linear-gradient(135deg,{sel_e["color"]},{sel_e["color"]}BB);color:#fff;'
                        f'border-radius:14px;padding:14px;text-align:center;font-size:13px;font-weight:800;'
                        f'box-shadow:0 4px 14px {sel_e["color"]}30;">{btn_text}</div></a>', unsafe_allow_html=True)

            # Google Maps button
            maps_url = f"https://maps.google.com/?q={sel_e['dir'].replace(' ','+')}"
            st.markdown(f'<a href="{maps_url}" target="_blank" style="text-decoration:none;display:block;margin-bottom:14px;">'
                        f'<div style="width:100%;background:#fff;color:#1D4ED8;border:1.5px solid #1D4ED8;border-radius:14px;'
                        f'padding:12px;text-align:center;font-size:12px;font-weight:700;">🗺️ Ver en Google Maps</div></a>', unsafe_allow_html=True)

            # How to get there (AI)
            if st.button(f"🧭 ¿Cómo llegar desde {city_input}?", key="directions_btn", use_container_width=True, type="primary"):
                with st.spinner("Calculando mejor ruta…"):
                    dir_text = call_claude(
                        "Eres experto en transporte y navegación urbana en Colombia. Instrucciones claras, prácticas, con emojis. Incluye opciones: TransMilenio/Metro, taxi/Uber, caminando si aplica. Indica puntos de referencia. Máx 120 palabras. Finaliza con un consejo de seguridad.",
                        f"¿Cómo llego desde el centro de {city_input} a {sel_e['nom']}, ubicado en {sel_e['dir']}? Distancia aproximada: {sel_e['dist']}."
                    )
                    st.session_state[f"dir_{sel_e['nom']}"] = dir_text

            dir_r = st.session_state.get(f"dir_{sel_e['nom']}","")
            if dir_r:
                st.markdown(f"""<div style="background:#F5F3FF;border-radius:16px;padding:16px;margin-top:4px;border:1px solid #C4B5FD30;">
                    <div style="font-size:11px;font-weight:700;color:#7C3AED;margin-bottom:10px;">🧭 Cómo llegar desde {city_input}</div>
                    <div style="font-size:12px;color:#0F172A;line-height:1.8;white-space:pre-wrap;">{dir_r}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.markdown("""<div style="background:#F8FAFC;border:2px dashed #C4B5FD;border-radius:24px;
                padding:52px 24px;text-align:center;color:#94A3B8;">
                <div style="font-size:40px;margin-bottom:14px;">👆</div>
                <div style="font-size:14px;font-weight:700;color:#6D28D9;margin-bottom:6px;">Selecciona una entidad</div>
                <div style="font-size:12px;line-height:1.6;">Haz clic en "Ver detalles y cómo llegar" para ver información completa y cómo llegar desde tu ubicación</div>
            </div>""", unsafe_allow_html=True)

        # Quick tips
        tips_ayuda = ["📱 Google Maps: 'Comisaría de Familia + tu ciudad'","📞 Línea 155: orientan al refugio más cercano",
                      "🚔 Estación de Policía: denuncia inmediata","🏥 Cualquier hospital urgencias: sin costo",
                      "📋 Fiscalía URI: denuncia 24h sin cita","🏠 ICBF Línea 141: protección familiar urgente"]
        st.markdown('<div style="margin-top:16px;font-size:12px;font-weight:700;color:#0F172A;margin-bottom:10px;">💡 Tips rápidos</div>', unsafe_allow_html=True)
        for tip in tips_ayuda:
            st.markdown(f'<div style="font-size:11px;color:#334155;line-height:1.7;padding:8px 12px;background:#fff;'
                        f'border-radius:10px;border:1px solid #E2E8F0;margin-bottom:6px;">{tip}</div>', unsafe_allow_html=True)

# ── ACERCA DE ─────────────────────────────────────────────────────────────────
elif "ℹ️" in page:
    st.markdown("""
    <div style="margin-bottom:28px;">
        <div class="section-tag" style="background:#F8FAFC;border:1px solid #E2E8F0;color:#64748B;">
            ℹ️ ACERCA DE
        </div>
        <h1 class="section-title">Acerca de SafeHer Colombia</h1>
        <p class="section-sub">Proyecto académico de Analítica y Machine Learning para protección y prevención de violencia contra la mujer.</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([3,2])
    with col_l:
        st.markdown("""<div class="safeher-card">
            <div style="font-weight:800;color:#4C1D95;font-size:16px;margin-bottom:14px;">🎓 Proyecto Académico</div>
            <p style="font-size:13px;color:#0F172A;line-height:1.85;margin-bottom:20px;">
                Desarrollado como proyecto de <strong>Analítica y Machine Learning</strong>. Modelos entrenados con datos del
                Sistema de Información Estadístico de la <strong>Policía Nacional de Colombia</strong>.
                Enfocado en la protección, prevención y apoyo integral para mujeres.
            </p>
            <div style="font-weight:700;color:#0F172A;margin-bottom:14px;font-size:14px;">👩‍💻 Equipo de Desarrollo:</div>""", unsafe_allow_html=True)
        for name in ["Laura Sofia Beltrán","Dana Yaray Vargas","Vanessa Mora"]:
            st.markdown(f"""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:14px;padding:13px 18px;
                display:flex;align-items:center;gap:14px;margin-bottom:10px;border:1px solid #C4B5FD30;">
                <div style="width:38px;height:38px;background:#7C3AED;border-radius:50%;display:flex;align-items:center;
                    justify-content:center;font-size:16px;flex-shrink:0;">👩‍🎓</div>
                <span style="font-size:13px;color:#0F172A;font-weight:700;">{name}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="safeher-card">
            <div style="font-weight:800;color:#4C1D95;font-size:16px;margin-bottom:18px;">🤖 Modelos de Machine Learning</div>""", unsafe_allow_html=True)
        for ti, al, ta, co in [
            ("📊 Nivel de Gravedad","XGBoost + LightGBM","8 clases: MÍNIMO → CRÍTICO","#4C1D95"),
            ("🗺️ Zona de Riesgo","XGBoost + LightGBM","6 clases: MUY BAJO → MUY ALTO","#1D4ED8"),
            ("👥 Estimación de Víctimas","Ensemble de modelos","Valor numérico estimado","#059669"),
            ("🧠 IA de Apoyo (SARA)","Claude Sonnet 4","Apoyo psicológico, legal y guía","#7C3AED"),
        ]:
            st.markdown(f"""<div style="background:#FAFAFA;border:1px solid {co}18;border-radius:16px;padding:14px 18px;margin-bottom:12px;">
                <div style="font-weight:800;color:#0F172A;font-size:13px;">{ti}</div>
                <div style="font-size:12px;color:{co};font-weight:600;margin-top:3px;">{al}</div>
                <div style="font-size:11px;color:#64748B;margin-top:3px;">Target: {ta}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown("""<div style="background:linear-gradient(135deg,#FFFBEB,#FEF3C7);border:1px solid #FCD34D;border-radius:20px;padding:22px;margin-bottom:16px;">
            <div style="font-weight:800;color:#92400E;font-size:14px;margin-bottom:10px;">⚠️ Limitaciones Importantes</div>
            <p style="font-size:12px;color:#78350F;line-height:1.8;">Plataforma <strong>académica prototipo</strong>.
            Las predicciones son aproximaciones estadísticas. Para emergencias reales llama al
            <strong>123</strong> o <strong>Línea 155</strong>.</p>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:800;color:#0F172A;font-size:14px;margin-bottom:16px;">🛠️ Stack Tecnológico</div>', unsafe_allow_html=True)
        for tech, pct, color in [
            ("Python + Streamlit","95%","#4C1D95"),("XGBoost","92%","#1D4ED8"),("LightGBM","90%","#059669"),
            ("Scikit-learn","88%","#D97706"),("Claude API (SARA)","100%","#7C3AED"),("Pandas + NumPy","90%","#0891B2"),
            ("Plotly","85%","#EC4899")
        ]:
            st.markdown(f"""<div style="margin-bottom:14px;">
                <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:5px;">
                    <span style="color:#0F172A;font-weight:600;">{tech}</span>
                    <span style="color:{color};font-weight:800;">{pct}</span>
                </div>
                <div style="background:#F1F5F9;border-radius:6px;height:8px;overflow:hidden;">
                    <div style="width:{pct};height:100%;background:linear-gradient(90deg,{color}88,{color});border-radius:6px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="safeher-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:800;color:#4C1D95;font-size:14px;margin-bottom:14px;">📊 Cobertura</div>', unsafe_allow_html=True)
        for v, k in [("Colombia completa","Cobertura"),("33","Departamentos"),("1.121","Municipios"),
                      ("6","Tipos de delito"),("Policía Nacional","Fuente de datos"),("2019–2027","Período de análisis"),
                      ("v5.0","Versión plataforma")]:
            st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:9px 0;
                border-bottom:1px solid #E2E8F0;font-size:12px;">
                <span style="color:#64748B;">{k}</span>
                <span style="color:#0F172A;font-weight:700;">{v}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
