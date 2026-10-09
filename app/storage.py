import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path: str):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                source TEXT NOT NULL,
                title TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY,
                document_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            );
            """
        )
        self.connection.commit()

    def clear(self):
        self.connection.execute("DELETE FROM chunks")
        self.connection.execute("DELETE FROM documents")
        self.connection.commit()

    def add_document(self, source: str, title: str, chunks: list[str]):
        cursor = self.connection.execute(
            "INSERT INTO documents(source, title) VALUES (?, ?)",
            (source, title),
        )
        document_id = cursor.lastrowid

        self.connection.executemany(
            """
            INSERT INTO chunks(document_id, chunk_index, content)
            VALUES (?, ?, ?)
            """,
            [
                (document_id, index, chunk)
                for index, chunk in enumerate(chunks)
            ],
        )
        self.connection.commit()

    def search(self, terms: list[str], limit: int = 3):
        if not terms:
            return []

        conditions = " OR ".join("c.content LIKE ?" for _ in terms)
        parameters = [f"%{term}%" for term in terms]

        rows = self.connection.execute(
            f"""
            SELECT
                c.id,
                c.chunk_index,
                c.content,
                d.source,
                d.title
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE {conditions}
            """,
            parameters,
        ).fetchall()

        results = []
        for row in rows:
            text = row["content"].lower()
            score = sum(text.count(term.lower()) for term in terms)
            results.append({
                "id": row["id"],
                "chunk_index": row["chunk_index"],
                "content": row["content"],
                "source": row["source"],
                "title": row["title"],
                "score": score,
            })

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:limit]

    def stats(self):
        document_count = self.connection.execute(
            "SELECT COUNT(*) FROM documents"
        ).fetchone()[0]
        chunk_count = self.connection.execute(
            "SELECT COUNT(*) FROM chunks"
        ).fetchone()[0]

        return {
            "documents": document_count,
            "chunks": chunk_count,
        }

    def close(self):
        self.connection.close()