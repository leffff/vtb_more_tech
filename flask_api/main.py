from flask import Flask
from recsys.online_pipelines import rank_news
from sqlite_db.db_handler import put_data, first_db_creation

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


if __name__ == "__main__":
    app.config["WTF_CSRF_ENABLED"] = False
    app.run(debug=True)
