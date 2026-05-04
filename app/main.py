import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import AnyHttpUrl, BaseModel

from .store import create_link, resolve_link

app = FastAPI(title="MiniLink", version="0.1.0")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


class ShortenRequest(BaseModel):
    url: AnyHttpUrl


class ShortenResponse(BaseModel):
    code: str
    short_url: str


@app.post("/shorten", response_model=ShortenResponse, status_code=201)
def shorten(body: ShortenRequest) -> ShortenResponse:
    code = create_link(str(body.url))
    return ShortenResponse(code=code, short_url=f"{BASE_URL}/{code}")


@app.get("/{code}")
def redirect(code: str) -> RedirectResponse:
    url = resolve_link(code)
    if url is None:
        raise HTTPException(status_code=404, detail="short code not found")
    return RedirectResponse(url=url, status_code=302)
