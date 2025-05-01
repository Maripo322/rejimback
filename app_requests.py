from sqlalchemy import select, delete, func
import random
from models import async_session, User, Word, Repeat, Studied

async def add_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

async def get_random_word(user_id):
    async def get_count(subquery):
        return await session.scalar(select(func.count()).select_from(subquery))
    
    async with async_session() as session:
        repeat_words = select(Repeat.word_id).where(Repeat.user_id == user_id)
        studied_words = select(Studied.word_id).where(Studied.user_id == user_id)
        excluded_words = repeat_words.union(studied_words)

        categories = []
        weights = []

        repeat_count = await get_count(repeat_words)
        if repeat_count > 0:
            categories.append("repeat")
            weights.append(0.1)

        for difficulty in [1, 2, 3]:
            query = select(Word.word_id).where(
                Word.word_difficulty == difficulty,
                ~Word.word_id.in_(excluded_words)
            )
            count = await get_count(query)
            if count > 0:
                categories.append(f"d{difficulty}")
                weights.append(0.3)

        if not categories:
            return None

        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        chosen_category = random.choices(categories, weights=normalized_weights, k=1)[0]

        if chosen_category == "repeat":
            stmt = select(Word).join(Repeat).where(
                Repeat.user_id == user_id
            ).order_by(func.random()).limit(1)
        else:
            difficulty = int(chosen_category[1])
            stmt = select(Word).where(
                Word.word_difficulty == difficulty,
                ~Word.word_id.in_(excluded_words)
            ).order_by(func.random()).limit(1)

        word = await session.scalar(stmt)
        if not word:
            return None

        return {
            "word_id": word.word_id,
            "word_eng": word.word_eng,
            "word_rus": word.word_rus,
            "was_in_repeat": chosen_category == "repeat"
        }

async def handle_answer(user_id, word_id, was_in_repeat):
    async with async_session() as session:
        if was_in_repeat:
            await session.execute(
                delete(Repeat).where(
                    Repeat.user_id == user_id,
                    Repeat.word_id == word_id
                )
            )
            if not await session.scalar(select(Studied).where(
                Studied.user_id == user_id,
                Studied.word_id == word_id
            )):
                session.add(Studied(user_id=user_id, word_id=word_id))
        else:
            if not await session.scalar(select(Repeat).where(
                Repeat.user_id == user_id,
                Repeat.word_id == word_id
            )):
                session.add(Repeat(user_id=user_id, word_id=word_id))
        await session.commit()

async def get_learned_count(user_id):
    async with async_session() as session:
        return await session.scalar(
            select(func.count(Studied.studied_id)).where(Studied.user_id == user_id)
        )

async def get_repeat_count(user_id):
    async with async_session() as session:
        return await session.scalar(
            select(func.count(Repeat.repeat_id)).where(Repeat.user_id == user_id)
        )

# ============ NEW QUIZ MODES ============

async def get_quiz_by_difficulty(user_id: int, difficulty: int):
    async with async_session() as session:
        stmt_word = select(Word).where(Word.word_difficulty == difficulty).order_by(func.random()).limit(1)
        word = await session.scalar(stmt_word)
        if not word:
            return None

        stmt_distr = (
            select(Word.word_rus)
            .where(Word.word_id != word.word_id)
            .order_by(func.random())
            .limit(3)
        )
        rows = await session.execute(stmt_distr)
        distractors = [r[0] for r in rows.fetchall()]

        options = distractors + [word.word_rus]
        random.shuffle(options)

        return {
            "word_id": word.word_id,
            "word_eng": word.word_eng,
            "options": options
        }

async def check_answer(word_id: int, selected_option: str) -> bool:
    async with async_session() as session:
        word = await session.get(Word, word_id)
        if not word:
            return False
        return word.word_rus == selected_option
