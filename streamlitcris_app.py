import fitz
from mistralai import Mistral
import streamlit as st
st.markdown("""
<h1 style="font-size:60px; margin:0;">
  <span style="font-size:45px;">a</span>ClaraBot   🤖
</h1>
""", unsafe_allow_html=True)

if "history" not in st.session_state:  # Historial de chats
    st.session_state.history = []

# Archivos
uploaded_file = st.file_uploader(
    "Si lo deseas, puedes subir un documento .pdf o .txt el cual quieras comprender. ", type=("txt", "pdf"))
file_text = None

if uploaded_file:
    if uploaded_file.type == "text/plain":
        file_text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            file_text = "\n".join(page.get_text() for page in doc)

# API 
client = Mistral(st.secrets["MISTRAL_API_KEY"])
model = "mistral-small-2506"

# Prompt por el usuario
prompt = st.chat_input("Pregunta lo que quieras")

# Historial de mensajes en vivo
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Deteccion del texto
if prompt:
    if file_text and not any(m["role"] == "system" for m in st.session_state.history):
        st.session_state.history.insert(0, {
            "role": "system",
            "content": f'''El usuario ha subido un documento y necesita una explicación clara, breve y orientada a resultados inmediatos.
            La respuesta debe centrarse en los puntos más relevantes y prácticos, destacando implicaciones y beneficios sin detalles técnicos innecesarios.
            Sin embargo, esto no implica que se usen terminos sin explicar, de manera que cada concepto debe explicarse de forma sencilla,
            sin asumir que el usuario tiene conocimientos preivos. A continuacion el documento proporcionado:\n\n{file_text}'''

        })

    st.session_state.history.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)  # lectura prompt

    # Mistral responde
    response = client.chat.complete(
        model=model,
        messages=st.session_state.history
    )
    reply = response.choices[0].message.content

    # Muestra del mensaje
    st.session_state.history.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").markdown(reply)
