from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import database.config
from database.models import WikiMap


class Database(object):
    def __init__(self, uri=None, sslmode=True):
        if uri is None:
            self.DATABASE_URI = database.config.get_env_database_url(sslmode=sslmode)
        else:
            self.DATABASE_URI = database.config.make_sqlalchemy_uri(
                uri, sslmode=sslmode
            )
        self.engine = create_engine(self.DATABASE_URI)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def close(self):
        self.Session.close_all()

        self.engine.dispose()

    def get_available_maps(self):
        sess = self.Session()
        available_maps = sess.query(WikiMap).order_by(WikiMap.title).all()
        # data_path = Path("static/data")
        # available_maps = []
        # for child in data_path.iterdir():
        #     if child.suffix == ".json":
        #         available_maps.append(child.stem)
        sess.close()
        return available_maps


Base = declarative_base()

if __name__ == "__main__":
    testdb = Database()
