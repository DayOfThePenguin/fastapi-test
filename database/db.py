import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

import database.config
from database.models import WikiMap

Base = declarative_base()


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
        sess.close()
        return available_maps


def get_database() -> Database:
    """get a Database object to be added to the fastapi or router instance

    will default to trying to get an ssl connection to the database, if unable
    to get an ssl connection, it will still return a non-ssl Database object

    Returns
    -------
    db : Database
        Database object for the fastapi or router instance
    """
    try:  # default: try production ssl
        db = Database()
        sess = db.Session()
        sess.query(WikiMap).first()
        sess.close()
        logging.info("SSL connection to database SUCCEEDED")
    except OperationalError:  # happens on local db
        logging.critical("SSL connection to database FAILED, connecting without SSL")
        db = Database(sslmode=False)
    return db


if __name__ == "__main__":
    testdb = Database()
