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
    # Nota: Aquí integrarías un servicio STT (Speech to Text)
    # Por ahora, simularemos la entrada de texto para la lógica
    user_input = "Hello, I want to practice my English today." 
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Llamada a Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages])
    response = chat.send_message(user_input)
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.rerun()
