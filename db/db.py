import sqlite3
def initialize(path):
    conn = sqlite3.connect(path)
    return conn
