import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

PG_URL = 'postgresql+psycopg2://user:password@localhost:5433/weather_db'
MYSQL_URL = 'mysql+pymysql://user:password@localhost:3306/weather_db'

DATABASE_URL = os.getenv('DB_URL', PG_URL)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_session_for_url(url: str):
    custom_engine = create_engine(url, echo=False)
    CustomSession = sessionmaker(autocommit=False, autoflush=False, bind=custom_engine)
    return CustomSession(), custom_engine