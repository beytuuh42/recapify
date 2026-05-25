import hashlib
import json
from pathlib import Path
from typing import Optional

_CACHE_DIR = Path(__file__).parent / ".cache"


def _key(title: str, season: int, episode: int, language: str) -> str:
    raw = f"{title.lower()}|{season}|{episode}|{language.lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def read(title: str, season: int, episode: int, language: str) -> Optional[dict]:
    path = _CACHE_DIR / f"{_key(title, season, episode, language)}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def write(title: str, season: int, episode: int, language: str, data: dict) -> None:
    _CACHE_DIR.mkdir(exist_ok=True)
    path = _CACHE_DIR / f"{_key(title, season, episode, language)}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
