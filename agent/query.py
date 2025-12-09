#!/usr/bin/env python3
"""
Script simple para hacer consultas al agente desde línea de comandos
Uso: python query.py "¿Quién es Rick Sanchez?"
"""

import os
import sys
from dotenv import load_dotenv
from agent import RickMortyAgent, MCPClient

load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("Uso: python query.py 'tu pregunta aquí'")
        print("\nEjemplos:")
        print("  python query.py '¿Quién es Rick Sanchez?'")
        print("  python query.py 'Busca personajes aliens'")
        print("  python query.py 'Dame estadísticas'")
        sys.exit(1)
    
    # Obtener query de argumentos
    query = " ".join(sys.argv[1:])
    
    # Inicializar agente
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8000")
    
    if not gemini_api_key:
        print("❌ Error: GEMINI_API_KEY no configurada")
        sys.exit(1)
    
    print(f"📝 Pregunta: {query}")
    print("🤔 Procesando...\n")
    
    try:
        mcp_client = MCPClient(mcp_server_url)
        agent = RickMortyAgent(gemini_api_key, mcp_client)
        
        response = agent.process_query(query)
        
        print("🤖 Respuesta:")
        print("=" * 70)
        print(response)
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()