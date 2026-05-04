import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_store():
    store._reset()
    yield
    store._reset()


def test_shorten_returns_code_and_short_url():
    resp = client.post("/shorten", json={"url": "https://example.com"})
    assert resp.status_code == 201
    data = resp.json()
    assert "code" in data
    assert "short_url" in data
    assert data["code"] in data["short_url"]


def test_shorten_code_is_six_chars():
    resp = client.post("/shorten", json={"url": "https://example.com"})
    assert len(resp.json()["code"]) == 6


def test_redirect_follows_to_original_url():
    resp = client.post("/shorten", json={"url": "https://example.com"})
    code = resp.json()["code"]
    redir = client.get(f"/{code}", follow_redirects=False)
    assert redir.status_code == 302
    assert "example.com" in redir.headers["location"]


def test_redirect_unknown_code_returns_404():
    resp = client.get("/doesnotexist", follow_redirects=False)
    assert resp.status_code == 404


def test_shorten_rejects_non_url():
    resp = client.post("/shorten", json={"url": "not-a-url"})
    assert resp.status_code == 422


def test_hit_counter_increments():
    resp = client.post("/shorten", json={"url": "https://example.com"})
    code = resp.json()["code"]
    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)
    entry = store.get_all()[0]
    assert entry["hits"] == 2
