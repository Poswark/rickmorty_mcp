import os
from typing import Optional

class Config:
    """Configuración del servidor MCP"""
    
    # API Configuration
    RICKMORTY_API_BASE: str = "https://rickandmortyapi.com/api"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Proxy Configuration (para RHEL)
    HTTP_PROXY: Optional[str] = os.getenv("HTTP_PROXY")
    HTTPS_PROXY: Optional[str] = os.getenv("HTTPS_PROXY")
    NO_PROXY: Optional[str] = os.getenv("NO_PROXY")
    
    # Rate Limiting
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    @classmethod
    def get_proxies(cls) -> dict:
        """Retorna configuración de proxy si está definida"""
        proxies = {}
        if cls.HTTP_PROXY:
            proxies['http'] = cls.HTTP_PROXY
        if cls.HTTPS_PROXY:
            proxies['https'] = cls.HTTPS_PROXY
        return proxies if proxies else None

config = Config()
