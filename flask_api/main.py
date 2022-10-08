from flask import Flask

app = Flask(__name__)


@app.route("/buh", methods=["GET"])
def buh_news():
    return "buh news"


@app.route("/business", methods=["GET"])
def business_news():
    return "business news"


if __name__ == "__main__":
    app.config["WTF_CSRF_ENABLED"] = False
    app.run(debug=True)
