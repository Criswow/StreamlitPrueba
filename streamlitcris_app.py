import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# 1. Configuración de Seguridad (Usa Secrets de Streamlit)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Configuración de la Página
st.set_page_config(page_title="Tutor IA - English Project", layout="centered")

st.title("🗣️ IA English Tutor")
st.write("Bienvenido a tu secuencia didáctica interactiva.")

# 3. Sidebar para Perfil del Estudiante y Roles
with st.sidebar:
    st.header("Configuración")
    student_id = st.text_input("ID o Nombre del Estudiante", placeholder="Ej: Juan Pérez")
    
    modo = st.selectbox("Elige tu interlocutor:", 
                        ["Profesor de Inglés", "Personaje Histórico (Sugerencia)"])
    
    if modo == "Personaje Histórico (Sugerencia)":
        personaje = st.text_input("¿Con qué personaje quieres hablar?", "Albert Einstein")
    else:
        personaje = "Tutor de Inglés"

# 4. Prompt Base (MCER y Adaptabilidad)
system_prompt = f"""
Actúa como un profesor de inglés experto siguiendo el Marco Común Europeo (MCER).
Tu rol actual es: {personaje}.
Objetivo: Conversar con el estudiante {student_id}, detectar su nivel y corregir errores de forma pedagógica.
Al final de la interacción, debes estar listo para generar un reporte de 'Gustos', 'Nivel' y 'Mejoras'.
"""

# 5. Lógica del Chat (Memoria de sesión)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# Mostrar mensajes previos (sin mostrar el system prompt)
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Interfaz de Voz
st.write("---")
audio_data = mic_recorder(start_prompt="Haz clic para hablar 🎤", stop_prompt="Detener grabación ⏹️")

if audio_data:
    # Mostramos un indicador de carga
    with st.spinner("Escuchando y pensando..."):
        try:
            # 1. Convertir bytes de audio para Gemini
            audio_bytes = audio_data['bytes']
            
            # 2. Enviar el audio directamente a Gemini (Multimodal)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Creamos el mensaje incluyendo el historial y el nuevo audio
            # Añadimos una instrucción clara para que actúe según el rol
            prompt_instruccion = f"Asistente, recuerda tu rol: {personaje}. Escucha este audio y responde al estudiante {student_id} de forma pedagógica siguiendo el MCER."
            
            response = model.generate_content([
                prompt_instruccion,
                {"mime_type": "audio/wav", "data": audio_bytes}
            ])

            # 3. Guardar en el historial
            st.session_state.messages.append({"role": "user", "content": "🎤 Mensaje de voz enviado"})
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # Forzar actualización para mostrar respuesta
            st.rerun()
            
        except Exception as e:
            st.error(f"Hubo un problema procesando el audio: {e}")
