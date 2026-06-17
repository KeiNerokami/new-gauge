import sqlite3
import argparse
from pathlib import Path


DB = Path(
    "cogs/databases/replacer.db"
)


def connect():

    db = sqlite3.connect(
        DB
    )

    db.row_factory = (
        sqlite3.Row
    )

    return db


def ensure():

    db = connect()

    db.execute("""
    CREATE TABLE IF NOT EXISTS replacements(

        id INTEGER
        PRIMARY KEY
        AUTOINCREMENT,

        word TEXT
        UNIQUE,

        replacement TEXT
    )
    """)

    db.commit()

    db.close()


def add(
    word,
    replacement
):

    db = connect()

    try:

        db.execute("""
        INSERT INTO replacements(
            word,
            replacement
        )

        VALUES(
            ?,
            ?
        )
        """,
        (
            word,
            replacement
        ))

        db.commit()

        print(
            f"Added: {word} → {replacement}"
        )

    except sqlite3.IntegrityError:

        print(
            "Word already exists."
        )

    db.close()


def show():

    db = connect()

    rows = db.execute("""
    SELECT
        id,
        word,
        replacement

    FROM replacements

    ORDER BY id
    """).fetchall()

    db.close()

    if not rows:

        print(
            "No words."
        )

        return

    print()

    for r in rows:

        print(
            f"[{r['id']}] "
            f"{r['word']} "
            f"→ "
            f"{r['replacement']}"
        )

    print()


def delete(
    idx
):

    db = connect()

    cur = db.execute("""
    DELETE
    FROM replacements

    WHERE id=?
    """,
    (
        idx,
    ))

    db.commit()

    db.close()

    if cur.rowcount:

        print(
            "Deleted."
        )

    else:

        print(
            "Index not found."
        )


def edit(
    idx,
    word,
    replacement
):

    db = connect()

    cur = db.execute("""
    UPDATE replacements

    SET
        word=?,
        replacement=?

    WHERE id=?
    """,
    (
        word,
        replacement,
        idx
    ))

    db.commit()

    db.close()

    if cur.rowcount:

        print(
            "Updated."
        )

    else:

        print(
            "Index not found."
        )


def main():

    ensure()

    parser = argparse.ArgumentParser(
        prog="words.py",
        description=
        "SQLite word injector"
    )

    parser.add_argument(
        "word",
        nargs="?"
    )

    parser.add_argument(
        "replacement",
        nargs="?"
    )

    parser.add_argument(
        "-l",
        "--list",

        action="store_true"
    )

    parser.add_argument(
        "-D",
        "--delete",

        type=int
    )

    parser.add_argument(
        "-e",
        "--edit",

        nargs=3,

        metavar=(
            "INDEX",
            "WORD",
            "REPLACEMENT"
        )
    )

    args = (
        parser.parse_args()
    )

    if args.list:

        show()

        return


    if args.delete is not None:

        delete(
            args.delete
        )

        return


    if args.edit:

        edit(
            int(
                args.edit[0]
            ),

            args.edit[1],

            args.edit[2]
        )

        return


    if (
        args.word
        and
        args.replacement
    ):

        add(
            args.word,
            args.replacement
        )

        return


    parser.print_help()


if __name__ == "__main__":

    main()
