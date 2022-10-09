import pandas as pd


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


def get_new_news(conn):
    news = conn.execute(
        """
        SELECT * FROM news WHERE date(post_date) = date('now', '-1 day')
        """
    ).fetchall()

    news = pd.DataFrame(news)

    return news


def query_new_offline_data_catboost(categories) -> tuple:
    import sqlite3
    conn = sqlite3.connect('../vtb_hack.db')
    c = conn.cursor()

    like_columns = [f"{category}" for category in categories]
    needed_columns = [f"features_{i}" for i in range(32)]

    new_news_embeddings = get_new_news(c)

    category_counts = count_samples_in_categories(c, categories)

    for i, category in enumerate(categories):
        new_news_embeddings[like_columns[i]] = int((new_news_embeddings[like_columns[i]] / category_counts[i]) > 0.5)

    return new_news_embeddings, needed_columns, like_columns
