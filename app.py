import streamlit as st
import pandas as pd
import numpy as np
import joblib
import warnings
import os
import plotly.graph_objects as go
import plotly.express as px
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="SafeHer Colombia",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: #07051A !important;
    color: #EDE9FE !important;
}
.stApp {
    background:
        radial-gradient(ellipse 90% 60% at 15% -5%, rgba(120,40,220,0.22) 0%, transparent 55%),
        radial-gradient(ellipse 70% 50% at 85% 100%, rgba(160,130,255,0.10) 0%, transparent 50%),
        #07051A !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#110A30 0%,#0A071E 100%) !important;
    border-right: 1px solid rgba(130,80,255,0.2) !important;
}
[data-testid="stSidebar"] * { color: #EDE9FE !important; }
[data-testid="stSidebarNav"] { display:none; }
[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border-radius: 12px !important;
    padding: 11px 16px !important;
    cursor: pointer !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: rgba(237,233,254,0.6) !important;
    transition: all 0.2s !important;
    width: 100% !important;
    display: block !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(130,80,255,0.15) !important;
    color: #EDE9FE !important;
}
h1,h2,h3,h4,h5 { font-family:'Syne',sans-serif !important; color:#EDE9FE !important; }
[data-testid="metric-container"] {
    background: linear-gradient(135deg,rgba(130,80,255,0.14),rgba(100,50,200,0.07)) !important;
    border: 1px solid rgba(130,80,255,0.28) !important;
    border-radius: 18px !important;
    padding: 1.2rem !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
[data-testid="metric-container"]:hover { transform:translateY(-3px) !important; box-shadow:0 10px 35px rgba(130,80,255,0.22) !important; }
[data-testid="stMetricValue"] { color:#C4B5FD !important; font-family:'Syne',sans-serif !important; font-size:2.1rem !important; font-weight:800 !important; }
[data-testid="stMetricLabel"] { color:rgba(237,233,254,0.5) !important; font-size:0.78rem !important; }
.stButton > button {
    background: linear-gradient(135deg,#7C3AED,#5B21B6) !important;
    color: white !important; border: none !important;
    border-radius: 14px !important; padding: 0.65rem 1.8rem !important;
    font-weight: 600 !important; font-size: 0.9rem !important;
    font-family: 'Plus Jakarta Sans',sans-serif !important;
    width: 100% !important; transition: all 0.25s !important;
    box-shadow: 0 4px 18px rgba(109,40,217,0.38) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(109,40,217,0.55) !important;
    background: linear-gradient(135deg,#8B5CF6,#7C3AED) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: rgba(130,80,255,0.09) !important;
    border: 1px solid rgba(130,80,255,0.32) !important;
    border-radius: 12px !important; color: #EDE9FE !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(130,80,255,0.09) !important;
    border: 1px solid rgba(130,80,255,0.32) !important;
    border-radius: 12px !important; color: #EDE9FE !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(130,80,255,0.65) !important;
    box-shadow: 0 0 0 3px rgba(130,80,255,0.18) !important;
}
.stMultiSelect > div > div {
    background: rgba(130,80,255,0.09) !important;
    border: 1px solid rgba(130,80,255,0.32) !important;
    border-radius: 12px !important;
}
.stCheckbox label { color: rgba(237,233,254,0.8) !important; font-size:0.9rem !important; }
[data-testid="stDateInput"] input {
    background: rgba(130,80,255,0.09) !important;
    border: 1px solid rgba(130,80,255,0.32) !important;
    border-radius: 12px !important; color: #EDE9FE !important;
}
.stProgress > div > div { background: linear-gradient(90deg,#7C3AED,#A78BFA) !important; border-radius:6px !important; }
.stProgress > div { background: rgba(130,80,255,0.15) !important; border-radius:6px !important; }
#MainMenu, footer, header { visibility:hidden !important; }
[data-testid="stDecoration"] { display:none !important; }
.block-container { padding-top:1.5rem !important; padding-bottom:3rem !important; }
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#07051A; }
::-webkit-scrollbar-thumb { background:rgba(130,80,255,0.4); border-radius:3px; }
hr { border-color:rgba(130,80,255,0.18) !important; margin:1rem 0 !important; }
@keyframes fadeUp { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:translateY(0)} }
@keyframes pulseRed { 0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.55)} 50%{box-shadow:0 0 0 14px rgba(239,68,68,0)} }
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-7px)} }
@keyframes glowPurple { 0%,100%{box-shadow:0 0 22px rgba(130,80,255,0.3)} 50%{box-shadow:0 0 44px rgba(130,80,255,0.6)} }
</style>
""", unsafe_allow_html=True)

# ── MODELOS ──
BASE = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource(show_spinner=False)
def cargar():
    pg  = joblib.load(os.path.join(BASE,'preprocessor_gravedad.pkl'))
    xg  = joblib.load(os.path.join(BASE,'xgb_gravedad.pkl'))
    lg  = joblib.load(os.path.join(BASE,'pipe_lgbm_gravedad.pkl'))
    leg = joblib.load(os.path.join(BASE,'le_target_gravedad.pkl'))
    ez  = joblib.load(os.path.join(BASE,'encoders_zona.pkl'))
    xz  = joblib.load(os.path.join(BASE,'xgb_zona.pkl'))
    lz  = joblib.load(os.path.join(BASE,'lgbm_zona.pkl'))
    lez = joblib.load(os.path.join(BASE,'le_target_zona.pkl'))
    geo = pd.read_excel(os.path.join(BASE,'departamentos_municipios_unicos.xlsx'))
    return pg,xg,lg,leg,ez,xz,lz,lez,geo

with st.spinner('🛡️ Cargando SafeHer...'):
    pg,xg,lg,leg,ez,xz,lz,lez,geo = cargar()

DEPTOS      = sorted(geo['DEPARTAMENTO_HECHO'].unique())
DM          = geo.groupby('DEPARTAMENTO_HECHO')['MUNICIPIO_HECHO'].apply(sorted).to_dict()
DELITOS     = list(ez['GRUPO_DELITO'].classes_)
SEXOS       = list(ez['SEXO'].classes_)
ETARIOS     = list(ez['GRUPO_ETARIO'].classes_)

NC = {'MÍNIMO':'#10B981','MUY BAJO':'#34D399','BAJO':'#60A5FA',
      'MEDIO-BAJO':'#FCD34D','MEDIO-ALTO':'#F59E0B','ALTO':'#EF4444',
      'MUY ALTO':'#DC2626','CRÍTICO':'#7F1D1D'}
NI = {'MÍNIMO':'🟢','MUY BAJO':'🟢','BAJO':'🔵','MEDIO-BAJO':'🟡',
      'MEDIO-ALTO':'🟠','ALTO':'🔴','MUY ALTO':'🔴','CRÍTICO':'⚫'}
NB = {'MÍNIMO':'rgba(16,185,129,0.13)','MUY BAJO':'rgba(52,211,153,0.13)',
      'BAJO':'rgba(96,165,250,0.13)','MEDIO-BAJO':'rgba(252,211,77,0.13)',
      'MEDIO-ALTO':'rgba(245,158,11,0.16)','ALTO':'rgba(239,68,68,0.16)',
      'MUY ALTO':'rgba(220,38,38,0.22)','CRÍTICO':'rgba(127,29,29,0.32)'}

def pred_grav(dep,mun,del_,sex,eta,año,mod):
    r = pd.DataFrame([{'MUNICIPIO_HECHO':mun,'DEPARTAMENTO_HECHO':dep,
                        'GRUPO_DELITO':del_,'SEXO':sex,'GRUPO_ETARIO':eta,'AÑO_HECHOS':int(año)}])
    try:
        if mod=='XGBoost': X=pg.transform(r); p=xg.predict(X)[0]; pr=xg.predict_proba(X)[0]
        else: p=lg.predict(r)[0]; pr=lg.predict_proba(r)[0]
        lab=leg.inverse_transform([p])[0]
        return lab, dict(zip(leg.classes_,(pr*100).round(1)))
    except Exception as e: return f'Error:{e}',{}

def pred_zona(dep,mun,del_,sex,eta,año,mod):
    r = pd.DataFrame([{'DEPARTAMENTO_HECHO':dep,'MUNICIPIO_HECHO':mun,
                        'AÑO_HECHOS':int(año),'GRUPO_DELITO':del_,'SEXO':sex,'GRUPO_ETARIO':eta}])
    try:
        re=r.copy()
        for c in ['DEPARTAMENTO_HECHO','MUNICIPIO_HECHO','GRUPO_DELITO','SEXO','GRUPO_ETARIO']:
            re[c]=ez[c].transform(re[c])
        if mod=='XGBoost': p=xz.predict(re)[0]; pr=xz.predict_proba(re)[0]
        else: p=lz.predict(re)[0]; pr=lz.predict_proba(re)[0]
        lab=lez.inverse_transform([p])[0]
        return lab, dict(zip(lez.classes_,(pr*100).round(1)))
    except Exception as e: return f'Error:{e}',{}

def barras(probas):
    orden = sorted(probas.keys(), key=lambda x:probas[x], reverse=True)
    h=""
    for n in orden:
        p=probas[n]; c=NC.get(n,'#888'); i=NI.get(n,'')
        h+=f"""<div style="display:flex;align-items:center;gap:10px;margin:5px 0;">
<span style="min-width:112px;font-size:0.73rem;color:rgba(237,233,254,0.58);font-family:'Plus Jakarta Sans',sans-serif;">{i} {n}</span>
<div style="flex:1;background:rgba(255,255,255,0.07);border-radius:8px;height:9px;overflow:hidden;">
<div style="width:{p}%;height:100%;background:linear-gradient(90deg,{c}bb,{c});border-radius:8px;"></div></div>
<span style="min-width:38px;font-size:0.73rem;color:{c};text-align:right;font-weight:700;">{p:.1f}%</span></div>"""
    st.markdown(h, unsafe_allow_html=True)

def card(titulo, subtitulo, color="#7C3AED", icono=""):
    return f"""<div style="background:linear-gradient(135deg,{color}14,{color}07);
border:1px solid {color}35;border-radius:20px;padding:1.4rem;height:100%;
transition:all 0.22s;animation:fadeUp 0.5s ease-out;">
<div style="font-size:2rem;margin-bottom:10px;">{icono}</div>
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#EDE9FE;font-size:0.95rem;margin-bottom:5px;">{titulo}</div>
<div style="font-size:0.78rem;color:rgba(237,233,254,0.52);line-height:1.55;">{subtitulo}</div></div>"""

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""<div style="background:linear-gradient(135deg,rgba(120,55,220,0.35),rgba(140,90,255,0.18));
border-bottom:1px solid rgba(130,80,255,0.22);padding:1.8rem 1.2rem 1.4rem;
margin:-1rem -1rem 1.2rem;text-align:center;">
<div style="width:58px;height:58px;margin:0 auto 12px;background:linear-gradient(135deg,#7C3AED,#A78BFA);
border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:1.9rem;
box-shadow:0 8px 28px rgba(109,40,217,0.55);animation:float 3.5s ease-in-out infinite;">🛡️</div>
<div style="font-family:'Syne',sans-serif;font-size:1.45rem;font-weight:800;color:#EDE9FE;letter-spacing:-0.02em;">SafeHer</div>
<div style="font-size:0.7rem;color:#A78BFA;margin-top:3px;letter-spacing:0.14em;text-transform:uppercase;font-weight:600;">Colombia · IA Protección</div>
</div>""", unsafe_allow_html=True)

    pagina = st.radio("", [
        "🏠  Inicio","📊  Predicción ML","🗺️  Mapa de Riesgo",
        "✈️  Viaje Seguro","🚨  Emergencias","📋  Denuncias",
        "🤖  Apoyo IA","🚔  Ayuda Cercana","ℹ️  Acerca de",
    ], label_visibility="collapsed")

    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="background:linear-gradient(135deg,rgba(239,68,68,0.18),rgba(220,38,38,0.09));
border:1px solid rgba(239,68,68,0.32);border-radius:16px;padding:1rem;text-align:center;
animation:pulseRed 2.5s infinite;">
<div style="font-size:0.65rem;color:rgba(237,233,254,0.45);letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px;">🚨 Emergencias</div>
<a href="tel:123" style="text-decoration:none;display:block;font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#EF4444;line-height:1;">123</a>
<div style="font-size:0.68rem;color:rgba(237,233,254,0.4);margin-bottom:8px;">Policía Nacional</div>
<a href="tel:155" style="text-decoration:none;display:block;font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#A78BFA;line-height:1;">155</a>
<div style="font-size:0.68rem;color:rgba(237,233,254,0.4);">Línea Mujer 24/7</div></div>""", unsafe_allow_html=True)

    st.markdown("""<div style="text-align:center;margin-top:.9rem;font-size:0.65rem;color:rgba(237,233,254,0.22);">
Plataforma académica v2.0 · Datos: Policía Nacional</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# INICIO
# ══════════════════════════════════════════
if "Inicio" in pagina:
    st.markdown("""<div style="animation:fadeUp 0.55s ease-out;">
<div style="display:inline-block;background:rgba(130,80,255,0.14);border:1px solid rgba(130,80,255,0.32);
border-radius:50px;padding:5px 18px;font-size:0.72rem;color:#A78BFA;font-weight:600;
letter-spacing:.12em;text-transform:uppercase;margin-bottom:1rem;">⚡ Sistema Inteligente de Protección · Colombia</div>
<div style="font-family:'Syne',sans-serif;font-size:clamp(2rem,5vw,3.6rem);font-weight:800;line-height:1.1;
background:linear-gradient(135deg,#EDE9FE 0%,#C4B5FD 45%,#8B5CF6 100%);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:1rem;">
Protegiendo Mujeres<br>con Inteligencia Artificial</div>
<p style="color:rgba(237,233,254,0.58);font-size:1.02rem;line-height:1.78;max-width:680px;
margin-bottom:2rem;font-weight:300;">
Plataforma de análisis predictivo, apoyo y protección para mujeres en Colombia.
Modelos de Machine Learning entrenados con datos reales de la Policía Nacional —
cobertura de los 33 departamentos y 1.121 municipios del país.</p></div>""", unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    for col,v,l,i in zip([c1,c2,c3,c4,c5],
        ["1.121","33","6","3","24/7"],
        ["Municipios","Departamentos","Tipos delito","Modelos ML","Disponible"],
        ["📍","🗺️","⚖️","🤖","🛡️"]):
        with col: st.metric(f"{i} {l}", v)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:700;
margin-bottom:1.2rem;color:#EDE9FE;">🧩 Módulos disponibles</div>""", unsafe_allow_html=True)

    mods = [
        ("📊","Predicción ML","XGBoost + LightGBM en tiempo real para cualquier municipio","#7C3AED"),
        ("🗺️","Mapa de Riesgo","Riesgo predicho por departamento con gráficas comparativas","#2563EB"),
        ("✈️","Viaje Seguro","Análisis de seguridad por destino antes de viajar","#059669"),
        ("🚨","Emergencias","Alertas rápidas, líneas directas y salida discreta","#DC2626"),
        ("📋","Denuncias","Registro anónimo con acompañamiento legal y psicológico","#D97706"),
        ("🤖","Apoyo IA","Chat 24/7 para orientación legal y emocional","#7C3AED"),
        ("🚔","Ayuda Cercana","Policía, Fiscalía, hospitales y casas refugio","#0891B2"),
        ("🔒","Salida Rápida","Cambio instantáneo de pantalla en situaciones de riesgo","#4B5563"),
    ]
    cols=st.columns(4)
    for i,(ic,ti,de,co) in enumerate(mods):
        with cols[i%4]:
            st.markdown(f"""<div style="background:linear-gradient(135deg,{co}13,{co}06);
border:1px solid {co}30;border-radius:18px;padding:1.4rem;margin-bottom:1rem;min-height:160px;
animation:fadeUp {0.3+i*.07:.2f}s ease-out;">
<div style="font-size:1.8rem;margin-bottom:9px;">{ic}</div>
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#EDE9FE;font-size:0.93rem;margin-bottom:5px;">{ti}</div>
<div style="font-size:0.77rem;color:rgba(237,233,254,0.52);line-height:1.55;">{de}</div></div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background:linear-gradient(135deg,rgba(245,158,11,0.11),rgba(217,119,6,0.06));
border:1px solid rgba(245,158,11,0.28);border-radius:16px;padding:1rem 1.4rem;
display:flex;align-items:center;gap:12px;margin-top:.4rem;">
<span style="font-size:1.35rem;">⚠️</span>
<span style="color:rgba(237,233,254,0.68);font-size:0.87rem;line-height:1.6;">
<b style="color:#FCD34D;">Aviso académico:</b> Plataforma prototipo.
Para emergencias reales llama al <b style="color:#EF4444;">123</b> o la
<b style="color:#A78BFA;">Línea Mujer 155</b> — gratuita, 24/7.</span></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# PREDICCIÓN
# ══════════════════════════════════════════
elif "Predicción" in pagina:
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#EDE9FE;margin-bottom:3px;">
📊 Módulo de Predicción ML</div>
<p style="color:rgba(237,233,254,0.52);font-size:0.93rem;margin-bottom:1.4rem;">
Obtén predicciones en tiempo real con los modelos entrenados con datos reales de Colombia.</p>""", unsafe_allow_html=True)

    with st.container():
        st.markdown("""<div style="background:linear-gradient(135deg,rgba(130,80,255,0.11),rgba(100,50,200,0.06));
border:1px solid rgba(130,80,255,0.26);border-radius:22px;padding:1.6rem;margin-bottom:1.2rem;">
<div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.95rem;color:#C4B5FD;margin-bottom:1rem;">⚙️ Parámetros de entrada</div>""", unsafe_allow_html=True)

        c1,c2,c3=st.columns(3)
        with c1:
            dep=st.selectbox("🗺️ Departamento", DEPTOS, index=list(DEPTOS).index('ANTIOQUIA'))
            mun=st.selectbox("📍 Municipio", DM.get(dep,[]))
            año=st.selectbox("📅 Año", list(range(2015,2028)), index=8)
        with c2:
            del_=st.selectbox("⚖️ Tipo de delito", DELITOS, index=DELITOS.index('VIOLENCIA INTRAFAMILIAR'))
            sex=st.selectbox("👤 Sexo", SEXOS, index=SEXOS.index('FEMENINO'))
            eta=st.selectbox("🎂 Grupo etario", ETARIOS, index=ETARIOS.index('DE 27 A 59 AÑOS'))
        with c3:
            mg=st.selectbox("🤖 Modelo Gravedad", ['XGBoost','LightGBM'])
            mz=st.selectbox("🤖 Modelo Zona", ['XGBoost','LightGBM'])
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
            run=st.button("🔮 Ejecutar Predicción")
        st.markdown("</div>", unsafe_allow_html=True)

    if run:
        with st.spinner('Ejecutando modelos...'):
            gl,gp=pred_grav(dep,mun,del_,sex,eta,año,mg)
            zl,zp=pred_zona(dep,mun,del_,sex,eta,año,mz)

        OG=['MÍNIMO','MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO','CRÍTICO']
        OZ=['MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO']
        gi=OG.index(gl)+1 if gl in OG else 3
        zi=OZ.index(zl)+1 if zl in OZ else 2
        est=max(1,gi*zi); rmin=max(1,est-gi); rmax=est+gi*2
        cg=NC.get(gl,'#888'); cz=NC.get(zl,'#888')

        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(130,80,255,0.13),rgba(100,50,200,0.07));
border:1px solid rgba(130,80,255,0.3);border-radius:16px;padding:.95rem 1.4rem;margin-bottom:1rem;
display:flex;align-items:center;gap:12px;animation:fadeUp 0.4s ease-out;">
<span style="font-size:1.4rem;">📍</span>
<div><div style="font-weight:600;color:#EDE9FE;font-size:0.95rem;">{dep} · {mun}</div>
<div style="font-size:0.78rem;color:rgba(237,233,254,0.48);">{del_} · {sex} · {eta} · {año}</div></div></div>""", unsafe_allow_html=True)

        c1,c2,c3=st.columns(3)
        with c1:
            bg=NB.get(gl,'rgba(130,80,255,0.1)')
            st.markdown(f"""<div style="background:{bg};border:1px solid {cg}42;border-radius:22px;padding:1.4rem;animation:fadeUp 0.5s ease-out;">
<div style="font-size:0.62rem;color:rgba(237,233,254,0.42);font-weight:600;letter-spacing:.12em;text-transform:uppercase;margin-bottom:11px;">
NIVEL DE GRAVEDAD · {mg}</div>
<div style="font-size:2.1rem;margin-bottom:5px;">{NI.get(gl,'🔵')}</div>
<div style="font-family:'Syne',sans-serif;font-size:1.55rem;font-weight:800;color:{cg};margin-bottom:15px;line-height:1.1;">{gl}</div>
<div style="height:1px;background:rgba(255,255,255,0.08);margin-bottom:11px;"></div>
<div style="font-size:0.68rem;color:rgba(237,233,254,0.42);margin-bottom:9px;font-weight:600;letter-spacing:.08em;">PROBABILIDADES</div>""", unsafe_allow_html=True)
            barras(gp)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            bz=NB.get(zl,'rgba(130,80,255,0.1)')
            st.markdown(f"""<div style="background:{bz};border:1px solid {cz}42;border-radius:22px;padding:1.4rem;animation:fadeUp 0.6s ease-out;">
<div style="font-size:0.62rem;color:rgba(237,233,254,0.42);font-weight:600;letter-spacing:.12em;text-transform:uppercase;margin-bottom:11px;">
ZONA DE RIESGO · {mz}</div>
<div style="font-size:2.1rem;margin-bottom:5px;">{NI.get(zl,'🔵')}</div>
<div style="font-family:'Syne',sans-serif;font-size:1.55rem;font-weight:800;color:{cz};margin-bottom:15px;line-height:1.1;">{zl}</div>
<div style="height:1px;background:rgba(255,255,255,0.08);margin-bottom:11px;"></div>
<div style="font-size:0.68rem;color:rgba(237,233,254,0.42);margin-bottom:9px;font-weight:600;letter-spacing:.08em;">PROBABILIDADES</div>""", unsafe_allow_html=True)
            barras(zp)
            st.markdown("</div>", unsafe_allow_html=True)

        with c3:
            st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(130,80,255,0.17),rgba(100,50,200,0.1));
border:1px solid rgba(130,80,255,0.32);border-radius:22px;padding:1.4rem;animation:glowPurple 3s infinite;height:100%;">
<div style="font-size:0.62rem;color:rgba(237,233,254,0.42);font-weight:600;letter-spacing:.12em;text-transform:uppercase;margin-bottom:11px;">
VÍCTIMAS ESTIMADAS</div>
<div style="font-size:0.75rem;color:rgba(237,233,254,0.38);margin-bottom:14px;">Combinación Gravedad + Zona</div>
<div style="font-family:'Syne',sans-serif;font-size:4.2rem;font-weight:800;line-height:1;margin-bottom:6px;
background:linear-gradient(135deg,#EDE9FE,#8B5CF6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{est}</div>
<div style="font-size:0.77rem;color:rgba(237,233,254,0.38);margin-bottom:18px;">Rango: <b style="color:rgba(237,233,254,0.62);">{rmin} — {rmax}</b></div>
<div style="height:1px;background:rgba(255,255,255,0.08);margin-bottom:14px;"></div>
<div style="display:flex;flex-direction:column;gap:9px;">
<div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:9px 12px;
display:flex;justify-content:space-between;align-items:center;">
<span style="font-size:0.73rem;color:rgba(237,233,254,0.48);">Gravedad</span>
<span style="font-weight:700;color:{cg};font-size:0.82rem;">{gl}</span></div>
<div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:9px 12px;
display:flex;justify-content:space-between;align-items:center;">
<span style="font-size:0.73rem;color:rgba(237,233,254,0.48);">Zona</span>
<span style="font-weight:700;color:{cz};font-size:0.82rem;">{zl}</span></div>
</div></div>""", unsafe_allow_html=True)

        # Gráfica de radar comparativa
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:#C4B5FD;margin-bottom:.8rem;">
📈 Análisis Comparativo por Tipo de Delito</div>""", unsafe_allow_html=True)

        with st.spinner('Calculando comparativa...'):
            comp=[]
            for d in DELITOS:
                try:
                    gl2,_=pred_grav(dep,mun,d,sex,eta,año,mg)
                    zl2,_=pred_zona(dep,mun,d,sex,eta,año,mz)
                    OG2=['MÍNIMO','MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO','CRÍTICO']
                    OZ2=['MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO']
                    g2=OG2.index(gl2)+1 if gl2 in OG2 else 3
                    z2=OZ2.index(zl2)+1 if zl2 in OZ2 else 2
                    comp.append({'Delito':d,'Score':(g2+z2)/2,'Gravedad':gl2,'Zona':zl2})
                except: pass

        if comp:
            dfc=pd.DataFrame(comp).sort_values('Score',ascending=True)
            CMAP_D={'MUY BAJO':'#10B981','BAJO':'#34D399','MEDIO-BAJO':'#FCD34D',
                    'MEDIO-ALTO':'#F59E0B','ALTO':'#EF4444','MUY ALTO':'#DC2626'}
            fig=go.Figure(go.Bar(
                y=dfc['Delito'], x=dfc['Score'],
                orientation='h',
                marker=dict(color=[CMAP_D.get(z,'#888') for z in dfc['Zona']],opacity=0.88,
                            line=dict(color='rgba(0,0,0,0.15)',width=1)),
                text=[f"{r['Gravedad']} · {r['Zona']}" for _,r in dfc.iterrows()],
                textposition='outside',
                textfont=dict(size=10,color='rgba(237,233,254,0.65)'),
                hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>',
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#EDE9FE',family='Plus Jakarta Sans'),
                xaxis=dict(gridcolor='rgba(130,80,255,0.1)',zeroline=False,title='Score de Riesgo'),
                yaxis=dict(gridcolor='rgba(130,80,255,0.05)'),
                margin=dict(t=20,b=20,l=10,r=160), height=300,
                title=dict(text=f'Riesgo por tipo de delito — {mun}',font=dict(size=13,color='#C4B5FD')),
            )
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════
# MAPA DE RIESGO
# ══════════════════════════════════════════
elif "Mapa" in pagina:
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#EDE9FE;margin-bottom:3px;">
🗺️ Mapa de Riesgo por Departamento</div>
<p style="color:rgba(237,233,254,0.52);margin-bottom:1.4rem;">
Visualiza y compara el nivel de riesgo predicho en todos los departamentos de Colombia.</p>""", unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns([2,2,1,1])
    with c1: filt=st.selectbox("🗺️ Departamento",['Todos']+list(DEPTOS))
    with c2: mdel=st.selectbox("⚖️ Tipo de delito",DELITOS,index=DELITOS.index('VIOLENCIA INTRAFAMILIAR'))
    with c3: mano=st.selectbox("📅 Año",list(range(2015,2028)),index=8)
    with c4:
        st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
        gen=st.button("🗺️ Generar")

    if gen:
        deps=list(DEPTOS) if filt=='Todos' else [filt]
        res=[]
        prog=st.progress(0,"Calculando predicciones...")
        for i,d in enumerate(deps):
            ms=DM.get(d,[])
            if not ms: continue
            try:
                zl,_=pred_zona(d,ms[0],mdel,'FEMENINO','DE 27 A 59 AÑOS',mano,'XGBoost')
                gl,_=pred_grav(d,ms[0],mdel,'FEMENINO','DE 27 A 59 AÑOS',mano,'XGBoost')
                OZ=['MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO']
                OG=['MÍNIMO','MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO','CRÍTICO']
                zs=OZ.index(zl)+1 if zl in OZ else 3
                gs=OG.index(gl)+1 if gl in OG else 3
                res.append({'Depto':d,'Zona':zl,'Gravedad':gl,'Score':round((zs+gs)/2,1)})
            except: pass
            prog.progress((i+1)/len(deps))
        prog.empty()

        if res:
            dfr=pd.DataFrame(res).sort_values('Score',ascending=False)
            CMAP={'MUY BAJO':'#10B981','BAJO':'#34D399','MEDIO-BAJO':'#FCD34D',
                  'MEDIO-ALTO':'#F59E0B','ALTO':'#EF4444','MUY ALTO':'#DC2626'}

            # Gráfica de barras principal
            fig=go.Figure(go.Bar(
                x=dfr['Depto'], y=dfr['Score'],
                marker=dict(color=[CMAP.get(z,'#888') for z in dfr['Zona']],
                            opacity=0.9,line=dict(color='rgba(0,0,0,0.18)',width=1)),
                text=dfr['Zona'], textposition='outside',
                textfont=dict(size=9,color='rgba(237,233,254,0.65)'),
                hovertemplate='<b>%{x}</b><br>Zona: %{text}<br>Score: %{y:.1f}<extra></extra>',
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#EDE9FE',family='Plus Jakarta Sans'),
                title=dict(text=f'<b>{mdel}</b> — {mano}',font=dict(size=14,color='#C4B5FD')),
                xaxis=dict(tickangle=-42,gridcolor='rgba(130,80,255,0.09)',tickfont=dict(size=9.5)),
                yaxis=dict(title='Score',gridcolor='rgba(130,80,255,0.09)',zeroline=False),
                margin=dict(t=55,b=145,l=40,r=20), height=460, bargap=0.28,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Leyenda de colores
            st.markdown("<div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:1rem;'>" +
                "".join([f"<div style='display:flex;align-items:center;gap:5px;font-size:0.77rem;color:rgba(237,233,254,0.58);'>"
                         f"<div style='width:11px;height:11px;border-radius:3px;background:{c};'></div>{n}</div>"
                         for n,c in CMAP.items()]) + "</div>", unsafe_allow_html=True)

            # Pie chart de distribución
            dist=dfr['Zona'].value_counts().reset_index()
            dist.columns=['Zona','Cantidad']
            fig2=go.Figure(go.Pie(
                labels=dist['Zona'], values=dist['Cantidad'],
                marker=dict(colors=[CMAP.get(z,'#888') for z in dist['Zona']],
                            line=dict(color='rgba(0,0,0,0.2)',width=2)),
                hole=0.55,
                textinfo='label+percent',
                textfont=dict(size=11,color='#EDE9FE'),
                hovertemplate='%{label}<br>%{value} departamentos<extra></extra>',
            ))
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#EDE9FE',family='Plus Jakarta Sans'),
                showlegend=False,
                title=dict(text='Distribución de zonas',font=dict(size=13,color='#C4B5FD')),
                margin=dict(t=50,b=20,l=20,r=20), height=320,
                annotations=[dict(text=f'<b>{len(dfr)}</b><br>deptos',x=0.5,y=0.5,
                                  font=dict(size=14,color='#EDE9FE'),showarrow=False)]
            )

            col_pie,col_tab=st.columns([1,2])
            with col_pie: st.plotly_chart(fig2, use_container_width=True)
            with col_tab:
                st.markdown("<div style='font-family:Syne,sans-serif;font-weight:700;color:#EDE9FE;margin-bottom:.8rem;'>📋 Tabla de resultados</div>", unsafe_allow_html=True)
                df_show=dfr.copy()
                df_show.insert(1,'',df_show['Zona'].map(NI))
                st.dataframe(df_show[['Depto','','Zona','Gravedad','Score']],
                             use_container_width=True,hide_index=True,height=280)

# ══════════════════════════════════════════
# VIAJE SEGURO
# ══════════════════════════════════════════
elif "Viaje" in pagina:
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#EDE9FE;margin-bottom:3px;">
✈️ Viaje Seguro</div>
<p style="color:rgba(237,233,254,0.52);margin-bottom:1.4rem;">
Consulta el nivel de seguridad de tu destino antes de viajar.</p>""", unsafe_allow_html=True)

    c1,c2,c3=st.columns([2,2,1])
    with c1: vdep=st.selectbox("🗺️ Destino — Departamento",DEPTOS)
    with c2: vmun=st.selectbox("📍 Ciudad / Municipio",DM.get(vdep,[]))
    with c3:
        st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
        con=st.button("🔍 Analizar destino")

    if con:
        with st.spinner('Analizando seguridad del destino...'):
            rv=[]
            for d in DELITOS:
                try:
                    zl,_=pred_zona(vdep,vmun,d,'FEMENINO','DE 27 A 59 AÑOS',2024,'XGBoost')
                    gl,_=pred_grav(vdep,vmun,d,'FEMENINO','DE 27 A 59 AÑOS',2024,'XGBoost')
                    OZ=['MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO']
                    rv.append({'Delito':d,'Zona':zl,'Gravedad':gl,'ZScore':OZ.index(zl)+1 if zl in OZ else 3})
                except: pass

        if rv:
            avg=np.mean([r['ZScore'] for r in rv])
            if avg<=2: sg,sc,si,sm='BAJO','#10B981','🟢','Destino relativamente seguro para viajeras.'
            elif avg<=4: sg,sc,si,sm='MEDIO','#F59E0B','🟡','Viaja con precaución. Evita zonas poco iluminadas de noche.'
            else: sg,sc,si,sm='ALTO','#EF4444','🔴','Riesgo elevado. Toma medidas de seguridad adicionales.'

            ca,cb=st.columns([1,2])
            with ca:
                st.markdown(f"""<div style="background:linear-gradient(135deg,{sc}16,{sc}08);
border:2px solid {sc}52;border-radius:22px;padding:2rem;text-align:center;animation:fadeUp 0.5s ease-out;">
<div style="font-size:3rem;margin-bottom:10px;">{si}</div>
<div style="font-size:0.65rem;color:rgba(237,233,254,0.42);letter-spacing:.1em;text-transform:uppercase;margin-bottom:5px;">SEGURIDAD GENERAL</div>
<div style="font-family:'Syne',sans-serif;font-size:2.1rem;font-weight:800;color:{sc};">{sg}</div>
<div style="font-size:0.82rem;color:rgba(237,233,254,0.52);margin-top:10px;line-height:1.55;">{sm}</div>
<div style="margin-top:14px;font-size:0.73rem;color:rgba(237,233,254,0.38);">📍 {vmun}, {vdep}</div>
</div>""", unsafe_allow_html=True)

                # Score gauge
                fig_g=go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=round(avg,1),
                    number={'font':{'color':'#EDE9FE','family':'Syne','size':28}},
                    gauge=dict(
                        axis=dict(range=[1,6],tickcolor='rgba(237,233,254,0.3)',
                                  tickfont=dict(color='rgba(237,233,254,0.4)',size=9)),
                        bar=dict(color=sc,thickness=0.28),
                        bgcolor='rgba(255,255,255,0.05)',
                        borderwidth=0,
                        steps=[
                            dict(range=[1,2],color='rgba(16,185,129,0.2)'),
                            dict(range=[2,4],color='rgba(245,158,11,0.2)'),
                            dict(range=[4,6],color='rgba(239,68,68,0.2)'),
                        ],
                        threshold=dict(line=dict(color=sc,width=3),thickness=0.8,value=avg)
                    )
                ))
                fig_g.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#EDE9FE'),
                    margin=dict(t=30,b=20,l=30,r=30), height=200,
                )
                st.plotly_chart(fig_g, use_container_width=True)

            with cb:
                st.markdown("<div style='font-family:Syne,sans-serif;font-weight:700;color:#EDE9FE;margin-bottom:.8rem;'>Análisis por tipo de delito</div>", unsafe_allow_html=True)
                for r in rv:
                    cd=NC.get(r['Zona'],'#888'); id_=NI.get(r['Zona'],'🔵')
                    st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;
background:rgba(255,255,255,0.04);border-radius:11px;padding:10px 14px;margin-bottom:6px;
border:1px solid rgba(255,255,255,0.06);">
<span style="font-size:0.85rem;color:rgba(237,233,254,0.72);">{r['Delito']}</span>
<div style="display:flex;align-items:center;gap:8px;">
<span style="font-size:0.76rem;color:rgba(237,233,254,0.38);">{r['Gravedad']}</span>
<span style="font-size:0.85rem;font-weight:700;color:{cd};">{id_} {r['Zona']}</span></div></div>""", unsafe_allow_html=True)

                st.markdown("""<div style="background:rgba(130,80,255,0.09);border:1px solid rgba(130,80,255,0.22);
border-radius:16px;padding:1.1rem;margin-top:.8rem;">
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#C4B5FD;margin-bottom:.7rem;">💡 Recomendaciones</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:7px;">
<div style="font-size:0.8rem;color:rgba(237,233,254,0.62);">✅ Comparte tu itinerario</div>
<div style="font-size:0.8rem;color:rgba(237,233,254,0.62);">✅ Usa transporte formal</div>
<div style="font-size:0.8rem;color:rgba(237,233,254,0.62);">✅ Ten cargado el celular</div>
<div style="font-size:0.8rem;color:rgba(237,233,254,0.62);">✅ Evita zonas solas de noche</div>
<div style="font-size:0.8rem;color:rgba(237,233,254,0.62);">✅ Anota el número de emergencia local</div>
<div style="font-size:0.8rem;color:rgba(237,233,254,0.62);">✅ Avisa a alguien tu llegada</div>
</div></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# EMERGENCIAS
# ══════════════════════════════════════════
elif "Emergencias" in pagina:
    st.markdown("""<div style="background:linear-gradient(135deg,rgba(239,68,68,0.18),rgba(220,38,38,0.09));
border:1px solid rgba(239,68,68,0.35);border-radius:22px;padding:1.5rem;margin-bottom:1.5rem;
animation:pulseRed 2.5s infinite;">
<div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#FCA5A5;">🚨 Centro de Emergencias</div>
<p style="color:rgba(237,233,254,0.58);margin:4px 0 0;font-size:0.93rem;">
Si estás en peligro, presiona el botón que describe tu situación. Los enlaces te conectarán directamente.</p></div>""", unsafe_allow_html=True)

    opciones=[
        ("🆘","Estoy en peligro","tel:123","Llama al 123 ahora","#DC2626"),
        ("👣","Me están siguiendo","tel:123","Llama al 123","#D97706"),
        ("🔇","No puedo hablar","sms:123","Envía SMS al 123","#7C3AED"),
        ("🏃","Estoy secuestrada","tel:123","Emergencia máxima — 123","#B91C1C"),
        ("🚔","Necesito Policía","tel:123","Policía Nacional — 123","#2563EB"),
        ("🚑","Necesito Ambulancia","tel:132","Cruz Roja — 132","#059669"),
        ("💜","Apoyo psicológico","tel:137","Línea Salud Mental — 137","#6D28D9"),
        ("👩","Línea Mujer","tel:155","Línea 155 — 24/7 Gratis","#8B5CF6"),
    ]
    cols=st.columns(4)
    for i,(ic,tx,href,sub,co) in enumerate(opciones):
        with cols[i%4]:
            st.markdown(f"""<a href="{href}" style="text-decoration:none;">
<div style="background:linear-gradient(135deg,{co}1a,{co}0a);border:1.5px solid {co}48;
border-radius:18px;padding:1.25rem;text-align:center;cursor:pointer;margin-bottom:.8rem;
min-height:118px;transition:all 0.2s;display:block;">
<div style="font-size:2rem;margin-bottom:7px;">{ic}</div>
<div style="font-weight:600;color:#EDE9FE;font-size:0.87rem;margin-bottom:3px;">{tx}</div>
<div style="font-size:0.7rem;color:{co};font-weight:600;">{sub}</div></div></a>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.05rem;color:#EDE9FE;margin-bottom:.9rem;">
📞 Líneas de Emergencia Colombia — toca para llamar</div>""", unsafe_allow_html=True)

    lineas=[
        ("tel:123","123","Policía Nacional","🚔","#3B82F6"),
        ("tel:155","155","Línea Mujer 24/7","💜","#8B5CF6"),
        ("tel:125","125","Defensa Civil","🟢","#10B981"),
        ("tel:132","132","Cruz Roja","❤️","#EF4444"),
        ("tel:137","137","Salud Mental","🧠","#A78BFA"),
        ("tel:106","106","Bomberos","🔥","#F59E0B"),
    ]
    cols2=st.columns(6)
    for col,(href,num,desc,ic,co) in zip(cols2,lineas):
        with col:
            st.markdown(f"""<a href="{href}" style="text-decoration:none;">
<div style="background:linear-gradient(135deg,{co}17,{co}09);border:1px solid {co}42;
border-radius:18px;padding:1.1rem;text-align:center;cursor:pointer;">
<div style="font-size:1.4rem;margin-bottom:5px;">{ic}</div>
<div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:{co};">{num}</div>
<div style="font-size:0.68rem;color:rgba(237,233,254,0.48);margin-top:3px;">{desc}</div></div></a>""", unsafe_allow_html=True)

    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
    ca,cb=st.columns(2)
    with ca:
        st.markdown("""<div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.28);border-radius:18px;padding:1.2rem;">
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#FCD34D;margin-bottom:.7rem;">🔒 Salida Rápida</div>
<p style="color:rgba(237,233,254,0.62);font-size:0.86rem;line-height:1.6;margin-bottom:.8rem;">
Presiona el enlace para ir a una página neutra de inmediato:</p>
<div style="display:flex;gap:8px;flex-wrap:wrap;">
<a href="https://www.google.com" target="_blank" style="background:rgba(245,158,11,0.25);color:#FCD34D;
padding:6px 14px;border-radius:8px;font-size:0.82rem;text-decoration:none;font-weight:600;">→ Google</a>
<a href="https://www.weather.com" target="_blank" style="background:rgba(245,158,11,0.15);color:#FCD34D;
padding:6px 14px;border-radius:8px;font-size:0.82rem;text-decoration:none;font-weight:600;">→ Clima</a>
<a href="https://www.eltiempo.com" target="_blank" style="background:rgba(245,158,11,0.15);color:#FCD34D;
padding:6px 14px;border-radius:8px;font-size:0.82rem;text-decoration:none;font-weight:600;">→ Noticias</a>
</div></div>""", unsafe_allow_html=True)
    with cb:
        st.markdown("""<div style="background:rgba(130,80,255,0.1);border:1px solid rgba(130,80,255,0.24);border-radius:18px;padding:1.2rem;">
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#C4B5FD;margin-bottom:.7rem;">💡 En caso de emergencia</div>
<div style="display:flex;flex-direction:column;gap:6px;">
<div style="font-size:0.82rem;color:rgba(237,233,254,0.62);">🔵 Mantén la calma y ve a un lugar concurrido</div>
<div style="font-size:0.82rem;color:rgba(237,233,254,0.62);">🔵 Llama o envía tu ubicación a alguien de confianza</div>
<div style="font-size:0.82rem;color:rgba(237,233,254,0.62);">🔵 Memoriza: <b style="color:#EDE9FE;">123</b> Policía · <b style="color:#A78BFA;">155</b> Mujer</div>
<div style="font-size:0.82rem;color:rgba(237,233,254,0.62);">🔵 No confrontes al agresor directamente</div>
<div style="font-size:0.82rem;color:rgba(237,233,254,0.62);">🔵 Documenta evidencia si es seguro hacerlo</div>
</div></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# DENUNCIAS
# ══════════════════════════════════════════
elif "Denuncias" in pagina:
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#EDE9FE;margin-bottom:3px;">
📋 Registro de Denuncia</div>
<p style="color:rgba(237,233,254,0.52);margin-bottom:1.4rem;">
Registra un hecho de forma segura y confidencial. Puedes hacerlo completamente anónima.</p>""", unsafe_allow_html=True)

    cf,ci=st.columns([2,1])
    with cf:
        st.markdown("""<div style="background:rgba(130,80,255,0.09);border:1px solid rgba(130,80,255,0.22);
