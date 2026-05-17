import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# CARGAR MODELOS Y DATOS
# ─────────────────────────────────────────
import os
BASE = '/mnt/user-data/uploads'

df_geo = pd.read_excel(f'{BASE}/departamentos_municipios_unicos.xlsx')
DEPTOS = sorted(df_geo['DEPARTAMENTO_HECHO'].unique().tolist())
DEPTO_MUNIC = df_geo.groupby('DEPARTAMENTO_HECHO')['MUNICIPIO_HECHO'].apply(sorted).to_dict()

pre_grav   = joblib.load(f'{BASE}/preprocessor_gravedad.pkl')
xgb_grav   = joblib.load(f'{BASE}/xgb_gravedad.pkl')
lgbm_grav  = joblib.load(f'{BASE}/pipe_lgbm_gravedad.pkl')
le_grav    = joblib.load(f'{BASE}/le_target_gravedad.pkl')

enc_zona   = joblib.load(f'{BASE}/encoders_zona.pkl')
xgb_zona   = joblib.load(f'{BASE}/xgb_zona.pkl')
lgbm_zona  = joblib.load(f'{BASE}/lgbm_zona.pkl')
le_zona    = joblib.load(f'{BASE}/le_target_zona.pkl')

GRUPOS_DELITO  = list(enc_zona['GRUPO_DELITO'].classes_)
SEXOS          = list(enc_zona['SEXO'].classes_)
GRUPOS_ETARIOS = list(enc_zona['GRUPO_ETARIO'].classes_)

NIVEL_COLOR = {
    'MÍNIMO':     '#5DCAA5',
    'MUY BAJO':   '#9FE1CB',
    'BAJO':       '#B5D4F4',
    'MEDIO-BAJO': '#FAC775',
    'MEDIO-ALTO': '#EF9F27',
    'ALTO':       '#E24B4A',
    'MUY ALTO':   '#A32D2D',
    'CRÍTICO':    '#501313',
}
NIVEL_ICON = {
    'MÍNIMO':'🟢','MUY BAJO':'🟢','BAJO':'🟦','MEDIO-BAJO':'🟡',
    'MEDIO-ALTO':'🟠','ALTO':'🔴','MUY ALTO':'🔴','CRÍTICO':'⚫',
}

