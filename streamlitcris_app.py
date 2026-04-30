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
    with st.spinner("La IA (v2.5) está escuchando tu inglés..."):
        try:
            # 1. CAMBIO CLAVE: Usar el modelo nativo de audio 2.5
            model_name = 'models/gemini-2.5-flash-native-audio-latest'
            model = genai.GenerativeModel(model_name)
            
            # 2. Formato de audio para Gemini 2.5
            audio_blob = {
                "mime_type": "audio/wav",
                "data": audio_data['bytes']
            }
            
            # 3. Contexto pedagógico
            contexto = f"""
            Role: {personaje}. 
            Student: {student_id}. 
            Task: Listen to the student's English, provide feedback based on CEFR (MCER) standards, and maintain the conversation.
            """
            
            # 4. Generación de respuesta
            response = model.generate_content([contexto, audio_blob])

            # 5. Guardar en historial
            st.session_state.display_history.append({"role": "user", "content": "🎤 [Audio de voz]"})
            st.session_state.display_history.append({"role": "assistant", "content": response.text})
            
            # 6. AUDIO DE RESPUESTA (Mejorado)
            # Usamos el texto de la IA para generar la voz de vuelta
            clean_text = response.text[:300].replace(" ", "%20")
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={clean_text}&tl=en"
            
            st.markdown(f"### 🤖 {personaje}:")
            st.write(response.text)
            st.audio(tts_url, format="audio/mp3", autoplay=True)
            
            st.rerun()

        except Exception as e:
            st.error(f"Error con modelo 2.5: {e}")


elif audio_data and not student_id:
    st.warning("Por favor, ingresa tu nombre en la barra lateral antes de hablar.")
