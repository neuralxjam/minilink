import os
import secrets
import string
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import AnyHttpUrl, BaseModel, TypeAdapter, ValidationError
from sqlalchemy import update as sa_update
from sqlmodel import Session, select

from .cache import cache_del, cache_get, cache_set
from .db import create_db_and_tables, get_session
from .models import Link

ALPHABET = string.ascii_letters + string.digits
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

_url_adapter = TypeAdapter(AnyHttpUrl)


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


# ── JSON API ──────────────────────────────────────────────────────────────────


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
    cache_set(code, link.url)
    return ShortenResponse(code=code, short_url=f"{BASE_URL}/{code}")


@app.get("/{code}")
def redirect(code: str, session: Session = Depends(get_session)) -> RedirectResponse:
    url = cache_get(code)

    if url is None:
        link = session.exec(select(Link).where(Link.code == code)).first()
        if link is None:
            raise HTTPException(status_code=404, detail="short code not found")
        cache_set(code, link.url)
        url = link.url
    else:
        exists = session.exec(select(Link.id).where(Link.code == code)).first()
        if exists is None:
            cache_del(code)
            raise HTTPException(status_code=404, detail="short code not found")

    session.execute(sa_update(Link).where(Link.code == code).values(hits=Link.hits + 1))
    session.commit()
    return RedirectResponse(url=url, status_code=302)


# ── Dashboard ─────────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/dashboard/links", response_class=HTMLResponse)
def dashboard_links(
    request: Request, session: Session = Depends(get_session)
) -> HTMLResponse:
    links = session.exec(select(Link).order_by(Link.hits.desc()).limit(20)).all()
    return templates.TemplateResponse(request, "_links.html", {"links": links})


@app.post("/shorten/form", response_class=HTMLResponse, include_in_schema=False)
def shorten_form(
    request: Request,
    url: str = Form(...),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    try:
        validated_url = str(_url_adapter.validate_python(url))
    except ValidationError:
        return HTMLResponse(
            '<p class="text-sm text-red-500">'
            "Invalid URL — include the scheme, e.g. https://example.com"
            "</p>",
            status_code=422,
        )

    code = _unique_code(session)
    link = Link(code=code, url=validated_url)
    session.add(link)
    session.commit()
    cache_set(code, link.url)

    short_url = f"{BASE_URL}/{code}"
    html = (
        '<div class="flex items-center gap-2 text-sm">'
        '<span class="text-green-600 font-medium">&#10003; Created:</span>'
        f'<a href="{short_url}" target="_blank"'
        ' class="text-indigo-600 hover:underline font-mono">'
        f"{short_url}</a>"
        '<button onclick="navigator.clipboard.writeText(\''
        f"{short_url}"
        '\')" class="text-xs text-gray-500 hover:text-gray-700 border'
        ' border-gray-200 rounded px-2 py-0.5 ml-1">Copy</button>'
        "</div>"
    )
    response = HTMLResponse(content=html)
    response.headers["HX-Trigger"] = "linksUpdated"
    return response
