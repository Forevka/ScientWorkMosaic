from models.file import DBFile
from marshmallow import Schema, fields, post_load

class File(Schema):
    file_id = fields.UUID()

class DownloadableFile(Schema):
    link_to_file = fields.Url()