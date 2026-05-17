# 🛡️ SafeHer Colombia — Plataforma de Protección con IA

Sistema inteligente de protección y prevención para mujeres en Colombia, desarrollado con **Dash (Python)** y modelos de Machine Learning entrenados con datos reales de la Policía Nacional.

---

## 👩‍💻 Autoras
- Laura Sofia Beltrán
- Dana Yaray Vargas  
- Vanessa Mora

---

## 📁 Estructura de archivos requeridos

```
safeher_app.py                      ← Aplicación principal
requirements.txt                    ← Dependencias Python
Procfile                            ← Para despliegue en Heroku

── Modelos (misma carpeta o /mnt/user-data/uploads/)
   preprocessor_gravedad.pkl
   xgb_gravedad.pkl
   pipe_lgbm_gravedad.pkl
   le_target_gravedad.pkl
   scaler_gravedad.pkl
   encoders_zona.pkl
   xgb_zona.pkl
   lgbm_zona.pkl
   le_target_zona.pkl
   departamentos_municipios_unicos.xlsx
```

---

## 🚀 Cómo correr localmente

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ajustar ruta de los modelos
En `safeher_app.py`, línea ~20, cambia:
```python
BASE = '/mnt/user-data/uploads'
```
por la carpeta donde tengas los `.pkl`:
```python
BASE = './modelos'    # si los pones en una carpeta "modelos"
# ó
BASE = '.'            # si están en la misma carpeta que safeher_app.py
```

### 3. Correr la app
```bash
python safeher_app.py
```
Abre en tu navegador: **http://localhost:8050**

---

## ☁️ Despliegue en Heroku (nivel medio)

### Requisitos previos
- Cuenta en [heroku.com](https://heroku.com) (gratis)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) instalado
- Git instalado

### Pasos

#### 1. Cambiar la ruta BASE en safeher_app.py
Los `.pkl` deben estar **en la misma carpeta** que el app:
```python
BASE = os.path.dirname(os.path.abspath(__file__))
```
Y asegúrate de que la línea de carga sea:
```python
df_geo = pd.read_excel(os.path.join(BASE, 'departamentos_municipios_unicos.xlsx'))
pre_grav = joblib.load(os.path.join(BASE, 'preprocessor_gravedad.pkl'))
# ... etc
```

#### 2. Exponer el servidor Flask (requerido por Heroku)
Al final del archivo `safeher_app.py`, antes del `if __name__`:
```python
server = app.server   # ← Agregar esta línea
```

#### 3. Inicializar git y subir
```bash
git init
git add .
git commit -m "SafeHer Colombia - primera versión"

heroku create safeher-colombia
git push heroku main
heroku open
```

#### 4. Ver logs si hay errores
```bash
heroku logs --tail
```

**Nota Heroku gratuito:** El plan gratuito tiene límite de 512MB RAM y los dynos "duermen" después de 30 min de inactividad. Los modelos XGBoost + LightGBM pueden acercarse al límite — si hay problemas de memoria, usa solo un modelo por predicción.

---

## ☁️ Despliegue en Streamlit Cloud (alternativa más fácil)

Si prefieres una opción más sencilla, la app puede adaptarse a Streamlit:

1. Sube el repositorio a GitHub (con los `.pkl` o usando Git LFS para archivos grandes)
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. Despliega con un click

---

## 🤖 Modelos implementados

| Modelo | Algoritmos | Target | Features |
|--------|-----------|--------|----------|
| Nivel de Gravedad | XGBoost + LightGBM | 8 clases (MÍNIMO → CRÍTICO) | Municipio, Depto, Delito, Sexo, Etario, Año |
| Zona de Riesgo | XGBoost + LightGBM | 6 clases (MUY BAJO → MUY ALTO) | Municipio, Depto, Delito, Sexo, Etario, Año |
| Total Víctimas | Estimación combinada | Valor numérico | Basado en Gravedad + Zona |

---

## 🎨 Módulos de la plataforma

1. **🏠 Inicio** — Hero con estadísticas y accesos rápidos
2. **📊 Predicción** — Formulario con los 3 modelos (usuario elige XGBoost o LightGBM)
3. **🗺️ Mapa de Riesgo** — Gráfica de barras por departamento con filtros
4. **🚨 Emergencias** — Botones de alerta rápida + líneas de ayuda
5. **📋 Denuncias** — Formulario anónimo de reporte
6. **🤖 Apoyo IA** — Chat con respuestas sobre derechos, ayuda y recursos
7. **ℹ️ Acerca de** — Información del proyecto y limitaciones

---

## ⚠️ Aviso importante

Esta es una plataforma académica prototipo. Las predicciones son aproximaciones estadísticas y **NO deben usarse como única fuente de decisión** en situaciones reales de riesgo.

Para emergencias: **llama al 123** o la **Línea Mujer 155** (gratuita, 24/7).
