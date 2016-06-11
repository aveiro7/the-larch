from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
	return "Hello!"

@app.route('/user/<username>')
def show_user(username):
	return "@" + username + "'s posts."

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
	return render_template('hello.html', name=name)


if __name__ == "__main__":
	app.run()