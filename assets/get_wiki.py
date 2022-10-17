import re
import aiohttp


async def get_wiki(query: str) -> str:
    async with aiohttp.ClientSession() as session:
        # First, make a wiki search and choose the first page
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": "1"
        }

        async with session.get("https://en.wikipedia.org/w/api.php",
                               params=params) as response:
            res_json = await response.json()

        results = res_json["query"]["search"]
        if not results:
            return "Result not found"
        
        if re.search("may refer to", results[0]["snippet"]) is not None:
            return "Be more specific"

        page_id = results[0]["pageid"]

        # Second, search the specific pageid to get the extract
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "pageids": page_id,
            "exsentences": "3",
            "explaintext": 1
        }

        async with session.get("https://en.wikipedia.org/w/api.php",
                               params=params) as response:
            res_json = await response.json()

        page = next(iter(res_json["query"]["pages"].values()))
        return page["extract"]
