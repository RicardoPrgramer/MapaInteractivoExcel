import streamlit as st
import pandas as pd
import folium
from folium import Popup
from streamlit_folium import st_folium
from datetime import datetime

st.title("📍 Visualizador de Coordenadas en Mapa desde Excel")

# Subir archivo Excel
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    # Leer archivo Excel
    xls = pd.ExcelFile(archivo)
    hojas = xls.sheet_names

    # Seleccionar hoja
    hoja_seleccionada = st.selectbox("Selecciona una hoja", hojas)

    # Leer la hoja seleccionada
    df = xls.parse(hoja_seleccionada)

    # Verificamos columnas necesarias
    columnas_requeridas = {'HORA', 'LATITUD', 'LONGITUD'}
    if not columnas_requeridas.issubset(df.columns):
        st.error(f"La hoja debe contener las columnas: {', '.join(columnas_requeridas)}")
    else:
        # Conversión de la columna HORA
        def convertir_hora(valor):
            for fmt in ("%H:%M:%S", "%H:%M", "%Y-%m-%d %H:%M:%S", "%H:%M:%S.%f"):
                try:
                    return pd.to_datetime(str(valor).strip(), format=fmt).time()
                except:
                    continue
            return None

        df['HORA'] = df['HORA'].apply(convertir_hora)

        # Elegir rango de hora
        hora_min = min(df['HORA'])
        hora_max = max(df['HORA'])

        hora_inicio = st.time_input("Hora de inicio", value=hora_min)
        hora_fin = st.time_input("Hora de fin", value=hora_max)

        # Filtrar por hora
        df_filtrado = df[df['HORA'].apply(lambda x: x is not None and hora_inicio <= x <= hora_fin)]

        if df_filtrado.empty:
            st.warning("No se encontraron datos en ese rango de horas.")
        else:
            # Crear el mapa
            lat_inicial = df_filtrado.iloc[0]['LATITUD']
            lon_inicial = df_filtrado.iloc[0]['LONGITUD']
            mapa = folium.Map(location=[lat_inicial, lon_inicial], zoom_start=14)

            # Agregar marcadores
            for _, fila in df_filtrado.iterrows():
                folium.CircleMarker(
                    location=[fila['LATITUD'], fila['LONGITUD']],
                    radius=3, #Radio de los puntos dibujados en mapa
                    color="green",
                    fill=True,
                    fill_color="green",
                    popup=folium.Popup(f"Hora: {fila['HORA']}", parse_html=True)  
                ).add_to(mapa)

            st.markdown("### 🗺️ Mapa de Coordenadas")
            st_folium(mapa, width=700, height=500)
