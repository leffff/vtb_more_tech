import sqlite3

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
            CREATE TABLE users (
                       user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                       category VARCHAR(30) NOT NULL)
                       """
        )
        request = f"""
            CREATE TABLE news (
                       news_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                       title TEXT NOT NULL,
                       full_text TEXT NOT NULL,
                       link TEXT NOT NULL,
                       post_date DATE NOT NULL,
                       digest TEXT NOT NULL,
                       trend TEXT NOT NULL, 
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

print(first_db_creation())
