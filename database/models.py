# from uuid import uuid4
import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSON, UUID

from sqlalchemy import create_engine

from sqlalchemy.types import SmallInteger


BASE = declarative_base()


class WikiMap(BASE):
    __tablename__ = "maps"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), primary_key=True, index=True)
    json_data = Column(JSON())
    levels = Column(SmallInteger())
    pages_per_level = Column(SmallInteger())

    def __repr__(self):
        msg = "<WikiMap: (\n\t"
        msg += "id={},\n\t".format(self.id)
        msg += "title='{}',\n\t".format(self.title)
        msg += "json_data - not displayed,\n\t"
        msg += "levels={},\n\t".format(self.levels)
        msg += "pages_per_level={}\n".format(self.pages_per_level)
        msg += ")>"
        return msg
