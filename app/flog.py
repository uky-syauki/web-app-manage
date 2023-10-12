import sqlite3

class LOG:
    con = sqlite3.connect('log.db')
    cursor = con.cursor()
    def rec(self, data):
        self.cursor.execute()