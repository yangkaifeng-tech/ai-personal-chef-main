import base64

import httpx
from langchain.messages import HumanMessage

from app.agents.prompts import INGREDIENT_RECOGNITION_PROMPT


async def image_url_to_data_url(image_url: str) -> str:
    """Download an image and convert it to a Base64 data URL."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as http_client:
        image_response = await http_client.get(image_url)
        image_response.raise_for_status()
        content_type = image_response.headers.get("content-type", "image/jpeg").split(";", 1)[0]
        image_data = base64.b64encode(image_response.content).decode("ascii")
        return f"data:{content_type};base64,{image_data}"


async def identify_ingredients(model, image_url: str) -> str:
    """Use the vision model directly, then pass text into the Agent."""
    image_data_url = await image_url_to_data_url(image_url)
    response = await model.ainvoke([
        HumanMessage(content=[
            {
                "type": "text",
                "text": INGREDIENT_RECOGNITION_PROMPT,
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_data_url,
                },
            },
        ])
    ])

    if isinstance(response.content, str):
        return response.content

    return str(response.content)
