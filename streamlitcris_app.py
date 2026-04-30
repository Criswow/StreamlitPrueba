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
            # FORZAMOS LA VERSIÓN DE LA API Y EL MODELO
            # A veces 'gemini-1.5-flash' requiere el prefijo completo en ciertas regiones
            model_name = 'models/gemini-1.5-flash'
            model = genai.GenerativeModel(model_name)
            
            # 1. Preparar el audio en el formato exacto que pide la v1beta
            audio_blob = {
                "mime_type": "audio/wav",
                "data": audio_data['bytes']
            }
            
            # 2. Historial simplificado
            contexto = f"Role: {personaje}. Student: {student_id}. MCER English Tutor."
            
            # 3. Generar respuesta
            # Usamos una lista simple para evitar el error de Blob anterior
            response = model.generate_content([contexto, audio_blob])

            # 4. Guardar para mostrar en pantalla
            st.session_state.display_history.append({"role": "user", "content": "🎤 [Audio]"})
            st.session_state.display_history.append({"role": "assistant", "content": response.text})
            
            # 5. ¡SOLUCIÓN PARA ESCUCHAR! 
            # El link anterior podía fallar. Usaremos este método más directo:
            st.markdown(f"### 🤖 {personaje} dice:")
            st.write(response.text)
            
            # Generar audio automático
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={response.text[:250].replace(' ', '%20')}&tl=en"
            st.audio(tts_url, format="audio/mp3", autoplay=True)
            
            st.rerun()

        except Exception as e:
            st.error(f"Error detectado: {e}")
            # Si sigue saliendo 404, esta línea nos dirá qué modelos sí puedes usar:
            modelos_disponibles = [m.name for m in genai.list_models()]
            st.info(f"Modelos disponibles en tu cuenta: {modelos_disponibles}")


elif audio_data and not student_id:
    st.warning("Por favor, ingresa tu nombre en la barra lateral antes de hablar.")
