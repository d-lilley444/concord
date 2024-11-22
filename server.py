from flask import Flask, render_template,url_for,g,redirect,request
import sqlite3
import json
import hashlib
import flask_login
import uuid

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


@app.route('/signup',methods=['GET','POST'])
def signup():

    if request.method == 'GET':
        return render_template("signup.html")

    if request.method == 'POST':

        #gets the attributes from the form
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        if email == None or username == None or password == None:
            return render_template("signup.html", errors = "somethings missing")
       
        #hash the password
        hashed = hashlib.sha256(password.encode())

        con = get_db()
        cur = con.cursor()

        sql = "INSERT INTO users (username,email,hash) VALUES (?,?,?)"
        valaues = (username,email,hashed.hexdigest())
        cur.execute(sql,valaues)
        con.commit()
        #probably need other checks here ??

        return redirect(url_for('login'))
    

@app.route("/login",methods = ['GET','POST'])
def login():

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        if email == None or password == None:
            return render_template("login.html", errors = "somethings missing")
       
        #hash the password
        hashed = hashlib.sha256(password.encode())

        con = get_db()
        cur = con.cursor()

        sql = "SELECT * FROM users WHERE email = ?"
        valaues = (email,)
        cur.execute(sql,valaues)
        user_info = cur.fetchone()

        #app.logger.info(f"USER LGIN INFO = {user_info[0]}, {user_info[1]}, {user_info[2]}")

        if user_info == None:
            return render_template("login.html",errors="Soemthing went wrong")

        if hashed.hexdigest() == user_info[3]:
            user = User()
            user.id = user_info['user_id']
            user.username = user_info['username']
            user.email = user_info['email']

            flask_login.login_user(user)
            return redirect(url_for('landing'))

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    #return "Unauthorized", 401
    return redirect(url_for('login'))


@app.route("/")
def index():
    return render_template ("index.html")

@app.route("/landing")
def landing():

    loggedin = None

    if flask_login.current_user.is_authenticated:
        loggedin = flask_login.current_user

        #get the servers they are a part of 

        return render_template("profile_landing.html",loggedin_user = loggedin)
    else:
        return render_template("login.html")

##SERVERS landing page 

@app.route("/servers",methods=['GET','POST'])
@flask_login.login_required
def servers():
    loggedin = None

    if flask_login.current_user.is_authenticated:
        loggedin = flask_login.current_user

        con = get_db()
        cur = con.cursor()

        sql = ""


    ##allow the user to create a server ? 
        return render_template("servers_landing.html",loggedin_user = loggedin)
    

@app.route("/create_server",methods=['GET','POST'])
@flask_login.login_required
def createServer():

    loggedin = None

    if flask_login.current_user.is_authenticated:
        loggedin = flask_login.current_user

        if request.method == 'GET':
            return render_template("server_create.html")

        if request.method == 'POST':
            #get the server info from the form 
            serverName = request.form.get('server-name')
            serverPassword = request.form.get('server-pass')
            servrUUID = str(uuid.uuid4())
            creatorId = loggedin.id ##may not be this ?

            con = get_db()
            cur = con.cursor()

            sql = "INSERT INTO servers (name,password,uuid,creator_id) VALUES (?,?,?,?)"
            values = (serverName,serverPassword,servrUUID,creatorId,)
            #try catch ??
            cur.execute(sql,values)
            con.commit()

            #redirect back to page 
            return redirect(url_for('servers'))




