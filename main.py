from flask import Flask
from flask import render_template
from user import User
app = Flask(__name__)

@app.route('/')
def hello_world():
	return "Hello!"

@app.route('/user/<username>')
def show_user(username):
	user = User(username)
	return render_template('user.html', user)

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
	return render_template('hello.html', name=name)


if __name__ == "__main__":
	app.run()