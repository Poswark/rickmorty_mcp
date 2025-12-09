"""
Rick and Morty AI Agent
Agente inteligente que usa Gemini para interactuar con el servidor MCP
"""

import os
import sys
import json
import logging
import time
from typing import Dict, Any, List, Optional
import google.generativeai as genai
import requests
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT, USER_GREETING, ERROR_MESSAGES

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar Rich para output bonito
console = Console()


class MCPClient:
    """Cliente para interactuar con el servidor MCP"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session = requests.Session()
        logger.info(f"MCPClient inicializado con URL: {server_url}")
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Llama a una herramienta del servidor MCP
        
        Args:
            tool_name: Nombre de la herramienta
            **kwargs: Argumentos para la herramienta
            
        Returns:
            Resultado de la herramienta
        """
        try:
            logger.info(f"Llamando herramienta: {tool_name} con args: {kwargs}")
            
            # En FastMCP, las herramientas se exponen como endpoints
            # Por ahora simulamos la respuesta directa a la API
            # En producción, esto se conectaría al servidor MCP via stdio
            
            # Mapeo directo a la API de Rick and Morty para el POC
            base_url = "https://rickandmortyapi.com/api"
            
            if tool_name == "get_character":
                url = f"{base_url}/character/{kwargs.get('character_id')}"
                response = self.session.get(url, timeout=30)
                
            elif tool_name == "search_characters":
                params = {k: v for k, v in kwargs.items() if v is not None}
                response = self.session.get(f"{base_url}/character/", params=params, timeout=30)
                
            elif tool_name == "get_multiple_characters":
                ids = ",".join(map(str, kwargs.get('character_ids', [])))
                response = self.session.get(f"{base_url}/character/{ids}", timeout=30)
                
            elif tool_name == "get_location":
                url = f"{base_url}/location/{kwargs.get('location_id')}"
                response = self.session.get(url, timeout=30)
                
            elif tool_name == "search_locations":
                params = {k: v for k, v in kwargs.items() if v is not None and k != 'type_filter'}
                if 'type_filter' in kwargs and kwargs['type_filter']:
                    params['type'] = kwargs['type_filter']
                response = self.session.get(f"{base_url}/location/", params=params, timeout=30)
                
            elif tool_name == "get_episode":
                url = f"{base_url}/episode/{kwargs.get('episode_id')}"
                response = self.session.get(url, timeout=30)
                
            elif tool_name == "search_episodes":
                params = {k: v for k, v in kwargs.items() if v is not None}
                response = self.session.get(f"{base_url}/episode/", params=params, timeout=30)
                
            elif tool_name == "get_all_characters_summary":
                response = self.session.get(f"{base_url}/character/", timeout=30)
                data = response.json()
                return {
                    "total_characters": data["info"]["count"],
                    "total_pages": data["info"]["pages"],
                    "sample_characters": [
                        {
                            "id": char["id"],
                            "name": char["name"],
                            "status": char["status"],
                            "species": char["species"]
                        }
                        for char in data["results"][:5]
                    ]
                }
            
            elif tool_name == "health_check":
                return {
                    "server": "healthy",
                    "rickmorty_api": "healthy",
                    "timestamp": time.time()
                }
            
            else:
                raise ValueError(f"Herramienta desconocida: {tool_name}")
            
            response.raise_for_status()
            result = response.json()
            logger.info(f"Herramienta {tool_name} ejecutada exitosamente")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error llamando herramienta {tool_name}: {e}")
            return {"error": str(e), "tool": tool_name}
        except Exception as e:
            logger.error(f"Error inesperado en {tool_name}: {e}")
            return {"error": str(e), "tool": tool_name}
    
    def health_check(self) -> bool:
        """Verifica si el servidor MCP está saludable"""
        try:
            result = self.call_tool("health_check")
            return "error" not in result
        except Exception:
            return False


