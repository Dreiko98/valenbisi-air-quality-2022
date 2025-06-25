# Valenbisi × Air Quality 2022

> **Dashboard interactivo para analizar la relación entre el uso de la bici pública y la calidad del aire en València (2022)**

---

## 🚲 Descripción del proyecto

Este proyecto explora la relación entre la movilidad sostenible (uso de Valenbisi) y la contaminación atmosférica en la ciudad de València durante 2022, utilizando datos abiertos. Incluye un pipeline ETL propio, análisis exploratorio de datos (EDA) y un dashboard profesional e interactivo desarrollado con Streamlit.

---

## 🌟 Beneficios y motivación
- Facilita la toma de decisiones basadas en datos para ciudadanía y administración.
- Permite identificar patrones de movilidad y su impacto en la calidad del aire.
- Herramienta visual, intuitiva y reproducible para fomentar políticas de transporte sostenible.

---

## 📊 Funcionalidades principales
- **KPIs** de movilidad y contaminación.
- Series temporales y heatmaps interactivos.
- Mapas de estaciones y comparativas espaciales.
- Matriz de correlación y modelo de regresión lineal.
- Comparativas entre días laborables y fines de semana.
- Filtros y visualizaciones interactivas.

---

## 🗂️ Estructura del repositorio

```
📂 data/
   ├─ city_bike_air_2022.csv           # Merge ciudad (mes × día × hora)
   ├─ bike_air_spatial_hour_2022.csv   # Merge estación-hora
   ├─ ... (otros CSV intermedios)
📂 air_txt/                            # Ficheros de aire originales
app.py                                # Dashboard principal (Streamlit)
eda_valenbisi_air.py                  # Script de EDA y generación de figuras
build_valencia_bike_air_2022.py       # Pipeline ETL
requirements.txt                      # Dependencias
README.md                             # Este documento
logo.png, favicon.png                 # Recursos visuales
```

---

## 🚀 Cómo ejecutar el dashboard

### 1. **Requisitos**
- Python 3.8+
- Ver dependencias en `requirements.txt`

### 2. **Instalación local**
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 3. **Despliegue online (recomendado)**
Puedes desplegar la app gratis en [Streamlit Cloud](https://streamlit.io/cloud):
1. Sube este repositorio a GitHub.
2. Ve a Streamlit Cloud y crea una nueva app desde tu repo.
3. Selecciona `app.py` como archivo principal.
4. Obtendrás un enlace público para compartir tu dashboard.

---

## 📦 Pipeline de datos
- **ETL automatizado:** descarga, limpieza, validación y agregación de datos de Valenbisi y calidad del aire.
- **Outputs clave:**
  - `city_bike_air_2022.csv`: datos agregados ciudad-hora.
  - `bike_air_spatial_hour_2022.csv`: datos estación-hora enlazados espacialmente.

---

## 🛠️ Tecnologías empleadas
- **Python** (pandas, scikit-learn, seaborn)
- **Streamlit** (dashboard interactivo)
- **Plotly** (visualizaciones interactivas)

---

## 👥 Autores
- Josep Ferrer García
- [Germán Mallo Faure](https://germanmallo.com)

---

## 📹 Demo y recursos
- **Demo online:** [Pon aquí el enlace de tu app desplegada]
- **Vídeo explicativo:** [Pon aquí el enlace al vídeo demo]

---

## 📄 Licencia
Proyecto académico para la Universitat Politècnica de València (UPV). Uso libre para fines educativos.
