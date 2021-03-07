from flask import Flask, render_template
import sqlite3
from data import *

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/debug')
def debug():
    create_table()
    add_movie(("Wall-E","2008",8.4,''))
    s = str(get_all_movies())
    return s

if __name__ == "__main__":
    app.run(debug = True)