import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort
from flask import render_template, flash


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'larch.db'),
    SECRET_KEY='development_key',
    USERNAME='admin',
    PASSWORD='default'
))

# this helps to keep configuration in a separate file
# this should be pointed to by the environment variable
# silent mode turned on prevents from errors when there is no such variable
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# DATABASE SETUP

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print "Initialized the database."

# this would be called every time the app context tears down
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# VIEW FUNCTIONS

@app.route('/')
def show_posts():
    db = get_db()
    query = '''select p.id, p.text, u.login as author 
            from posts p 
                join users u on p.author = u.id
            where u.active = 1
            order by p.id desc'''
    cur = db.execute(query)
    posts = cur.fetchall()

    query = '''select c.id, c.text, c.post as post_id, u.login as author 
            from comments c 
                join users u on c.author = u.id
            where u.active = 1'''
    cur = db.execute(query)
    comments = cur.fetchall()

    return render_template('show_all_posts.html', 
        posts=posts, comments=comments)

@app.route('/add', methods=['POST'])
def add_post():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into posts (text, author) values (?, ?)', 
        [request.form['text'], session.get('user_id')])
    db.commit()
    flash('New post was succesfully published')
    return redirect(url_for('show_posts'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        db = get_db()
        cur = db.execute('select * from users where login=?', [login])
        if cur.fetchall():
            error = 'This username is already taken.'
        else:
            db.execute('insert into users (login, password) values (?, ?)',
                [login, password])
            user_id = db.execute('select max(id) from users').fetchone()[0]
            db.commit()

            session['logged_in'] = True
            session['user_id'] = user_id
            session['username'] = login
            flash('You are succesfully registered')
            return redirect(url_for('show_posts'))
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':

        login = request.form['username']
        password = request.form['password']

        db = get_db()
        query = '''select u.id, u.password 
                from users u 
                where u.login=? and u.active = 1'''

        cur = db.execute(query, [login])
        result = cur.fetchone()

        if result is None:
            error = "There is no such user."
        else:
            pwd = result[1]
            if password != pwd:
                error = "The password is wrong."
            else:
                session['logged_in'] = True
                session['user_id'] = result[0]
                session['username'] = login
                flash('You are logged in')
                return redirect(url_for('show_posts'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You are logged out')
    return redirect(url_for('show_posts'))


@app.route('/delete/<post_id>')
def delete_post(post_id):
    db = get_db()
    db.execute('delete from posts where id=?', post_id)
    db.commit()
    flash('Deleted post')
    return redirect(url_for('show_posts'))


@app.route('/post/<post_id>')
def show_post(post_id):
    db = get_db()
    query = '''select *
            from posts
                join users u on u.id = posts.author
            where id = ? and u.active = 1'''
    cur = db.execute(query, [post_id])
    post = cur.fetchone()

    query = '''select c.text, u.login as author 
                from comments c 
                    join users u on c.author = u.id 
                where post = ? and u.active = 1'''
    cur = db.execute(query, [post_id])
    comments = cur.fetchall()

    return render_template('show_post.html', post=post, comments=comments)


@app.route('/edit/<post_id>', methods=['POST'])
def edit_post(post_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('update posts set text = ? where id=?', 
        [request.form['text'], post_id])
    db.commit()
    flash('Edited post')
    return redirect(url_for('show_posts'))

@app.route('/add_comment/<post_id>', methods=['POST'])
def add_comment(post_id):
    db = get_db()
    db.execute('insert into comments(text, author, post) values (?, ?, ?)',
        [request.form['text'], session.get('user_id'), post_id])
    db.commit()
    return redirect(url_for('show_posts'))

@app.route('/delete_comment/<comment_id>')
def delete_comment(comment_id):
    db = get_db()
    db.execute('delete from comments where id=?', [comment_id])
    db.commit()
    return redirect(url_for('show_posts'))

@app.route('/edit_comment/<comment_id>')
def edit_comment(comment_id):
    flash('Editing comments would require JavaScript - working on it! :)')
    return redirect(url_for('show_posts'))

@app.route('/user/<login>')
def show_user(login):
    db = get_db()
    query = '''select p.id, p.text, u.login as author 
            from posts p 
                join users u on p.author = u.id 
            where u.login = ? and u.active = 1
            order by p.id desc'''
    cur = db.execute(query, [login])
    posts = cur.fetchall()

    query = '''select u.id
            from users u
            where u.login = ?
                and u.active = 1'''
    cur = db.execute(query, [login])
    user_id = cur.fetchone()
    if user_id:
        user_id = user_id[0]
    else:
        login = None

    query = '''select c.text, u.login as author, c.post as post_id
            from comments c
                join users u on u.id = c.author
                join posts p on p.id = c.post
            where p.author = ?
                and u.active = 1'''
    cur = db.execute(query, [user_id])
    comments = cur.fetchall()
    
    return render_template('show_user.html', posts=posts, comments=comments, login=login)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/delete_user')
def delete_user():
    db = get_db()
    db.execute('update users set active=0 where id=?', [session.get('user_id')])
    db.commit()
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Your account was succesfully deleted.')
    return redirect(url_for('show_posts'))

if __name__ == "__main__":
	app.run()