from flask import Flask, redirect, url_for
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root_dir():
	#print("<h1>Redirecting to the valid URL --- root dir is empty</h1>")
	print("Redirecting to the valid URL --- root dir is empty")
	return redirect(url_for("say_name"))

@app.route('/hostname', methods=['GET'])
def say_name():
	hostname = os.uname()[1]
	return f"Your request was handled by node: {hostname}\n"


if __name__ == '__main__':
	app.run(host='0.0.0.0')
