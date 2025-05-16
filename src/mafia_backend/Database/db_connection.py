import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Database:

    def __init__(self):
        DATABASE_USER = os.getenv("DATABASE_USERNAME")
        DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
        DATABASE_HOST = os.getenv("DATABASE_HOST")
        DATABASE_PORT = os.getenv("DATABASE_PORT")
        DATABASE_NAME = os.getenv("DATABASE_NAME")

        if os.environ['ENV'] == 'test':
            DATABASE_HOST = "localhost"

        self.connection_string = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

        self.engine = create_engine(self.connection_string)

        # Create a session factory
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)