from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.radar.storage.models import Base

def get_engine(db_url: str):
    return create_engine(db_url)

def init_db(db_url: str):
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
