import os
import typing
import uuid
import asyncio

import asyncpg
from loguru import logger

from models.file import DBFile, db_file_from_dict



class DBService:
    conn: asyncpg.Connection
    password: str
    user: str
    database: str
    host: str

    def __init__(self, password: str, host: str, user: str = 'postgres', database: str = 'mosaic',):
        self.password: str = password
        self.user: str = user
        self.database: str = database
        self.host: str = host
        self.loop = None
        #

    async def connect(self, migrate: bool = False, loop=None) -> None:
        self.conn = await asyncpg.connect(user=self.user, password=self.password,
                                          database=self.database, host=self.host, loop=asyncio.get_event_loop())

        logger.info('connected')
        if migrate:
            path_to_migrations = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'migrations'))
            if os.path.exists(path_to_migrations):
                logger.error('Migrations directory doesnt exist')
                return
            for filename in os.listdir(path_to_migrations):
                if filename.endswith(".sql"):
                    sql_migration = open(os.path.join(
                        path_to_migrations, filename), 'r').read()
                    try:
                        res = await self.conn.execute(sql_migration)
                        logger.debug('Apply sql migration ' +
                                    str(filename) + "res: "+str(res))
                    except Exception as e:
                        logger.error(e)
    
    async def insert_new_file(self, file: typing.BinaryIO) -> typing.Optional[DBFile]:
        sql = ("INSERT into in_files (content) values ($1) RETURNING file_id, content", file)

        res = await self.conn.fetchrow(*sql)
        if res:
            return db_file_from_dict(res)
    
    async def find_file_by_id(self, file_id: uuid.UUID) -> typing.Optional[DBFile]:
        sql = ("SELECT * from in_files where file_id = $1", file_id)

        res = await self.conn.fetchrow(*sql)
        if res:
            return db_file_from_dict(res)

    async def get_all_not_processed_files(self,) -> typing.List[DBFile]:
        sql = "SELECT * from in_files"

        res = await self.conn.fetch(sql)
        if res:
            return [db_file_from_dict(i) for i in res]#db_file_from_dict(res)
        return []

    