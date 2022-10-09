from recsys.online_pipelines import rank_news
import yaml
import os

with open("config.yaml") as fin:
    config = yaml.safe_load(fin)

print(
    rank_news(
              digest_extractor_folder=config["digests"]["local_dir"],
              embedding_extractor_folder=config["embeddings"]["local_dir"],
              catboost_folder=config["catboost"]["local_dir"],
              svd_folder=config["svd"]["local_dir"]
    ), sep="\n\n"
)