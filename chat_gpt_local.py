import streamlit as st
import os

from openai import OpenAI
from groq import Groq
from mistralai import Mistral
import anthropic


# Llama a la clave API de otro archivo

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]


# Título de la aplicación
st.title(":robot_face: My Local ChatGPT :sunglasses:")

uploaded_files = st.file_uploader(
    "Choose a file",
    accept_multiple_files=True
    )


init_content = "Hola, soy Local ChatGPT, un asistente que puede usar múltiples modelos de lenguaje para apoyarte, ¿En qué puedo ayudarte?"

# Using "with" notation
with st.sidebar:
    st.title("ChatGPT Model Selection")
    selected_model = st.radio(
        "Selecciona el modelo a utilizar",
        (
            "o1-mini",
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-3.5-turbo",
            "gpt-4-turbo",
            "llama3-8b-8192",
            "llama3-70b-8192",
            "mixtral-8x7b-32768",
            "mistral-large-latest",
            "claude-3-5-sonnet-20240620",
        ),
    )

    st.session_state["llm_model"] = selected_model

    st.write(f"Ahora estás usando el modelo: {st.session_state["llm_model"]}.")

    # Botón para reiniciar el contexto
    if st.button("Nuevo Chat"):
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": init_content,
            }
        ]


# Inicializa el estado de la sesión si es necesario
if "messages" not in st.session_state:
    if selected_model != "claude-3-5-sonnet-20240620":
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": init_content,
            }
        ]


# Mostrar mensajes existentes
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Campo de entrada del usuario
if user_input := st.chat_input():
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Manejo de errores en la respuesta
    try:

        if selected_model in ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "gpt-4-turbo"]:
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=selected_model,
                messages=st.session_state["messages"],
            )
        elif selected_model == "mistral-large-latest":
            client = Mistral(api_key=MISTRAL_API_KEY)
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=st.session_state["messages"],
            )

        elif selected_model == "claude-3-5-sonnet-20240620":
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            response = client.messages.create(
                model=selected_model,
                max_tokens=1000,
                temperature=0,
                system=init_content,
                messages=[{"role": "user", "content": [{"type": "text", "text": str(st.session_state["messages"])}]}],
            )
        else:
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model=selected_model,  # Se puede cambiar el modelo
                messages=st.session_state["messages"],
            )

        if selected_model == "claude-3-5-sonnet-20240620":
            for msg in response.content:
                response_content = msg.text
        else:
            response_content = response.choices[0].message.content
        st.session_state["messages"].append(
            {"role": "assistant", "content": response_content}
        )
        st.chat_message("assistant").write(response_content)
    except Exception as e:
        st.error(f"Ocurrió un error al comunicarse con la API: {e}")
