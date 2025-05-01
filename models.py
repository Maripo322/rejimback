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


    async with async_session() as session:
        word_count = await session.scalar(select(func.count(Word.word_id)))
        if word_count == 0:
            initial_words = [
                {"word_eng": "dog", "word_rus": "собака", "word_difficulty": 1},
                {"word_eng": "tree", "word_rus": "дерево", "word_difficulty": 1},
                {"word_eng": "book", "word_rus": "книга", "word_difficulty": 2},
                {"word_eng": "phone", "word_rus": "телефон", "word_difficulty": 2},
                {"word_eng": "friend", "word_rus": "друг", "word_difficulty": 1},
                {"word_eng": "sun", "word_rus": "солнце", "word_difficulty": 1},
                {"word_eng": "moon", "word_rus": "луна", "word_difficulty": 2},
                {"word_eng": "water", "word_rus": "вода", "word_difficulty": 2},
                {"word_eng": "fire", "word_rus": "огонь", "word_difficulty": 2},
                {"word_eng": "mountain", "word_rus": "гора", "word_difficulty": 2},
                {"word_eng": "river", "word_rus": "река", "word_difficulty": 2},
                {"word_eng": "flower", "word_rus": "цветок", "word_difficulty": 1},
                {"word_eng": "bird", "word_rus": "птица", "word_difficulty": 1},
                {"word_eng": "fish", "word_rus": "рыба", "word_difficulty": 1},
                {"word_eng": "sky", "word_rus": "небо", "word_difficulty": 1},
                {"word_eng": "star", "word_rus": "звезда", "word_difficulty": 2},
                {"word_eng": "cloud", "word_rus": "облако", "word_difficulty": 2},
                {"word_eng": "rain", "word_rus": "дождь", "word_difficulty": 1},
                {"word_eng": "snow", "word_rus": "снег", "word_difficulty": 3},
                {"word_eng": "wind", "word_rus": "ветер", "word_difficulty": 3},
                {"word_eng": "forest", "word_rus": "лес", "word_difficulty": 2},
                {"word_eng": "ocean", "word_rus": "океан", "word_difficulty": 3},
                {"word_eng": "island", "word_rus": "остров", "word_difficulty": 2},
                {"word_eng": "beach", "word_rus": "пляж", "word_difficulty": 2},
                {"word_eng": "desert", "word_rus": "пустыня", "word_difficulty": 3},
                {"word_eng": "lake", "word_rus": "озеро", "word_difficulty": 2},
                {"word_eng": "garden", "word_rus": "сад", "word_difficulty": 2},
                {"word_eng": "field", "word_rus": "поле", "word_difficulty": 3},
                {"word_eng": "hill", "word_rus": "холм", "word_difficulty": 3},
                {"word_eng": "valley", "word_rus": "долина", "word_difficulty": 3},         
            ]
            for word_data in initial_words:
                session.add(Word(**word_data))
            await session.commit()