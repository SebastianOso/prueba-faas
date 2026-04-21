import asyncio
from fastapi import APIRouter, HTTPException, Query
import httpx

router = APIRouter(
    prefix="/pokemon",
    tags=["pokemon"]
)

async def fetch_pokemon_data(client, pokemon_id):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    try:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error al obtener pokemon {pokemon_id}: {e}")
    return None # Si falla, regresamos None para filtrarlo después

"""
@router.get("/dividir-batch")
async def handle_pokemons(
    inicio: int = Query(1, ge=1, description="ID inicial del Pokémon"),
    fin: int = Query(50, ge=1, description="ID final del Pokémon")
):
    
    # Validación simple para evitar errores de rango
    if inicio > fin:
        raise HTTPException(
            status_code=400, 
            detail="El valor de 'inicio' no puede ser mayor que 'fin'"
        )

    agrupados_por_tipo = {}
    
    async with httpx.AsyncClient(verify=False) as client:
        for i in range(inicio, fin + 1):
            url = f"https://pokeapi.co/api/v2/pokemon/{i}"
            
            try:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    tipos = [t["type"]["name"] for t in data["types"]]
                    
                    info_basica = {
                        "id": data["id"],
                        "nombre": data["name"],
                        "imagen": data["sprites"]["front_default"]
                    }
                    
                    for tipo in tipos:
                        if tipo not in agrupados_por_tipo:
                            agrupados_por_tipo[tipo] = []
                        agrupados_por_tipo[tipo].append(info_basica)
                
            except Exception as e:
                print(f"Error al obtener pokemon {i}: {e}")
                continue # Si falla uno, intentamos con el siguiente

    return {
        "rango": {"desde": inicio, "hasta": fin},
        "total_tipos_encontrados": len(agrupados_por_tipo),
        "data": agrupados_por_tipo
    }
"""

@router.get("/dividir-batch")
async def handle_pokemons(
    inicio: int = Query(1, ge=1, description="ID inicial del Pokémon"),
    fin: int = Query(50, ge=1, description="ID final del Pokémon")
):
    if inicio > fin:
        raise HTTPException(status_code=400, detail="'inicio' no puede ser mayor que 'fin'")

    async with httpx.AsyncClient(verify=False) as client:
        tareas = [fetch_pokemon_data(client, i) for i in range(inicio, fin + 1)]
        
        # Ejecutamos todas las peticiones al mismo tiempo
        resultados = await asyncio.gather(*tareas)

    agrupados_por_tipo = {}
    
    
    # Procesamos los resultados (filtrando los que fallaron y devolvieron None)
    for data in filter(None, resultados):
        info_basica = {
            "id": data["id"],
            "nombre": data["name"],
            "imagen": data["sprites"]["front_default"]
        }
        
        for t in data["types"]:
            tipo = t["type"]["name"]
            agrupados_por_tipo.setdefault(tipo, []).append(info_basica)

    return {
        "rango": {"desde": inicio, "hasta": fin},
        "total_tipos_encontrados": len(agrupados_por_tipo),
        "data": agrupados_por_tipo
    }

@router.get("/{pokemon_id}")
async def get_pokemon(pokemon_id: str):
    """
    Información de pokemon 
    """

    # url a consumir
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"

    # hacer la petición al endpoint de la api a consumir
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url)

    # error handling
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Ese pokemon no existe en la BD")
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Internal server error")
    
    data = response.json()

    return {
        "id": data["id"],
        "nombre": data["name"],
        "tipos": [t["type"]["name"] for t in data["types"]],
        "imagen": data["sprites"]["front_default"]
    }