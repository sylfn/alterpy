import aiohttp

the_bot_id = 0
admins: set[int] = set()
session: aiohttp.ClientSession = None
