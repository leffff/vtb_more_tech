from datetime import datetime
from typing import Tuple

import joblib
import numpy as np
import pandas as pd
import torch
from catboost import CatBoostClassifier
from torch.utils.data import TensorDataset
from tqdm import tqdm
from transformers import AutoTokenizer, T5ForConditionalGeneration, RobertaTokenizerFast, AutoModel

from recsys.utils import preprocess


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
        scores = self.model.predict_proba(table)[:, 1]
        return pd.DataFrame(scores, columns=[self.category])


class DigestExtractor:
    def __init__(self, download_models_cache, model_folder):
        if download_models_cache:
            self.model = T5ForConditionalGeneration.from_pretrained("IlyaGusev/rut5_base_sum_gazeta")
            self.tokenizer = AutoTokenizer.from_pretrained(
                "IlyaGusev/rut5_base_sum_gazeta",
                do_lower_case=False,
                do_basic_tokenize=False,
                strip_accents=False
            )
        else:
            self.model = T5ForConditionalGeneration.from_pretrained(model_folder, local_files_only=True)
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_folder, local_files_only=True,
                do_lower_case=False,
                do_basic_tokenize=False,
                strip_accents=False
            )
    def tokenize(self, sentences: list, seq_len) -> tuple:
        input_ids = []
        attention_masks = []
        for row in tqdm(list(sentences)):
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

    def get_digest(self, data: pd.DataFrame) -> pd.DataFrame:
        input_ids, attention_masks = self.tokenize(data["full_text"].apply(preprocess), 256)
        digests = []

        for i in tqdm(range(len(input_ids))):
            output_ids = self.model.generate(
                input_ids=torch.unsqueeze(input_ids[i], 0),
                attention_mask=torch.unsqueeze(attention_masks[i], 0),
                max_length=64,
                no_repeat_ngram_size=3,
                num_beams=3,
                top_p=0.9
            )[0].detach().cpu().numpy()

            digest = self.tokenizer.decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            digests.append(digest)

        return pd.DataFrame(data={"digest": digests})


class EmbeddingExtractor:
    def __init__(self, download_models_cache, model_folder, svd_path):
        if download_models_cache:
            self.model = AutoModel.from_pretrained("sberbank-ai/ruRoberta-large")
            self.tokenizer = RobertaTokenizerFast.from_pretrained(
                "sberbank-ai/ruRoberta-large"
            )
        else:
            self.model = AutoModel.from_pretrained(model_folder, local_files_only=True)
            self.tokenizer = RobertaTokenizerFast.from_pretrained(
                model_folder, local_files_only=True
            )
        with open(svd_path, "rb") as fin:
            self.svd = joblib.load(fin)

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

    def get_embeddings(self, data: pd.DataFrame) -> pd.DataFrame:
        input_ids, attention_masks = self.tokenize(data["full_text"].apply(preprocess), 128)

        embeddings = []
        self.model.eval()
        with torch.no_grad():
            for i in tqdm(range(len(input_ids))):
                output = self.model(
                    input_ids=torch.unsqueeze(input_ids[i], 0),
                    attention_mask=torch.unsqueeze(attention_masks[i], 0)
                )["pooler_output"].detach().cpu().numpy()

                embeddings.append(output)

        embeddings = np.vstack(embeddings)
        svd_embeddings = self.svd.transform(embeddings)

        return pd.DataFrame(svd_embeddings, columns=[f"feature_{i}" for i in range(32)])

