import json
import re

from pathlib import Path

from sqlalchemy.engine import create_engine

from database.models import WikiMap
from database.db import Database
from database import models

Base = models.BASE


def get_available_sample_maps():
    data_path = Path("static/sample_data")
    available_maps = []
    for child in data_path.iterdir():
        if child.suffix == ".json":
            available_maps.append(child.stem)
    return available_maps


def create_sample_entries(session_maker):
    maps = get_available_sample_maps()
    pattern = re.compile(r"(.+)_l_(\d+)_lpp_(\d+)")
    titles = []
    levels = []
    lpps = []
    json_files = []

    for page_map in maps:
        print(str(map))
        results = pattern.split(str(page_map))
        titles.append(results[1].replace("_", " "))
        levels.append(results[2])
        lpps.append(results[3])
        file_name = page_map + ".json"
        json_files.append(file_name)

    sess = session_maker()
    for i, file in enumerate(json_files):
        if (
            sess.query(WikiMap)
            .filter_by(title=titles[i], levels=levels[i], lpp=lpps[i])
            .first()
            is not None
        ):
            print("Found duplicate: {}".format(titles[i]))
            continue  # don't add duplicates
        with open("static/sample_data/{}".format(file), "r") as f:
            json_dict = json.load(f)
        dummy_map = WikiMap(
            title=titles[i],
            json_data=json_dict,
            levels=levels[i],
            lpp=lpps[i],
        )
        sess.add(dummy_map)
    sess.commit()
    sess.close()


def delete_recreate_database(uri) -> None:
    """[summary]

    [extended_summary]

    Parameters
    ----------
    uri : [type]
        [description]
    """
    engine = create_engine(uri)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    engine.dispose()


def create_database(uri: str) -> None:
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
    engine.dispose()


def get_all(db):
    sess = db.Session()
    query = sess.query(WikiMap).order_by(WikiMap.title).all()
    sess.close()
    return query


if __name__ == "__main__":
    database = Database(sslmode=False)
    # delete_recreate_database(database.DATABASE_URI)
    create_sample_entries(database.Session)
    results = get_all(database)
    print(results)
    database.close()
