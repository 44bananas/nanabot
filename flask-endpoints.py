#flask-endpoints

from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/username_query')
def username_query():
    con = sqlite3.connect("tc_usernames.db")
    username = request.args.get("username")
    if username != "" and any([username.lower() in i for i in con.execute("SELECT * FROM names").fetchall()]):
        return 'True'
    else:
        return 'False'

app.run()