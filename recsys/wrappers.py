from datetime import datetime
from typing import Tuple

import joblib
import numpy as np
import pandas as pd
import torch
from catboost import CatBoostClassifier
from torch.utils.data import TensorDataset
from tqdm import tqdm
from transformers import AutoTokenizer, EncoderDecoderModel


class CatBoostWrapper:
    def __init__(self, path_to_base_model, category: str):
        self.model = CatBoostClassifier().load_model(path_to_base_model)
        self.category = category

    def update(self, new_news) -> "CatBoostWrapper":
        new_model = CatBoostClassifier(**self.model.params)
        new_model.fit(
            new_news.drop(labels=[self.category], axis=1),
            new_news[self.category],
            init_model=self.model,
        )
        self.model = new_model
        return self

    def save(self, save_folder) -> None:
        self.model.save_model(f"{save_folder}/{datetime.now()}.cbm")

    def get_scores(self, table) -> pd.DataFrame:
        scores = self.model.predict_proba(table)
        return pd.DataFrame(scores, columns=[self.category])


class BERTWrapper:
    def __init__(self, model_folder, svd_path):
        self.model = EncoderDecoderModel.from_pretrained(f"../{model_folder}", local_files_only=True)
        self.tokenizer = AutoTokenizer.from_pretrained(
            f"../{model_folder}", local_files_only=True
        )
        self.svd = joblib.load(svd_path)

    def tokenize(self, sentences: list, seq_len) -> tuple:
        input_ids = []
        attention_masks = []
        for row in tqdm(sentences):
            encoded_dict = self.tokenizer.encode_plus(
                row,
                add_special_tokens=True,
                max_length=seq_len,
                truncation=True,
                pad_to_max_length=True,
                return_attention_mask=True,
                return_tensors="pt",
            )

            input_ids.append(encoded_dict["input_ids"])

            attention_masks.append(encoded_dict["attention_mask"])

        input_ids = torch.cat(input_ids, dim=0)
        attention_masks = torch.cat(attention_masks, dim=0)
        return input_ids, attention_masks

    def get_dataloader(self, input_ids, attention_masks):
        dataset = TensorDataset(input_ids, attention_masks)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=1)

        return dataloader

    def get_digest(self, input_ids, attention_mask) -> list:
        output_ids = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=64,
            no_repeat_ngram_size=3,
            num_beams=3,
            top_p=0.95
        )[0]

        digests = []
        for el in output_ids:
            digest = self.tokenizer.decode(el, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            digests.append(digest)

        return digests

    def get_trend(self, input_ids, attention_mask) -> list:
        output_ids = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=16,
            no_repeat_ngram_size=3,
            num_beams=5,
            top_p=0.95
        )[0]

        trends = []
        for el in output_ids:
            trend = self.tokenizer.decode(el, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            trends.append(trend)

        return trends

    def get_embeddings(self, input_ids, attention_mask) -> np.ndarray:
        self.model.eval()
        with torch.no_grad():
            embeddings = self.model.encoder(
                input_ids=input_ids,
                attention_mask=attention_mask
            ).cpu().numpy()

        embeddings = self.svd.transform(embeddings)

        return embeddings

    def process_parsed_data(self, data: pd.DataFrame) -> Tuple[list, list, pd.DataFrame]:
        input_ids, attention_masks = self.tokenize(data["full_text"], 60)

        digests = self.get_digest(input_ids, attention_masks)
        trends = self.get_trend(input_ids, attention_masks)

        embeddings = pd.DataFrame(self.get_embeddings(input_ids, attention_masks),
                                  columns=[f"feature_{i}" for i in range(32)])

        return digests, trends, embeddings
