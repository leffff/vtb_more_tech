# vtb_more_tech

## Установка

Запустите в терминале команду `pip install -r requirements.txt`

## Запуск
1. Выполните файл `init_recsys.py`
2. Выполните файл `main.py`

## Структура проекта
* main.py - Главный исполняемый файл
* parsing - инструменты сбора и обработки новостей
* catboost_models - модели рекомендации новостей для каждой категории
* svd_models - папка для моделей SVD
* recsys - модели выявления трендов и дайджестов
* sqlite_db - инструменты работы с базой данных
* config.yaml - config проекта

# Запросы на сервер
### POST:
* `/offline_training` - отправка рекомендательных моделей на дообучение
   + вызывается функция `update_all_models` из `recsys/offline_pipelines.py`, </br> 
   которая вызывает загрузку новых данных через функцию `query_new_offline_data_catboost`</br> 
   из `recsys/load_offline_data.py`. Новые модели сохраняются в `catboost_models`
* `/like/\<int:pk>/\<string:field>` - механика лайка
   + вызывается функция `set_like` из `sqlite_db/db_handler.py`, которая добавляет лайк конкретной новости в бд

### GET:
* `/buh` - получение новостей для бухгалтеров
  + вызывается функция `rank_news` из `recsys/online_pipelines.py`, </br> 
    которая вызывает загрузку новых данных через функции `parsing/parsing.py`</br> 
   `parse_clerk` и `parse_consultant`. Новости обрабатываются классами </br>
   `DigestExtractor` и `EmbeddingsExtractor` а так же скорятся по релевантности </br>
   для бухгалтеров `CatBoostWrapper` моделью.
  + Н
  + Все новые данные уходят в бд, а рекомендованные в API
   
* `/business` - получение новостей для бизнеса
    + Здесь происходит то же, что и в `/buh` только для роли бизнес