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
    with st.spinner("IA procesando..."):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 1. Convertimos el historial de mensajes a un solo bloque de texto
            # Esto evita el error de tipo 'Content'
            contexto_historial = "\n".join([
                f"{m['role']}: {m['content']}" for m in st.session_state.display_history
            ])
            
            # 2. Preparamos las partes: Contexto + Historial + Audio
            prompt_final = f"""
            System: Actúa como {personaje}. Estudiante: {student_id}. 
            Historial previo: {contexto_historial}
            Instrucción: Escucha el audio adjunto y responde siguiendo el hilo de la charla y el nivel MCER.
            """
            
            audio_part = {
                "mime_type": "audio/wav",
                "data": audio_data['bytes']
            }
            
            # 3. Enviamos como una lista simple (Texto y Diccionario de Audio)
            response = model.generate_content([prompt_final, audio_part])

            # 4. Actualizamos historiales para la interfaz
            st.session_state.display_history.append({"role": "user", "content": "🎤 [Audio de voz]"})
            st.session_state.display_history.append({"role": "assistant", "content": response.text})
            
            # 5. Voz de respuesta (TTS)
            st.audio(f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={response.text[:200]}&tl=en")
            
            st.rerun()

        except Exception as e:
            st.error(f"Error de procesamiento: {e}")


elif audio_data and not student_id:
    st.warning("Por favor, ingresa tu nombre en la barra lateral antes de hablar.")
