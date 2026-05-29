import streamlit as st
import pandas as pd
import re

# 1. Configuración de la pantalla para celulares
st.set_page_config(page_title="Cancionero Iglesia", page_icon="🎵", layout="centered")

# 2. Conectar con tu Google Sheets (Reemplaza con tu link)
# IMPORTANTE: Cambiar el "/edit?usp=sharing" del final por "/export?format=csv"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1j-VAdu7VTkeIGMY4d8Fa1ahlfjeMmg9rZkglWjG9an0/export?format=csv"

@st.cache_data(ttl=60) # Se actualiza solo cada 1 minuto si agregás canciones
def cargar_datos():
    try:
        return pd.read_csv(SHEET_URL)
    except:
        # Datos de prueba por si el link falla al principio
        return pd.DataFrame({
            "Titulo": ["Dios Incomparable", "Cuan Grande es Él"],
            "Autor": ["Generación 12", "Tradicional"],
            "Letra": ["[G] Dios de mi cora[C]zón, te de[D]seo", "[C] Señor mi [F] Dios, al con[C]templar los [G] cielos"]
        })

df = cargar_datos()

# 3. Lógica mágica para cambiar los acordes automáticamente
NOTAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transponer_texto(texto, semitonos):
    if semitonos == 0:
        return texto
    
    def reemplazar_acorde(match):
        acorde = match.group(1)
        # Separar la nota base del modificador (ej: "C" y "m", "F#" y "7")
        nota_base = acorde[:2] if len(acorde) > 1 and acorde[1] in ["#", "b"] else acorde[0]
        modificador = acorde[len(nota_base):]
        
        if nota_base in NOTAS:
            idx = (NOTAS.index(nota_base) + semitonos) % 12
            return f"**[{NOTAS[idx]}{modificador}]**"
        return f"**[{acorde}]**"

    # Busca todo lo que esté entre corchetes [ ]
    return re.sub(r'\[([^\]]+)\]', reemplazar_acorde, texto)

# --- INTERFAZ DE LA APP ---
st.title("🎵 Cancionero de la Banda")

# Buscador inteligente
buscar = st.text_input("🔍 Buscar por título o autor...", "")

# Filtrar lista
if buscar:
    df_filtrado = df[df['Titulo'].str.contains(buscar, case=False) | df['Autor'].str.contains(buscar, case=False)]
else:
    df_filtrado = df

# Selector de canción
if not df_filtrado.empty:
    canciones = df_filtrado['Titulo'].tolist()
    seleccion = st.selectbox("📖 Elegí una canción:", canciones)
    
    # Datos de la canción elegida
    datos_cancion = df_filtrado[df_filtrado['Titulo'] == seleccion].iloc[0]
    
    st.subheader(f"{datos_cancion['Titulo']}")
    st.caption(f"Autor: {datos_cancion['Autor']}")
    
    # Selector de cambio de tono (-6 a +6 semitonos)
    cambio = st.slider("🎼 Cambiar Tono (Semitonos):", min_value=-6, max_value=6, value=0, step=1)
    
    # Procesar letra y mostrarla respetando los saltos de línea
    letra_lista = datos_cancion['Letra']
    letra_transpuesta = transponer_texto(letra_lista, cambio)
    
    # Reemplazar los saltos de línea para que Streamlit los dibuje bien
    letra_final = letra_transpuesta.replace("\n", "<br>")
    st.markdown(f"<div style='font-size:18px; line-height:1.8;'>{letra_final}</div>", unsafe_allowed_html=True)
else:
    st.warning("No se encontraron canciones con ese nombre.")
