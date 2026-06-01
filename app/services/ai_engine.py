
import requests
from ..core.config import AI_API_URL, AI_API_KEY


def generate_response(prompt: str, persona: str = None):

    try:
        res = requests.post(
            AI_API_URL,
            headers={
                "Content-Type": "application/json",
                "x-api-key": AI_API_KEY
            },
            json={
                "prompt": prompt,
                "persona": persona or "IGRIS — calm intelligent AI assistant"
            }
        )

        data = res.json()

        return (
            data.get("data", {}).get("response")
            or "No response from AI"
        )

    except Exception as e:
        return f"AI ERROR: {str(e)}"