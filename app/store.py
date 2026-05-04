import secrets
import string

ALPHABET = string.ascii_letters + string.digits
_links: dict[str, dict] = {}


def _generate_code(length: int = 6) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def create_link(url: str) -> str:
    for _ in range(10):
        code = _generate_code()
        if code not in _links:
            _links[code] = {"url": url, "hits": 0}
            return code
    raise RuntimeError("could not generate unique code after 10 attempts")


def resolve_link(code: str) -> str | None:
    entry = _links.get(code)
    if entry is None:
        return None
    entry["hits"] += 1
    return entry["url"]


def get_all() -> list[dict]:
    return [{"code": k, **v} for k, v in _links.items()]


def _reset() -> None:
    _links.clear()
