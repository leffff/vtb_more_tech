import datetime

import numpy as np
import pandas as pd
from sqlalchemy.orm import load_only

from db.db_setup import AsyncSessionLocal, async_get_db
from db.models.user import News, User
from category_config import categories


def count_samples_in_categories(conn, categories):
    category_counts = []
    n_category = conn.execute(
        f"""
        SELECT category, COUNT(category) from users GROUP BY category 
        """
    ).fetchall()
    print(n_category)

    for i in range(len(categories)):
        category_counts.append(n_category[1][i])

    return category_counts


def get_new_news(conn, columns):
    news = conn.execute(
        """
        SELECT * FROM news WHERE date(post_date) = date('now', '-1 day')
        """
    ).fetchall()

    news = pd.DataFrame(news)

    return news


def query_new_offline_data_catboost(conn) -> tuple:
    like_columns = [f"{category}_likes" for category in categories]
    needed_columns = [f"features_{i}" for i in range(32)]

    new_news_embeddings = get_new_news(conn, needed_columns + like_columns)

    category_counts = count_samples_in_categories(conn, categories)

    for i, category in enumerate(categories):
        new_news_embeddings[like_columns[i]] /= category_counts[i]

    return new_news_embeddings, needed_columns, like_columns


import sqlite3
conn = sqlite3.connect('../vtb_hack.db')
c = conn.cursor()
print(get_new_news(c, []))