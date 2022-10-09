import sqlite3

import pandas
from pandas import DataFrame

from os import getenv


# Первое создание базы данных
'''
Первое создание базы данных.
return {"result": "ok"}
return {"result": "database already exists"}
return {"result": "unknown error"}
'''


def first_db_creation():
    with sqlite3.connect("../vtb_hack.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                       user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                       category VARCHAR(30) NOT NULL)
                       """
        )
        request = f"""
            CREATE TABLE IF NOT EXISTS news (
                       news_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                       title TEXT NOT NULL,
                       full_text TEXT NOT NULL,
                       link TEXT NOT NULL,
                       post_date DATE NOT NULL,
                       trend TEXT NOT NULL, 
                       digest TEXT NOT NULL,
                       insight TEXT NOT NULL,
                       """ + \
                ', '.join([f"feature_{i} REAL  NOT NULL" for i in range(32)]) + ", " + \
                  """
                  buh_likes INTEGER NOT NULL,
                 business_likes INTEGER NOT NULL)
                  """


        cursor.execute(
            request
        )

        conn.commit()
        return {"status": "ok"}


def put_data(data: DataFrame) -> None:
    with sqlite3.connect("../vtb_hack.db") as conn:
        cursor = conn.cursor()
        data = data.to_numpy()
        for row in data:
            row[1] = row[1].replace('\"', '\"\"')
            row[2] = row[2].replace('\"', '\"\"')
            args = ('\"' + str(item) + '\"' for item in row)
            print(args)
            cursor.execute(f"INSERT INTO news VALUES ({', '.join(args)})")


def set_like(news_id: int, field: str):
    with sqlite3.connect("../vtb_hack.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE news SET {field}_likes={field}_likes+1 WHERE news_id={news_id}")