border-radius:22px;padding:1.6rem;">
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#C4B5FD;margin-bottom:1rem;">📝 Formulario</div>""", unsafe_allow_html=True)

        anon=st.checkbox("🔒 Denuncia anónima (recomendado)", value=True)
        c1,c2=st.columns(2)
        with c1:
            dd=st.selectbox("⚖️ Tipo de delito",DELITOS)
            ddep=st.selectbox("🗺️ Departamento",DEPTOS,key='dd')
        with c2:
            dmun=st.text_input("📍 Municipio",placeholder="Municipio...")
            dfec=st.date_input("📅 Fecha aproximada")
        dhora=st.text_input("🕐 Hora aproximada",placeholder="Ej: 10:30 PM")
        ddesc=st.text_area("📝 Descripción detallada",
            placeholder="Describe lo que ocurrió. Toda la información es confidencial...",height=130)
        opts=st.multiselect("Opciones adicionales:",[
            "🤝 Acompañamiento jurídico","🧠 Apoyo psicológico",
            "📸 Tengo evidencia","📲 Quiero ser contactada por trabajadora social"])

        env=st.button("📤 Enviar Denuncia de Forma Segura")
        st.markdown("</div>", unsafe_allow_html=True)

        if env:
            if ddesc.strip():
                st.markdown("""<div style="background:rgba(16,185,129,0.11);border:1px solid rgba(16,185,129,0.32);
border-radius:14px;padding:1.2rem;margin-top:.8rem;">
<div style="font-weight:700;color:#34D399;font-size:1rem;margin-bottom:5px;">✅ Denuncia registrada exitosamente</div>
<div style="color:rgba(237,233,254,0.62);font-size:0.86rem;line-height:1.6;">
Tu reporte fue recibido de forma segura.<br>
Para denuncia oficial: <b style="color:#EDE9FE;">Fiscalía</b> · <b style="color:#A78BFA;">Línea 155</b> · <b style="color:#60A5FA;">Comisaría de Familia</b></div></div>""", unsafe_allow_html=True)
            else:
                st.warning("Por favor escribe una descripción del hecho.")

    with ci:
        st.markdown("""<div style="background:rgba(130,80,255,0.09);border:1px solid rgba(130,80,255,0.22);
border-radius:22px;padding:1.3rem;margin-bottom:1rem;">
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#C4B5FD;margin-bottom:.8rem;">📞 Entidades Oficiales</div>""", unsafe_allow_html=True)
        ents=[
            ("tel:155","💜 Línea 155","Gratuita · 24/7 · Confidencial","#8B5CF6"),
            ("https://www.fiscalia.gov.co","⚖️ Fiscalía General","Denuncia penal formal","#7C3AED"),
            ("https://www.icbf.gov.co","👨‍👩‍👧 ICBF","01800-112-137","#D97706"),
            ("tel:123","🚔 Policía Nacional","Emergencias — 123","#2563EB"),
        ]
        for href,nom,desc,co in ents:
            st.markdown(f"""<a href="{href}" target="_blank" style="text-decoration:none;">
<div style="background:linear-gradient(135deg,{co}12,{co}06);border:1px solid {co}28;
border-radius:12px;padding:10px 13px;margin-bottom:7px;cursor:pointer;">
<div style="font-weight:600;color:#EDE9FE;font-size:0.85rem;">{nom}</div>
<div style="font-size:0.73rem;color:rgba(237,233,254,0.48);margin-top:2px;">{desc}</div></div></a>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("""<div style="background:rgba(245,158,11,0.09);border:1px solid rgba(245,158,11,0.24);
border-radius:16px;padding:1rem;">
<div style="font-size:0.82rem;color:rgba(237,233,254,0.6);line-height:1.65;">
⚠️ Esta plataforma es un <b style="color:#FCD34D;">prototipo académico</b>.
Para denuncias con validez legal, dirígete a las entidades oficiales.</div></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# APOYO IA
# ══════════════════════════════════════════
elif "Apoyo" in pagina:
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#EDE9FE;margin-bottom:3px;">
🤖 Apoyo con Inteligencia Artificial</div>
<p style="color:rgba(237,233,254,0.52);margin-bottom:1.4rem;">
Estoy aquí para escucharte y orientarte. Todo lo que compartas es confidencial 💜</p>""", unsafe_allow_html=True)

    RESP={
        'denunci':'📋 Para denunciar en Colombia tienes varias opciones: la **Fiscalía General** (presencial), la **Comisaría de Familia**, o la **Línea 155** (gratuita, 24/7). Tienes derecho a ser atendida de forma prioritaria y a la confidencialidad total de tu caso.',
        'sigu':'🔒 Si crees que te están siguiendo: **no corras**, cambia de ruta hacia un lugar concurrido. Entra a un banco, tienda o establecimiento público. Llama a alguien de confianza y mantenla en línea. Si el peligro es inmediato: **marca el 123**.',
        'psicolog':'💜 No estás sola en esto. Colombia tiene la **Línea 137 de Salud Mental** — gratuita y confidencial. También el ICBF: **01800-112-137**. ¿Quieres contarme más sobre cómo te sientes?',
        'derecho':'⚖️ Tus derechos: vida libre de violencia (**Ley 1257/2008**), atención prioritaria en salud, confidencialidad de tu denuncia, medidas de protección en **24 horas**, orientación jurídica gratuita en la Defensoría del Pueblo.',
        'peligro':'🚨 Si estás en **peligro inmediato**: llama al **123** ahora. Si no puedes hablar, envía tu ubicación por WhatsApp a alguien de confianza. Permanece en lugares visibles y concurridos.',
        'miedo':'💜 Sentir miedo es completamente válido. Lo que describes suena muy difícil. Mereces estar segura. ¿Puedes contarme más? Estoy aquí para ayudarte a encontrar el camino.',
        'sola':'💜 No estás sola. SafeHer está contigo y hay personas dispuestas a ayudarte. La **Línea 155** tiene consejeras disponibles 24/7. ¿Quieres que te oriente sobre los recursos más cercanos?',
        'violencia':'⚠️ La violencia nunca es tu culpa. Llama a la **Línea 155** ahora — gratuita, confidencial, 24/7. Si estás en peligro inmediato: **123**. ¿Estás en un lugar seguro en este momento?',
        'legal':'⚖️ Puedes: hacer denuncia anónima, solicitar medidas de protección inmediata, recibir orientación jurídica gratuita en la **Defensoría del Pueblo**, y exigir confidencialidad total. ¿Sobre qué aspecto necesitas más información?',
        'ayuda':'🤝 Puedo orientarte sobre: dónde denunciar, qué hacer si te siguen, apoyo psicológico, tus derechos legales, emergencias. ¿Qué necesitas hoy?',
        'secuestr':'🚨 Esto es una emergencia. Si puedes, llama al **123** ahora mismo. Si no puedes hablar, envía un SMS al 123 con tu ubicación. El GAULA (antiextorsión) también puede ayudar: **165**.',
        'acoso':'💜 El acoso es un delito. Puedes denunciarlo en la Comisaría de Familia o en la Fiscalía. Guarda capturas de pantalla o evidencia si el acoso es digital. ¿Quieres que te explique el proceso paso a paso?',
    }

    def resp(msg):
        m=msg.lower()
        for k,v in RESP.items():
            if k in m: return v
        return '💬 Gracias por escribirme. Puedo orientarte sobre **dónde denunciar**, qué hacer si te **siguen**, **apoyo psicológico**, tus **derechos legales**, o emergencias. ¿Qué necesitas hoy?'

    if 'ch' not in st.session_state: st.session_state.ch=[]

    st.markdown("<div style='font-size:0.78rem;color:rgba(237,233,254,0.42);margin-bottom:7px;'>Preguntas frecuentes:</div>", unsafe_allow_html=True)
    qc=st.columns(4)
    pregs=["¿Dónde denuncio?","¿Qué hago si me siguen?","Necesito apoyo emocional","¿Cuáles son mis derechos?"]
    for i,(c,p) in enumerate(zip(qc,pregs)):
        with c:
            if st.button(p,key=f"q{i}"):
                st.session_state.ch.append({'u':p,'ia':resp(p)})
                st.rerun()

    # Área chat
    st.markdown("""<div style="background:linear-gradient(135deg,rgba(110,45,220,0.11),rgba(130,80,255,0.06));
border:1px solid rgba(130,80,255,0.22);border-radius:22px;padding:1.2rem;
min-height:340px;max-height:420px;overflow-y:auto;margin:1rem 0;">""", unsafe_allow_html=True)

    st.markdown("""<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:12px;">
<div style="background:linear-gradient(135deg,#7C3AED,#A78BFA);border-radius:50%;width:33px;height:33px;
display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">🤖</div>
<div style="background:rgba(130,80,255,0.16);border:1px solid rgba(130,80,255,0.22);
border-radius:5px 18px 18px 18px;padding:12px 16px;color:#EDE9FE;font-size:0.87rem;line-height:1.68;max-width:84%;">
Hola 💜 Soy la IA de apoyo de SafeHer. Estoy aquí para orientarte — puedes preguntarme sobre
<b>dónde denunciar</b>, <b>qué hacer en peligro</b>, tus <b>derechos legales</b>, <b>apoyo psicológico</b>,
o simplemente hablar. Todo es confidencial.</div></div>""", unsafe_allow_html=True)

    for h in st.session_state.ch:
        st.markdown(f"""<div style="display:flex;justify-content:flex-end;margin-bottom:9px;">
<div style="background:rgba(110,45,220,0.38);border:1px solid rgba(130,80,255,0.32);
border-radius:18px 5px 18px 18px;padding:10px 15px;color:#EDE9FE;font-size:0.87rem;line-height:1.6;max-width:78%;">{h['u']}</div></div>
<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:12px;">
<div style="background:linear-gradient(135deg,#7C3AED,#A78BFA);border-radius:50%;width:28px;height:28px;
display:flex;align-items:center;justify-content:center;font-size:0.85rem;flex-shrink:0;">🤖</div>
<div style="background:rgba(130,80,255,0.13);border:1px solid rgba(130,80,255,0.18);
border-radius:5px 18px 18px 18px;padding:11px 15px;color:#EDE9FE;font-size:0.87rem;line-height:1.68;max-width:84%;">{h['ia']}</div></div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    ci2,cb2=st.columns([5,1])
    with ci2:
        inp=st.text_input("","",placeholder="Escribe aquí... (Ej: Necesito ayuda, ¿dónde denuncio?)",
                          label_visibility="collapsed",key="inp")
    with cb2:
        if st.button("Enviar ➤"):
            if inp.strip():
                st.session_state.ch.append({'u':inp,'ia':resp(inp)})
                st.rerun()

    c3a,c3b,c3c=st.columns(3)
    for col,num,desc,co in [(c3a,"155","Línea Mujer 24/7","#8B5CF6"),(c3b,"137","Salud Mental","#34D399"),(c3c,"01800-112-137","ICBF Nacional","#FCD34D")]:
        with col:
            st.markdown(f"""<a href="tel:{num.replace('-','')}" style="text-decoration:none;">
<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
border-radius:14px;padding:.9rem;text-align:center;cursor:pointer;">
<div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;color:{co};">{num}</div>
<div style="font-size:0.72rem;color:rgba(237,233,254,0.45);margin-top:3px;">{desc}</div></div></a>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# AYUDA CERCANA
# ══════════════════════════════════════════
elif "Ayuda" in pagina:
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#EDE9FE;margin-bottom:3px;">
🚔 Ayuda Cercana</div>
<p style="color:rgba(237,233,254,0.52);margin-bottom:1.4rem;">
Encuentra entidades de apoyo. Toca cada tarjeta para ir al sitio oficial o llamar directamente.</p>""", unsafe_allow_html=True)

    ents=[
        ("🚔","Policía Nacional","Emergencias y denuncias","tel:123","Llama: 123","#2563EB"),
        ("⚖️","Fiscalía General","Denuncias penales formales","https://www.fiscalia.gov.co","fiscalia.gov.co","#7C3AED"),
        ("🏥","Cruz Roja","Atención médica de urgencias","tel:132","Llama: 132","#059669"),
        ("🏠","Casas Refugio","Alojamiento seguro temporal","tel:155","Línea 155","#D97706"),
        ("🧠","Salud Mental","Apoyo emocional profesional","tel:137","Línea 137","#8B5CF6"),
        ("👨‍⚖️","Defensoría del Pueblo","Orientación jurídica gratuita","https://www.defensoria.gov.co","defensoria.gov.co","#0891B2"),
        ("👨‍👩‍👧","Comisaría de Familia","Violencia intrafamiliar","https://www.icbf.gov.co","Alcaldía local","#BE185D"),
        ("📚","ICBF","Protección familia","tel:018001121137","01800-112-137","#B45309"),
    ]
    cols=st.columns(4)
    for i,(ic,nom,desc,href,cont,co) in enumerate(ents):
        with cols[i%4]:
            st.markdown(f"""<a href="{href}" target="_blank" style="text-decoration:none;">
<div style="background:linear-gradient(135deg,{co}16,{co}07);border:1px solid {co}32;
border-radius:20px;padding:1.3rem;margin-bottom:1rem;cursor:pointer;transition:all 0.2s;min-height:155px;">
<div style="font-size:1.9rem;margin-bottom:9px;">{ic}</div>
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#EDE9FE;font-size:0.9rem;margin-bottom:4px;">{nom}</div>
<div style="font-size:0.76rem;color:rgba(237,233,254,0.52);margin-bottom:9px;line-height:1.4;">{desc}</div>
<div style="background:{co}22;border-radius:7px;padding:4px 10px;font-size:0.73rem;color:{co};font-weight:600;display:inline-block;">{cont}</div>
</div></a>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""<div style="background:rgba(130,80,255,0.09);border:1px solid rgba(130,80,255,0.22);border-radius:18px;padding:1.2rem;">
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#C4B5FD;margin-bottom:.8rem;">🔍 ¿Cómo encontrar ayuda física cercana?</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:9px;">
<div style="font-size:0.83rem;color:rgba(237,233,254,0.62);">📱 Busca en Google Maps: "Comisaría de Familia + tu ciudad"</div>
<div style="font-size:0.83rem;color:rgba(237,233,254,0.62);">📞 Llama al 155 para que te orienten al refugio más cercano</div>
<div style="font-size:0.83rem;color:rgba(237,233,254,0.62);">🚔 Dirígete a la estación de Policía más cercana</div>
<div style="font-size:0.83rem;color:rgba(237,233,254,0.62);">🏥 Cualquier hospital debe atenderte en urgencias sin costo</div>
</div></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# ACERCA DE
# ══════════════════════════════════════════
elif "Acerca" in pagina:
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#EDE9FE;margin-bottom:1.4rem;">
ℹ️ Acerca de SafeHer Colombia</div>""", unsafe_allow_html=True)

    c1,c2=st.columns([3,2])
    with c1:
        st.markdown("""<div style="background:rgba(130,80,255,0.09);border:1px solid rgba(130,80,255,0.22);border-radius:22px;padding:1.5rem;margin-bottom:1rem;">
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#C4B5FD;font-size:1.05rem;margin-bottom:.9rem;">🎓 Proyecto Académico</div>
<p style="color:rgba(237,233,254,0.68);line-height:1.75;font-size:0.9rem;">
Desarrollado como proyecto de <b style="color:#EDE9FE;">Analítica y Machine Learning</b>.
Modelos entrenados con datos del Sistema de Información Estadístico, Delincuencial,
Contravencional y Operativo de la <b style="color:#EDE9FE;">Policía Nacional de Colombia</b>.</p>
<div style="height:1px;background:rgba(130,80,255,0.2);margin:1rem 0;"></div>
<div style="font-weight:600;color:#EDE9FE;margin-bottom:.6rem;">👩‍💻 Equipo:</div>""", unsafe_allow_html=True)
        for n in ["Laura Sofia Beltrán","Dana Yaray Vargas","Vanessa Mora"]:
            st.markdown(f"""<div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:9px 13px;
display:flex;align-items:center;gap:10px;margin-bottom:6px;">
<span style="font-size:1.1rem;">👩‍🎓</span>
<span style="color:rgba(237,233,254,0.78);font-size:0.88rem;">{n}</span></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""<div style="background:rgba(130,80,255,0.09);border:1px solid rgba(130,80,255,0.22);border-radius:22px;padding:1.5rem;">
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#C4B5FD;font-size:1.05rem;margin-bottom:.9rem;">🤖 Modelos de Machine Learning</div>""", unsafe_allow_html=True)
        for ti,al,ta,co in [("📊 Nivel de Gravedad","XGBoost + LightGBM","8 clases: MÍNIMO → CRÍTICO","#7C3AED"),
                             ("🗺️ Zona de Riesgo","XGBoost + LightGBM","6 clases: MUY BAJO → MUY ALTO","#2563EB"),
                             ("👥 Total de Víctimas","Estimación combinada","Valor numérico estimado","#059669")]:
            st.markdown(f"""<div style="background:linear-gradient(135deg,{co}13,{co}07);border:1px solid {co}30;
border-radius:12px;padding:11px 14px;margin-bottom:7px;">
<div style="font-weight:600;color:#EDE9FE;font-size:0.88rem;margin-bottom:3px;">{ti}</div>
<div style="font-size:0.76rem;color:{co};margin-bottom:2px;">{al}</div>
<div style="font-size:0.73rem;color:rgba(237,233,254,0.42);">Target: {ta}</div></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("""<div style="background:rgba(245,158,11,0.09);border:1px solid rgba(245,158,11,0.26);border-radius:22px;padding:1.3rem;margin-bottom:1rem;">
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#FCD34D;margin-bottom:.7rem;">⚠️ Limitaciones</div>
<p style="color:rgba(237,233,254,0.62);font-size:0.84rem;line-height:1.7;">
Plataforma <b style="color:#EDE9FE;">académica prototipo</b>. Las predicciones son aproximaciones estadísticas.
Para emergencias: <b style="color:#EF4444;">123</b> o <b style="color:#A78BFA;">Línea 155</b>.</p></div>""", unsafe_allow_html=True)

        # Gráfica de tecnologías
        techs=['Streamlit','XGBoost','LightGBM','Scikit-learn','Plotly','Pandas']
        vals=[95,92,90,88,85,90]
        fig=go.Figure(go.Bar(
            x=vals, y=techs, orientation='h',
            marker=dict(color=['#7C3AED','#2563EB','#059669','#D97706','#8B5CF6','#0891B2'],opacity=0.85),
            text=[f'{v}%' for v in vals], textposition='outside',
            textfont=dict(size=10,color='rgba(237,233,254,0.65)'),
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#EDE9FE',family='Plus Jakarta Sans'),
            xaxis=dict(range=[0,115],showgrid=False,showticklabels=False),
            yaxis=dict(gridcolor='rgba(130,80,255,0.08)'),
            margin=dict(t=35,b=15,l=10,r=55), height=250,
            title=dict(text='Stack tecnológico',font=dict(size=12,color='#C4B5FD')),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""<div style="background:rgba(16,185,129,0.09);border:1px solid rgba(16,185,129,0.26);border-radius:20px;padding:1.2rem;">
<div style="font-family:'Syne',sans-serif;font-weight:700;color:#34D399;margin-bottom:.8rem;">📊 Datos del modelo</div>""", unsafe_allow_html=True)
        for k,v in [("Cobertura","Colombia completa"),("Departamentos","33"),
                    ("Municipios","1.121"),("Tipos delito","6"),("Fuente","Policía Nacional")]:
            st.markdown(f"""<div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:5px;">
<span style="color:rgba(237,233,254,0.48);">{k}</span>
<span style="color:#EDE9FE;font-weight:600;">{v}</span></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
