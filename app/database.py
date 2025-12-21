from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Optional, Tuple
from config import Config

Base = declarative_base()

class Mapping(Base):
    __tablename__ = 'mappings'
    
    slug = Column(String, primary_key=True)
    tmdb_id = Column(String)
    imdb_id = Column(String, index=True)

class Database:
    def __init__(self):
        if Config.DB_TYPE == 'postgresql':
            engine = create_engine(Config.DB_CONNECTION_STRING)
        else:
            engine = create_engine(f'sqlite:///{Config.DB_PATH}')
        
        Base.metadata.create_all(engine)
        session_factory = sessionmaker(bind=engine)
        self.Session = scoped_session(session_factory)
    
    def get_mapping(self, slug: str) -> Optional[Tuple[str, str]]:
        session = self.Session()
        try:
            mapping = session.query(Mapping).filter_by(slug=slug).first()
            return (mapping.tmdb_id, mapping.imdb_id) if mapping else None
        finally:
            session.close()
    
    def get_slug_by_imdb(self, imdb_id: str) -> Optional[str]:
        session = self.Session()
        try:
            mapping = session.query(Mapping).filter_by(imdb_id=imdb_id).first()
            return mapping.slug if mapping else None
        finally:
            session.close()
    
    def set_mapping(self, slug: str, tmdb_id: str, imdb_id: str):
        session = self.Session()
        try:
            mapping = session.query(Mapping).filter_by(slug=slug).first()
            if mapping:
                mapping.tmdb_id = tmdb_id
                mapping.imdb_id = imdb_id
            else:
                mapping = Mapping(slug=slug, tmdb_id=tmdb_id, imdb_id=imdb_id)
                session.add(mapping)
            session.commit()
        finally:
            session.close()

# Global database instance
db = Database()
