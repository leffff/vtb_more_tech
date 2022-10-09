from flask import Flask

from init_recsys import init_recsys_cache
from recsys.online_pipelines import rank_news
from recsys.offline_pipelines import update_all_models
from sqlite_db.db_handler import put_data, first_db_creation, set_like

first_db_creation()
app = Flask(__name__)


@app.route("/buh", methods=["GET"])
def buh_news():
    news, _, to_db = rank_news()
    put_data(to_db)
    return news


@app.route("/business", methods=["GET"])
def business_news():
    _, news, to_db = rank_news()
    put_data(to_db)
    return news.to_json()


@app.route("/like/<int:pk>/<string:field>", methods=["POST"])
def like(pk: int, field: str):
    set_like(pk, field)


@app.route("/offline_training", methods=["POST"])
def offline_training():
    update_all_models("catboost_models/")


if __name__ == "__main__":
    # init_recsys_cache()
    app.config["WTF_CSRF_ENABLED"] = False
    app.run(debug=True)
