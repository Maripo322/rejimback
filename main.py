from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import func, select
import app_requests as rq
from models import Word, init_db, async_session 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to the Quiz API!"}

class Answer(BaseModel):
    tg_id: int
    word_id: int
    was_in_repeat: bool

class ModeAnswer(BaseModel):
    tg_id: int
    word_id: int
    selected_option: str

@app.get("/api/quiz/{tg_id}")
async def get_quiz(tg_id: int):
    user = await rq.add_user(tg_id)
    word_pack = await rq.get_random_word(user.user_id)
    return word_pack or {"error": "No words available"}

@app.get("/api/stats/{tg_id}")
async def get_stats(tg_id: int):
    user = await rq.add_user(tg_id)
    learned = await rq.get_learned_count(user.user_id)
    in_repeat = await rq.get_repeat_count(user.user_id)
    return {"learnedCount": learned, "repeatCount": in_repeat}

@app.post("/api/answer")
async def post_answer(answer: Answer):
    user = await rq.add_user(answer.tg_id)
    await rq.handle_answer(user.user_id, answer.word_id, answer.was_in_repeat)
    return {"status": "ok"}

# ============ NEW QUIZ MODES ============

# Easy Mode
@app.get("/api/quiz/easy/{tg_id}")
async def get_quiz_easy(tg_id: int):
    user = await rq.add_user(tg_id)
    quiz = await rq.get_quiz_by_difficulty(user.user_id, 1)
    return quiz or {"error": "No words of difficulty=1"}

@app.post("/api/quiz/easy/answer")
async def answer_easy(ans: ModeAnswer):
    correct = await rq.check_answer(ans.word_id, ans.selected_option)
    user = await rq.add_user(ans.tg_id)
    next_quiz = await rq.get_quiz_by_difficulty(user.user_id, 1)
    return {"correct": correct, "next": next_quiz or {}}

# Medium Mode
@app.get("/api/quiz/medium/{tg_id}")
async def get_quiz_medium(tg_id: int):
    user = await rq.add_user(tg_id)
    quiz = await rq.get_quiz_by_difficulty(user.user_id, 2)
    return quiz or {"error": "No words of difficulty=2"}

@app.post("/api/quiz/medium/answer")
async def answer_medium(ans: ModeAnswer):
    correct = await rq.check_answer(ans.word_id, ans.selected_option)
    user = await rq.add_user(ans.tg_id)
    next_quiz = await rq.get_quiz_by_difficulty(user.user_id, 2)
    return {"correct": correct, "next": next_quiz or {}}

# Hard Mode
@app.get("/api/quiz/hard/{tg_id}")
async def get_quiz_hard(tg_id: int):
    user = await rq.add_user(tg_id)
    quiz = await rq.get_quiz_by_difficulty(user.user_id, 3)
    return quiz or {"error": "No words of difficulty=3"}

@app.post("/api/quiz/hard/answer")
async def answer_hard(ans: ModeAnswer):
    correct = await rq.check_answer(ans.word_id, ans.selected_option)
    user = await rq.add_user(ans.tg_id)
    next_quiz = await rq.get_quiz_by_difficulty(user.user_id, 3)
    return {"correct": correct, "next": next_quiz or {}}

@app.get("/api/random-words/{count}")
async def get_random_words(count: int):
    async with async_session() as session:
        stmt = select(Word.word_rus).order_by(func.random()).limit(count)
        result = await session.execute(stmt)
        return [word[0] for word in result.all()]