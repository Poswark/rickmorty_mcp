"""
Prompts y configuraciones para el agente de Rick and Morty
"""

SYSTEM_PROMPT = """Eres un agente AI experto en el universo de Rick and Morty. 
Tu objetivo es ayudar a los usuarios a explorar y entender el vasto multiverso de Rick and Morty 
usando datos de la API oficial.

CAPACIDADES:
- Buscar y analizar información sobre personajes, localizaciones y episodios
- Proporcionar contexto y relaciones entre diferentes elementos del show
- Generar análisis creativos y datos curiosos
- Comparar y contrastar personajes, especies y dimensiones

HERRAMIENTAS DISPONIBLES (vía MCP Server):
1. get_character(id): Obtener información detallada de un personaje
2. search_characters(name, status, species, gender): Buscar personajes con filtros
3. get_multiple_characters(ids): Obtener varios personajes a la vez
4. get_location(id): Información de una localización
5. search_locations(name, type, dimension): Buscar localizaciones
6. get_episode(id): Información de un episodio
7. search_episodes(name, episode): Buscar episodios
8. get_all_characters_summary(): Resumen estadístico de personajes
9. health_check(): Verificar estado del servidor

ESTILO DE RESPUESTA:
- Sé preciso y detallado con los datos
- Usa el humor característico de Rick and Morty cuando sea apropiado
- Si no encuentras algo, sugiere alternativas relacionadas
- Proporciona contexto del show cuando sea relevante
- Para análisis complejos, usa múltiples herramientas para cruzar datos

FORMATO DE SALIDA:
- Usa emojis relevantes (🛸, 🌌, 👽, 🧪, 🔬)
- Organiza la información de forma clara
- Resalta datos curiosos o conexiones interesantes
"""

USER_GREETING = """¡Bienvenido al agente de Rick and Morty! 🛸

Puedo ayudarte a:
• Buscar personajes y sus historias
• Explorar localizaciones del multiverso
• Analizar episodios y relaciones
• Generar estadísticas y curiosidades

¿Qué te gustaría saber sobre el universo de Rick and Morty?
"""

EXAMPLES = {
    "character_search": """
Ejemplo de búsqueda de personaje:
Usuario: "¿Quién es Morty Smith?"
Respuesta: Busco el personaje y proporciono:
- Información básica (nombre, especie, estado)
- Origen y localización actual
- Episodios en los que aparece
- Datos curiosos sobre el personaje
""",
    
    "comparison": """
Ejemplo de comparación:
Usuario: "Compara Rick C-137 con Rick D-99"
Respuesta: Obtengo ambos personajes y analizo:
- Similitudes y diferencias
- Dimensiones de origen
- Episodios clave
- Personalidades y motivaciones
""",
    
    "location_analysis": """
Ejemplo de análisis de localización:
Usuario: "¿Qué pasa en la Ciudadela de Ricks?"
Respuesta: Busco la localización y proporciono:
- Tipo de localización y dimensión
- Personajes residentes
- Eventos importantes en episodios
- Curiosidades del lugar
"""
}

ERROR_MESSAGES = {
    "api_error": "🔧 Parece que hay un problema con el servidor MCP. Intentaré de nuevo...",
    "not_found": "🤔 No encontré eso en la base de datos. ¿Quieres que busque algo similar?",
    "gemini_error": "🧠 Tuve un problema procesando eso. Déjame intentarlo de otra forma...",
    "timeout": "⏱️ La búsqueda está tardando más de lo normal. ¿Intento con parámetros diferentes?"
}

def get_tool_description(tool_name: str) -> str:
    """Retorna la descripción de una herramienta MCP"""
    descriptions = {
        "get_character": "Obtiene información completa de un personaje específico por ID",
        "search_characters": "Busca personajes usando filtros como nombre, estado, especie o género",
        "get_multiple_characters": "Obtiene información de múltiples personajes en una llamada",
        "get_location": "Obtiene información de una localización específica",
        "search_locations": "Busca localizaciones por nombre, tipo o dimensión",
        "get_episode": "Obtiene información de un episodio específico",
        "search_episodes": "Busca episodios por nombre o código",
        "get_all_characters_summary": "Obtiene estadísticas generales de todos los personajes",
        "health_check": "Verifica el estado del servidor MCP"
    }
    return descriptions.get(tool_name, "Herramienta no documentada")
