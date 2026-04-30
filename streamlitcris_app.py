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

# 4. Inicializar Historial y Prompt
if "messages" not in st.session_state:
    system_prompt = f"Actúa como un profesor de inglés experto (MCER). Tu rol: {personaje}. Estudiante: {student_id}. Detecta errores y nivel de forma pedagógica."
    st.session_state.messages = [{"role": "user", "parts": [system_prompt]}]
    st.session_state.display_history = [] # Para mostrar en pantalla sin el system prompt

# 5. Mostrar mensajes previos
for msg in st.session_state.display_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Interfaz de Voz
st.write("---")
audio_data = mic_recorder(start_prompt="Haz clic para hablar 🎤", stop_prompt="Detener grabación ⏹️")

if audio_data and student_id:
    with st.spinner("IA procesando tu voz..."):
        try:
            # 1. Configurar modelo de forma explícita
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 2. Preparar las partes (Contexto y Audio)
            # Pasamos el audio como un diccionario con 'mime_type' y 'data'
            audio_part = {
                "mime_type": "audio/wav",
                "data": audio_data['bytes']
            }
            
            prompt_didactico = f"Role: {personaje}. Student: {student_id}. Use CEFR/MCER standards. Respond to the audio."

            # 3. Generar contenido
            response = model.generate_content([prompt_didactico, audio_part])

            # 4. Guardar en historial
            st.session_state.display_history.append({"role": "user", "content": "🎤 [Mensaje de voz]"})
            st.session_state.display_history.append({"role": "assistant", "content": response.text})
            
            # 5. ¡SOLUCIÓN PARA ESCUCHAR! (TTS con Autoplay)
            # Limpiamos el texto para la URL (máximo 250 caracteres para estabilidad)
            clean_text = response.text[:250].replace(" ", "%20").replace("\n", "")
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={clean_text}&tl=en"
            
            st.audio(tts_url, format="audio/mp3", autoplay=True)
            
            st.rerun()

        except Exception as e:
            st.error(f"Error detectado: {e}")
            # Esto nos dirá si el modelo realmente no existe en tu región
            if "404" in str(e):
                st.info("Intentando listar modelos disponibles...")
                available = [m.name for m in genai.list_models()]
                st.write(available)


elif audio_data and not student_id:
    st.warning("Por favor, ingresa tu nombre en la barra lateral antes de hablar.")
