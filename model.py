import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()
        self.table_name = "telephone_book"
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                        name TEXT,
                        number TEXT,
                        comment TEXT
                        )
        """)

    def add_entry(self, name: str, number: str, comment: str):
        self.cursor.execute(f"INSERT INTO {self.table_name} (name, number, comment) VALUES (?, ?, ?)",
                            (name, number, comment))
        self.conn.commit()

    def delete_entry(self, id: int):
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE ROWID = ?", (id,))
        self.conn.commit()

    def vacuum(self):
        self.cursor.execute("VACUUM")
        self.conn.commit()

    def change_entry(self, id: int, field: str, change_to: str):
        self.cursor.execute(f"UPDATE {self.table_name} SET {field} = ? WHERE ROWID = ?", (change_to, id))
        self.conn.commit()

    def get_contacts(self) -> list[tuple[int, str, str, str]]:
        self.cursor.execute(f"SELECT ROWID, * FROM {self.table_name}")
        return self.cursor.fetchall()

    def search(self, keyword: str, name_only: bool = False) -> list[tuple[int, str, str, str]]:
        keyword_pattern = f"%{keyword}%"

        if not name_only:
            query = f"""SELECT ROWID, * FROM {self.table_name}
                    WHERE name LIKE ? COLLATE NOCASE 
                    OR number LIKE ? COLLATE NOCASE 
                    OR comment LIKE ? COLLATE NOCASE
            """
            self.cursor.execute(query, (keyword_pattern, keyword_pattern, keyword_pattern))
        else:
            query = f"""SELECT ROWID, * FROM {self.table_name}
                       WHERE name LIKE ? COLLATE NOCASE
            """
            self.cursor.execute(query, (keyword_pattern,))

        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
