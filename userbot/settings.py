"""Userbot sozlamalari — JSON faylda saqlanadi (qayta start'da yo'qolmaydi)."""
import json
import os

SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "userbot_settings.json"
)

_DEFAULTS = {"target_bot": "@funstat"}


def _load() -> dict:
    if not os.path.exists(SETTINGS_PATH):
        return dict(_DEFAULTS)
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in _DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(_DEFAULTS)


def _save(data: dict) -> None:
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_target_bot() -> str:
    return _load().get("target_bot") or _DEFAULTS["target_bot"]


def set_target_bot(username: str) -> str:
    username = (username or "").strip()
    # t.me/xxx yoki https://t.me/xxx dan username ajratish
    if "t.me/" in username:
        username = username.split("t.me/", 1)[1].strip("/")
    username = "@" + username.lstrip("@")
    data = _load()
    data["target_bot"] = username
    _save(data)
    return username
