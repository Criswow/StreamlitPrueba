import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# 1. Configuración de Seguridad
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Configuración de la Página
st.set_page_config(page_title="Tutor IA - English Project", layout="centered")

st.title("🗣️ IA English Tutor")
st.write("Bienvenido a tu secuencia didáctica interactiva.")

# 3. Sidebar y Configuración
with st.sidebar:
    st.header("Configuración")
    student_id = st.text_input("ID o Nombre del Estudiante", placeholder="Ej: Juan Pérez")
    modo = st.selectbox("Elige tu interlocutor:", ["Profesor de Inglés", "Personaje Histórico"])
    
    personaje = "Tutor de Inglés"
    if modo == "Personaje Histórico":
        personaje = st.text_input("¿Con qué personaje quieres hablar?", "Albert Einstein")

# 4. Inicializar Historial y Memoria
if "display_history" not in st.session_state:
    st.session_state.display_history = [] 

# 5. Mostrar mensajes previos en pantalla
for msg in st.session_state.display_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Interfaz de Grabación
st.write("---")
audio_data = mic_recorder(start_prompt="Haz clic para hablar 🎤", stop_prompt="Detener grabación ⏹️")

# 7. Lógica de Procesamiento (CUANDO HAY AUDIO)
if audio_data and student_id:
    with st.spinner("La IA está escuchando..."):
        try:
            # Seleccionamos el modelo más estable según tu lista de 2026
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Formato de audio para Gemini
            audio_blob = {
                "mime_type": "audio/wav",
                "data": audio_data['bytes']
            }
            
            # Instrucción del sistema + Contexto
            prompt_tutor = f"You are {personaje}, an English teacher. Evaluate {student_id} based on CEFR/MCER standards. Be encouraging and clear. Respond to their voice."

            # Generación de la respuesta
            response = model.generate_content([prompt_tutor, audio_blob])

            # Guardar en el historial de pantalla
            st.session_state.display_history.append({"role": "user", "content": "🎤 [Mensaje de voz]"})
            st.session_state.display_history.append({"role": "assistant", "content": response.text})
            
            # --- SALIDA DE AUDIO Y TEXTO (Dentro del proceso exitoso) ---
            st.markdown(f"### 🤖 {personaje} dice:")
            st.write(response.text)
            
            # Limpiar texto para el motor de voz (TTS)
            texto_voz = response.text[:250].replace(" ", "%20").replace("\n", " ")
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={texto_voz}&tl=en"
            
            # Reproducción automática
            st.audio(tts_url, format="audio/mp3", autoplay=True)
            
            # Botón de respaldo para escuchar
            st.link_button("🔊 Escuchar respuesta completa", tts_url)
            
            # Refrescar para mostrar el nuevo mensaje en el historial
            st.rerun()

        except Exception as e:
            if "429" in str(e):
                st.error("Cuota excedida. Por favor, espera 60 segundos antes de volver a hablar.")
            else:
                st.error(f"Error técnico: {e}")

elif audio_data and not student_id:
    st.warning("⚠️ Por favor, ingresa tu nombre en la barra lateral para poder evaluarte.")
