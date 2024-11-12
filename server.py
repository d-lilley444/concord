from flask import Flask, render_template,url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template ("index.html")

@app.route("/signup",methods=['GET','POST'])
def signup():
    return render_template('signup.html')


