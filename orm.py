import sqlite3


class Database:
    def __init__(self, path: str):
        self.connection = sqlite3.Connection(path)

    @property
    def tables(self):
        return []
