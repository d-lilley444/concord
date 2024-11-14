from flask import Flask, render_template,url_for,g
import sqlite3
import json
import hashlib
import flask_login

app = Flask(__name__)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

#TODO -- put this in an enviroment variable 
app.config['SECRET_KEY'] = "super secret key"

database_path = "concordDatabase.db"

def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(database_path)
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()


@login_manager.user_loader
def user_loader(id):
    con = get_db()
    cur = con.cursor()

    sql = "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)"
    values = (id,)
    cur.execute(sql,values)
    user_exists = cur.fetchone()

    if user_exists[0] == 1:

        sql = "SELECT * FROM users WHERE user_id = ?"
        values = (id,)
        cur.execute(sql,values)
        info = cur.fetchone()

        user = User()
        user.id = info['user_id']
        user.username = info['username']
        user.email = info['email']
        return user
    else:
        return None

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    con = get_db()
    cur = con.cursor()

    sql = "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)"
    values = (email,)
    cur.execute(sql,values)
    user_exists = cur.fetchone()

    if user_exists[0] == 1:

        sql = "SELECT * FROM users WHERE email = ?"
        values = (email,)
        cur.execute(sql,values)
        info = cur.fetchone()

        user = User()
        user.id = info['user_id']
        user.username = info['username']
        user.email = info['email']
        return user
    else:
        return None







@app.route("/")
def index():
    return render_template ("index.html")

@app.route("/signup",methods=['GET','POST'])
def signup():
    return render_template('signup.html')


