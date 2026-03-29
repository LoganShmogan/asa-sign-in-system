# database.py — SQLite local database for the ASA Sign-in System
# All data stays on-device. DB file: asa_data.db (next to this script)

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "asa_data.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ── Schema ────────────────────────────────────────────────────────────────────

def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS members (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name      TEXT NOT NULL,
            last_name       TEXT NOT NULL,
            date_of_birth   TEXT,
            school          TEXT,
            mornings_asa    INTEGER DEFAULT 0,
            afternoons_asa  INTEGER DEFAULT 0,
            needs_pickup    INTEGER DEFAULT 0,
            activity        TEXT,
            activity_time   TEXT,
            created_at      TEXT DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS caregivers (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id               INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
            full_name               TEXT NOT NULL,
            phone                   TEXT,
            street_address          TEXT,
            suburb                  TEXT,
            city                    TEXT,
            email                   TEXT,
            emergency_contact_name  TEXT,
            emergency_contact_phone TEXT,
            relationship            TEXT DEFAULT 'Parent/Guardian'
        );

        CREATE TABLE IF NOT EXISTS sign_ins (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id   INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
            direction   TEXT NOT NULL CHECK(direction IN ('IN', 'OUT')),
            timestamp   TEXT DEFAULT (datetime('now', 'localtime')),
            notes       TEXT,
            signature   BLOB
        );

        CREATE TABLE IF NOT EXISTS notices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT,
            body        TEXT NOT NULL,
            source      TEXT DEFAULT 'facebook',
            post_id     TEXT UNIQUE,
            posted_at   TEXT,
            fetched_at  TEXT DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS admins (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT UNIQUE NOT NULL,
            password_hash   TEXT NOT NULL
        );
        """)
        # Seed default admin if none exists (password: "admin1234")
        cur = conn.execute("SELECT COUNT(*) FROM admins")
        if cur.fetchone()[0] == 0:
            h = hashlib.sha256("admin1234".encode()).hexdigest()
            conn.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                         ("admin", h))

        # Seed sample members for development
        cur = conn.execute("SELECT COUNT(*) FROM members")
        if cur.fetchone()[0] == 0:
            sample = [
                ("Jessica", "Allen",   "2015-03-12", "Central Normal School", 1, 1, 0, "Hockey",       "4:30pm, T/W/D"),
                ("Justin",  "Carter",  "2014-07-22", "Central Normal School", 0, 1, 1, "Piano Lessons", "4:35pm, T/W/D"),
                ("Jason",   "Miller",  "2013-11-05", "Hokowhitu School",      1, 1, 0, "Soccer",        "4:30pm, M/W/F"),
                ("Jasmine", "Williams","2015-09-18", "Central Normal School", 1, 0, 0, "Dance",         "5:00pm, M/W"),
                ("John",    "Zilkway", "2014-02-28", "Hokowhitu School",      0, 1, 0, "Karate",        "4:45pm, T/TH"),
            ]
            for m in sample:
                conn.execute("""INSERT INTO members
                    (first_name, last_name, date_of_birth, school,
                     mornings_asa, afternoons_asa, needs_pickup, activity, activity_time)
                    VALUES (?,?,?,?,?,?,?,?,?)""", m)


# ── Member queries ────────────────────────────────────────────────────────────

def search_members(query: str):
    """Return members whose full name contains the query string (case-insensitive)."""
    q = f"%{query}%"
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM members
            WHERE (first_name || ' ' || last_name) LIKE ?
            ORDER BY last_name, first_name
        """, (q,)).fetchall()
    return [dict(r) for r in rows]


