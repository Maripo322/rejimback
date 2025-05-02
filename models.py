from sqlalchemy import ForeignKey, String, BigInteger, func, select
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)  

class Word(Base):
    __tablename__ = 'words'
    word_id : Mapped[int] = mapped_column(primary_key=True)
    word_eng : Mapped[str] = mapped_column(String(64)) 
    word_rus : Mapped[str] = mapped_column(String(64))
    word_difficulty : Mapped[int] = mapped_column()

class Repeat(Base):
    __tablename__ = 'repeat'
    repeat_id : Mapped[int] = mapped_column(primary_key=True)
    word_id : Mapped[int] = mapped_column(ForeignKey('words.word_id'))
    user_id : Mapped[int] = mapped_column(ForeignKey('users.user_id'))

class Studied(Base):
    __tablename__ = 'studied'
    studied_id : Mapped[int] = mapped_column(primary_key=True)
    word_id : Mapped[int] = mapped_column(ForeignKey('words.word_id'))
    user_id : Mapped[int] = mapped_column(ForeignKey('users.user_id'))

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)