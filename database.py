import sqlite3 as sq
# import asyncpg
# import aiosqlite


class Database:

    def __init__(self, db_name="chat.db"):
        self.path_to_db = db_name

    @property
    def connection(self):
        return sq.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()

        connection = self.connection
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        if commit:
            connection.commit()
        connection.close()

        return data

    def create_table(self):
        sql = ("CREATE TABLE IF NOT EXISTS Chat(id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, name TEXT, "
               "content TEXT)")
        self.execute(sql, commit=True)

    def create_ad_sets_table(self):
        sql = """CREATE TABLE IF NOT EXISTS ad_metrics(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        adset_id TEXT NOT NULL,
        adset_name TEXT,
        campaign_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        spend REAL,
        impressions INTEGER,
        clicks INTEGER,
        leads INTEGER,
        cr REAL,
        cpl REAL,
        ctr REAL,
        cpm REAL);"""
        self.execute(sql, commit=True)

    def create_table_status(self):
        sql = ("CREATE TABLE IF NOT EXISTS status(campaign_id TEXT, campaign_name TEXT, adset_id TEXT, adset_name TEXT,"
               "status TEXT, date_stop TEXT)")
        self.execute(sql, commit=True)

    def insert_into(self, role: str, content: str):
        sql = "INSERT OR IGNORE INTO Chat(role, content) VALUES (?, ?)"
        parameters = (role, content)
        self.execute(sql, parameters=parameters, commit=True)

    def insert_into_with_func(self, role: str, name: str, content: str):
        sql = "INSERT OR IGNORE INTO Chat(role, name, content) VALUES (?, ?, ?)"
        parameters = (role, name, content)
        self.execute(sql, parameters=parameters, commit=True)

    def insert_into_status_table(self, params):
        sql = ("INSERT OR IGNORE INTO status(campaign_id, campaign_name, adset_id, adset_name, status) "
               "VALUES (?, ?, ?, ?, ?)")
        self.execute(sql, parameters=params, commit=True)

    def get_chat(self):
        sql = "SELECT * FROM Chat ORDER BY id ASC"
        data = self.execute(sql, fetchall=True)
        return data

    def insert_ad_metrics(self, params):
        sql = """INSERT OR IGNORE INTO ad_metrics(
        adset_id,
        adset_name,
        campaign_id,
        timestamp,
        spend,
        impressions,
        clicks,
        leads,
        cr,
        cpl,
        ctr,
        cpm) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.execute(sql, parameters=params, commit=True)

    def get_metrics(self, campaign_id):
        sql = """SELECT * FROM ad_metrics WHERE campaign_id=? ORDER BY adset_id ASC"""
        data = self.execute(sql, (campaign_id,), fetchall=True)
        return data

    def get_campaigns(self):
        sql = "SELECT campaign_id, campaign_name FROM status"
        return self.execute(sql, fetchall=True)


db = Database()
# db.create_table_status()
# db.create_table()
# db.create_ad_sets_table()
