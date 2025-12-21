from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from typing import Optional, Tuple
from datetime import datetime, timedelta
from config import Config

Base = declarative_base()

class Mapping(Base):
    __tablename__ = 'mappings'
    
    slug = Column(String, primary_key=True)
    tmdb_id = Column(String)
    imdb_id = Column(String, index=True)

class FailedMapping(Base):
    __tablename__ = 'failed_mappings'
    
    imdb_id = Column(String, primary_key=True)
    checked_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self):
        if Config.DB_TYPE == 'postgresql':
            engine = create_engine(
                Config.DB_CONNECTION_STRING,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args=connect_args
            )
        else:
            engine = create_engine(
                f'sqlite:///{Config.DB_PATH}',
                pool_size=5,
                max_overflow=10
            )
        
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
    
    def is_failed_mapping(self, imdb_id: str, ttl_days: int = 30) -> bool:
        session = self.Session()
        try:
            failed = session.query(FailedMapping).filter_by(imdb_id=imdb_id).first()
            if not failed:
                return False
            # Check if expired
            if datetime.utcnow() - failed.checked_at > timedelta(days=ttl_days):
                session.delete(failed)
                session.commit()
                return False
            return True
        finally:
            session.close()
    
    def add_failed_mapping(self, imdb_id: str):
        session = self.Session()
        try:
            failed = session.query(FailedMapping).filter_by(imdb_id=imdb_id).first()
            if failed:
                failed.checked_at = datetime.utcnow()
            else:
                failed = FailedMapping(imdb_id=imdb_id)
                session.add(failed)
            session.commit()
        finally:
            session.close()

# Global database instance
db = Database()
