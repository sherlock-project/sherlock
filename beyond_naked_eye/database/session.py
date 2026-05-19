from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from beyond_naked_eye.config import SETTINGS
from beyond_naked_eye.database.models import Base

engine = create_engine(SETTINGS.database_url, future=True)
SessionLocal = sessionmaker(engine, class_=Session, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
