from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Link


def test_shorten_returns_code_and_short_url(client: TestClient):
    resp = client.post("/shorten", json={"url": "https://example.com"})
    assert resp.status_code == 201
    data = resp.json()
    assert "code" in data
    assert "short_url" in data
    assert data["code"] in data["short_url"]


def test_shorten_code_is_six_chars(client: TestClient):
    resp = client.post("/shorten", json={"url": "https://example.com"})
    assert len(resp.json()["code"]) == 6


def test_redirect_follows_to_original_url(client: TestClient):
    resp = client.post("/shorten", json={"url": "https://example.com"})
    code = resp.json()["code"]
    redir = client.get(f"/{code}", follow_redirects=False)
    assert redir.status_code == 302
    assert "example.com" in redir.headers["location"]


def test_redirect_unknown_code_returns_404(client: TestClient):
    resp = client.get("/doesnotexist", follow_redirects=False)
    assert resp.status_code == 404


def test_shorten_rejects_non_url(client: TestClient):
    resp = client.post("/shorten", json={"url": "not-a-url"})
    assert resp.status_code == 422


def test_hit_counter_increments(client: TestClient, session: Session):
    resp = client.post("/shorten", json={"url": "https://example.com"})
    code = resp.json()["code"]
    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)
    session.expire_all()
    link = session.exec(select(Link).where(Link.code == code)).first()
    assert link.hits == 2


# ── Dashboard ─────────────────────────────────────────────────────────────────


def test_dashboard_renders(client: TestClient):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "MiniLink" in resp.text
    assert "hx-post" in resp.text


def test_dashboard_links_empty(client: TestClient):
    resp = client.get("/dashboard/links")
    assert resp.status_code == 200
    assert "No links yet" in resp.text


def test_dashboard_links_shows_entries(client: TestClient):
    client.post("/shorten", json={"url": "https://example.com"})
    resp = client.get("/dashboard/links")
    assert resp.status_code == 200
    assert "example.com" in resp.text


def test_shorten_form_creates_link(client: TestClient):
    resp = client.post("/shorten/form", data={"url": "https://example.com"})
    assert resp.status_code == 200
    assert resp.headers.get("HX-Trigger") == "linksUpdated"
    assert "localhost:8000" in resp.text  # short_url in the result HTML


def test_shorten_form_rejects_invalid_url(client: TestClient):
    resp = client.post("/shorten/form", data={"url": "not-a-url"})
    assert resp.status_code == 422
    assert "Invalid URL" in resp.text
