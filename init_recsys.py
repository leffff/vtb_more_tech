import os

import yaml
from transformers import T5ForConditionalGeneration, AutoTokenizer, AutoModel, RobertaTokenizerFast


def init_recsys():
    os.system(f"git lfs install")
    os.system(f"git clone https://huggingface.co/IlyaGusev/rubert_telegram_headlines")
    os.system(f"git clone https://huggingface.co/sberbank-ai/ruRoberta-large")


def init_recsys_cache():
    digest_model = T5ForConditionalGeneration.from_pretrained("IlyaGusev/rut5_base_sum_gazeta")
    digest_tokenizer = AutoTokenizer.from_pretrained(
        "IlyaGusev/rut5_base_sum_gazeta",
        do_lower_case=False,
        do_basic_tokenize=False,
        strip_accents=False
    )
    model = AutoModel.from_pretrained("sberbank-ai/ruRoberta-large")
    tokenizer = RobertaTokenizerFast.from_pretrained(
        "sberbank-ai/ruRoberta-large"
    )

with open("config.yaml") as fin:
    config = yaml.safe_load(fin)

if config["download_models_cache"]:
    init_recsys_cache()
else:
    init_recsys()