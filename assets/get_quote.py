import aiohttp


async def get_quote() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.quotable.io/random") as response:
            json = await response.json()
            text = json["content"]
            author = json["author"]
            return (f"{text} - {author}")
