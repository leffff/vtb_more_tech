import os

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

    news = pd.concat(news_parsed)

    digest_model = DigestExtractor(digest_extractor_folder)
    embeddings_model = EmbeddingExtractor(embedding_extractor_folder, f"{svd_folder}/{os.listdir(svd_folder)[-1]}")

    scorers = []
    for sub_folder in os.listdir(catboost_folder):
        scorers.append(CatBoostWrapper(f"{catboost_folder}/{sub_folder}/{os.listdir(sub_folder)[-1]}",
                                       sub_folder.split("_")[0]))

    digests = digest_model.get_digest(news)
    embeddings = embeddings_model.get_embeddings(news)

    scores = [cbc.get_scores(embeddings) for cbc in scorers]

    buh_news = pd.concat([news, digests, scores[0][:, 1]], axis=1)
    business_news = pd.concat([news, digests, scores[1][:, 1]], axis=1)

    to_db = pd.concat([news, digests, embeddings], axis=1)

    return buh_news, business_news, to_db
