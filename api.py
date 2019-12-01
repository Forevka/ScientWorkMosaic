from models.file import DBFile, db_file_from_dict
import base64
import typing
from services.dbservice import DBService
import asyncio
from aiohttp_apispec import (
    docs,
    request_schema,
    setup_aiohttp_apispec,
)
from aiohttp import web
from request_schema.file import File, DownloadableFile
from marshmallow  import ValidationError
from loguru import logger 
from utils import download_file_to_memory
import json

db = DBService(password='werdwerd2012', host='194.67.198.163', database='mosaic')

@docs(
    tags=["get file"],
    summary="get file",
    description="get file",
)
@request_schema(File())
async def get_file_by_id(request: web.Request):
    if request.can_read_body:
        payload = await request.json()
        if payload:
            try:
                file_model: File = File().load(payload)
            except ValidationError as ex:
                logger.error(ex)
                return web.json_response(ex.normalized_messages(), status=400)

            file: DBFile = await db.find_file_by_id(file_model['file_id'])
            if file:
                return web.json_response(file.to_dict())

    return web.Response(status=201)

@docs(
    tags=["download"],
    summary="download file to db by given link",
    description="download file to db by given link",
)
@request_schema(DownloadableFile())
async def download_file_by_link(request: web.Request):
    if request.can_read_body:
        payload = await request.json()
        if payload:
            try:
                file_model: DownloadableFile = DownloadableFile().load(payload)
            except ValidationError as ex:
                logger.error(ex)
                return web.json_response(ex.normalized_messages(), status=400)

            try:
                raw_file: typing.BinaryIO = await download_file_to_memory(file_model['link_to_file'])
            except Exception as ex:
                logger.error(ex)
                return web.json_response(f'{"error": {ex}}', status=400)
            else:
                file: DBFile = await db.insert_new_file(raw_file)

            if file:
                return web.json_response(file.to_dict())

    return web.Response(status=201)

@docs(
    tags=["files"],
    summary="files get available",
    description="files get available",
)
@request_schema(DownloadableFile())
async def get_all_not_procced_files(request: web.Request):
    files: typing.List[DBFile] = await db.get_all_not_processed_files()

    if files:
        return web.json_response([i.to_dict() for i in files])

    return web.Response(status=201)


@docs(
    tags=["mosaic"],
    summary="start processing img to mosaic",
    description="start processing img to mosaic",
)
@request_schema(DownloadableFile())
async def start_processing(request: web.Request):
    files: typing.List[DBFile] = await db.get_all_not_processed_files()

    if files:
        return web.json_response([i.to_dict() for i in files])

    return web.Response(status=201)



async def on_startup(app):
    await db.connect()


app = web.Application()
app.on_startup.append(on_startup)
app.add_routes([web.get('/', get_file_by_id), 
                web.post('/file', download_file_by_link),
                web.get('/files', get_all_not_procced_files),
                ])



if __name__ == '__main__':
    setup_aiohttp_apispec(
        app=app, 
        title="My Documentation", 
        version="v1",
        url="/api/docs/swagger.json",
        swagger_path="/api/docs",
    )

    web.run_app(app, port=9999)