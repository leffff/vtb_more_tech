import os

def init_recsys():
    os.system(f"git lfs install")
    os.system(f"git clone https://huggingface.co/IlyaGusev/rubert_telegram_headlines")
    os.system(f"git clone https://huggingface.co/sberbank-ai/ruRoberta-large")

init_recsys()