from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import urllib
from Config import constants

from sqlalchemy import MetaData

conn = f"""Driver={constants.DRIVER};Server=tcp:{constants.SERVER},1433;Database={constants.DATABASE};Uid={constants.USER_NAME};Pwd={constants.PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""

params = urllib.parse.quote_plus(conn)
conn_str = "mssql+aioodbc:///?autocommit=true&odbc_connect={}".format(params)
# conn_str = 'sqlite+aiosqlite:///./async_chill_out.db'

engine = create_async_engine(conn_str, connect_args={"check_same_thread": False, "charset": "UTF-8"})

AsyncSessionLocal = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()

async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        print("database connection trying close")
        await session.close()
        print("database connection closed")
    
metadata = MetaData()

async def reflect_tables():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.reflect)