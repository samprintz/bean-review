import httpx
from typing import Sequence


async def predict_accounts(
    narrations: Sequence[str],
    host: str,
    port: int,
) -> list[str]:
    """Send narrations to AI service and return predicted accounts.

    Args:
        narrations: List of transaction narrations to predict accounts for.
        host: AI service host.
        port: AI service port.

    Returns:
        List of predicted accounts in same order as input narrations.
    """
    url = f"http://{host}:{port}/predict"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={"texts": list(narrations)},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("accounts", [])
