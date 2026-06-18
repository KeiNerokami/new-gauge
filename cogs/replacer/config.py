import sqlite3
from pathlib import Path

DB = Path("cogs/databases/replacer.db")


class ReplaceDB:

    def __init__(self):

        self.conn = sqlite3.connect(
            DB,
            check_same_thread=False
        )

        self.conn.row_factory = sqlite3.Row

        self.create_tables()


    def create_tables(self):

        cur = self.conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS replacements(
            guild_id TEXT,
            word TEXT COLLATE NOCASE,
            replacement TEXT,

            PRIMARY KEY(
                guild_id,
                word
            )
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            guild_id TEXT PRIMARY KEY,

            enabled INTEGER
            DEFAULT 1,

            bypass_role TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS channels(
            guild_id TEXT,
            channel_id TEXT,

            PRIMARY KEY(
                guild_id,
                channel_id
            )
        )
        """)

        self.conn.commit()


    def ensure_guild(
        self,
        guild_id: int
    ):

        self.conn.execute("""
        INSERT OR IGNORE
        INTO settings(
            guild_id
        )
        VALUES(?)
        """,
        (
            str(guild_id),
        ))

        self.conn.commit()


    def get_replacements(
        self,
        guild_id: int
    ):

        self.ensure_guild(
            guild_id
        )

        rows = self.conn.execute("""
        SELECT
            word,
            replacement

        FROM replacements

        WHERE guild_id=?
        """,
        (
            str(guild_id),
        )).fetchall()

        return {
            r["word"]:
            r["replacement"]

            for r in rows
        }


    def add_replacement(
        self,
        guild_id,
        word,
        replacement
    ):

        self.conn.execute("""
        INSERT OR REPLACE
        INTO replacements
        VALUES(
            ?,
            ?,
            ?
        )
        """,
        (
            str(guild_id),
            word,
            replacement
        ))

        self.conn.commit()


    def remove_replacement(
        self,
        guild_id,
        word
    ):

        cur = self.conn.execute("""
        DELETE
        FROM replacements

        WHERE
        guild_id=?
        AND
        word=?
        """,
        (
            str(guild_id),
            word
        ))

        self.conn.commit()

        return cur.rowcount > 0


    def clear_replacements(
        self,
        guild_id
    ):

        cur = self.conn.execute("""
        DELETE
        FROM replacements

        WHERE guild_id=?
        """,
        (
            str(guild_id),
        ))

        self.conn.commit()

        return cur.rowcount


    def get_channels(
        self,
        guild_id
    ):

        rows = self.conn.execute("""
        SELECT
        channel_id

        FROM channels

        WHERE guild_id=?
        """,
        (
            str(guild_id),
        )).fetchall()

        return [
            r["channel_id"]
            for r in rows
        ]


    def add_channel(
        self,
        guild_id,
        channel_id
    ):

        existing = self.get_channels(
            guild_id
        )

        if channel_id in existing:
            return "duplicate"

        if len(existing) >= 10:
            return "limit"

        self.conn.execute("""
        INSERT
        INTO channels

        VALUES(
            ?,
            ?
        )
        """,
        (
            str(guild_id),
            str(channel_id)
        ))

        self.conn.commit()

        return "added"


    def remove_channel(
        self,
        guild_id,
        channel_id
    ):

        cur = self.conn.execute("""
        DELETE
        FROM channels

        WHERE
        guild_id=?
        AND
        channel_id=?
        """,
        (
            str(guild_id),
            str(channel_id)
        ))

        self.conn.commit()

        return cur.rowcount > 0


    def clear_channels(
        self,
        guild_id
    ):

        cur = self.conn.execute("""
        DELETE
        FROM channels

        WHERE guild_id=?
        """,
        (
            str(guild_id),
        ))

        self.conn.commit()

        return cur.rowcount


    def enabled(
        self,
        guild_id
    ):

        self.ensure_guild(
            guild_id
        )

        row = self.conn.execute("""
        SELECT enabled

        FROM settings

        WHERE guild_id=?
        """,
        (
            str(guild_id),
        )).fetchone()

        return bool(
            row["enabled"]
        )


    def toggle(
        self,
        guild_id
    ):

        state = (
            not self.enabled(
                guild_id
            )
        )

        self.conn.execute("""
        UPDATE settings

        SET enabled=?

        WHERE guild_id=?
        """,
        (
            int(state),
            str(guild_id)
        ))

        self.conn.commit()

        return state


    def set_bypass_role(
        self,
        guild_id,
        role_id
    ):

        self.conn.execute("""
        UPDATE settings

        SET bypass_role=?

        WHERE guild_id=?
        """,
        (
            str(role_id),
            str(guild_id)
        ))

        self.conn.commit()


    def get_bypass_role(
        self,
        guild_id
    ):

        self.ensure_guild(
            guild_id
        )

        row = self.conn.execute("""
        SELECT bypass_role

        FROM settings

        WHERE guild_id=?
        """,
        (
            str(guild_id),
        )).fetchone()

        return (
            row["bypass_role"]
            if row
            else None
        )


    def clear_bypass_role(
        self,
        guild_id
    ):

        self.conn.execute("""
        UPDATE settings

        SET bypass_role=NULL

        WHERE guild_id=?
        """,
        (
            str(guild_id),
        ))

        self.conn.commit()


db = ReplaceDB()