class RickMortyAgent:
    """Agente principal que usa Gemini para procesar consultas"""
    
    def __init__(self, gemini_api_key: str, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        
        # Configurar Gemini
        genai.configure(api_key=gemini_api_key)
        
        # Lista de modelos a probar (en orden de preferencia)
        # Basado en modelos disponibles en Gemini 2.x API
        models_to_try = [
            'gemini-2.5-flash',           # Recomendado: rápido y eficiente
            'gemini-flash-latest',        # Alias al último flash
            'gemini-2.0-flash',           # Alternativa 2.0
            'gemini-2.5-pro',             # Más potente pero más lento
            'gemini-pro-latest',          # Alias al último pro
        ]
        
        model_initialized = False
        
        for model_name in models_to_try:
            try:
                logger.info(f"Intentando inicializar modelo: {model_name}")
                
                # Intentar con system_instruction primero (versión nueva)
                try:
                    self.model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=SYSTEM_PROMPT
                    )
                except TypeError:
                    # Fallback para versiones antiguas
                    self.model = genai.GenerativeModel(model_name=model_name)
                    logger.warning("Versión antigua de google-generativeai detectada, usando sin system_instruction")
                
                # Iniciar chat
                self.chat = self.model.start_chat(history=[])
                
                # Si no soporta system_instruction, lo enviamos como primer mensaje
                if not hasattr(self.model, 'system_instruction') or model_name == 'gemini-pro':
                    logger.info("Enviando system prompt como mensaje inicial")
                    self.chat.send_message(SYSTEM_PROMPT)
                
                logger.info(f"✅ Modelo inicializado exitosamente: {model_name}")
                model_initialized = True
                break
                
            except Exception as e:
                logger.warning(f"❌ Error con modelo {model_name}: {e}")
                continue
        
        if not model_initialized:
            raise RuntimeError(
                "No se pudo inicializar ningún modelo de Gemini. "
                "Verifica tu API key y que tengas acceso a los modelos Gemini. "
                "Obtén tu key en: https://makersuite.google.com/app/apikey"
            )
    
    def process_query(self, user_query: str) -> str:
        """
        Procesa una consulta del usuario usando Gemini y las herramientas MCP
        
        Args:
            user_query: Consulta del usuario
            
        Returns:
            Respuesta generada por el agente
        """
        try:
            logger.info(f"Procesando query: {user_query}")
            
            # Analizar qué herramientas necesitamos con Gemini
            analysis_prompt = f"""
Analiza esta consulta del usuario y determina qué herramientas MCP necesitas usar:

CONSULTA: {user_query}

HERRAMIENTAS DISPONIBLES:
- get_character(character_id): Para obtener un personaje específico por ID
- search_characters(name, status, species, gender): Para buscar personajes
- get_location(location_id): Para obtener una localización específica
- search_locations(name, type_filter, dimension): Para buscar localizaciones
- get_episode(episode_id): Para obtener un episodio específico
- search_episodes(name, episode): Para buscar episodios
- get_all_characters_summary(): Para estadísticas generales

Responde en formato JSON con esta estructura:
{{
    "tools_needed": [
        {{"tool": "nombre_herramienta", "params": {{"param1": "valor1"}}}}
    ],
    "reasoning": "Por qué necesitas estas herramientas"
}}
"""
            
            # Obtener plan de Gemini
            response = self.chat.send_message(analysis_prompt)
            plan_text = response.text
            
            # Limpiar y parsear JSON (Gemini a veces incluye markdown)
            plan_text = plan_text.strip()
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_text:
                plan_text = plan_text.split("```")[1].split("```")[0].strip()
            
            try:
                plan = json.loads(plan_text)
            except json.JSONDecodeError as e:
                logger.warning(f"No se pudo parsear plan JSON: {e}. Usando búsqueda simple.")
                # Fallback: buscar por nombre si menciona un personaje
                plan = {
                    "tools_needed": [{"tool": "search_characters", "params": {"name": user_query}}],
                    "reasoning": "Búsqueda simple por nombre"
                }
            
            logger.info(f"Plan generado: {plan['reasoning']}")
            
            # Ejecutar herramientas
            tool_results = []
            for tool_call in plan.get("tools_needed", []):
                tool_name = tool_call.get("tool")
                params = tool_call.get("params", {})
                
                result = self.mcp_client.call_tool(tool_name, **params)
                tool_results.append({
                    "tool": tool_name,
                    "params": params,
                    "result": result
                })
            
            # Generar respuesta final con Gemini
            final_prompt = f"""
CONSULTA ORIGINAL: {user_query}

DATOS OBTENIDOS DE LAS HERRAMIENTAS:
{json.dumps(tool_results, indent=2, ensure_ascii=False)}

Ahora genera una respuesta amigable, informativa y entretenida para el usuario.
Usa emojis relevantes (🛸, 👽, 🌌) y organiza la información de forma clara.
Si los datos muestran errores, indícalo de forma natural.
"""
            
            final_response = self.chat.send_message(final_prompt)
            
            logger.info("Respuesta generada exitosamente")
            return final_response.text
            
        except Exception as e:
            logger.error(f"Error procesando query: {e}")
            return f"{ERROR_MESSAGES['gemini_error']}\n\nError técnico: {str(e)}"
    
    def interactive_mode(self):
        """Modo interactivo de chat"""
        console.print(Panel(USER_GREETING, title="🛸 Rick and Morty Agent", border_style="cyan"))
        
        # Verificar health del servidor
        if not self.mcp_client.health_check():
            console.print("⚠️  [yellow]Advertencia: El servidor MCP no responde[/yellow]")
        
        while True:
            try:
                # Obtener input del usuario
                user_input = Prompt.ask("\n[bold cyan]Tú[/bold cyan]")
                
                if user_input.lower() in ['salir', 'exit', 'quit', 'q']:
                    console.print("[yellow]¡Hasta luego! 👋[/yellow]")
                    break
                
                if not user_input.strip():
                    continue
                
                # Procesar query
                console.print("\n[bold green]🤖 Agente[/bold green]: Pensando...", end="\r")
                response = self.process_query(user_input)
                
                # Mostrar respuesta
                console.print("\n[bold green]🤖 Agente[/bold green]:")
                console.print(Markdown(response))
                
            except KeyboardInterrupt:
                console.print("\n[yellow]¡Hasta luego! 👋[/yellow]")
                break
            except Exception as e:
                logger.error(f"Error en modo interactivo: {e}")
                console.print(f"[red]Error: {e}[/red]")


def main():
    """Función principal"""
    # Verificar variables de entorno
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8000")
    
    if not gemini_api_key:
        console.print("[red]Error: GEMINI_API_KEY no está configurada[/red]")
        console.print("Obtén tu API key en: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    # Inicializar cliente MCP
    mcp_client = MCPClient(mcp_server_url)
    
    # Inicializar agente
    agent = RickMortyAgent(gemini_api_key, mcp_client)
    
    # Iniciar modo interactivo
    agent.interactive_mode()


if __name__ == "__main__":
    main()