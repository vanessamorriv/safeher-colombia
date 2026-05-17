import streamlit as st
import pandas as pd
import numpy as np
import joblib
import warnings
import os
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────
st.set_page_config(
    page_title="SafeHer Colombia",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Fondo general */
.stApp {
    background: #0F0A1E;
    color: #EDE9FE;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #1A1030 !important;
    border-right: 1px solid rgba(124,58,237,0.25);
}
[data-testid="stSidebar"] * { color: #EDE9FE !important; }

/* Títulos */
h1, h2, h3, h4 { color: #EDE9FE !important; font-family: 'DM Sans', sans-serif !important; }

/* Métricas */
[data-testid="metric-container"] {
    background: #1A1030;
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 12px;
    padding: 1rem;
}
[data-testid="stMetricValue"] { color: #A78BFA !important; font-size: 2rem !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: rgba(237,233,254,0.6) !important; }

/* Botones */
.stButton > button {
    background: linear-gradient(135deg, #7C3AED, #A78BFA) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    width: 100%;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(124,58,237,0.4) !important;
}

/* Botón emergencia */
.btn-emerg > button {
    background: linear-gradient(135deg, #DC2626, #EF4444) !important;
    animation: pulseRed 2s infinite;
}
@keyframes pulseRed {
    0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.5); }
    50% { box-shadow: 0 0 0 12px rgba(239,68,68,0); }
}

/* Selectboxes e inputs */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div > input,
[data-testid="stTextArea"] textarea {
    background: rgba(124,58,237,0.08) !important;
    border: 1px solid rgba(124,58,237,0.3) !important;
    border-radius: 10px !important;
    color: #EDE9FE !important;
}

/* Cards personalizadas */
.card {
    background: #1A1030;
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-danger {
    background: rgba(220,38,38,0.08);
    border: 1px solid rgba(220,38,38,0.3);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-success {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 16px;
    padding: 1.2rem;
}
.card-warn {
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 16px;
    padding: 1.2rem;
}
.nivel-badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 50px;
    font-weight: 700;
    font-size: 1rem;
    margin: 4px 0;
}
.proba-bar-container {
    background: rgba(124,58,237,0.1);
    border-radius: 6px;
    height: 10px;
    overflow: hidden;
    margin: 4px 0;
}
.chat-msg-user {
    background: rgba(124,58,237,0.3);
    border-radius: 12px 12px 4px 12px;
    padding: 10px 16px;
    margin: 6px 0;
    text-align: right;
    color: #EDE9FE;
}
.chat-msg-ia {
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 12px 12px 12px 4px;
    padding: 10px 16px;
    margin: 6px 0;
    color: #EDE9FE;
    line-height: 1.6;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #EDE9FE, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.15;
    margin-bottom: 1rem;
}
.subtexto {
    color: rgba(237,233,254,0.6);
    font-size: 1.05rem;
    line-height: 1.7;
}
.linea-div {
    border: none;
    border-top: 1px solid rgba(124,58,237,0.2);
    margin: 1.2rem 0;
}
/* Ocultar menú hamburguesa y footer de streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# CARGAR MODELOS
# ─────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def cargar_modelos():
    pre_grav  = joblib.load(os.path.join(BASE, 'preprocessor_gravedad.pkl'))
    xgb_grav  = joblib.load(os.path.join(BASE, 'xgb_gravedad.pkl'))
    lgbm_grav = joblib.load(os.path.join(BASE, 'pipe_lgbm_gravedad.pkl'))
    le_grav   = joblib.load(os.path.join(BASE, 'le_target_gravedad.pkl'))
    enc_zona  = joblib.load(os.path.join(BASE, 'encoders_zona.pkl'))
    xgb_zona  = joblib.load(os.path.join(BASE, 'xgb_zona.pkl'))
    lgbm_zona = joblib.load(os.path.join(BASE, 'lgbm_zona.pkl'))
    le_zona   = joblib.load(os.path.join(BASE, 'le_target_zona.pkl'))
    df_geo    = pd.read_excel(os.path.join(BASE, 'departamentos_municipios_unicos.xlsx'))
    return pre_grav, xgb_grav, lgbm_grav, le_grav, enc_zona, xgb_zona, lgbm_zona, le_zona, df_geo

with st.spinner('Cargando modelos...'):
    pre_grav, xgb_grav, lgbm_grav, le_grav, enc_zona, xgb_zona, lgbm_zona, le_zona, df_geo = cargar_modelos()

DEPTOS       = sorted(df_geo['DEPARTAMENTO_HECHO'].unique().tolist())
DEPTO_MUNIC  = df_geo.groupby('DEPARTAMENTO_HECHO')['MUNICIPIO_HECHO'].apply(sorted).to_dict()
GRUPOS_DELITO  = list(enc_zona['GRUPO_DELITO'].classes_)
SEXOS          = list(enc_zona['SEXO'].classes_)
GRUPOS_ETARIOS = list(enc_zona['GRUPO_ETARIO'].classes_)

NIVEL_COLOR = {
    'MÍNIMO':'#10B981','MUY BAJO':'#34D399','BAJO':'#60A5FA',
    'MEDIO-BAJO':'#FCD34D','MEDIO-ALTO':'#F59E0B','ALTO':'#EF4444',
    'MUY ALTO':'#DC2626','CRÍTICO':'#7F1D1D',
}
NIVEL_ICON = {
    'MÍNIMO':'🟢','MUY BAJO':'🟢','BAJO':'🔵','MEDIO-BAJO':'🟡',
    'MEDIO-ALTO':'🟠','ALTO':'🔴','MUY ALTO':'🔴','CRÍTICO':'⚫',
}

# ─────────────────────────────────────────
# FUNCIONES PREDICCIÓN
# ─────────────────────────────────────────
def predecir_gravedad(depto, munic, delito, sexo, etario, anio, modelo='XGBoost'):
    row = pd.DataFrame([{
        'MUNICIPIO_HECHO': munic, 'DEPARTAMENTO_HECHO': depto,
        'GRUPO_DELITO': delito, 'SEXO': sexo,
        'GRUPO_ETARIO': etario, 'AÑO_HECHOS': int(anio)
    }])
    try:
        if modelo == 'XGBoost':
            X = pre_grav.transform(row)
            pred = xgb_grav.predict(X)[0]
            proba = xgb_grav.predict_proba(X)[0]
        else:
            pred = lgbm_grav.predict(row)[0]
            proba = lgbm_grav.predict_proba(row)[0]
        label = le_grav.inverse_transform([pred])[0]
        probas = dict(zip(le_grav.classes_, (proba * 100).round(1)))
        return label, probas
    except Exception as e:
        return f'Error: {e}', {}

def predecir_zona(depto, munic, delito, sexo, etario, anio, modelo='XGBoost'):
    row = pd.DataFrame([{
        'DEPARTAMENTO_HECHO': depto, 'MUNICIPIO_HECHO': munic,
        'AÑO_HECHOS': int(anio), 'GRUPO_DELITO': delito,
        'SEXO': sexo, 'GRUPO_ETARIO': etario,
    }])
    try:
        row_enc = row.copy()
        for col in ['DEPARTAMENTO_HECHO','MUNICIPIO_HECHO','GRUPO_DELITO','SEXO','GRUPO_ETARIO']:
            row_enc[col] = enc_zona[col].transform(row_enc[col])
        if modelo == 'XGBoost':
            pred = xgb_zona.predict(row_enc)[0]
            proba = xgb_zona.predict_proba(row_enc)[0]
        else:
            pred = lgbm_zona.predict(row_enc)[0]
            proba = lgbm_zona.predict_proba(row_enc)[0]
        label = le_zona.inverse_transform([pred])[0]
        probas = dict(zip(le_zona.classes_, (proba * 100).round(1)))
        return label, probas
    except Exception as e:
        return f'Error: {e}', {}

def mostrar_barras_probabilidad(probas):
    orden = sorted(probas.keys(), key=lambda x: probas[x], reverse=True)
    for nivel in orden:
        pct = probas[nivel]
        col = NIVEL_COLOR.get(nivel, '#888')
        icono = NIVEL_ICON.get(nivel, '')
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin:4px 0;">
            <span style="min-width:130px;font-size:0.78rem;color:rgba(237,233,254,0.65);">{icono} {nivel}</span>
            <div style="flex:1;background:rgba(124,58,237,0.15);border-radius:6px;height:10px;overflow:hidden;">
                <div style="width:{pct}%;height:100%;background:{col};border-radius:6px;transition:width 0.5s;"></div>
            </div>
            <span style="min-width:42px;font-size:0.78rem;color:{col};text-align:right;font-weight:600;">{pct:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR — NAVEGACIÓN
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 1.5rem;">
        <div style="font-size:2.5rem;">🛡️</div>
        <div style="font-size:1.4rem;font-weight:800;color:#EDE9FE;">SafeHer</div>
        <div style="font-size:0.78rem;color:#A78BFA;margin-top:2px;">Colombia · Sistema IA</div>
    </div>
    <hr style="border-color:rgba(124,58,237,0.2);margin-bottom:1rem;">
    """, unsafe_allow_html=True)

    pagina = st.radio("", [
        "🏠  Inicio",
        "📊  Predicción ML",
        "🗺️  Mapa de Riesgo",
        "🚨  Emergencias",
        "📋  Denuncias",
        "🤖  Apoyo IA",
        "ℹ️  Acerca de",
    ], label_visibility="collapsed")

    st.markdown("<hr style='border-color:rgba(124,58,237,0.2);margin:1.5rem 0 1rem;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.78rem;color:rgba(237,233,254,0.4);text-align:center;">
        Líneas de emergencia<br>
        <span style="color:#EF4444;font-weight:700;font-size:1.1rem;">123</span> Policía &nbsp;|&nbsp;
        <span style="color:#A78BFA;font-weight:700;font-size:1.1rem;">155</span> Mujer
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# PÁGINA: INICIO
# ─────────────────────────────────────────
if "Inicio" in pagina:
    st.markdown("""
    <div style="padding: 2rem 0 1rem;">
        <div style="font-size:0.8rem;color:#A78BFA;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.8rem;">
            Sistema Inteligente de Protección
        </div>
        <div class="hero-title">Protegiendo Mujeres<br>con Inteligencia Artificial</div>
        <p class="subtexto">
            Plataforma de análisis predictivo y apoyo para la seguridad de mujeres en Colombia.
            Modelos de Machine Learning entrenados con datos reales de la Policía Nacional.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📍 Municipios", "1.121", "Cubiertos")
    with col2:
        st.metric("🗺️ Departamentos", "33", "Colombia")
    with col3:
        st.metric("⚖️ Tipos de delito", "6", "Categorías")
    with col4:
        st.metric("🤖 Modelos", "3", "Predictivos")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🧩 Módulos de la Plataforma")

    c1, c2, c3 = st.columns(3)
    modulos = [
        ("📊", "Predicción ML", "Analiza riesgo con XGBoost y LightGBM en tiempo real para cualquier municipio de Colombia."),
        ("🗺️", "Mapa de Riesgo", "Visualiza niveles de peligro predichos por departamento con filtros de delito y año."),
        ("🚨", "Emergencias", "Botones de alerta rápida y líneas de ayuda directas para situaciones de peligro."),
        ("📋", "Denuncias", "Registra hechos de forma anónima y segura con opciones de acompañamiento."),
        ("🤖", "Apoyo IA", "Asistente empático disponible 24/7 para orientación legal y emocional."),
        ("🔒", "Salida Rápida", "Modo discreto disponible en la sección de Emergencias."),
    ]
    for i, (ico, titulo, desc) in enumerate(modulos):
        col = [c1, c2, c3][i % 3]
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;min-height:160px;">
                <div style="font-size:2rem;margin-bottom:8px;">{ico}</div>
                <div style="font-weight:700;color:#EDE9FE;margin-bottom:6px;">{titulo}</div>
                <div style="font-size:0.82rem;color:rgba(237,233,254,0.6);line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card-warn">
        <b>⚠️ Aviso:</b> Esta es una plataforma académica prototipo. Para emergencias reales llama al 
        <b style="color:#EF4444;">123</b> o la Línea Mujer <b style="color:#A78BFA;">155</b> (gratuita, 24/7).
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# PÁGINA: PREDICCIÓN
# ─────────────────────────────────────────
elif "Predicción" in pagina:
    st.markdown("## 📊 Módulo de Predicción ML")
    st.markdown('<p class="subtexto">Ingresa los datos para obtener predicciones de los 3 modelos entrenados con datos reales de Colombia.</p>', unsafe_allow_html=True)
    st.markdown("<hr class='linea-div'>", unsafe_allow_html=True)

    with st.container():
        st.markdown("#### ⚙️ Parámetros de Entrada")
        col1, col2, col3 = st.columns(3)

        with col1:
            depto = st.selectbox("🗺️ Departamento", DEPTOS, index=DEPTOS.index('ANTIOQUIA'))
            munics = DEPTO_MUNIC.get(depto, [])
            munic = st.selectbox("📍 Municipio", munics)
            anio  = st.selectbox("📅 Año", list(range(2015, 2028)), index=8)

        with col2:
            delito = st.selectbox("⚖️ Tipo de Delito", GRUPOS_DELITO, index=GRUPOS_DELITO.index('VIOLENCIA INTRAFAMILIAR'))
            sexo   = st.selectbox("👤 Sexo", SEXOS, index=SEXOS.index('FEMENINO'))
            etario = st.selectbox("🎂 Grupo Etario", GRUPOS_ETARIOS, index=GRUPOS_ETARIOS.index('DE 27 A 59 AÑOS'))

        with col3:
            mod_grav = st.selectbox("🤖 Modelo — Gravedad", ['XGBoost', 'LightGBM'])
            mod_zona = st.selectbox("🤖 Modelo — Zona Riesgo", ['XGBoost', 'LightGBM'])
            st.markdown("<br>", unsafe_allow_html=True)
            predecir = st.button("🔮 Predecir ahora")

    if predecir:
        with st.spinner('Ejecutando modelos...'):
            grav_label, grav_probas = predecir_gravedad(depto, munic, delito, sexo, etario, anio, mod_grav)
            zona_label, zona_probas = predecir_zona(depto, munic, delito, sexo, etario, anio, mod_zona)

        st.markdown("<br>", unsafe_allow_html=True)

        # Resumen
        st.markdown(f"""
        <div class="card" style="border-color:rgba(124,58,237,0.5);background:rgba(124,58,237,0.08);">
            <b style="color:#A78BFA;">📍 Predicción para:</b>
            <span style="color:rgba(237,233,254,0.75);margin-left:8px;">
                {depto} · {munic} · {delito} · {sexo} · {etario} · {anio}
            </span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        # ── Gravedad ──
        with col1:
            col_g = NIVEL_COLOR.get(grav_label, '#888')
            icono_g = NIVEL_ICON.get(grav_label, '🔵')
            st.markdown(f"""
            <div class="card">
                <div style="font-size:0.7rem;color:rgba(237,233,254,0.5);font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">
                    Nivel de Gravedad · {mod_grav}
                </div>
                <div style="font-size:2rem;margin-bottom:4px;">{icono_g}</div>
                <div style="font-size:1.6rem;font-weight:800;color:{col_g};margin-bottom:16px;">{grav_label}</div>
                <hr class="linea-div">
                <div style="font-size:0.78rem;color:rgba(237,233,254,0.5);margin-bottom:8px;">Distribución de probabilidades</div>
            """, unsafe_allow_html=True)
            mostrar_barras_probabilidad(grav_probas)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Zona ──
        with col2:
            col_z = NIVEL_COLOR.get(zona_label, '#888')
            icono_z = NIVEL_ICON.get(zona_label, '🔵')
            st.markdown(f"""
            <div class="card">
                <div style="font-size:0.7rem;color:rgba(237,233,254,0.5);font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">
                    Zona de Riesgo · {mod_zona}
                </div>
                <div style="font-size:2rem;margin-bottom:4px;">{icono_z}</div>
                <div style="font-size:1.6rem;font-weight:800;color:{col_z};margin-bottom:16px;">{zona_label}</div>
                <hr class="linea-div">
                <div style="font-size:0.78rem;color:rgba(237,233,254,0.5);margin-bottom:8px;">Distribución de probabilidades</div>
            """, unsafe_allow_html=True)
            mostrar_barras_probabilidad(zona_probas)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Víctimas ──
        with col3:
            orden_g = ['MÍNIMO','MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO','CRÍTICO']
            orden_z = ['MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO']
            g_idx = orden_g.index(grav_label) + 1 if grav_label in orden_g else 3
            z_idx = orden_z.index(zona_label) + 1 if zona_label in orden_z else 2
            estimado = max(1, g_idx * z_idx)
            rango_min = max(1, estimado - g_idx)
            rango_max = estimado + g_idx * 2
            st.markdown(f"""
            <div class="card">
                <div style="font-size:0.7rem;color:rgba(237,233,254,0.5);font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">
                    Total Víctimas Estimadas
                </div>
                <div style="font-size:0.78rem;color:rgba(237,233,254,0.5);margin-bottom:12px;">
                    Basado en Gravedad + Zona de Riesgo
                </div>
                <div style="font-size:3.5rem;font-weight:800;color:#A78BFA;margin-bottom:4px;">{estimado}</div>
                <div style="font-size:0.82rem;color:rgba(237,233,254,0.5);margin-bottom:16px;">
                    Rango estimado: {rango_min} — {rango_max}
                </div>
                <hr class="linea-div">
                <div style="margin-top:8px;">
                    <div style="font-size:0.75rem;color:rgba(237,233,254,0.5);">Gravedad detectada</div>
                    <div style="color:{NIVEL_COLOR.get(grav_label,'#888')};font-weight:600;">{grav_label}</div>
                </div>
                <div style="margin-top:10px;">
                    <div style="font-size:0.75rem;color:rgba(237,233,254,0.5);">Zona detectada</div>
                    <div style="color:{NIVEL_COLOR.get(zona_label,'#888')};font-weight:600;">{zona_label}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# PÁGINA: MAPA DE RIESGO
# ─────────────────────────────────────────
elif "Mapa" in pagina:
    st.markdown("## 🗺️ Mapa de Riesgo por Departamento")
    st.markdown('<p class="subtexto">Visualiza el nivel de riesgo predicho para cada departamento de Colombia.</p>', unsafe_allow_html=True)
    st.markdown("<hr class='linea-div'>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([2,2,1,1])
    with col1:
        filtro_depto = st.selectbox("Filtrar departamento", ['Todos los departamentos'] + DEPTOS)
    with col2:
        mapa_delito = st.selectbox("Tipo de delito", GRUPOS_DELITO, index=GRUPOS_DELITO.index('VIOLENCIA INTRAFAMILIAR'))
    with col3:
        mapa_anio = st.selectbox("Año", list(range(2015,2028)), index=8)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        generar = st.button("🗺️ Generar")

    if generar:
        deptos_usar = DEPTOS if filtro_depto == 'Todos los departamentos' else [filtro_depto]
        resultados = []
        prog = st.progress(0, text="Calculando predicciones...")
        for i, dep in enumerate(deptos_usar):
            munics = DEPTO_MUNIC.get(dep, [])
            if not munics: continue
            try:
                zona_l, zona_p = predecir_zona(dep, munics[0], mapa_delito, 'FEMENINO', 'DE 27 A 59 AÑOS', mapa_anio)
                grav_l, _      = predecir_gravedad(dep, munics[0], mapa_delito, 'FEMENINO', 'DE 27 A 59 AÑOS', mapa_anio)
                orden_z = ['MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO']
                orden_g = ['MÍNIMO','MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO','CRÍTICO']
                z_s = orden_z.index(zona_l)+1 if zona_l in orden_z else 3
                g_s = orden_g.index(grav_l)+1 if grav_l in orden_g else 3
                resultados.append({'Departamento':dep,'Zona':zona_l,'Gravedad':grav_l,'Score':round((z_s+g_s)/2,1)})
            except: pass
            prog.progress((i+1)/len(deptos_usar), text=f"Procesando {dep}...")
        prog.empty()

        if resultados:
            import plotly.graph_objects as go
            df_r = pd.DataFrame(resultados).sort_values('Score', ascending=False)
            COLOR_MAP = {
                'MUY BAJO':'#10B981','BAJO':'#34D399','MEDIO-BAJO':'#FCD34D',
                'MEDIO-ALTO':'#F59E0B','ALTO':'#EF4444','MUY ALTO':'#DC2626'
            }
            fig = go.Figure(go.Bar(
                x=df_r['Departamento'], y=df_r['Score'],
                marker_color=[COLOR_MAP.get(z,'#888') for z in df_r['Zona']],
                text=df_r['Zona'], textposition='outside',
                hovertemplate='<b>%{x}</b><br>Zona: %{text}<br>Score: %{y}<extra></extra>',
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#EDE9FE',
                title=dict(text=f'Riesgo por Departamento — {mapa_delito} ({mapa_anio})', font=dict(size=15)),
                xaxis=dict(tickangle=-45, gridcolor='rgba(124,58,237,0.1)'),
                yaxis=dict(title='Score de Riesgo', gridcolor='rgba(124,58,237,0.1)'),
                margin=dict(t=60,b=150,l=40,r=20), height=480,
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### 📋 Tabla de Resultados")
            df_r['Color Zona'] = df_r['Zona'].map(NIVEL_ICON)
            st.dataframe(
                df_r[['Departamento','Color Zona','Zona','Gravedad','Score']].rename(columns={'Color Zona':''}),
                use_container_width=True, hide_index=True, height=350
            )

# ─────────────────────────────────────────
# PÁGINA: EMERGENCIAS
# ─────────────────────────────────────────
elif "Emergencias" in pagina:
    st.markdown("## 🚨 Centro de Emergencias")
    st.markdown('<p class="subtexto">Si estás en peligro, selecciona la opción que describe tu situación.</p>', unsafe_allow_html=True)
    st.markdown("<hr class='linea-div'>", unsafe_allow_html=True)

    st.markdown("#### ¿Qué está pasando?")
    col1, col2, col3 = st.columns(3)
    opciones = [
        ("🆘", "Estoy en peligro", "#DC2626"),
        ("👣", "Me están siguiendo", "#D97706"),
        ("🔇", "No puedo hablar", "#7C3AED"),
        ("🚔", "Necesito Policía", "#2563EB"),
        ("🚑", "Necesito Ambulancia", "#059669"),
        ("💬", "Apoyo psicológico", "#7C3AED"),
    ]
    for i, (ico, texto, color) in enumerate(opciones):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(f"""
            <div style="background:{color}15;border:2px solid {color}44;border-radius:16px;
                        padding:1.5rem;text-align:center;cursor:pointer;margin-bottom:0.8rem;">
                <div style="font-size:2.5rem;margin-bottom:8px;">{ico}</div>
                <div style="font-weight:600;color:#EDE9FE;">{texto}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📞 Líneas de Emergencia Colombia")
    c1,c2,c3,c4 = st.columns(4)
    lineas = [
        (c1, "155", "Línea Mujer 24/7", "#A78BFA"),
        (c2, "123", "Policía Nacional", "#60A5FA"),
        (c3, "125", "Defensa Civil", "#34D399"),
        (c4, "132", "Cruz Roja", "#F87171"),
    ]
    for col, num, desc, color in lineas:
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:2.2rem;font-weight:800;color:{color};">{num}</div>
                <div style="font-size:0.82rem;color:rgba(237,233,254,0.6);margin-top:4px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card-warn">
        <b>🔒 Salida Rápida</b><br>
        <span style="color:rgba(237,233,254,0.65);font-size:0.9rem;">
        Si necesitas salir rápidamente de esta página, presiona 
        <kbd style="background:#333;padding:2px 6px;border-radius:4px;">Alt + F4</kbd> o 
        cierra la pestaña del navegador. También puedes ir directamente a 
        <a href="https://www.google.com" target="_blank" style="color:#F59E0B;">Google.com</a>
        </span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# PÁGINA: DENUNCIAS
# ─────────────────────────────────────────
elif "Denuncias" in pagina:
    st.markdown("## 📋 Registro de Denuncia")
    st.markdown('<p class="subtexto">Registra un hecho de forma segura. Puedes hacerlo de forma anónima.</p>', unsafe_allow_html=True)
    st.markdown("<hr class='linea-div'>", unsafe_allow_html=True)

    anonimo = st.checkbox("🔒 Denuncia anónima (recomendado)", value=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        den_delito = st.selectbox("⚖️ Tipo de delito", GRUPOS_DELITO)
    with col2:
        den_depto = st.selectbox("🗺️ Departamento", DEPTOS, key='den_depto')
    with col3:
        den_munic = st.text_input("📍 Municipio", placeholder="Escribe el municipio...")

    col4, col5 = st.columns(2)
    with col4:
        den_fecha = st.date_input("📅 Fecha aproximada")
    with col5:
        den_hora = st.text_input("🕐 Hora aproximada", placeholder="Ej: 10:30 PM")

    den_desc = st.text_area("📝 Descripción del hecho",
        placeholder="Describe lo que ocurrió con el mayor detalle posible...",
        height=120)

    st.markdown("**Opciones adicionales:**")
    opciones_den = st.multiselect("", [
        "Solicitar acompañamiento",
        "Solicitar apoyo psicológico",
        "Tengo evidencia (fotos/audio/video)"
    ])

    if st.button("📤 Enviar Denuncia"):
        if den_desc:
            st.markdown("""
            <div class="card-success">
                <b>✅ Denuncia registrada exitosamente</b><br>
                <span style="color:rgba(237,233,254,0.7);font-size:0.9rem;">
                Tu reporte ha sido recibido. Para denuncias oficiales dirígete a la Fiscalía 
                General de la Nación o llama a la Línea 155.
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Por favor escribe una descripción del hecho.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card-warn">
        <b>⚠️ Importante:</b> Esta plataforma es un prototipo académico. Para denuncias oficiales 
        dirígete a la <b>Fiscalía General de la Nación</b>, la <b>Policía Nacional</b> o llama 
        a la <b>Línea 155</b> (atención a mujeres, gratuita 24/7).
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# PÁGINA: APOYO IA
# ─────────────────────────────────────────
elif "Apoyo" in pagina:
    st.markdown("## 🤖 Apoyo con Inteligencia Artificial")
    st.markdown('<p class="subtexto">Estoy aquí para orientarte y acompañarte. Todo lo que compartas es confidencial.</p>', unsafe_allow_html=True)
    st.markdown("<hr class='linea-div'>", unsafe_allow_html=True)

    RESPUESTAS = {
        'denunci':  '📋 Para denunciar en Colombia puedes ir a la Fiscalía General de la Nación, la Comisaría de Familia más cercana, o usar la Línea 155 (gratuita, 24/7). También puedes registrar tu denuncia aquí en SafeHer de forma anónima.',
        'sigu':     '🔒 Si crees que te están siguiendo: cambia de ruta, entra a un lugar concurrido, llama a alguien de confianza. Si el peligro es inmediato marca el 123. Activa el botón de emergencia en esta app.',
        'psicolog': '💜 Entiendo que puedes estar pasando por un momento difícil. Colombia tiene la Línea 137 de Salud Mental, gratuita y confidencial. También puedes acceder al ICBF al 01800-112-137. Estoy aquí contigo.',
        'derecho':  '⚖️ Tienes derecho a vivir una vida libre de violencia (Ley 1257 de 2008), a recibir atención prioritaria en salud, a la confidencialidad en tu denuncia y a medidas de protección inmediata.',
        'peligro':  '🚨 Si estás en peligro INMEDIATO, llama al 123 ahora. Si no puedes hablar, envía tu ubicación a alguien de confianza.',
        'apoyo':    '💜 Estoy aquí para escucharte. Lo que te pasa no es tu culpa. Mereces sentirte segura y protegida. ¿Quieres que te oriente sobre recursos de apoyo emocional o ayuda legal?',
        'ayuda':    '🤝 Puedo ayudarte con: dónde denunciar, qué hacer si te siguen, apoyo psicológico, tus derechos legales o cómo actuar en una emergencia. ¿Qué necesitas?',
    }

    def responder(msg):
        m = msg.lower()
        for clave, resp in RESPUESTAS.items():
            if clave in m: return resp
        return '💬 Gracias por escribirme. Puedo orientarte sobre: dónde denunciar, qué hacer si te siguen, apoyo psicológico, tus derechos o emergencias. ¿Qué necesitas hoy?'

    if 'chat_historia' not in st.session_state:
        st.session_state.chat_historia = []

    # Preguntas rápidas
    st.markdown("**Preguntas frecuentes:**")
    qc1, qc2, qc3, qc4 = st.columns(4)
    preguntas_rapidas = [
        (qc1, "¿Dónde denuncio?"),
        (qc2, "¿Qué hago si me siguen?"),
        (qc3, "Necesito apoyo emocional"),
        (qc4, "¿Cuáles son mis derechos?"),
    ]
    for col, pregunta in preguntas_rapidas:
        with col:
            if st.button(pregunta, key=f"q_{pregunta}"):
                st.session_state.chat_historia.append({'user': pregunta, 'ia': responder(pregunta)})

    st.markdown("<br>", unsafe_allow_html=True)

    # Área del chat
    st.markdown('<div class="card" style="min-height:320px;">', unsafe_allow_html=True)
    st.markdown("""
    <div class="chat-msg-ia">
        🤖 Hola, soy la IA de apoyo de SafeHer 💜 Estoy aquí para ayudarte. 
        Puedes preguntarme sobre dónde denunciar, cómo pedir ayuda, qué hacer en 
        una situación de riesgo, o simplemente hablar si lo necesitas.
    </div>
    """, unsafe_allow_html=True)

    for h in st.session_state.chat_historia:
        st.markdown(f'<div class="chat-msg-user">👤 {h["user"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-msg-ia">{h["ia"]}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    col_inp, col_btn = st.columns([5, 1])
    with col_inp:
        user_input = st.text_input("", placeholder="Escribe aquí... (Ej: ¿Dónde puedo denunciar?)",
                                   label_visibility="collapsed", key="chat_input")
    with col_btn:
        enviar = st.button("Enviar ➤")

    if enviar and user_input.strip():
        st.session_state.chat_historia.append({'user': user_input, 'ia': responder(user_input)})
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📞 Recursos de Ayuda")
    rc1, rc2, rc3 = st.columns(3)
    recursos = [
        (rc1, "155", "Línea Mujer 24/7", "#A78BFA"),
        (rc2, "137", "Salud Mental", "#34D399"),
        (rc3, "01800-112-137", "ICBF Nacional", "#FCD34D"),
    ]
    for col, num, desc, color in recursos:
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:1.5rem;font-weight:800;color:{color};">{num}</div>
                <div style="font-size:0.8rem;color:rgba(237,233,254,0.6);margin-top:4px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# PÁGINA: ACERCA DE
# ─────────────────────────────────────────
elif "Acerca" in pagina:
    st.markdown("## ℹ️ Acerca de SafeHer Colombia")

    st.markdown("""
    <div class="card">
        <h4 style="color:#A78BFA;margin-bottom:0.8rem;">🎓 Proyecto Académico</h4>
        <p style="color:rgba(237,233,254,0.7);line-height:1.7;font-size:0.95rem;">
        Desarrollado como proyecto de Analítica y Machine Learning. Los modelos fueron entrenados 
        con datos del Sistema de Información Estadístico, Delincuencial, Contravencional y 
        Operativo de la Policía Nacional de Colombia.
        </p>
        <br>
        <b style="color:#EDE9FE;">Autoras:</b>
        <ul style="color:rgba(237,233,254,0.7);margin-top:6px;line-height:2;">
            <li>Laura Sofia Beltrán</li>
            <li>Dana Yaray Vargas</li>
            <li>Vanessa Mora</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🤖 Modelos de Machine Learning")
    modelos_info = [
        ("Nivel de Gravedad", "XGBoost + LightGBM", "8 clases: MÍNIMO → CRÍTICO",
         "Municipio, Departamento, Delito, Sexo, Grupo Etario, Año"),
        ("Zona de Riesgo", "XGBoost + LightGBM", "6 clases: MUY BAJO → MUY ALTO",
         "Municipio, Departamento, Delito, Sexo, Grupo Etario, Año"),
        ("Total de Víctimas", "Estimación combinada", "Valor numérico estimado",
         "Basado en Gravedad + Zona de Riesgo"),
    ]
    for titulo, algos, target, features in modelos_info:
        st.markdown(f"""
        <div class="card" style="margin-bottom:0.8rem;">
            <div style="font-weight:700;color:#EDE9FE;margin-bottom:4px;">{titulo}</div>
            <div style="font-size:0.82rem;color:#A78BFA;margin-bottom:4px;">Algoritmos: {algos}</div>
            <div style="font-size:0.82rem;color:rgba(237,233,254,0.6);">Target: {target}</div>
            <div style="font-size:0.8rem;color:rgba(237,233,254,0.45);margin-top:4px;">Features: {features}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card-warn">
        <b>⚠️ Limitaciones importantes</b><br>
        <span style="color:rgba(237,233,254,0.7);font-size:0.9rem;">
        Esta es una plataforma académica prototipo. Las predicciones son aproximaciones estadísticas 
        y NO deben usarse como única fuente de decisión en situaciones reales de riesgo. 
        Para emergencias siempre llama al <b style="color:#EF4444;">123</b> o la 
        <b style="color:#A78BFA;">Línea Mujer 155</b> (gratuita, 24/7).
        </span>
    </div>
    """, unsafe_allow_html=True)
