#Streamlit
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

#Configuración
st.set_page_config(page_title="Alerta de riesgo académico", page_icon="bar_chart:",layout="wide")
st.title("Modelo de riesgo académico por región y carrera")

#Leer data final
df = pd.read_csv('df_final.csv', encoding='utf-8')

#Filtros sidebar
st.sidebar.header("Filtros")

#Región
regiones = ["Todas"] + sorted(df["Región"].dropna().unique().tolist())
region_sel = st.sidebar.selectbox("Región de procedencia", regiones)

#Código UdeC 
codigos = ["Todos"] + sorted(df["Código UdeC"].unique().tolist())
codigo_sel = st.sidebar.selectbox("Código UdeC de la carrera", codigos)

#Umbral de riesgo por motivación
umbral_motiv = st.sidebar.slider("Umbral de motivación para activar alerta", min_value=1,max_value=5, value=3,)

#Filtrado de datos según selecciones
df_filtrado = df.copy()

if region_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Región"] == region_sel]

if codigo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Código UdeC"] == codigo_sel]

if df_filtrado.empty:
    st.warning("No hay datos que cumplan con los filtros seleccionados.")
    st.stop()

#Métricas resumen al inicio de la web
motiv_prom = df_filtrado["Nivel motivación"].mean()
dur_prom = df_filtrado["Duracion promedio carrera (semestres)"].mean()
nem_prom = df_filtrado["Puntaje NEM promedio carrera"].mean()

c1, c2, c3 = st.columns(3)
c1.metric("Motivación promedio", f"{motiv_prom:.2f}")
c2.metric("Duración promedio de la carrera (semestres)", f"{dur_prom:.2f}")
c3.metric("Puntaje NEM promedio carrera", f"{nem_prom:.1f}")

st.markdown("---")

# Motivación promedio por región
df_graf = (df_filtrado.groupby(["Región", "Código UdeC"])["Nivel motivación"].mean().reset_index(name="Motivación_prom"))
fig = px.bar(df_graf, x="Región", y="Motivación_prom",title="Motivación promedio por región y carrera",)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

#tabla de alertas
# Creamos una columna de alerta simple según el umbral elegido
df_filtrado = df_filtrado.copy()
df_filtrado["Alerta_riesgo"] = np.where(df_filtrado["Nivel motivación"] <= umbral_motiv,"RIESGO ALTO","Sin alerta",)

st.subheader("Estudiantes filtrados") #Titulo tabla

st.write("Alerta: Estudiantes con "f"**Nivel motivación ≤ {umbral_motiv}** marcan **Riesgo alto**.") #describe lo que hara la tabla
st.dataframe(df_filtrado[["Código UdeC","Género","Región","Nivel motivación","Puntaje NEM promedio carrera","Duracion promedio carrera (semestres)","Total titulaciones (2007-2024)","Alerta_riesgo",]],
    use_container_width=True,) #muestra la tabla con las columnas seleccionadas

n_riesgo = (df_filtrado["Alerta_riesgo"] == "RIESGO ALTO").sum() #numero de estudiantes en riesgo alto
st.info(f"Estudiantes en **riesgo alto** (filtro actual): **{n_riesgo}**")