def get_member(member_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
    return dict(row) if row else None


def get_caregiver(member_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM caregivers WHERE member_id=? LIMIT 1", (member_id,)
        ).fetchone()
    return dict(row) if row else None


def upsert_member(data: dict):
    """Insert or update a member record. Pass id=None for new records."""
    with get_conn() as conn:
        if data.get("id"):
            conn.execute("""UPDATE members SET
                first_name=:first_name, last_name=:last_name,
                date_of_birth=:date_of_birth, school=:school,
                mornings_asa=:mornings_asa, afternoons_asa=:afternoons_asa,
                needs_pickup=:needs_pickup, activity=:activity,
                activity_time=:activity_time
                WHERE id=:id""", data)
            return data["id"]
        else:
            cur = conn.execute("""INSERT INTO members
                (first_name, last_name, date_of_birth, school,
                 mornings_asa, afternoons_asa, needs_pickup, activity, activity_time)
                VALUES (:first_name,:last_name,:date_of_birth,:school,
                        :mornings_asa,:afternoons_asa,:needs_pickup,:activity,:activity_time)
                """, data)
            return cur.lastrowid


def upsert_caregiver(data: dict):
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM caregivers WHERE member_id=?", (data["member_id"],)
        ).fetchone()
        if existing:
            data["id"] = existing["id"]
            conn.execute("""UPDATE caregivers SET
                full_name=:full_name, phone=:phone, street_address=:street_address,
                suburb=:suburb, city=:city, email=:email,
                emergency_contact_name=:emergency_contact_name,
                emergency_contact_phone=:emergency_contact_phone,
                relationship=:relationship
                WHERE id=:id""", data)
        else:
            conn.execute("""INSERT INTO caregivers
                (member_id, full_name, phone, street_address, suburb, city,
                 email, emergency_contact_name, emergency_contact_phone, relationship)
                VALUES (:member_id,:full_name,:phone,:street_address,:suburb,:city,
                        :email,:emergency_contact_name,:emergency_contact_phone,:relationship)
                """, data)


def delete_member(member_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM members WHERE id=?", (member_id,))


# ── Sign-in / out ─────────────────────────────────────────────────────────────

def record_sign(member_id: int, direction: str, notes: str = "", signature: bytes = None):
    with get_conn() as conn:
        conn.execute("""INSERT INTO sign_ins (member_id, direction, notes, signature)
                        VALUES (?,?,?,?)""",
                     (member_id, direction, notes, signature))


def get_last_sign(member_id: int):
    """Return the most recent sign record for a member."""
    with get_conn() as conn:
        row = conn.execute("""SELECT * FROM sign_ins WHERE member_id=?
                              ORDER BY timestamp DESC LIMIT 1""",
                           (member_id,)).fetchone()
    return dict(row) if row else None


def get_today_signs():
    """Return all sign events from today."""
    today = datetime.now().strftime("%Y-%m-%d")
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT s.*, m.first_name, m.last_name
            FROM sign_ins s JOIN members m ON s.member_id=m.id
            WHERE s.timestamp LIKE ?
            ORDER BY s.timestamp DESC
        """, (f"{today}%",)).fetchall()
    return [dict(r) for r in rows]


# ── Notices ───────────────────────────────────────────────────────────────────

def upsert_notices(posts: list):
    """Insert/update a list of post dicts from the Facebook API."""
    with get_conn() as conn:
        for p in posts:
            conn.execute("""INSERT INTO notices (title, body, source, post_id, posted_at)
                            VALUES (:title, :body, 'facebook', :post_id, :posted_at)
                            ON CONFLICT(post_id) DO UPDATE SET
                                body=excluded.body, posted_at=excluded.posted_at,
                                fetched_at=datetime('now','localtime')
                         """, p)


def get_notices(limit: int = 10):
    with get_conn() as conn:
        rows = conn.execute("""SELECT * FROM notices
                               ORDER BY posted_at DESC LIMIT ?""", (limit,)).fetchall()
    return [dict(r) for r in rows]


# ── Auth ──────────────────────────────────────────────────────────────────────

def check_admin_password(password: str) -> bool:
    h = hashlib.sha256(password.encode()).hexdigest()
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM admins WHERE password_hash=?", (h,)).fetchone()
    return row is not None


def set_admin_password(new_password: str):
    h = hashlib.sha256(new_password.encode()).hexdigest()
    with get_conn() as conn:
        conn.execute("UPDATE admins SET password_hash=? WHERE username='admin'", (h,))
