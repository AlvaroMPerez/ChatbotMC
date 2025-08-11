import httpx
from microsoft.graph import Graph
from typing import List

async def link_promociones() -> List[str] | None:
    graph = Graph()
    try:
        token = await graph.get_token()
    finally:
        await graph.credential.close()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = "https://graph.microsoft.com/v1.0/users/a66db278-2cb8-4d2a-8cb5-3824c1dfffb9/drive/root:/promociones:/children"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    link_imagenes: List[str] = []
    if response.status_code == 200:
        data = response.json()
        for item in data.get('value', []):
            image_link = item.get('@microsoft.graph.downloadUrl')
            if image_link:
                link_imagenes.append(image_link)
        return link_imagenes
    else:
        print("Error al obtener imágenes:", response.text)
        return None