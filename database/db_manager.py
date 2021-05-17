import json
from pathlib import Path

from sqlalchemy.engine import create_engine

from database.models import WikiMap
from database.db import Database
from database import config, crud, models

Base = models.BASE


def get_available_sample_maps():
    data_path = Path("static/sample_data")
    available_maps = []
    for child in data_path.iterdir():
        if child.suffix == ".json":
            available_maps.append(child.stem)
    return available_maps


def create_dummy_entries(session_maker):
    sample_maps = get_available_sample_maps()
    json_dict = {
        "nodes": [
            {"id": "Quantum Mechanics", "group": 0},
            {"id": "A. Douglas Stone", "group": 1},
            {"id": "Abdus Salam", "group": 1},
            {"id": "Abraham Pais", "group": 1},
        ],
        "links": [
            {"source": "Quantum Mechanics", "target": "A. Douglas Stone", "value": 1},
            {"source": "Quantum Mechanics", "target": "Abdus Salam", "value": 1},
            {"source": "Quantum Mechanics", "target": "Abraham Pais", "value": 1},
        ],
    }
    dummy_map = WikiMap(
        title="Quantum Mechanics",
        json_data=json_dict,
        levels=1,
        pages_per_level=3,
    )
    sess = session_maker()
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
    uri = config.get_production_config_locally()
    database = Database(uri)
    create_dummy_entries(database.Session)
    results = get_all(database)
    print(results)
    database.close()
