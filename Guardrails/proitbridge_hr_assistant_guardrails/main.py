import traceback
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.access.permissions import can_see_all_records
from src.audit.guard_log import clear_events, read_events
from src.auth.users import DEMO_USERS, current_user, sign_in, sign_out
from src.core.config import FRONTEND_DIR, MODEL, has_api_key
from src.runner.guarded_runner import ask_hr_with_guardrails, compare_users, user_card, warm_up


@asynccontextmanager
async def lifespan(app):
    try:
        warm_up()
    except Exception as error:
        print(f"Warm-up skipped: {error}")
    yield


app = FastAPI(title="PROITBRIDGE HR Assistant · Guardrails", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class SignIn(BaseModel):
    user_id: str


class Question(BaseModel):
    question: str


def signed_in_user(authorization):
    user = current_user(authorization.removeprefix("Bearer ").strip())
    if user is None:
        raise HTTPException(status_code=401, detail="Please sign in first.")
    return user


def check_ready(question):
    if not has_api_key():
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is missing. Add it to the .env file and restart the app.")
    if not question.strip():
        raise HTTPException(status_code=400, detail="Please type a question.")


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/status")
def status():
    return {"has_api_key": has_api_key(), "model": MODEL}


@app.get("/api/users")
def users():
    return [user_card(user) for user in DEMO_USERS.values()]


@app.post("/api/login")
def login(body: SignIn):
    token = sign_in(body.user_id)
    if token is None:
        raise HTTPException(status_code=404, detail="Unknown demo user.")
    return {"token": token, "user": user_card(DEMO_USERS[body.user_id])}


@app.get("/api/me")
def me(authorization: str = Header(default="")):
    return user_card(signed_in_user(authorization))


@app.post("/api/logout")
def logout(authorization: str = Header(default="")):
    sign_out(authorization.removeprefix("Bearer ").strip())
    return {"signed_out": True}


@app.post("/api/ask")
def ask(body: Question, authorization: str = Header(default="")):
    user = signed_in_user(authorization)
    check_ready(body.question)
    try:
        return ask_hr_with_guardrails(user, body.question)
    except Exception as error:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"The HR Assistant could not answer: {error}")


@app.post("/api/compare")
def compare(body: Question, authorization: str = Header(default="")):
    signed_in_user(authorization)
    check_ready(body.question)
    try:
        return compare_users(body.question)
    except Exception as error:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"The HR Assistant could not answer: {error}")


@app.get("/api/audit")
def audit(authorization: str = Header(default="")):
    user = signed_in_user(authorization)
    if can_see_all_records(user.role):
        return read_events()
    return read_events(user_id=user.user_id)


@app.delete("/api/audit")
def reset_audit(authorization: str = Header(default="")):
    user = signed_in_user(authorization)
    if not can_see_all_records(user.role):
        raise HTTPException(status_code=403, detail="Only HR Admin can clear the log.")
    clear_events()
    return read_events()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
