import sqlite3
from datetime import datetime, timezone


def upsert(
    conn: sqlite3.Connection,
    account_id: int,
    kwh: float,
    peak: bool,
    total: float,
    run_id: int | None,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO account_last_success(account_id, kwh, peak, total, run_id, success_at)
        VALUES (?,?,?,?,?,?)
        ON CONFLICT(account_id) DO UPDATE SET
            kwh=excluded.kwh,
            peak=excluded.peak,
            total=excluded.total,
            run_id=excluded.run_id,
            success_at=excluded.success_at
        """,
        (account_id, kwh, 1 if peak else 0, total, run_id, now),
    )
    conn.commit()


def get(conn: sqlite3.Connection, account_id: int) -> dict | None:
    row = conn.execute(
        """
        SELECT account_id, kwh, peak, total, run_id, success_at
        FROM account_last_success WHERE account_id=?
        """,
        (account_id,),
    ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["peak"] = bool(d["peak"])
    return d


def delete(conn: sqlite3.Connection, account_id: int) -> None:
    conn.execute("DELETE FROM account_last_success WHERE account_id=?", (account_id,))
    conn.commit()
