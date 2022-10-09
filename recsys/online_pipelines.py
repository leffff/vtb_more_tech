import os

import numpy as np
import pandas as pd

from parsing.parsing import parse_clerk, parse_consultant
from recsys.wrappers import DigestExtractor, CatBoostWrapper, EmbeddingExtractor


def rank_news(digest_extractor_folder="rubert_telegram_headlines",
              embedding_extractor_folder="",
              catboost_folder="catboost_models",
              svd_folder="svd_models") -> tuple:
    news_parsed = []
    for parser in [parse_clerk, parse_consultant]:
        news_parsed.append(parser())

    news = pd.concat(news_parsed).dropna().reset_index(drop=True)

    digest_model = DigestExtractor(digest_extractor_folder)
    embeddings_model = EmbeddingExtractor(embedding_extractor_folder, f"{svd_folder}/{os.listdir(svd_folder)[-1]}")

    scorers = []
    for sub_folder in os.listdir(catboost_folder):
        full_sub_folder = f"{catboost_folder}/{sub_folder}"
        scorers.append(CatBoostWrapper(f"{full_sub_folder}/{os.listdir(full_sub_folder)[-1]}",
                                       sub_folder.split("_")[0]))

    digests = digest_model.get_digest(news).reset_index(drop=True)
    embeddings = embeddings_model.get_embeddings(news).reset_index(drop=True)
    insights = pd.DataFrame(data={"insights": ["AAAA"] * news.shape[0]})

    scores = [cbc.get_scores(embeddings).reset_index(drop=True) for cbc in scorers]

    buh_news = pd.concat([news, digests, scores[0]], axis=1)
    business_news = pd.concat([news, digests, scores[1]], axis=1)

    likes = pd.DataFrame(
        data={
            "buh_likes": np.zeros(news.shape[0]),
            "business_likes": np.zeros(news.shape[0])
        }
    )

    to_db = pd.concat([news, digests, insights, embeddings, likes], axis=1)

    return buh_news, business_news, to_db
