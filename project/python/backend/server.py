from flask import Flask, jsonify, request
from StateChannelBackend import StateChannelBackend
import json
import logging
import sys
import os

logging.basicConfig(level=logging.DEBUG)


st = StateChannelBackend()
app = Flask(__name__)

with open("content/content.json", "r") as f:
	content = json.load(f)


@app.route('/catalog')
def catalog():
    return jsonify({k: content[k]["price"] for k in content.keys()})


@app.route('/buy', methods=['POST'])
def buy():

	if request.method != "POST":
		return 200

	receipt = {k: v[0] for k, v in dict(request.form).items()}
	wid = receipt["wid"]
	del receipt["wid"]

	app.logger.debug("AAA")
	app.logger.debug(receipt)

	if st.receiveReceipt(receipt):
		return jsonify({"wid": wid, "access_code": content[wid]["access_code"]})
	else:
		return 200

@app.route('/watch', methods = ["POST"])
def watch():
	if request.method != "POST":
		return 200

	wid, code = request.form["wid"], request.form["access_code"]
	if content[wid]["access_code"] == code:
		with open(os.path.join("content", content[wid]["file"]), "r") as f:
			c = f.readlines()
		return jsonify({"content": "\n".join(c)})
	else:
		return 200


if __name__ == "__main__":
    app.run(debug=True)
