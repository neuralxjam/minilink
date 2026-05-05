import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import app.cache as cache_module
import app.db as db_module
from app.db import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    monkeypatch.setattr(
        cache_module,
        "_redis",
        fakeredis.FakeRedis(decode_responses=True),
    )


@pytest.fixture(name="client")
def client_fixture(session: Session, monkeypatch):
    monkeypatch.setattr(db_module, "create_db_and_tables", lambda: None)
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()
