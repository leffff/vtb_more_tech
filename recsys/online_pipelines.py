import os

import pandas as pd

from parsing.parsing import parse_clerk, parse_consultant
from wrappers import BERTWrapper, CatBoostWrapper


def rank_news(lm_folder="rubert_telegram_headlines",
              catboost_folder="catboost_models",
              svd_path="svd_models") -> tuple:
    news_parsed = []
    for parser in [parse_clerk, parse_consultant]:
        news_parsed.append(parser())

    news = pd.concat(news_parsed)

    bert = BERTWrapper(lm_folder, svd_path)
    scorers = []
    for sub_folder in os.listdir(catboost_folder):
        scorers.append(CatBoostWrapper(f"{sub_folder}/{os.listdir(sub_folder)[-1]}",
                                       sub_folder.split("_")[0]))

    digests, trends, embeddings = bert.process_parsed_data(news)

    scores = [cbc.get_scores(embeddings) for cbc in scorers]

    # FIX: automate hardcode
    buh_news = pd.concat([news, digests, trends, scores[0][:, 1]], axis=1)
    business_news = pd.concat([news, digests, trends, scores[1][:, 1]], axis=1)

    to_db = pd.concat([news, digests, trends, embeddings], axis=1)

    return buh_news, business_news, to_db
