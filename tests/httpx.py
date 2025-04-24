import asyncio
import httpx


async def add_major(manufacturer_name: str, is_valid: bool):
    url = 'http://127.0.0.1:8000/dictionaries/manufacturers/add/'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "manufacturer_name": manufacturer_name,
        "is_valid": is_valid
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        return response.json()


# вызов функции
response = asyncio.run(add_major(manufacturer_name='ogog', is_valid=True))
print(response)
