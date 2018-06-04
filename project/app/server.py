import logging

from flask import Flask, jsonify, request

from backend.Server import Server

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

sr = Server()

@app.route("/catalog")
def catalog():
    return jsonify({k: sr.content[k]["price"] for k in sr.content.keys()})


@app.route("/maintenance")
def maintenance():
    sr.performMaintenanceUserAccounts()
    return "200"


@app.route("/buy", methods=["POST"])
def buy():
    if request.method != "POST":
        return "403"

    receipt = {k: v[0] for k, v in dict(request.form).items()}
    wid = receipt["wid"]
    del receipt["wid"]

    resp = sr.approveBuy(wid, receipt)
    if resp:
        return jsonify(resp)
    else:
        return "404"


@app.route("/watch", methods=["POST"])
def watch():
    if request.method != "POST":
        return "403"

    wid, code = request.form["wid"], request.form["access_code"]
    resp = sr.showContent(wid, code)

    if resp:
        return jsonify(resp)
    else:
        return "404"


if __name__ == "__main__":
    app.run(debug=True)
