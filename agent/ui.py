"""
Streamlit UI para el agente de Rick and Morty
Ejecutar: streamlit run ui.py
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Importar el agente
from agent import RickMortyAgent, MCPClient

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="🛸 Rick and Morty Agent",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: rgba(100, 200, 255, 0.2);
        border-left: 5px solid #64c8ff;
    }
    .agent-message {
        background-color: rgba(150, 255, 150, 0.2);
        border-left: 5px solid #96ff96;
    }
    .sidebar .sidebar-content {
        background-color: rgba(255, 255, 255, 0.1);
    }
    h1 {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar el agente en session state
@st.cache_resource
def init_agent():
    """Inicializar agente una sola vez"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8000")
    
    if not gemini_api_key:
        st.error("❌ GEMINI_API_KEY no configurada")
        st.stop()
    
    mcp_client = MCPClient(mcp_server_url)
    agent = RickMortyAgent(gemini_api_key, mcp_client)
    
    return agent

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Rick_and_Morty.svg/1200px-Rick_and_Morty.svg.png", width=200)
    st.title("🛸 Rick & Morty Agent")
    st.markdown("---")
    
    st.markdown("### 🎯 Qué puedo hacer:")
    st.markdown("""
    - 🔍 Buscar personajes
    - 🌌 Explorar localizaciones
    - 📺 Analizar episodios
    - 📊 Generar estadísticas
    - 🤔 Responder preguntas
    """)
    
    st.markdown("---")
    st.markdown("### 💡 Ejemplos:")
    
    if st.button("¿Quién es Rick Sanchez?"):
        st.session_state.query = "¿Quién es Rick Sanchez?"
    
    if st.button("Busca aliens vivos"):
        st.session_state.query = "Busca personajes aliens que estén vivos"
    
    if st.button("Primer episodio"):
        st.session_state.query = "Cuéntame del primer episodio"
    
    if st.button("Estadísticas"):
        st.session_state.query = "Dame estadísticas generales"
    
    st.markdown("---")
    
    # Verificar health
    if st.button("🔍 Verificar estado"):
        agent = init_agent()
        health = agent.mcp_client.health_check()
        if health:
            st.success("✅ Servidor MCP: OK")
        else:
            st.error("❌ Servidor MCP: Error")
    
    if st.button("🗑️ Limpiar chat"):
        st.session_state.messages = []
        st.rerun()

# Main content
st.title("🛸 Rick and Morty Agent")
st.markdown("### Pregunta lo que quieras sobre el universo de Rick and Morty")

# Inicializar historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

# Inicializar agente
agent = init_agent()

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generar respuesta del agente
    with st.chat_message("assistant"):
        with st.spinner("🤔 Pensando..."):
            try:
                response = agent.process_query(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Manejar consultas desde los botones del sidebar
if "query" in st.session_state and st.session_state.query:
    query = st.session_state.query
    st.session_state.query = None  # Reset
    
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Generar respuesta
    with st.spinner("🤔 Pensando..."):
        try:
            response = agent.process_query(query)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white;'>
    <p>Desarrollado por Gio | Powered by Gemini 2.5 Flash + MCP</p>
</div>
""", unsafe_allow_html=True)