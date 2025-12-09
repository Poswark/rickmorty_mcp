# Ejemplos de Uso - Rick and Morty MCP Lab

Este documento contiene ejemplos de consultas y casos de uso del agente.

## Ejemplos Básicos

### Búsqueda de Personajes

```
Tú: ¿Quién es Rick Sanchez?
🤖: Rick Sanchez (ID: 1) es el protagonista de la serie. Es un científico genio, alcohólico y cínico. 
    Estado: Vivo
    Especie: Humano
    Género: Masculino
    Origen: Tierra (Dimensión C-137)
```

```
Tú: Busca personajes llamados Morty
🤖: Encontré varios personajes:
    1. Morty Smith (ID: 2) - Principal Morty de la serie
    2. Evil Morty (ID: 19) - Morty malvado con parche en el ojo
    3. Mascot Morty (ID: 281) - Versión mascota de Morty
    [... más resultados]
```

### Filtros Avanzados

```
Tú: Muéstrame todos los personajes humanos vivos
🤖: [Usa search_characters con status="alive" y species="Human"]
    He encontrado 173 personajes humanos vivos, incluyendo:
    - Rick Sanchez
    - Morty Smith
    - Summer Smith
    - Beth Smith
    - Jerry Smith
    [...]
```

```
Tú: ¿Qué personajes son aliens femeninos?
🤖: [Usa search_characters con species="Alien" y gender="Female"]
    Algunos personajes aliens femeninos:
    - Unity (ID: 10) - Entidad colmena
    - Gaia (ID: 68) - Planeta viviente
    - Tammy Guetermann (ID: 95) - Agente Galáctico
    [...]
```

## Episodios

```
Tú: ¿Cuál es el primer episodio?
🤖: El primer episodio es "Pilot" (S01E01), emitido el 2 de diciembre de 2013.
    Participan 19 personajes principales.
```

```
Tú: Busca episodios con "Pickle" en el nombre
🤖: Encontré "Pickle Rick" (S03E03), emitido el 6 de agosto de 2017.
    Es el famoso episodio donde Rick se convierte en pepinillo.
```

## Localizaciones

```
Tú: ¿Qué localizaciones hay en la dimensión C-137?
🤖: [Usa search_locations con dimension="Dimension C-137"]
    Principales localizaciones de C-137:
    - Earth (C-137) - Planeta tipo Tierra
    - [Más localizaciones]
```

```
Tú: Muéstrame todos los planetas
🤖: [Usa search_locations con type="Planet"]
    He encontrado múltiples planetas:
    - Earth (C-137)
    - Abadango
    - Citadel of Ricks
    [...]
```

## Análisis Complejos

```
Tú: Compara a Rick con Morty
🤖: [Obtiene ambos personajes y compara]
    
    RICK SANCHEZ (ID: 1)
    - Especie: Humano
    - Estado: Vivo
    - Origen: Tierra (C-137)
    - Características: Científico genio, cínico
    
    MORTY SMITH (ID: 2)
    - Especie: Humano  
    - Estado: Vivo
    - Origen: Tierra (C-137)
    - Características: Nieto de Rick, más empático
    
    Ambos son de la misma dimensión y aparecen en prácticamente 
    todos los episodios juntos.
```

```
Tú: ¿En cuántos episodios aparece Summer?
🤖: [Obtiene personaje Summer y cuenta episodios]
    Summer Smith aparece en 39 episodios de la serie.
```

## Casos de Uso Avanzados

### 1. Análisis de Personajes por Especie

```python
# Consulta: "Dame estadísticas de especies"
# El agente podría usar múltiples llamadas para agregar:

species_stats = {
    "Human": 173,
    "Alien": 421,
    "Robot": 23,
    "Humanoid": 89,
    "Animal": 34,
    # ...
}
```

### 2. Timeline de Episodios

```
Tú: Muéstrame todos los episodios de la temporada 1
🤖: [Busca episodes con filter por temporada]
    Temporada 1 (2013-2014):
    S01E01 - Pilot
    S01E02 - Lawnmower Dog
    S01E03 - Anatomy Park
    [... 11 episodios]
```

### 3. Network de Personajes

```
Tú: ¿Qué personajes aparecen con Rick en el episodio piloto?
🤖: [Obtiene episodio 1, luego obtiene todos sus personajes]
    En el episodio piloto aparecen:
    - Rick Sanchez
    - Morty Smith
    - Summer Smith
    - Beth Smith
    - Jerry Smith
    [... más personajes]
```

### 4. Búsquedas Geográficas

```
Tú: ¿Qué personajes son de la Tierra?
🤖: [Filtra por origin.name = "Earth"]
    Personajes terrestres principales:
    - Familia Smith
    - Mr. Poopybutthole
    - Birdperson
    [...]
```

## Comandos del Agente

### Modo Interactivo

```bash
python agent.py

# O con Docker
docker-compose exec agent python agent.py
```

### Consultas Directas (Programático)

```python
from agent import RickMortyAgent

agent = RickMortyAgent()

# Consulta simple
response = agent.process_query("¿Quién es Rick?")
print(response)

# Consulta compleja
response = agent.process_query(
    "Busca personajes aliens femeninos y dime cuántos hay"
)
print(response)
```

## Tips y Trucos

### 1. Búsquedas Eficientes

✅ **Bueno**: "Busca personajes llamados Rick"
❌ **Malo**: "Busca todos los personajes y filtra por Rick"

El agente es inteligente y usará los filtros apropiados.

### 2. Combinación de Filtros

```
"Muéstrame personajes humanos vivos de la Tierra"
→ species=Human, status=alive, origin=Earth
```

### 3. Contexto Implícito

El agente entiende contexto:

```
Tú: ¿Quién es Rick?
🤖: Rick Sanchez es...

Tú: ¿Y Morty?
🤖: [Entiende que te refieres a Morty Smith]
```

### 4. Preguntas de Seguimiento

```
Tú: Busca el episodio S01E01
🤖: [Info del episodio]

Tú: ¿Qué personajes aparecen ahí?
🤖: [Lista de personajes del episodio]
```

## Límites y Consideraciones

### Rate Limiting

La API de Rick and Morty no tiene autenticación pero puede tener límites:
- ~10,000 requests por día por IP
- Implementar cache si haces muchas consultas

### Datos Disponibles

- 826 personajes
- 51 episodios
- 126 localizaciones

### Rendimiento

- Consultas simples: <1s
- Consultas complejas (múltiples llamadas): 2-5s
- Con Gemini: +1-2s para generación

## Próximas Features

- [ ] Cache de respuestas de API
- [ ] Búsqueda fuzzy mejorada
- [ ] Análisis de relaciones entre personajes
- [ ] Visualizaciones con gráficos
- [ ] Export de resultados a JSON/CSV
- [ ] API REST para consultas programáticas
- [ ] WebSocket para updates en tiempo real

## Recursos

- [Rick and Morty API Docs](https://rickandmortyapi.com/documentation)
- [FastMCP Examples](https://github.com/jlowin/fastmcp/tree/main/examples)
- [Gemini API Reference](https://ai.google.dev/api/python)

---

**¿Tienes más ideas de consultas?** ¡Compártelas y las agregamos! 🛸
