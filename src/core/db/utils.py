import logging
from os.path import exists
from os import remove

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


DATABASE_PATH = "var/football.db"


def create_db_engine(db_path: str = DATABASE_PATH):
    return create_engine(f"sqlite:///{db_path}", echo=False)


def create_session(db_path: str = DATABASE_PATH):
    SessionLocal = sessionmaker(bind=create_db_engine(db_path), expire_on_commit=False)
    return SessionLocal()


def create_tables(db_path: str = DATABASE_PATH, delete_existing=True):
    if delete_existing and exists(db_path):
        logging.info(f"Removing '{db_path}'")
        remove(db_path)

    if not exists(db_path):
        Base.metadata.create_all(create_db_engine(db_path))
    else:
        logging.warning(f"{db_path} already exists, create tables abandoned")
