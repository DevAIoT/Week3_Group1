"""SQLite storage for gesture ratings."""

import sqlite3
from datetime import datetime, timezone


class RatingsDatabase:
    """SQLite-backed storage for 1-5 ratings."""

    def __init__(self, db_path="ratings.db"):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._create_table()
        self.socketio = None

    def _create_table(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'gesture'
            )
        """)
        self._conn.commit()

    def set_socketio(self, socketio):
        """Set SocketIO instance for event emission."""
        self.socketio = socketio

    def insert(self, rating, source="gesture"):
        """Insert a rating (1-5). Returns the new row id."""
        ts = datetime.now(timezone.utc).isoformat()
        cursor = self._conn.execute(
            "INSERT INTO ratings (rating, timestamp, source) VALUES (?, ?, ?)",
            (rating, ts, source),
        )
        self._conn.commit()
        row_id = cursor.lastrowid

        # Emit WebSocket event if connected
        if self.socketio:
            self.socketio.emit('new_rating', {
                'id': row_id,
                'rating': rating,
                'timestamp': ts,
                'source': source
            })

        return row_id

    def get_all(self, limit=100, offset=0):
        """Return ratings as list of dicts, newest first."""
        rows = self._conn.execute(
            "SELECT id, rating, timestamp, source FROM ratings "
            "ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_summary(self):
        """Return aggregate stats: count, average, min, max."""
        row = self._conn.execute(
            "SELECT COUNT(*) as count, "
            "AVG(rating) as average, "
            "MIN(rating) as min, "
            "MAX(rating) as max "
            "FROM ratings"
        ).fetchone()
        return {
            "count": row["count"],
            "average": round(row["average"], 2) if row["average"] else None,
            "min": row["min"],
            "max": row["max"],
        }

    def close(self):
        self._conn.close()
