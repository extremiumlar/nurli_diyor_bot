from __future__ import annotations

import json
from typing import Any, Iterable, Optional

import aiosqlite

from nb_adminsbot.config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS channels (
    chat_id      INTEGER PRIMARY KEY,
    title        TEXT NOT NULL,
    username     TEXT,
    added_by     INTEGER NOT NULL,
    added_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS channel_admins (
    chat_id      INTEGER NOT NULL,
    user_id      INTEGER NOT NULL,
    PRIMARY KEY (chat_id, user_id),
    FOREIGN KEY (chat_id) REFERENCES channels(chat_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS posts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id         INTEGER NOT NULL,
    message_id      INTEGER NOT NULL,
    author_id       INTEGER NOT NULL,
    reactions_json  TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(chat_id, message_id)
);

CREATE TABLE IF NOT EXISTS reaction_clicks (
    post_id   INTEGER NOT NULL,
    user_id   INTEGER NOT NULL,
    emoji     TEXT NOT NULL,
    PRIMARY KEY (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);
"""


_conn: Optional[aiosqlite.Connection] = None


async def init_db(db_path: str = None) -> None:
    global _conn
    path = db_path or settings.db_path
    _conn = await aiosqlite.connect(path)
    _conn.row_factory = aiosqlite.Row
    await _conn.executescript(SCHEMA)
    await _conn.commit()


async def close_db() -> None:
    global _conn
    if _conn is not None:
        await _conn.close()
        _conn = None


def db() -> aiosqlite.Connection:
    if _conn is None:
        raise RuntimeError("DB ulanishi ochilmagan. init_db() ni chaqiring.")
    return _conn


# ---------- Channels ----------

async def upsert_channel(chat_id: int, title: str, username: Optional[str], added_by: int) -> None:
    await db().execute(
        """INSERT INTO channels (chat_id, title, username, added_by)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(chat_id) DO UPDATE SET title=excluded.title, username=excluded.username""",
        (chat_id, title, username, added_by),
    )
    await db().commit()


async def remove_channel(chat_id: int) -> None:
    await db().execute("DELETE FROM channels WHERE chat_id = ?", (chat_id,))
    await db().commit()


async def get_channel(chat_id: int) -> Optional[aiosqlite.Row]:
    async with db().execute("SELECT * FROM channels WHERE chat_id = ?", (chat_id,)) as cur:
        return await cur.fetchone()


# ---------- Channel admins (cache) ----------

async def set_channel_admins(chat_id: int, user_ids: Iterable[int]) -> None:
    await db().execute("DELETE FROM channel_admins WHERE chat_id = ?", (chat_id,))
    await db().executemany(
        "INSERT OR IGNORE INTO channel_admins (chat_id, user_id) VALUES (?, ?)",
        [(chat_id, uid) for uid in user_ids],
    )
    await db().commit()


async def list_channels_for_user(user_id: int) -> list[aiosqlite.Row]:
    async with db().execute(
        """SELECT c.* FROM channels c
           JOIN channel_admins a ON a.chat_id = c.chat_id
           WHERE a.user_id = ?
           ORDER BY c.title COLLATE NOCASE""",
        (user_id,),
    ) as cur:
        return await cur.fetchall()


async def is_user_channel_admin(chat_id: int, user_id: int) -> bool:
    async with db().execute(
        "SELECT 1 FROM channel_admins WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id),
    ) as cur:
        return await cur.fetchone() is not None


# ---------- Posts (for reaction tracking) ----------

async def create_post(chat_id: int, message_id: int, author_id: int, reactions: list[str]) -> int:
    cur = await db().execute(
        "INSERT INTO posts (chat_id, message_id, author_id, reactions_json) VALUES (?, ?, ?, ?)",
        (chat_id, message_id, author_id, json.dumps(reactions, ensure_ascii=False)),
    )
    await db().commit()
    return cur.lastrowid or 0


async def get_post(chat_id: int, message_id: int) -> Optional[aiosqlite.Row]:
    async with db().execute(
        "SELECT * FROM posts WHERE chat_id = ? AND message_id = ?",
        (chat_id, message_id),
    ) as cur:
        return await cur.fetchone()


async def toggle_reaction(post_id: int, user_id: int, emoji: str) -> dict[str, Any]:
    async with db().execute(
        "SELECT emoji FROM reaction_clicks WHERE post_id = ? AND user_id = ?",
        (post_id, user_id),
    ) as cur:
        row = await cur.fetchone()
    current = row["emoji"] if row else None

    if current == emoji:
        await db().execute(
            "DELETE FROM reaction_clicks WHERE post_id = ? AND user_id = ?",
            (post_id, user_id),
        )
        user_pick: Optional[str] = None
    else:
        await db().execute(
            """INSERT INTO reaction_clicks (post_id, user_id, emoji)
               VALUES (?, ?, ?)
               ON CONFLICT(post_id, user_id) DO UPDATE SET emoji=excluded.emoji""",
            (post_id, user_id, emoji),
        )
        user_pick = emoji

    await db().commit()

    async with db().execute(
        "SELECT emoji, COUNT(*) AS cnt FROM reaction_clicks WHERE post_id = ? GROUP BY emoji",
        (post_id,),
    ) as cur:
        rows = await cur.fetchall()

    counts = {r["emoji"]: r["cnt"] for r in rows}
    return {"counts": counts, "user_pick": user_pick}


async def get_reaction_counts(post_id: int) -> dict[str, int]:
    async with db().execute(
        "SELECT emoji, COUNT(*) AS cnt FROM reaction_clicks WHERE post_id = ? GROUP BY emoji",
        (post_id,),
    ) as cur:
        rows = await cur.fetchall()
    return {r["emoji"]: r["cnt"] for r in rows}
