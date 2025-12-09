"""
Rick and Morty MCP Server
Servidor MCP que expone herramientas para interactuar con la API de Rick and Morty
"""

import logging
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import config

# Configurar logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar FastMCP
mcp = FastMCP("Rick and Morty MCP Server")

# Configurar session con reintentos y proxy
def get_session() -> requests.Session:
    """Crea una sesión HTTP configurada con reintentos y proxy"""
    session = requests.Session()
    
    # Configurar reintentos
    retry_strategy = Retry(
        total=config.MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Configurar proxy si existe
    proxies = config.get_proxies()
    if proxies:
        session.proxies.update(proxies)
        logger.info(f"Proxy configurado: {proxies}")
    
    return session

# Session global
http_session = get_session()


@mcp.tool()
def get_character(character_id: int) -> Dict[str, Any]:
    """
    Obtiene información detallada de un personaje por su ID.
    
    Args:
        character_id: ID del personaje (1-826)
        
    Returns:
        Diccionario con información del personaje incluyendo:
        - id, name, status, species, type, gender
        - origin, location
        - image, episode list, url, created
    """
    try:
        logger.info(f"Obteniendo personaje con ID: {character_id}")
        response = http_session.get(
            f"{config.RICKMORTY_API_BASE}/character/{character_id}",
            timeout=config.TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Personaje obtenido: {data.get('name', 'Unknown')}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obteniendo personaje {character_id}: {e}")
        return {"error": str(e), "character_id": character_id}


@mcp.tool()
def search_characters(
    name: Optional[str] = None,
    status: Optional[str] = None,
    species: Optional[str] = None,
    gender: Optional[str] = None,
    page: int = 1
) -> Dict[str, Any]:
    """
    Busca personajes con filtros opcionales.
    
    Args:
        name: Filtrar por nombre del personaje
        status: Filtrar por estado (alive, dead, unknown)
        species: Filtrar por especie (Human, Alien, etc)
        gender: Filtrar por género (Male, Female, Genderless, unknown)
        page: Número de página (default: 1)
        
    Returns:
        Diccionario con resultados paginados:
        - info: metadata de paginación
        - results: lista de personajes
    """
    try:
        params = {"page": page}
        if name:
            params["name"] = name
        if status:
            params["status"] = status.lower()
        if species:
            params["species"] = species
        if gender:
            params["gender"] = gender.lower()
        
        logger.info(f"Buscando personajes con filtros: {params}")
        response = http_session.get(
            f"{config.RICKMORTY_API_BASE}/character/",
            params=params,
            timeout=config.TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Encontrados {data['info']['count']} personajes")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error buscando personajes: {e}")
        return {"error": str(e), "filters": params}


@mcp.tool()
def get_multiple_characters(character_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Obtiene múltiples personajes por sus IDs en una sola llamada.
    
    Args:
        character_ids: Lista de IDs de personajes
        
    Returns:
        Lista de diccionarios con información de cada personaje
    """
    try:
        ids_str = ",".join(map(str, character_ids))
        logger.info(f"Obteniendo múltiples personajes: {ids_str}")
        response = http_session.get(
            f"{config.RICKMORTY_API_BASE}/character/{ids_str}",
            timeout=config.TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        # Si es solo un personaje, la API devuelve dict, no lista
        if isinstance(data, dict):
            data = [data]
        
        logger.info(f"Obtenidos {len(data)} personajes")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obteniendo múltiples personajes: {e}")
        return [{"error": str(e), "character_ids": character_ids}]


@mcp.tool()
def get_location(location_id: int) -> Dict[str, Any]:
    """
    Obtiene información de una localización por su ID.
    
    Args:
        location_id: ID de la localización
        
    Returns:
        Diccionario con información de la localización:
        - id, name, type, dimension
        - residents: lista de URLs de personajes
        - url, created
    """
    try:
        logger.info(f"Obteniendo localización con ID: {location_id}")
        response = http_session.get(
            f"{config.RICKMORTY_API_BASE}/location/{location_id}",
            timeout=config.TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Localización obtenida: {data.get('name', 'Unknown')}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obteniendo localización {location_id}: {e}")
        return {"error": str(e), "location_id": location_id}


@mcp.tool()
def search_locations(
    name: Optional[str] = None,
    type_filter: Optional[str] = None,
    dimension: Optional[str] = None,
    page: int = 1
) -> Dict[str, Any]:
    """
    Busca localizaciones con filtros opcionales.
    
    Args:
        name: Filtrar por nombre de la localización
        type_filter: Filtrar por tipo (Planet, Space station, etc)
        dimension: Filtrar por dimensión
        page: Número de página (default: 1)
        
    Returns:
        Diccionario con resultados paginados de localizaciones
    """
    try:
        params = {"page": page}
        if name:
            params["name"] = name
        if type_filter:
            params["type"] = type_filter
        if dimension:
            params["dimension"] = dimension
        
        logger.info(f"Buscando localizaciones con filtros: {params}")
        response = http_session.get(
            f"{config.RICKMORTY_API_BASE}/location/",
            params=params,
            timeout=config.TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Encontradas {data['info']['count']} localizaciones")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error buscando localizaciones: {e}")
        return {"error": str(e), "filters": params}


@mcp.tool()
def get_episode(episode_id: int) -> Dict[str, Any]:
    """
    Obtiene información de un episodio por su ID.
    
    Args:
        episode_id: ID del episodio
        
    Returns:
        Diccionario con información del episodio:
        - id, name, air_date, episode (código)
        - characters: lista de URLs de personajes
        - url, created
    """
    try:
        logger.info(f"Obteniendo episodio con ID: {episode_id}")
        response = http_session.get(
            f"{config.RICKMORTY_API_BASE}/episode/{episode_id}",
            timeout=config.TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Episodio obtenido: {data.get('name', 'Unknown')}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obteniendo episodio {episode_id}: {e}")
        return {"error": str(e), "episode_id": episode_id}


@mcp.tool()
def search_episodes(
    name: Optional[str] = None,
    episode: Optional[str] = None,
    page: int = 1
) -> Dict[str, Any]:
    """
    Busca episodios con filtros opcionales.
    
    Args:
        name: Filtrar por nombre del episodio
        episode: Filtrar por código de episodio (ej: S01E01)
        page: Número de página (default: 1)
        
    Returns:
        Diccionario con resultados paginados de episodios
    """
    try:
        params = {"page": page}
        if name:
            params["name"] = name
        if episode:
            params["episode"] = episode
        
        logger.info(f"Buscando episodios con filtros: {params}")
        response = http_session.get(
            f"{config.RICKMORTY_API_BASE}/episode/",
            params=params,
            timeout=config.TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Encontrados {data['info']['count']} episodios")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error buscando episodios: {e}")
        return {"error": str(e), "filters": params}


@mcp.tool()
def get_all_characters_summary() -> Dict[str, Any]:
    """
    Obtiene un resumen estadístico de todos los personajes.
    
    Returns:
        Diccionario con estadísticas:
        - total_characters: número total
        - total_pages: páginas disponibles
        - sample_characters: primeros 5 personajes como muestra
    """
    try:
        logger.info("Obteniendo resumen de personajes")
        response = http_session.get(
            f"{config.RICKMORTY_API_BASE}/character/",
            timeout=config.TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        summary = {
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
        logger.info(f"Resumen generado: {summary['total_characters']} personajes")
        return summary
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obteniendo resumen: {e}")
        return {"error": str(e)}


# Endpoint de health check
@mcp.tool()
def health_check() -> Dict[str, str]:
    """
    Verifica el estado del servidor y la conectividad con la API.
    
    Returns:
        Estado del servidor y API externa
    """
    try:
        response = http_session.get(
            f"{config.RICKMORTY_API_BASE}/character/1",
            timeout=5
        )
        api_status = "healthy" if response.status_code == 200 else "degraded"
    except Exception as e:
        api_status = f"unhealthy: {str(e)}"
    
    return {
        "server": "healthy",
        "rickmorty_api": api_status,
        "proxy_configured": "yes" if config.get_proxies() else "no"
    }


if __name__ == "__main__":
    logger.info("Iniciando Rick and Morty MCP Server")
    logger.info(f"Escuchando en {config.HOST}:{config.PORT}")
    
    # Para este POC, el servidor se mantiene corriendo en modo stdio
    # En producción, esto se conectaría vía SSE o stdio con el cliente
    # Por ahora, mantenemos el proceso vivo
    try:
        logger.info("Servidor MCP listo. Esperando conexiones...")
        # Mantener el servidor vivo
        import signal
        signal.pause()
    except KeyboardInterrupt:
        logger.info("Servidor detenido por usuario")
    except Exception as e:
        logger.error(f"Error en servidor: {e}")