import aiohttp        
import aiofiles
import typing

async def download_file_to_memory(link: str) -> typing.BinaryIO:
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            if resp.status == 200:
                return await resp.read()