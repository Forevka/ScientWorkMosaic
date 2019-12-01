from dataclasses import dataclass
import uuid
import base64
from typing import Any, TypeVar, Type, cast, BinaryIO
from loguru import logger


T = TypeVar("T")


def from_str(x: Any) -> bytes:
    assert isinstance(x, bytes)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class DBFile:
    file_id: uuid.UUID
    content: bytes

    @staticmethod
    def from_dict(obj: Any) -> 'DBFile':
        file_id = obj.get("file_id")
        content = from_str(obj.get("content"))
        return DBFile(file_id, content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["file_id"] = str(self.file_id)
        logger.info(self.content)
        result["content"] = base64.b64encode(self.content).decode('utf-8')
        return result


def db_file_from_dict(s: Any) -> DBFile:
    return DBFile.from_dict(s)


def db_file_to_dict(x: DBFile) -> Any:
    return to_class(DBFile, x)