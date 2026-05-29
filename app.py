import streamlit as st
import pandas as pd
import re

# 1. Configuración de la pantalla para celulares
st.set_page_config(page_title="Cancionero Iglesia", page_icon="🎵", layout="centered")

# 2. Conectar con tu Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1j-VAdu7VTkeIGMY4d8Fa1ahlfjeMmg9rZkglWjG9an0/export?format=csv"

@st.cache_data(ttl=60) # Se actualiza solo cada 1 minuto si agregás canciones
def cargar_datos():
    try:
        df_sheet = pd.read_csv(SHEET_URL)
        # Limpiamos espacios ocultos en los nombres de las columnas (ej: "Letra " -> "Letra")
        df_sheet.columns = df_sheet.columns.str.strip()
        return df_sheet
    except Exception as e:
        # Datos de prueba por si el link falla temporalmente
        return pd.DataFrame({
            "Titulo": ["Dios Incomparable", "Cuan Grande es Él"],
            "Autor": ["Generación 12", "Tradicional"],
            "Letra": ["[G] Dios de mi cora[C]zón, te de[D]seo", "[C] Señor mi [F] Dios, al con[C]templar los [G] cielos"]
        })

df = cargar_datos()

# 3. Lógica para cambiar los acordes automáticamente (Soporta menores y séptimas)
NOTAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transponer_texto(texto, semitonos):
    if semitonos == 0 or not isinstance(texto, str):
        return texto
    
    def reemplazar_acorde(match):
        acorde = match.group(1)
        # Extraer la nota base considerando sostenidos (ej: "F#" o "C")
        if len(acorde) > 1 and acorde[1] in ["#", "b"]:
            nota_base = acorde[:2]
        else:
            nota_base = acorde[0]
            
        modificador = acorde[len(nota_base):]
        
        # Normalizar bemoles simples a sostenidos si aparecen
        if nota_base == "Db": nota_base = "C#"
        elif nota_base == "Eb": nota_base = "D#"
        elif nota_base == "Gb": nota_base = "F#"
        elif nota_base == "Ab": nota_base = "G#"
        elif nota_base == "Bb": nota_base = "A#"
        
        if nota_base in NOTAS:
            idx = (NOTAS.index(nota_base) + semitonos) % 12
            return f"**[{NOTAS[idx]}{modificador}]**"
        return f"**[{acorde}]**"

    # Busca todo lo que esté entre corchetes [ ]
    return re.sub(r'\[([^\]]+)\]', reemplazar_acorde, texto)

# --- INTERFAZ DE LA APP ---
st.title("🎵 Cancionero de la Banda")

# Buscador inteligente por título o autor
buscar = st.text_input("🔍 Buscar por título o autor...", "")

# Filtrar lista de canciones de forma segura
if "Titulo" in df.columns:
    if buscar:
        # Se asegura de tratar todo como texto para evitar errores de búsqueda
        df_filtrado = df[df['Titulo'].astype(str).str.contains(buscar, case=False) | 
                         df['Autor'].astype(str).str.contains(buscar, case=False)]
    else:
        df_filtrado = df
else:
    st.error("❌ Error: No se encontró la columna 'Titulo' en tu Google Sheets. Revisá la fila 1 de tu Excel.")
    df_filtrado = pd.DataFrame()

# Selector de canción
if not df_filtrado.empty:
    canciones = df_filtrado['Titulo'].dropna().tolist()
    seleccion = st.selectbox("📖 Elegí una canción:", canciones)
    
    # Datos de la canción elegida
    datos_cancion = df_filtrado[df_filtrado['Titulo'] == seleccion].iloc[0]
    
    st.subheader(f"{datos_cancion['Titulo']}")
    st.caption(f"Autor: {datos_cancion['Autor'] if pd.notna(datos_cancion['Autor']) else 'Desconocido'}")
    
    # Selector de cambio de tono (-6 a +6 semitonos)
    cambio = st.slider("🎼 Cambiar Tono (Semitonos):", min_value=-6, max_value=6, value=0, step=1)
    
    # Conseguir la letra y validar que no esté vacía
    letra_lista = datos_cancion['Letra'] if 'Letra' in datos_cancion else ""
    
    if pd.isna(letra_lista) or str(letra_lista).strip() == "" or str(letra_lista).strip() == "nan":
        st.warning("⚠️ Esta canción todavía no tiene la letra cargada en el Excel.")
    else:
        letra_texto = str(letra_lista)
        
        # Cambiamos los acordes de tono automáticamente
        letra_transpuesta = transponer_texto(letra_texto, cambio)
        
        # Reemplazar saltos de línea para renderizar en HTML dentro de Streamlit
        letra_final = letra_transpuesta.replace("\n", "<br>")
        st.markdown(f"<div style='font-size:18px; line-height:1.8; font-family: sans-serif;'>{letra_final}</div>", unsafe_allowed_html=True)
else:
    if not df.empty:
        st.warning("No se encontraron canciones con ese nombre.")
