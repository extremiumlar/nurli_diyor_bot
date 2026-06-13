import json
import sqlite3
from typing import Any, Dict, Optional

from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType


class SQLiteFSMStorage(BaseStorage):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fsm_storage (
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                state  TEXT,
                data   TEXT NOT NULL DEFAULT '{}',
                PRIMARY KEY (chat_id, user_id)
            )
        """)
        conn.commit()
        conn.close()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _key(self, key: StorageKey):
        return key.chat_id, key.user_id

    async def set_state(self, key: StorageKey, state: StateType = None):
        state_str = state.state if state else None
        chat_id, user_id = self._key(key)
        conn = self._conn()
        conn.execute("""
            INSERT INTO fsm_storage (chat_id, user_id, state, data)
            VALUES (?, ?, ?, '{}')
            ON CONFLICT (chat_id, user_id) DO UPDATE SET state = excluded.state
        """, (chat_id, user_id, state_str))
        conn.commit()
        conn.close()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        chat_id, user_id = self._key(key)
        conn = self._conn()
        row = conn.execute(
            "SELECT state FROM fsm_storage WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        ).fetchone()
        conn.close()
        return row[0] if row else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]):
        chat_id, user_id = self._key(key)
        data_str = json.dumps(data, ensure_ascii=False)
        conn = self._conn()
        conn.execute("""
            INSERT INTO fsm_storage (chat_id, user_id, state, data)
            VALUES (?, ?, NULL, ?)
            ON CONFLICT (chat_id, user_id) DO UPDATE SET data = excluded.data
        """, (chat_id, user_id, data_str))
        conn.commit()
        conn.close()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        chat_id, user_id = self._key(key)
        conn = self._conn()
        row = conn.execute(
            "SELECT data FROM fsm_storage WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        ).fetchone()
        conn.close()
        if row and row[0]:
            return json.loads(row[0])
        return {}

    async def close(self):
        pass
