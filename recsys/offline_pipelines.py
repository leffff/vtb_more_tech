import os

from recsys.load_offline_data import query_new_offline_data_catboost
from recsys.wrappers import CatBoostWrapper


def catboost_train_pipeline(model_folder: str, category, data) -> None:
    path_to_init_model = f"{model_folder}/{os.listdir(model_folder)[-1]}"
    cbc = CatBoostWrapper(path_to_init_model, category=category)

    cbc.update(data)
    cbc.save(model_folder)


def update_all_models(global_model_folder, categories) -> None:
    category_models = os.listdir(global_model_folder)
    new_news, feature_cols, target_cols = query_new_offline_data_catboost(categories=categories)

    for sum_model_folder in category_models:
        category = sum_model_folder.split("_")[0]
        target_col = [col for col in target_cols if col.split("_")[0].startswith(category)][0]

        catboost_train_pipeline(f"{global_model_folder}/{sum_model_folder}",
                                category,
                                new_news[feature_cols + [target_col]])