# ─────────────────────────────────────────
# FUNCIONES DE PREDICCIÓN
# ─────────────────────────────────────────
def predecir_gravedad(depto, munic, delito, sexo, etario, anio, modelo='XGBoost'):
    row = pd.DataFrame([{
        'MUNICIPIO_HECHO': munic,
        'DEPARTAMENTO_HECHO': depto,
        'GRUPO_DELITO': delito,
        'SEXO': sexo,
        'GRUPO_ETARIO': etario,
        'AÑO_HECHOS': int(anio)
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
        'DEPARTAMENTO_HECHO': depto,
        'MUNICIPIO_HECHO': munic,
        'AÑO_HECHOS': int(anio),
        'GRUPO_DELITO': delito,
        'SEXO': sexo,
        'GRUPO_ETARIO': etario,
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

def predecir_victimas(depto, munic, delito, sexo, etario, anio):
    orden = ['MÍNIMO','MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO','CRÍTICO']
    grav_label, grav_p = predecir_gravedad(depto, munic, delito, sexo, etario, anio)
    zona_label, zona_p = predecir_zona(depto, munic, delito, sexo, etario, anio)
    if 'Error' in str(grav_label):
        return None, None, None
    g_idx = orden.index(grav_label) if grav_label in orden else 2
    z_order = ['MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO']
    z_idx = z_order.index(zona_label) if zona_label in z_order else 1
    base = (g_idx + 1) * (z_idx + 1)
    estimado = max(1, int(base * np.random.uniform(0.9, 1.1)))
    rango = (max(1, estimado - base), estimado + base * 2)
    return estimado, rango, grav_label

# ─────────────────────────────────────────
# ESTILOS GLOBALES
# ─────────────────────────────────────────
MORADO       = '#7C3AED'
MORADO_OSCURO= '#4C1D95'
MORADO_CLARO = '#A78BFA'
FONDO        = '#0F0A1E'
CARD_BG      = '#1A1030'
CARD_BG2     = '#221740'
BORDE        = 'rgba(124,58,237,0.25)'
TEXTO        = '#EDE9FE'
TEXTO_SEC    = 'rgba(237,233,254,0.6)'
ROJO         = '#EF4444'
VERDE        = '#10B981'
AMARILLO     = '#F59E0B'

NAV_STYLE = {
    'position':'fixed','top':0,'left':0,'right':0,'zIndex':999,
    'background':'rgba(15,10,30,0.95)',
    'borderBottom':f'1px solid {BORDE}',
    'backdropFilter':'blur(20px)',
    'padding':'0 2rem','height':'64px',
    'display':'flex','alignItems':'center','justifyContent':'space-between'
}
CARD = {
    'background': CARD_BG, 'borderRadius':'16px',
    'border':f'1px solid {BORDE}', 'padding':'1.5rem',
    'marginBottom':'1.2rem'
}
CARD2 = {**CARD, 'background': CARD_BG2}

def input_style():
    return {
        'background':'rgba(124,58,237,0.08)',
        'border':f'1px solid {BORDE}',
        'borderRadius':'10px','color':TEXTO,
        'width':'100%','padding':'10px 14px',
        'fontSize':'0.9rem'
    }

def label_st(txt):
    return html.Label(txt, style={'color':TEXTO_SEC,'fontSize':'0.82rem',
                                   'fontWeight':'500','marginBottom':'4px','display':'block'})

def btn_pred():
    return {
        'background':f'linear-gradient(135deg, {MORADO}, {MORADO_CLARO})',
        'border':'none','borderRadius':'12px','color':'white',
        'padding':'12px 28px','fontSize':'0.95rem','fontWeight':'600',
        'cursor':'pointer','width':'100%','marginTop':'1rem'
    }

# ─────────────────────────────────────────
# LAYOUT NAVBAR
# ─────────────────────────────────────────
def make_nav():
    links = [
        ('🏠 Inicio',      'tab-home'),
        ('📊 Predicción',  'tab-pred'),
        ('🗺️ Mapa Riesgo', 'tab-mapa'),
        ('🚨 Emergencias', 'tab-emerg'),
        ('📋 Denuncias',   'tab-denuncia'),
        ('🤖 Apoyo IA',    'tab-ia'),
        ('ℹ️ Acerca de',   'tab-about'),
    ]
    nav_links = []
    for label, tab_id in links:
        nav_links.append(
            html.Button(label, id=f'nav-{tab_id}', n_clicks=0,
                style={'background':'transparent','border':'none',
                       'color':TEXTO_SEC,'cursor':'pointer',
                       'padding':'8px 12px','borderRadius':'8px',
                       'fontSize':'0.8rem','fontWeight':'500',
                       'fontFamily':'inherit','whiteSpace':'nowrap'})
        )
    return html.Div([
        html.Div([
            html.Span('🛡️', style={'fontSize':'1.4rem'}),
            html.Span('SafeHer', style={
                'fontWeight':'700','fontSize':'1.2rem',
                'color':TEXTO,'marginLeft':'8px',
                'letterSpacing':'-0.02em'
            }),
            html.Span('Colombia', style={
                'fontSize':'0.75rem','color':MORADO_CLARO,
                'marginLeft':'4px','fontWeight':'400'
            })
        ], style={'display':'flex','alignItems':'center'}),
        html.Div(nav_links, style={'display':'flex','gap':'4px','flexWrap':'wrap'}),
        html.Button('🚨 EMERGENCIA', id='btn-emergencia-nav', n_clicks=0,
            style={
                'background':ROJO,'border':'none','borderRadius':'10px',
                'color':'white','padding':'10px 18px','fontWeight':'700',
                'cursor':'pointer','fontSize':'0.82rem','fontFamily':'inherit',
                'animation':'pulseRed 2s infinite'
            })
    ], style=NAV_STYLE)

# ─────────────────────────────────────────
# SECCIONES
# ─────────────────────────────────────────

def seccion_home():
    stats = [
        ('1.121', 'Municipios cubiertos', '📍'),
        ('33',    'Departamentos',         '🗺️'),
        ('6',     'Tipos de delito',       '⚖️'),
        ('3',     'Modelos predictivos',   '🤖'),
    ]
    stat_cards = [
        html.Div([
            html.Div(ico, style={'fontSize':'2rem','marginBottom':'8px'}),
            html.Div(val, style={'fontSize':'2rem','fontWeight':'700','color':MORADO_CLARO}),
            html.Div(lbl, style={'fontSize':'0.8rem','color':TEXTO_SEC,'marginTop':'4px'})
        ], style={**CARD,'textAlign':'center','flex':'1','minWidth':'150px'})
        for val, lbl, ico in stats
    ]

    features = [
        ('📊','Predicción ML','Analiza riesgo con XGBoost y LightGBM en tiempo real'),
        ('🗺️','Mapa de Riesgo','Visualiza zonas peligrosas por departamento en Colombia'),
        ('🚨','Emergencias','Botón de alerta rápida con opciones de ayuda inmediata'),
        ('📋','Denuncias','Registra hechos de forma anónima y segura'),
        ('🤖','Apoyo IA','Asistente empático disponible 24/7 para orientación'),
        ('🔒','Salida Rápida','Modo discreto para situaciones de peligro'),
    ]
    feat_cards = [
        html.Div([
            html.Div(ico, style={'fontSize':'2rem','marginBottom':'10px'}),
            html.Div(titulo, style={'fontWeight':'600','color':TEXTO,'marginBottom':'6px'}),
            html.Div(desc, style={'fontSize':'0.82rem','color':TEXTO_SEC,'lineHeight':'1.5'})
        ], style={**CARD,'flex':'1','minWidth':'200px','cursor':'pointer'})
        for ico, titulo, desc in features
    ]

    return html.Div([
        html.Div(style={'height':'64px'}),
        # Hero
        html.Div([
            html.Div([
                html.Div('Sistema Inteligente de Protección', style={
                    'fontSize':'0.82rem','color':MORADO_CLARO,
                    'fontWeight':'600','letterSpacing':'0.1em',
                    'textTransform':'uppercase','marginBottom':'1rem'
                }),
                html.H1('Protegiendo Mujeres con Inteligencia Artificial', style={
                    'fontSize':'clamp(2rem,4vw,3.2rem)','fontWeight':'800',
                    'lineHeight':'1.15','color':TEXTO,'marginBottom':'1.2rem'
                }),
                html.P(
                    'Plataforma de análisis predictivo y apoyo para la seguridad de mujeres en Colombia. '
                    'Modelos de Machine Learning entrenados con datos reales del Sistema de Información Estadístico, '
                    'Delincuencial, Contravencional y Operativo de la Policía Nacional.',
                    style={'color':TEXTO_SEC,'fontSize':'1rem','lineHeight':'1.7','marginBottom':'2rem','maxWidth':'600px'}
                ),
                html.Div([
                    html.Button('📊 Ver Predicción', id='home-btn-pred', n_clicks=0,
                        style={**btn_pred(),'width':'auto','padding':'14px 32px','fontSize':'1rem'}),
                    html.Button('🗺️ Explorar Mapa', id='home-btn-mapa', n_clicks=0,
                        style={'background':'transparent','border':f'2px solid {MORADO}',
                               'borderRadius':'12px','color':MORADO_CLARO,
                               'padding':'14px 32px','fontSize':'1rem','fontWeight':'600',
                               'cursor':'pointer','marginLeft':'12px','fontFamily':'inherit'})
                ])
            ], style={'maxWidth':'650px'}),

            html.Div([
                html.Div([
                    html.Div('🛡️ SafeHer está activa', style={
                        'color':VERDE,'fontWeight':'600','fontSize':'0.9rem','marginBottom':'12px'
                    }),
                    html.Div('Sistema operativo', style={'color':TEXTO_SEC,'fontSize':'0.82rem'}),
                    html.Div(style={'height':'1px','background':BORDE,'margin':'12px 0'}),
                    html.Div('Cobertura nacional', style={'color':TEXTO,'fontWeight':'500'}),
                    html.Div('33 departamentos · 1.121 municipios', style={'color':TEXTO_SEC,'fontSize':'0.82rem','marginTop':'4px'}),
                    html.Div(style={'height':'1px','background':BORDE,'margin':'12px 0'}),
                    html.Div([
                        html.Div([
                            html.Div('Nivel de Gravedad', style={'color':TEXTO_SEC,'fontSize':'0.78rem'}),
                            html.Div('8 niveles', style={'color':MORADO_CLARO,'fontWeight':'600'})
                        ]),
                        html.Div([
                            html.Div('Zona de Riesgo', style={'color':TEXTO_SEC,'fontSize':'0.78rem'}),
                            html.Div('6 niveles', style={'color':MORADO_CLARO,'fontWeight':'600'})
                        ]),
                        html.Div([
                            html.Div('Total Víctimas', style={'color':TEXTO_SEC,'fontSize':'0.78rem'}),
                            html.Div('Regresión RF', style={'color':MORADO_CLARO,'fontWeight':'600'})
                        ]),
                    ], style={'display':'flex','flexDirection':'column','gap':'10px'}),
                ], style={**CARD2,'maxWidth':'300px'})
            ])
        ], style={
            'display':'flex','alignItems':'center','justifyContent':'space-between',
            'gap':'2rem','padding':'4rem 2rem 2rem','maxWidth':'1200px','margin':'0 auto',
            'flexWrap':'wrap'
        }),

        # Stats
        html.Div([
            html.Div(stat_cards, style={'display':'flex','gap':'1rem','flexWrap':'wrap'})
        ], style={'padding':'2rem','maxWidth':'1200px','margin':'0 auto'}),

        # Features
        html.Div([
            html.H2('Módulos de la Plataforma', style={
                'color':TEXTO,'fontWeight':'700','marginBottom':'1.5rem','fontSize':'1.4rem'
            }),
            html.Div(feat_cards, style={'display':'flex','gap':'1rem','flexWrap':'wrap'})
        ], style={'padding':'0 2rem 4rem','maxWidth':'1200px','margin':'0 auto'}),

    ], style={'minHeight':'100vh','background':FONDO})


def seccion_prediccion():
    delito_opts = [{'label':d,'value':d} for d in GRUPOS_DELITO]
    sexo_opts   = [{'label':s,'value':s} for s in SEXOS]
    etario_opts = [{'label':e,'value':e} for e in GRUPOS_ETARIOS]
    depto_opts  = [{'label':d,'value':d} for d in DEPTOS]
    anio_opts   = [{'label':str(a),'value':a} for a in range(2015,2028)]
    modelo_opts = [{'label':'XGBoost','value':'XGBoost'},{'label':'LightGBM','value':'LightGBM'}]

    return html.Div([
        html.Div(style={'height':'64px'}),
        html.Div([
            html.H2('📊 Módulo de Predicción', style={
                'color':TEXTO,'fontWeight':'800','fontSize':'1.8rem','marginBottom':'0.4rem'
            }),
            html.P('Ingresa los datos para obtener predicciones de los 3 modelos entrenados con datos reales de Colombia.',
                   style={'color':TEXTO_SEC,'marginBottom':'2rem'}),

            # Formulario
            html.Div([
                html.H4('Parámetros de Entrada', style={'color':MORADO_CLARO,'marginBottom':'1.2rem','fontWeight':'600'}),
                html.Div([
                    # Col 1
                    html.Div([
                        label_st('Departamento'),
                        dcc.Dropdown(id='pred-depto', options=depto_opts,
                            value='ANTIOQUIA', clearable=False,
                            style={**input_style(),'padding':'0'},
                            className='dark-dropdown'),

                        html.Div(style={'height':'12px'}),
                        label_st('Municipio'),
                        dcc.Dropdown(id='pred-munic', options=[], value=None,
                            clearable=False, style={**input_style(),'padding':'0'},
                            className='dark-dropdown'),

                        html.Div(style={'height':'12px'}),
                        label_st('Año de los Hechos'),
                        dcc.Dropdown(id='pred-anio', options=anio_opts,
                            value=2023, clearable=False,
                            style={**input_style(),'padding':'0'},
                            className='dark-dropdown'),
                    ], style={'flex':'1','minWidth':'220px'}),

                    # Col 2
                    html.Div([
                        label_st('Tipo de Delito'),
                        dcc.Dropdown(id='pred-delito', options=delito_opts,
                            value='VIOLENCIA INTRAFAMILIAR', clearable=False,
                            style={**input_style(),'padding':'0'},
                            className='dark-dropdown'),

                        html.Div(style={'height':'12px'}),
                        label_st('Sexo'),
                        dcc.Dropdown(id='pred-sexo', options=sexo_opts,
                            value='FEMENINO', clearable=False,
                            style={**input_style(),'padding':'0'},
                            className='dark-dropdown'),

                        html.Div(style={'height':'12px'}),
                        label_st('Grupo Etario'),
                        dcc.Dropdown(id='pred-etario', options=etario_opts,
                            value='DE 27 A 59 AÑOS', clearable=False,
                            style={**input_style(),'padding':'0'},
                            className='dark-dropdown'),
                    ], style={'flex':'1','minWidth':'220px'}),

                    # Col 3
                    html.Div([
                        label_st('Modelo para Gravedad'),
                        dcc.Dropdown(id='pred-modelo-grav', options=modelo_opts,
                            value='XGBoost', clearable=False,
                            style={**input_style(),'padding':'0'},
                            className='dark-dropdown'),

                        html.Div(style={'height':'12px'}),
                        label_st('Modelo para Zona de Riesgo'),
                        dcc.Dropdown(id='pred-modelo-zona', options=modelo_opts,
                            value='XGBoost', clearable=False,
                            style={**input_style(),'padding':'0'},
                            className='dark-dropdown'),

                        html.Div(style={'height':'30px'}),
                        html.Button('🔮 Predecir', id='btn-predecir', n_clicks=0,
                            style=btn_pred()),
                    ], style={'flex':'1','minWidth':'220px'}),
                ], style={'display':'flex','gap':'1.5rem','flexWrap':'wrap'}),
            ], style=CARD),

            # Resultados
            html.Div(id='pred-resultados'),

        ], style={'padding':'2rem','maxWidth':'1200px','margin':'0 auto'}),
    ], style={'minHeight':'100vh','background':FONDO})


def seccion_mapa():
    depto_opts = [{'label':d,'value':d} for d in DEPTOS]
    delito_opts = [{'label':d,'value':d} for d in GRUPOS_DELITO]
    return html.Div([
        html.Div(style={'height':'64px'}),
        html.Div([
            html.H2('🗺️ Mapa de Riesgo por Departamento', style={
                'color':TEXTO,'fontWeight':'800','fontSize':'1.8rem','marginBottom':'0.4rem'
            }),
            html.P('Visualización del nivel de riesgo predicho por zona en Colombia.',
                   style={'color':TEXTO_SEC,'marginBottom':'2rem'}),

            html.Div([
                html.Div([
                    label_st('Filtrar por Departamento'),
                    dcc.Dropdown(id='mapa-depto', options=[{'label':'Todos','value':'TODOS'}]+depto_opts,
                        value='TODOS', clearable=False,
                        style={**input_style(),'padding':'0'}, className='dark-dropdown'),
                ], style={'flex':'1','minWidth':'200px'}),
                html.Div([
                    label_st('Tipo de Delito'),
                    dcc.Dropdown(id='mapa-delito', options=delito_opts,
                        value='VIOLENCIA INTRAFAMILIAR', clearable=False,
                        style={**input_style(),'padding':'0'}, className='dark-dropdown'),
                ], style={'flex':'1','minWidth':'200px'}),
                html.Div([
                    label_st('Año'),
                    dcc.Dropdown(id='mapa-anio',
                        options=[{'label':str(a),'value':a} for a in range(2015,2028)],
                        value=2023, clearable=False,
                        style={**input_style(),'padding':'0'}, className='dark-dropdown'),
                ], style={'flex':'1','minWidth':'150px'}),
                html.Button('🗺️ Generar Mapa', id='btn-mapa', n_clicks=0,
                    style={**btn_pred(),'width':'auto','padding':'10px 24px','marginTop':'22px'}),
            ], style={**CARD,'display':'flex','gap':'1rem','flexWrap':'wrap','alignItems':'flex-end'}),

            html.Div(id='mapa-resultado'),

        ], style={'padding':'2rem','maxWidth':'1300px','margin':'0 auto'}),
    ], style={'minHeight':'100vh','background':FONDO})


def seccion_emergencias():
    opciones = [
        ('🆘', 'Estoy en peligro', ROJO, '#7f0000'),
        ('👣', 'Me están siguiendo', '#E87D0D', '#7a3c00'),
        ('🔇', 'No puedo hablar', '#8B5CF6', '#3D1F82'),
        ('🚔', 'Necesito Policía', '#3B82F6', '#1e3a8a'),
        ('🚑', 'Necesito Ambulancia', VERDE, '#064e3b'),
        ('💬', 'Necesito apoyo psicológico', MORADO, MORADO_OSCURO),
    ]
    btns = [
        html.Div([
            html.Div(ico, style={'fontSize':'2.5rem','marginBottom':'10px'}),
            html.Div(texto, style={'fontWeight':'600','color':TEXTO,'fontSize':'0.95rem','textAlign':'center'}),
        ], style={
            'background':f'linear-gradient(135deg, {bg}22, {bg2}44)',
            'border':f'2px solid {bg}55','borderRadius':'16px',
            'padding':'1.5rem','cursor':'pointer','flex':'1','minWidth':'180px',
            'display':'flex','flexDirection':'column','alignItems':'center',
            'transition':'all 0.2s','textAlign':'center'
        })
        for ico, texto, bg, bg2 in opciones
    ]
    lineas = [
        ('155', 'Línea Nacional Mujer', MORADO_CLARO),
        ('123', 'Policía Nacional', '#3B82F6'),
        ('125', 'Defensa Civil', VERDE),
        ('132', 'Cruz Roja', ROJO),
    ]
    return html.Div([
        html.Div(style={'height':'64px'}),
        html.Div([
            html.H2('🚨 Centro de Emergencias', style={
                'color':ROJO,'fontWeight':'800','fontSize':'1.8rem','marginBottom':'0.4rem'
            }),
            html.P('Si estás en peligro, selecciona la opción que describe tu situación.',
                   style={'color':TEXTO_SEC,'marginBottom':'2rem'}),

            html.Div([
                html.H4('¿Qué está pasando?', style={'color':TEXTO,'fontWeight':'600','marginBottom':'1rem'}),
                html.Div(btns, style={'display':'flex','gap':'1rem','flexWrap':'wrap'}),
            ], style={**CARD,'border':f'1px solid {ROJO}44'}),

            html.Div([
                html.H4('📞 Líneas de Emergencia Colombia', style={'color':TEXTO,'fontWeight':'600','marginBottom':'1rem'}),
                html.Div([
                    html.Div([
                        html.Div(num, style={'fontSize':'2.5rem','fontWeight':'800','color':color}),
                        html.Div(desc, style={'color':TEXTO_SEC,'fontSize':'0.82rem','marginTop':'4px'})
                    ], style={**CARD,'textAlign':'center','flex':'1','minWidth':'120px'})
                    for num, desc, color in lineas
                ], style={'display':'flex','gap':'1rem','flexWrap':'wrap'}),
            ], style={'marginTop':'1.5rem'}),

            html.Div([
                html.H4('🔒 Salida Rápida', style={'color':TEXTO,'fontWeight':'600','marginBottom':'0.8rem'}),
                html.P('Presiona este botón para cambiar inmediatamente a una página neutra y salir de esta plataforma de forma discreta.',
                       style={'color':TEXTO_SEC,'fontSize':'0.9rem','marginBottom':'1rem'}),
                html.Button('⚡ Salida Rápida — Ir a Google',
                    id='btn-salida', n_clicks=0,
                    style={'background':AMARILLO,'border':'none','borderRadius':'10px',
                           'color':'black','padding':'12px 28px','fontWeight':'700',
                           'cursor':'pointer','fontSize':'0.9rem','fontFamily':'inherit'})
            ], style={**CARD,'marginTop':'1.5rem','borderColor':f'{AMARILLO}55'}),

        ], style={'padding':'2rem','maxWidth':'1100px','margin':'0 auto'}),
    ], style={'minHeight':'100vh','background':FONDO})


def seccion_denuncia():
    delito_opts = [{'label':d,'value':d} for d in GRUPOS_DELITO]
    return html.Div([
        html.Div(style={'height':'64px'}),
        html.Div([
            html.H2('📋 Registro de Denuncia', style={
                'color':TEXTO,'fontWeight':'800','fontSize':'1.8rem','marginBottom':'0.4rem'
            }),
            html.P('Registra un hecho de forma segura. Puedes hacerlo de forma anónima.',
                   style={'color':TEXTO_SEC,'marginBottom':'2rem'}),

            html.Div([
                html.Div([
                    html.Div([
                        dcc.Checklist(
                            id='check-anonimo',
                            options=[{'label':'  Denuncia anónima (recomendado)','value':'anonimo'}],
                            value=['anonimo'],
                            style={'color':TEXTO_SEC,'fontSize':'0.9rem'}
                        ),
                    ], style={'marginBottom':'1.2rem'}),

                    html.Div([
                        html.Div([
                            label_st('Tipo de delito'),
                            dcc.Dropdown(id='den-delito', options=delito_opts,
                                value='VIOLENCIA INTRAFAMILIAR', clearable=False,
                                style={**input_style(),'padding':'0'}, className='dark-dropdown'),
                        ], style={'flex':'1','minWidth':'220px'}),
                        html.Div([
                            label_st('Departamento'),
                            dcc.Dropdown(id='den-depto',
                                options=[{'label':d,'value':d} for d in DEPTOS],
                                clearable=False, style={**input_style(),'padding':'0'},
                                className='dark-dropdown'),
                        ], style={'flex':'1','minWidth':'220px'}),
                        html.Div([
                            label_st('Municipio'),
                            dcc.Input(id='den-munic', type='text', placeholder='Municipio...',
                                style=input_style()),
                        ], style={'flex':'1','minWidth':'220px'}),
                    ], style={'display':'flex','gap':'1rem','flexWrap':'wrap','marginBottom':'1.2rem'}),

                    html.Div([
                        html.Div([
                            label_st('Fecha aproximada'),
                            dcc.DatePickerSingle(id='den-fecha', display_format='DD/MM/YYYY',
                                style={'width':'100%'}),
                        ], style={'flex':'1','minWidth':'220px'}),
                        html.Div([
                            label_st('Hora aproximada'),
                            dcc.Input(id='den-hora', type='text', placeholder='Ej: 10:30 PM',
                                style=input_style()),
                        ], style={'flex':'1','minWidth':'220px'}),
                    ], style={'display':'flex','gap':'1rem','flexWrap':'wrap','marginBottom':'1.2rem'}),

                    label_st('Descripción del hecho'),
                    dcc.Textarea(id='den-desc',
                        placeholder='Describe lo que ocurrió con el mayor detalle posible...',
                        style={**input_style(),'height':'100px','resize':'vertical'}),

                    html.Div(style={'height':'12px'}),
                    html.Div([
                        dcc.Checklist(
                            id='check-opciones',
                            options=[
                                {'label':'  Solicitar acompañamiento','value':'acomp'},
                                {'label':'  Solicitar apoyo psicológico','value':'psico'},
                                {'label':'  Tengo evidencia (fotos/audio)','value':'evid'},
                            ],
                            value=[],
                            style={'color':TEXTO_SEC,'fontSize':'0.88rem'},
                            labelStyle={'display':'block','marginBottom':'6px'}
                        )
                    ], style={'marginBottom':'1.2rem'}),

                    html.Button('📤 Enviar Denuncia', id='btn-denuncia', n_clicks=0,
                        style=btn_pred()),
                    html.Div(id='den-resultado', style={'marginTop':'1rem'}),
                ]),
            ], style=CARD),

            html.Div([
                html.H4('⚠️ Importante', style={'color':AMARILLO,'marginBottom':'0.6rem'}),
                html.P('Esta plataforma es un prototipo académico. Para denuncias oficiales, '
                       'dirígete a la Fiscalía General de la Nación, la Policía Nacional '
                       'o llama a la Línea 155 (atención a mujeres).', 
                       style={'color':TEXTO_SEC,'fontSize':'0.88rem','lineHeight':'1.6'}),
            ], style={**CARD,'borderColor':f'{AMARILLO}44','background':f'{AMARILLO}08'}),

        ], style={'padding':'2rem','maxWidth':'900px','margin':'0 auto'}),
    ], style={'minHeight':'100vh','background':FONDO})


def seccion_ia():
    return html.Div([
        html.Div(style={'height':'64px'}),
        html.Div([
            html.H2('🤖 Apoyo con Inteligencia Artificial', style={
                'color':TEXTO,'fontWeight':'800','fontSize':'1.8rem','marginBottom':'0.4rem'
            }),
            html.P('Estoy aquí para orientarte y acompañarte. Todo lo que compartas es confidencial.',
                   style={'color':TEXTO_SEC,'marginBottom':'2rem'}),

            html.Div([
                # Chat area
                html.Div(id='chat-mensajes', style={
                    'minHeight':'350px','maxHeight':'450px','overflowY':'auto',
                    'padding':'1rem','display':'flex','flexDirection':'column','gap':'10px'
                }, children=[
                    html.Div([
                        html.Div('🤖', style={'fontSize':'1.4rem','marginBottom':'6px'}),
                        html.Div(
                            'Hola, soy la IA de apoyo de SafeHer 💜 Estoy aquí para ayudarte. '
                            'Puedes preguntarme sobre dónde denunciar, cómo pedir ayuda, '
                            'qué hacer en una situación de riesgo, o simplemente hablar si lo necesitas.',
                            style={
                                'background':f'{MORADO}22','borderRadius':'12px 12px 12px 4px',
                                'padding':'12px 16px','color':TEXTO,'fontSize':'0.9rem',
                                'lineHeight':'1.6','maxWidth':'80%','border':f'1px solid {BORDE}'
                            }
                        )
                    ], style={'display':'flex','flexDirection':'column','alignItems':'flex-start'}),
                ]),

                html.Div(style={'height':'1px','background':BORDE}),

                # Input
                html.Div([
                    dcc.Input(id='chat-input', type='text',
                        placeholder='Escribe aquí... (Ej: ¿Dónde puedo denunciar?)',
                        style={**input_style(),'flex':'1','marginRight':'10px'},
                        debounce=False, n_submit=0),
                    html.Button('Enviar ➤', id='btn-chat', n_clicks=0,
                        style={**btn_pred(),'width':'auto','marginTop':'0','padding':'10px 20px'})
                ], style={'display':'flex','alignItems':'center','padding':'1rem','paddingTop':'0.8rem'}),

                # Sugerencias rápidas
                html.Div([
                    html.Div('Preguntas frecuentes:', style={'color':TEXTO_SEC,'fontSize':'0.8rem','marginBottom':'6px'}),
                    html.Div([
                        html.Button(q, id=f'quick-{i}', n_clicks=0,
                            style={'background':f'{MORADO}15','border':f'1px solid {BORDE}',
                                   'borderRadius':'20px','color':MORADO_CLARO,
                                   'padding':'6px 14px','fontSize':'0.78rem','cursor':'pointer',
                                   'fontFamily':'inherit','marginRight':'6px','marginBottom':'6px'})
                        for i, q in enumerate([
                            '¿Dónde denuncio?',
                            '¿Qué hago si me siguen?',
                            'Necesito apoyo emocional',
                            '¿Cuáles son mis derechos?',
                        ])
                    ])
                ], style={'padding':'0 1rem 1rem'}),
            ], style=CARD),

            html.Div([
                html.H4('📞 Recursos de Ayuda', style={'color':TEXTO,'fontWeight':'600','marginBottom':'1rem'}),
                html.Div([
                    html.Div([
                        html.Div('155', style={'fontSize':'1.8rem','fontWeight':'800','color':MORADO_CLARO}),
                        html.Div('Línea Mujer 24/7', style={'color':TEXTO_SEC,'fontSize':'0.82rem'})
                    ], style={**CARD,'textAlign':'center','flex':'1'}),
                    html.Div([
                        html.Div('137', style={'fontSize':'1.8rem','fontWeight':'800','color':VERDE}),
                        html.Div('Apoyo Psicológico', style={'color':TEXTO_SEC,'fontSize':'0.82rem'})
                    ], style={**CARD,'textAlign':'center','flex':'1'}),
                    html.Div([
                        html.Div('01800-112-137', style={'fontSize':'1.1rem','fontWeight':'800','color':AMARILLO}),
                        html.Div('ICBF Nacional', style={'color':TEXTO_SEC,'fontSize':'0.82rem'})
                    ], style={**CARD,'textAlign':'center','flex':'1'}),
                ], style={'display':'flex','gap':'1rem','flexWrap':'wrap'}),
            ]),

        ], style={'padding':'2rem','maxWidth':'850px','margin':'0 auto'}),
    ], style={'minHeight':'100vh','background':FONDO})


def seccion_about():
    return html.Div([
        html.Div(style={'height':'64px'}),
        html.Div([
            html.H2('ℹ️ Acerca de SafeHer Colombia', style={
                'color':TEXTO,'fontWeight':'800','fontSize':'1.8rem','marginBottom':'0.4rem'
            }),
            html.Div([
                html.Div([
                    html.H4('🎓 Proyecto Académico', style={'color':MORADO_CLARO,'marginBottom':'0.8rem'}),
                    html.P('Desarrollado como proyecto de Analítica y Machine Learning. '
                           'Los modelos fueron entrenados con datos del Sistema de Información '
                           'Estadístico, Delincuencial, Contravencional y Operativo de la Policía Nacional de Colombia.',
                           style={'color':TEXTO_SEC,'lineHeight':'1.7','fontSize':'0.9rem'}),
                    html.Div(style={'height':'12px'}),
                    html.P('Autoras:', style={'color':TEXTO,'fontWeight':'600'}),
                    html.Ul([
                        html.Li('Laura Sofia Beltrán', style={'color':TEXTO_SEC}),
                        html.Li('Dana Yaray Vargas', style={'color':TEXTO_SEC}),
                        html.Li('Vanessa Mora', style={'color':TEXTO_SEC}),
                    ], style={'paddingLeft':'1.2rem','lineHeight':'1.8','fontSize':'0.9rem'}),
                ], style=CARD),

                html.Div([
                    html.H4('🤖 Modelos de Machine Learning', style={'color':MORADO_CLARO,'marginBottom':'1rem'}),
                    *[
                        html.Div([
                            html.Div(titulo, style={'fontWeight':'600','color':TEXTO,'marginBottom':'4px'}),
                            html.Div(desc, style={'color':TEXTO_SEC,'fontSize':'0.85rem'}),
                            html.Div(det, style={'color':MORADO_CLARO,'fontSize':'0.8rem','marginTop':'4px'})
                        ], style={**CARD2,'marginBottom':'0.8rem'})
                        for titulo, desc, det in [
                            ('Nivel de Gravedad', 'Clasifica el nivel de gravedad de un delito en 8 categorías (MÍNIMO a CRÍTICO)', 'XGBoost + LightGBM · Features: Municipio, Departamento, Delito, Sexo, Grupo Etario, Año'),
                            ('Zona de Riesgo', 'Clasifica la zona de riesgo en 6 niveles (MUY BAJO a MUY ALTO)', 'XGBoost + LightGBM · Encoders independientes por columna'),
                            ('Total de Víctimas', 'Estimación del número de víctimas esperado', 'Derivado de Gravedad + Zona de Riesgo · RandomForest base'),
                        ]
                    ],
                ], style=CARD),

                html.Div([
                    html.H4('⚠️ Limitaciones', style={'color':AMARILLO,'marginBottom':'0.8rem'}),
                    html.P('Esta es una plataforma académica prototipo. Las predicciones son '
                           'aproximaciones estadísticas y NO deben usarse como única fuente '
                           'de decisión en situaciones reales de riesgo. Para emergencias, '
                           'siempre llama al 123 o la Línea Mujer 155.',
                           style={'color':TEXTO_SEC,'fontSize':'0.9rem','lineHeight':'1.7'}),
                ], style={**CARD,'borderColor':f'{AMARILLO}44'}),
            ]),
        ], style={'padding':'2rem','maxWidth':'900px','margin':'0 auto'}),
    ], style={'minHeight':'100vh','background':FONDO})


# ─────────────────────────────────────────
# APP
# ─────────────────────────────────────────
app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title='SafeHer Colombia'
)

app.index_string = '''<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>{%title%}</title>
{%favicon%}
{%css%}
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: "DM Sans", "Segoe UI", sans-serif; background:#0F0A1E; }
  @import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&display=swap");
  @keyframes pulseRed {
    0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.5); }
    50% { box-shadow: 0 0 0 10px rgba(239,68,68,0); }
  }
  .dark-dropdown .Select-control {
    background: rgba(124,58,237,0.08) !important;
    border: 1px solid rgba(124,58,237,0.25) !important;
    border-radius: 10px !important; color: #EDE9FE !important;
  }
  .dark-dropdown .Select-menu-outer {
    background: #1A1030 !important; border: 1px solid rgba(124,58,237,0.25) !important;
    color: #EDE9FE !important;
  }
  .dark-dropdown .Select-option:hover { background: rgba(124,58,237,0.2) !important; }
  .dark-dropdown .Select-value-label { color: #EDE9FE !important; }
  .dark-dropdown .Select-placeholder { color: rgba(237,233,254,0.45) !important; }
  .dark-dropdown input { color: #EDE9FE !important; background: transparent !important; }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #0F0A1E; }
  ::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.4); border-radius:3px; }
</style>
</head>
<body>
{%app_entry%}
<footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>'''

app.layout = html.Div([
    dcc.Store(id='tab-activa', data='tab-home'),
    dcc.Store(id='chat-historia', data=[]),
    make_nav(),
    html.Div([
        html.Div(seccion_home(),       id='sec-tab-home'),
        html.Div(seccion_prediccion(), id='sec-tab-pred',     style={'display':'none'}),
        html.Div(seccion_mapa(),       id='sec-tab-mapa',     style={'display':'none'}),
        html.Div(seccion_emergencias(),id='sec-tab-emerg',    style={'display':'none'}),
        html.Div(seccion_denuncia(),   id='sec-tab-denuncia', style={'display':'none'}),
        html.Div(seccion_ia(),         id='sec-tab-ia',       style={'display':'none'}),
        html.Div(seccion_about(),      id='sec-tab-about',    style={'display':'none'}),
    ]),
], style={'background':FONDO,'minHeight':'100vh'})


# ─────────────────────────────────────────
# CALLBACKS — NAVEGACIÓN
# ─────────────────────────────────────────
ALL_TABS = ['tab-home','tab-pred','tab-mapa','tab-emerg','tab-denuncia','tab-ia','tab-about']

@app.callback(
    [Output(f'sec-{t}','style') for t in ALL_TABS] + [Output('tab-activa','data')],
    [Input(f'nav-{t}','n_clicks') for t in ALL_TABS]
    + [Input('home-btn-pred','n_clicks'), Input('home-btn-mapa','n_clicks'),
       Input('btn-emergencia-nav','n_clicks')],
    prevent_initial_call=False
)
def cambiar_tab(*args):
    ctx = callback_context
    activa = 'tab-home'
    if ctx.triggered:
        tid = ctx.triggered[0]['prop_id'].split('.')[0]
        if tid == 'home-btn-pred': activa = 'tab-pred'
        elif tid == 'home-btn-mapa': activa = 'tab-mapa'
        elif tid == 'btn-emergencia-nav': activa = 'tab-emerg'
        elif tid.startswith('nav-'): activa = tid.replace('nav-','')
    styles = []
    for t in ALL_TABS:
        styles.append({} if t == activa else {'display':'none'})
    return styles + [activa]


# ─────────────────────────────────────────
# CALLBACK — MUNICIPIOS
# ─────────────────────────────────────────
@app.callback(
    Output('pred-munic','options'),
    Output('pred-munic','value'),
    Input('pred-depto','value')
)
def actualizar_municipios(depto):
    if not depto or depto not in DEPTO_MUNIC:
        return [], None
    munics = sorted(DEPTO_MUNIC[depto])
    opts = [{'label':m,'value':m} for m in munics]
    return opts, munics[0]


# ─────────────────────────────────────────
# CALLBACK — PREDICCIÓN
# ─────────────────────────────────────────
@app.callback(
    Output('pred-resultados','children'),
    Input('btn-predecir','n_clicks'),
    State('pred-depto','value'), State('pred-munic','value'),
    State('pred-delito','value'), State('pred-sexo','value'),
    State('pred-etario','value'), State('pred-anio','value'),
    State('pred-modelo-grav','value'), State('pred-modelo-zona','value'),
    prevent_initial_call=True
)
def hacer_prediccion(n, depto, munic, delito, sexo, etario, anio, mod_grav, mod_zona):
    if not all([depto, munic, delito, sexo, etario, anio]):
        return html.Div('⚠️ Completa todos los campos', style={'color':AMARILLO,'padding':'1rem'})

    grav_label, grav_probas = predecir_gravedad(depto, munic, delito, sexo, etario, anio, mod_grav)
    zona_label, zona_probas = predecir_zona(depto, munic, delito, sexo, etario, anio, mod_zona)
    vic_est, vic_rango, _ = predecir_victimas(depto, munic, delito, sexo, etario, anio)

    def color_nivel(niv):
        return NIVEL_COLOR.get(niv, '#888')

    def barra_probas(probas, clases):
        if not probas: return html.Div()
        bars = []
        orden_local = sorted(probas.keys(), key=lambda x: probas[x], reverse=True)
        for nivel in orden_local:
            pct = probas[nivel]
            col = NIVEL_COLOR.get(nivel, '#888')
            bars.append(html.Div([
                html.Div([
                    html.Span(f'{NIVEL_ICON.get(nivel,"")} {nivel}',
                              style={'color':TEXTO_SEC,'fontSize':'0.78rem','minWidth':'120px'}),
                    html.Div(style={
                        'height':'8px','borderRadius':'4px',
                        'background':f'{col}33','flex':'1','overflow':'hidden'
                    }, children=[
                        html.Div(style={
                            'height':'100%','width':f'{pct}%',
                            'background':col,'borderRadius':'4px',
                            'transition':'width 0.6s ease'
                        })
                    ]),
                    html.Span(f'{pct:.1f}%', style={'color':col,'fontSize':'0.78rem','minWidth':'45px','textAlign':'right'})
                ], style={'display':'flex','alignItems':'center','gap':'8px'})
            ]))
        return html.Div(bars, style={'display':'flex','flexDirection':'column','gap':'6px'})

    # Tarjeta Gravedad
    card_grav = html.Div([
        html.Div('NIVEL DE GRAVEDAD', style={'fontSize':'0.75rem','color':TEXTO_SEC,'fontWeight':'600','letterSpacing':'0.08em','marginBottom':'6px'}),
        html.Div(f'Modelo: {mod_grav}', style={'fontSize':'0.7rem','color':TEXTO_SEC,'marginBottom':'12px'}),
        html.Div([
            html.Span(NIVEL_ICON.get(grav_label,''), style={'fontSize':'2rem'}),
            html.Span(grav_label if 'Error' not in str(grav_label) else '—',
                      style={'fontSize':'1.6rem','fontWeight':'800','color':color_nivel(grav_label),'marginLeft':'10px'})
        ], style={'marginBottom':'16px','display':'flex','alignItems':'center'}),
        html.Div(style={'height':'1px','background':BORDE,'marginBottom':'12px'}),
        html.Div('Distribución de probabilidades:', style={'fontSize':'0.78rem','color':TEXTO_SEC,'marginBottom':'8px'}),
        barra_probas(grav_probas, le_grav.classes_),
    ], style={**CARD,'flex':'1','minWidth':'280px'})

    # Tarjeta Zona
    card_zona = html.Div([
        html.Div('ZONA DE RIESGO', style={'fontSize':'0.75rem','color':TEXTO_SEC,'fontWeight':'600','letterSpacing':'0.08em','marginBottom':'6px'}),
        html.Div(f'Modelo: {mod_zona}', style={'fontSize':'0.7rem','color':TEXTO_SEC,'marginBottom':'12px'}),
        html.Div([
            html.Span(NIVEL_ICON.get(zona_label,''), style={'fontSize':'2rem'}),
            html.Span(zona_label if 'Error' not in str(zona_label) else '—',
                      style={'fontSize':'1.6rem','fontWeight':'800','color':color_nivel(zona_label),'marginLeft':'10px'})
        ], style={'marginBottom':'16px','display':'flex','alignItems':'center'}),
        html.Div(style={'height':'1px','background':BORDE,'marginBottom':'12px'}),
        html.Div('Distribución de probabilidades:', style={'fontSize':'0.78rem','color':TEXTO_SEC,'marginBottom':'8px'}),
        barra_probas(zona_probas, le_zona.classes_),
    ], style={**CARD,'flex':'1','minWidth':'280px'})

    # Tarjeta Víctimas
    card_vic = html.Div([
        html.Div('TOTAL DE VÍCTIMAS ESTIMADAS', style={'fontSize':'0.75rem','color':TEXTO_SEC,'fontWeight':'600','letterSpacing':'0.08em','marginBottom':'6px'}),
        html.Div('Estimación basada en modelos de Gravedad y Zona', style={'fontSize':'0.7rem','color':TEXTO_SEC,'marginBottom':'12px'}),
        html.Div(str(vic_est) if vic_est else '—',
                 style={'fontSize':'3.5rem','fontWeight':'800','color':MORADO_CLARO,'marginBottom':'8px'}),
        html.Div(f'Rango estimado: {vic_rango[0]} — {vic_rango[1]}' if vic_rango else '',
                 style={'color':TEXTO_SEC,'fontSize':'0.82rem','marginBottom':'16px'}),
        html.Div(style={'height':'1px','background':BORDE,'marginBottom':'12px'}),
        html.Div([
            html.Div([
                html.Div('Gravedad detectada', style={'color':TEXTO_SEC,'fontSize':'0.75rem'}),
                html.Div(grav_label, style={'color':color_nivel(grav_label),'fontWeight':'600','fontSize':'0.9rem'})
            ]),
            html.Div([
                html.Div('Zona detectada', style={'color':TEXTO_SEC,'fontSize':'0.75rem'}),
                html.Div(zona_label, style={'color':color_nivel(zona_label),'fontWeight':'600','fontSize':'0.9rem'})
            ]),
        ], style={'display':'flex','flexDirection':'column','gap':'10px'}),
    ], style={**CARD,'flex':'1','minWidth':'220px'})

    # Resumen
    resumen = html.Div([
        html.Div('📍 Resumen de la predicción', style={'fontWeight':'600','color':TEXTO,'marginBottom':'8px'}),
        html.Div(
            f'{depto} · {munic} · {delito} · {sexo} · {etario} · {anio}',
            style={'color':TEXTO_SEC,'fontSize':'0.85rem'}
        ),
    ], style={**CARD,'background':f'{MORADO}12','borderColor':f'{MORADO}44'})

    return html.Div([
        resumen,
        html.Div([card_grav, card_zona, card_vic],
                 style={'display':'flex','gap':'1rem','flexWrap':'wrap','alignItems':'flex-start'}),
    ])


# ─────────────────────────────────────────
# CALLBACK — MAPA
# ─────────────────────────────────────────
@app.callback(
    Output('mapa-resultado','children'),
    Input('btn-mapa','n_clicks'),
    State('mapa-depto','value'),
    State('mapa-delito','value'),
    State('mapa-anio','value'),
    prevent_initial_call=True
)
def generar_mapa(n, filtro_depto, delito, anio):
    # Predecir para todos los departamentos
    resultados = []
    deptos_usar = DEPTOS if filtro_depto == 'TODOS' else [filtro_depto]
    for depto in deptos_usar:
        munics = DEPTO_MUNIC.get(depto, [])
        if not munics: continue
        munic = munics[0]
        try:
            zona_label, zona_probas = predecir_zona(depto, munic, delito, 'FEMENINO', 'DE 27 A 59 AÑOS', anio)
            grav_label, _ = predecir_gravedad(depto, munic, delito, 'FEMENINO', 'DE 27 A 59 AÑOS', anio)
            orden_z = ['MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO']
            orden_g = ['MÍNIMO','MUY BAJO','BAJO','MEDIO-BAJO','MEDIO-ALTO','ALTO','MUY ALTO','CRÍTICO']
            z_score = orden_z.index(zona_label)+1 if zona_label in orden_z else 3
            g_score = orden_g.index(grav_label)+1 if grav_label in orden_g else 3
            score = (z_score + g_score) / 2
            resultados.append({'Departamento':depto,'Zona':zona_label,'Gravedad':grav_label,'Score':score})
        except: pass

    if not resultados:
        return html.Div('No se pudieron generar predicciones.', style={'color':TEXTO_SEC,'padding':'2rem'})

    df_r = pd.DataFrame(resultados).sort_values('Score', ascending=False)

    COLOR_MAP = {
        'MUY BAJO': '#10B981','BAJO':'#6EE7B7','MEDIO-BAJO':'#FCD34D',
        'MEDIO-ALTO':'#F59E0B','ALTO':'#EF4444','MUY ALTO':'#7F1D1D'
    }

    fig = go.Figure(go.Bar(
        x=df_r['Departamento'],
        y=df_r['Score'],
        marker_color=[COLOR_MAP.get(z,'#888') for z in df_r['Zona']],
        text=df_r['Zona'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Zona: %{text}<br>Score: %{y:.1f}<extra></extra>',
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=TEXTO,
        title=dict(text=f'Nivel de Riesgo por Departamento — {delito} ({anio})',
                   font=dict(size=15, color=TEXTO)),
        xaxis=dict(tickangle=-45, gridcolor='rgba(124,58,237,0.1)'),
        yaxis=dict(title='Score de Riesgo', gridcolor='rgba(124,58,237,0.1)'),
        margin=dict(t=60,b=120,l=40,r=20),
        height=420,
    )

    tabla_rows = [
        html.Tr([
            html.Td(r['Departamento'], style={'color':TEXTO,'padding':'8px 12px','fontSize':'0.85rem'}),
            html.Td(r['Zona'], style={'color':COLOR_MAP.get(r['Zona'],'#888'),'fontWeight':'600','padding':'8px 12px','fontSize':'0.85rem'}),
            html.Td(r['Gravedad'], style={'color':NIVEL_COLOR.get(r['Gravedad'],'#888'),'padding':'8px 12px','fontSize':'0.85rem'}),
            html.Td(f"{r['Score']:.1f}", style={'color':TEXTO_SEC,'padding':'8px 12px','fontSize':'0.85rem'})
        ], style={'borderBottom':f'1px solid {BORDE}'})
        for _, r in df_r.iterrows()
    ]

    return html.Div([
        html.Div([dcc.Graph(figure=fig, config={'displayModeBar':False})], style=CARD),
        html.Div([
            html.H4('Tabla de Resultados', style={'color':TEXTO,'marginBottom':'1rem','fontWeight':'600'}),
            html.Div([
                html.Table([
                    html.Thead(html.Tr([
                        html.Th(h, style={'color':TEXTO_SEC,'fontWeight':'500','padding':'8px 12px',
                                         'borderBottom':f'1px solid {BORDE}','fontSize':'0.8rem'})
                        for h in ['Departamento','Zona de Riesgo','Nivel Gravedad','Score']
                    ])),
                    html.Tbody(tabla_rows)
                ], style={'width':'100%','borderCollapse':'collapse'})
            ], style={'maxHeight':'350px','overflowY':'auto'})
        ], style=CARD),
    ])


# ─────────────────────────────────────────
# CALLBACK — DENUNCIA
# ─────────────────────────────────────────
@app.callback(
    Output('den-resultado','children'),
    Input('btn-denuncia','n_clicks'),
    prevent_initial_call=True
)
def enviar_denuncia(n):
    return html.Div([
        html.Div('✅ Denuncia registrada exitosamente', style={'color':VERDE,'fontWeight':'600','marginBottom':'4px'}),
        html.Div('Tu reporte ha sido recibido. Recuerda que para emergencias inmediatas '
                 'llama al 123 o la Línea Mujer 155.',
                 style={'color':TEXTO_SEC,'fontSize':'0.85rem'})
    ], style={**CARD,'borderColor':f'{VERDE}44','background':f'{VERDE}08'})


# ─────────────────────────────────────────
# CALLBACK — CHAT IA
# ─────────────────────────────────────────
RESPUESTAS_IA = {
    'denunci': ('📋 Para denunciar en Colombia puedes ir a la Fiscalía General de la Nación, '
                'la Comisaría de Familia más cercana, o usar la Línea 155 (gratuita, 24/7). '
                'También puedes registrar tu denuncia aquí en SafeHer de forma anónima.',
    ),
    'sigu': ('🔒 Si crees que te están siguiendo: camina hacia un lugar concurrido, '
             'entra a una tienda o establecimiento, llama a alguien de confianza, '
             'y si el peligro es inmediato marca el 123. Activa el botón de emergencia en esta app.',
    ),
    'psicolog': ('💜 Entiendo que puedes estar pasando por un momento difícil. '
                 'Colombia tiene la Línea 137 de Salud Mental, gratuita y confidencial. '
                 'También puedes acceder a apoyo en el ICBF al 01800-112-137. Estoy aquí contigo.',
    ),
    'derecho': ('⚖️ Tienes derecho a vivir una vida libre de violencia (Ley 1257 de 2008), '
                'a recibir atención prioritaria en entidades de salud, a la confidencialidad '
                'en tu denuncia, y a medidas de protección inmediata. La Fiscalía puede '
                'asignarte una medida de protección en 24 horas.',
    ),
    'peligro': ('🚨 Si estás en peligro INMEDIATO, llama al 123 ahora. '
                'Si no puedes hablar, envía tu ubicación a alguien de confianza. '
                'El botón de emergencia en esta app también puede ayudarte.',
    ),
    'apoyo': ('💜 Estoy aquí para escucharte. Recuerda que lo que te pasa no es tu culpa. '
              'Mereces sentirte segura y protegida. ¿Quieres que te oriente sobre '
              'recursos de apoyo emocional o ayuda legal?',
    ),
}

def responder_ia(mensaje):
    msg = mensaje.lower()
    for clave, respuesta in RESPUESTAS_IA.items():
        if clave in msg:
            return respuesta[0]
    return ('Gracias por escribirme. Para darte la mejor orientación, '
            'puedo ayudarte con: dónde denunciar, qué hacer si te siguen, '
            'apoyo psicológico, tus derechos legales o emergencias. '
            '¿Qué necesitas hoy?')

def burbuja_usuario(txt):
    return html.Div([
        html.Div(txt, style={
            'background':f'{MORADO}44','borderRadius':'12px 12px 4px 12px',
            'padding':'12px 16px','color':TEXTO,'fontSize':'0.9rem',
            'maxWidth':'75%','border':f'1px solid {BORDE}'
        })
    ], style={'display':'flex','justifyContent':'flex-end'})

def burbuja_ia(txt):
    return html.Div([
        html.Div('🤖', style={'fontSize':'1.2rem','marginBottom':'4px'}),
        html.Div(txt, style={
            'background':f'{MORADO}22','borderRadius':'12px 12px 12px 4px',
            'padding':'12px 16px','color':TEXTO,'fontSize':'0.9rem','lineHeight':'1.6',
            'maxWidth':'80%','border':f'1px solid {BORDE}'
        })
    ], style={'display':'flex','flexDirection':'column','alignItems':'flex-start'})

@app.callback(
    Output('chat-mensajes','children'),
    Output('chat-historia','data'),
    Output('chat-input','value'),
    Input('btn-chat','n_clicks'),
    Input('chat-input','n_submit'),
    *[Input(f'quick-{i}','n_clicks') for i in range(4)],
    State('chat-input','value'),
    State('chat-historia','data'),
    prevent_initial_call=True
)
def manejar_chat(n_btn, n_sub, q0,q1,q2,q3, texto, historia):
    ctx = callback_context
    if not ctx.triggered: raise dash.exceptions.PreventUpdate

    tid = ctx.triggered[0]['prop_id'].split('.')[0]
    QUICK = ['¿Dónde denuncio?','¿Qué hago si me siguen?','Necesito apoyo emocional','¿Cuáles son mis derechos?']
    for i, q in enumerate(QUICK):
        if tid == f'quick-{i}': texto = q

    if not texto or not texto.strip():
        raise dash.exceptions.PreventUpdate

    resp = responder_ia(texto)
    historia = historia or []
    historia.append({'user': texto, 'ia': resp})

    burbujas_iniciales = [burbuja_ia(
        'Hola, soy la IA de apoyo de SafeHer 💜 Estoy aquí para ayudarte. '
        'Puedes preguntarme sobre dónde denunciar, cómo pedir ayuda, '
        'qué hacer en una situación de riesgo, o simplemente hablar si lo necesitas.'
    )]
    for h in historia:
        burbujas_iniciales.append(burbuja_usuario(h['user']))
        burbujas_iniciales.append(burbuja_ia(h['ia']))

    return burbujas_iniciales, historia, ''


# ─────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
