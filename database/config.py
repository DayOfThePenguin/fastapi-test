from configparser import ConfigParser
from os import environ
from pathlib import Path


def get_env_database_url(sslmode=True):
    """get the "DATABASE_URL" environment variable and return an sqlalchemy-readable,
    ssl-using version
    Parameters
    ----------
    sslmode : bool=True
        whether to use sslmode in the database uri

    Returns
    -------
    database_uri : str
        string with the "DATABASE_URL" in sqlalchemy, ssl'ed form
    """

    database_uri = environ["DATABASE_URL"]
    database_uri = make_sqlalchemy_uri(database_uri, sslmode)

    return database_uri


def make_sqlalchemy_uri(uri, sslmode=True):
    """Convert regular postgres database uri to one that sqlalchemy can read

    Parameters
    ----------
    uri : str
        postgres uri you want to connect to, in the form of
        postgres://username:password@host:port/database or
        postgresql://username:password@host:port/database

    Returns
    -------
    uri: str
        uri that sqlalchemy can connect to, in the form of
        postgresql://username:password@host:port/database
    """
    if sslmode is True:
        uri = enforce_ssl(uri)
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    return uri


def enforce_ssl(uri):
    """Add a parameter to the Postgres URI that will enforce ssl use

    Added so when certs/more complicated security is added in the future, this can
    be expanded easily

    Parameters
    ----------
    uri : str
        string of the database_uri to add a sslmode to

    Returns
    -------
    uri : str
        database_uri with sslmode added
    """
    uri += "?sslmode=require"
    return uri


def get_production_config_locally():
    """get the production config from

    [extended_summary]
    """
    config_path = Path(".env/production.ini")
    production_config = ConfigParser()
    production_config.read_file(open(config_path))
    database_uri = production_config["postgres"]["DATABASE_URL"]
    database_uri = make_sqlalchemy_uri(database_uri)
    return database_uri
