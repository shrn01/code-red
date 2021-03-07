from flask import Flask, render_template
import sqlite3
from data import *

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html",movies = get_all_movies())


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/debug')
def debug():
    create_table()
    add_movie(("Wall-E","2008",8.4,'images/Wall-E.jpg'))
    add_movie(("Deadpool","2016",8,'images/Deadpool.jpg'))
    add_movie(("John Wick","2014",7.4,'images/John Wick.jpg'))
    add_movie(("Alita: Battle Angel","2019",7.3,'images/Alita Battle Angel.jpg'))
    add_movie(("The Dark Knight","2008",9,'images/The Dark Knight.jpg'))
    add_movie(("Iron Man","2008",7.9,'images/Iron Man.jpg'))
    add_movie(("Joker","2019",8.4,'images/Joker.jpg'))
    add_movie(("Parasite","2019",8.6,'images/Parasite.jpg'))
    s = str(get_all_movies())
    return s

if __name__ == "__main__":
    app.run(debug = True)