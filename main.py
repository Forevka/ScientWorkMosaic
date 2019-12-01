import asyncio
from services.dbservice import DBService
from loguru import logger

async def main():
    db = DBService(password='werdwerd2012', host='194.67.198.163', database='mosaic')
    await db.connect(migrate=False)
    file = open('../1.jpg', 'rb').read()
    file = await db.insert_new_file(file)
    logger.info(file)
    file = await db.find_file_by_id('484a9568-a996-4c5c-a386-5c60d9303eef')
    logger.info(file)
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())