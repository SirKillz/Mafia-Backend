import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

class Database:
    def __init__(self):
        user = os.getenv("DATABASE_USERNAME")
        password = os.getenv("DATABASE_PASSWORD")
        host = os.getenv("DATABASE_HOST")
        port = int(os.getenv("DATABASE_PORT", "5432"))
        name = os.getenv("DATABASE_NAME")
        sslmode = os.getenv("DATABASE_SSLMODE")

        self.url = URL.create(
            "postgresql+psycopg",
            username=user,
            password=password,  # raw password; URL.create escapes it correctly
            host=host,
            port=port,
            database=name,
            query={"sslmode": sslmode} if sslmode else {},
        )

    def get_engine(self):
        return create_engine(
            self.url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
        )
