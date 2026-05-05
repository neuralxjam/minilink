import os
import secrets
import string
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import AnyHttpUrl, BaseModel
from sqlalchemy import update as sa_update
from sqlmodel import Session, select

from .cache import cache_del, cache_get, cache_set
from .db import create_db_and_tables, get_session
from .models import Link

ALPHABET = string.ascii_letters + string.digits
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def _generate_code(length: int = 6) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def _unique_code(session: Session) -> str:
    for _ in range(10):
        code = _generate_code()
        if not session.exec(select(Link).where(Link.code == code)).first():
            return code
    raise RuntimeError("could not generate unique code after 10 attempts")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="MiniLink", version="0.1.0", lifespan=lifespan)


class ShortenRequest(BaseModel):
    url: AnyHttpUrl


class ShortenResponse(BaseModel):
    code: str
    short_url: str


@app.post("/shorten", response_model=ShortenResponse, status_code=201)
def shorten(
    body: ShortenRequest, session: Session = Depends(get_session)
) -> ShortenResponse:
    code = _unique_code(session)
    link = Link(code=code, url=str(body.url))
    session.add(link)
    session.commit()
    cache_set(code, link.url)  # write-through
    return ShortenResponse(code=code, short_url=f"{BASE_URL}/{code}")


@app.get("/{code}")
def redirect(code: str, session: Session = Depends(get_session)) -> RedirectResponse:
    url = cache_get(code)

    if url is None:
        # cache miss — fetch from DB and warm the cache
        link = session.exec(select(Link).where(Link.code == code)).first()
        if link is None:
            raise HTTPException(status_code=404, detail="short code not found")
        cache_set(code, link.url)
        url = link.url
    else:
        # cache hit — verify the code still exists (handles deleted links)
        exists = session.exec(select(Link.id).where(Link.code == code)).first()
        if exists is None:
            cache_del(code)
            raise HTTPException(status_code=404, detail="short code not found")

    # increment hits without a full SELECT on the hot path
    session.execute(sa_update(Link).where(Link.code == code).values(hits=Link.hits + 1))
    session.commit()
    return RedirectResponse(url=url, status_code=302)
