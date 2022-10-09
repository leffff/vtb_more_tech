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

# Пример работы api для `/buh`
{
    "title":{</br>
        "11":"Штраф за неуплату НДФЛ можно снизить или вообще добиться его отмены",</br>
        "27":"Пациентов с рекуррентным депрессивным расстройством будут лечить по новому стандарту",</br>
        "34":"Утвердили стандарт помощи при варикозном расширении вен на ногах"</br>
    },</br>
    "full_text":{</br>
        "11":"Обсуждение затеяли наши подписчики в канале «Красный уголок бухгалтера».\nУ компании не было денег на счете, и поэтому НДФЛ перечислили с опозданием. Налоговики оштрафовали фирму на 34 тыс. рублей.\nКоллеги советуют писать ходатайство о снижении штрафа. Аргументы — нарушение совершено впервые, финансовое положение компании тяжелое, ущерб государству не нанесен.\nКоллеги советуют ссылаться на п.3 статьи 114 НК, по которому при наличии хотя бы одного смягчающего ответственность обстоятельства размер штрафа подлежит уменьшению как минимум в 2 раза.\nВпрочем, есть еще п. 2 ст. 123 НК, по которому штрафа вообще можно избежать.\nЕсли налоговый агент сам уплатил долг по НДФЛ и пени по нему до того, как претензии по неуплате предъявили налоговики, то штрафа не будет.\nРазъяснение по этой норме есть в письме ФНС от 02.08.2022 № ЕА-4-15\/10852@.\nВ этом письме ФНС сетует, что налоговики выносят необоснованные решения о штрафах и нарушают права и законные интересы налогоплательщиков.\nПоэтому ФНС дала поручение налоговикам на местах проверять, уплачен ли налог и пени на момент составления акта. Если уплата есть, то штрафа быть не должно.",</br>
        "27":"Стандарт медпомощи взрослым при рекуррентном депрессивном расстройстве надо применять с 16 октября. Он регулирует оказание экстренной, неотложной и плановой помощи амбулаторно и в стационаре (в т.ч. дневном). Заболевание исключили из действующих стандартов по депрессии.\nНа этапе диагностики, помимо психиатра, пациента могут проконсультировать невролог, терапевт, окулист, гинеколог, психолог. По показаниям делают лабораторные и инструментальные исследования:\nПри лечении проводят групповую психообразовательную работу с больным и его родственниками. При необходимости назначают психотерапию, транскраниальную магнитную стимуляцию, электросудорожную терапию. В редких случаях возможна имплантация программируемой системы в область блуждающего нерва.\nСписок лекарств включает амитриптилин, кломипрамин, пароксетин, сертралин, агомелатин, вортиоксетин и др.\nКлинические рекомендации по данному заболеванию надо применять с 1 января 2023 года.\n",</br>
        "34":"16 октября вступает в силу стандарт диагностики и лечения варикозного расширения вен нижних конечностей у взрослых. Он регулирует оказание первичной медико-санитарной и специализированной помощи амбулаторно и в стационаре (в т.ч. дневном). Утратят силу стандарты специализированной помощи при варикозном расширении вен на ногах с язвой (воспалением) и при остром восходящем тромбофлебите большой или малой подкожных вен.\nЗаболевание диагностирует хирург. Могут сделать УЗДГ сосудов ног, дуплексное сканирование вен нижних конечностей.\nНа этапе лечения пациента осматривает физиотерапевт. При необходимости проводят оперативные вмешательства: удаление поверхностных вен, разрез, иссечение и закрытие вен ног и др. Среди немедикаментозных методов используют:\nПеречень лекарств включает гесперидин + диосмин, сульфатиазол серебра, кетопрофен и пр.\nКлинические рекомендации по данному заболеванию нужно применять с 1 января 2023 года.\n"</br>
    },</br>
    "link":{</br>
        "11":"https:\/\/www.klerk.ru\/buh\/news\/537137\/",</br>
        "27":"https:\/\/www.consultant.ru\/legalnews\/20536\/",</br>
        "34":"https:\/\/www.consultant.ru\/legalnews\/20527\/"</br>
    },</br>
    "post_date":{</br>
        "11":"2022-10-09",</br>
        "27":"2022-10-7",</br>
        "34":"2022-10-7"</br>
    },</br>
    "trend":{</br>
        "11":"НДФЛ",</br>
        "27":"Изменения-2022, Медорганизации, Требования к оказанию медпомощи",</br>
        "34":"Изменения-2022, Медорганизации, Требования к оказанию медпомощи"</br>
    },</br>
    "digest":{</br>
        "11":"Налоговики оштрафовали фирму на тыс рублей и штрафовали ее на тысячу рублей Коллеги советуют писать ходатайство о снижении штрафа Если налоговый агент сам уплатил долг по НДФЛ и пени по ",</br>
        "27":"Рекуррентное депрессивное расстройство исключили из действующих стандартов медпомощи взрослым при рекуррентном депрессивном расстройстве С октября они регулируют оказание экстренной неотложной и плановой помощи в т ч дневном",</br>
        "34":"В октябре вступает в силу стандарт диагностики и лечения варикозного расширения вен нижних конечностей у взрослых Вступает во внимание стандарт специализированной помощи при варикозном расширении вен на ногах и при остр"</br>
        }</br>
}