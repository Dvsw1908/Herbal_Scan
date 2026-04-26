import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "predictions.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path       TEXT    NOT NULL,
                predicted_class  TEXT    NOT NULL,
                confidence_score REAL    NOT NULL,
                timestamp        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_prediction(image_path: str, predicted_class: str, confidence_score: float) -> int:
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO predictions (image_path, predicted_class, confidence_score)
            VALUES (?, ?, ?)
            """,
            (image_path, predicted_class, round(confidence_score, 4)),
        )
        conn.commit()
        return cur.lastrowid


def get_all_predictions() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, image_path, predicted_class, confidence_score, timestamp
            FROM predictions
            ORDER BY id DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]


def delete_prediction(prediction_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute(
            "DELETE FROM predictions WHERE id = ?", (prediction_id,)
        )
        conn.commit()
        return cur.rowcount > 0
