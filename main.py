from flask import Flask, render_template, request
# import sqlite3
from PIL import Image
from io import BytesIO
import base64
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import os
from os import environ
from config import *
import config

# Defining app
app = Flask(__name__)


# SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
app.config.from_object(DevelopmentConfig)


# database 
db = SQLAlchemy(app)


# Home page
@app.route("/")
def index():
    movies = Movie.query.all()
    # print(type(movies))
    # print(movies)
    for i in range(len(movies)):
        movies[i].image = base64.b64encode(movies[i].image)
        movies[i].image = movies[i].image.decode('utf-8')
        # print(movies[i].image)
    return render_template("index.html",movies = movies)

# get a random movie < broken right now >
@app.route("/random")
def random():
    return "<p> You Should definitely watch The Lord of the Rings. </p>"


# method for users to add a movie 
@app.route("/contribute", methods = ['GET', 'POST'])
def contribute():
    if request.method == "GET":
        return render_template("contribute.html", post = False)
    elif request.method == "POST":
        image = resize_image(request.files.get('image').read())
        d = dict(request.form)
        movie = Movie(d,image)
        db.session.add(movie)
        db.session.commit()
        return render_template("contribute.html", post = True)


# About page
@app.route('/about')
def about():
    return render_template('about.html')


# admin page to delete any wrong info
@app.route('/admin',methods = ['GET','POST'])
def admin():
    if request.method == "GET":
        return render_template("admin.html", post = False)
    elif request.method == "POST":
        d = dict(request.form)
        if (d['password'] != 'CodeRed'):
            return render_template("admin.html",post = False)
        # delete_entry((d['movie']))
        obj = Movie.query.filter_by(movie = d['movie']).one()
        db.session.delete(obj)
        db.session.commit()
        return render_template("admin.html", post = True)


# # debug site
# @app.route('/debug')
# def debug():
#     create_table()
#     add_movie(("Wall-E","2008",8.4,to_blob('static/images/Wall-E.jpg')))
#     add_movie(("Deadpool","2016",8,to_blob('static/images/Deadpool.jpg')))
#     add_movie(("John Wick","2014",7.4,to_blob('static/images/John Wick.jpg')))
#     add_movie(("Alita: Battle Angel","2019",7.3,to_blob('static/images/Alita Battle Angel.jpg')))
#     add_movie(("The Dark Knight","2008",9,to_blob('static/images/The Dark Knight.jpg')))
#     add_movie(("Iron Man","2008",7.9,to_blob('static/images/Iron Man.jpg')))
#     add_movie(("Joker","2019",8.4,to_blob('static/images/Joker.jpg')))
#     add_movie(("Parasite","2019",8.6,to_blob('static/images/Parasite.jpg')))
#     s = str(get_all_movies())
#     return s


# convert a image to blob and return
def to_blob(img):
    with open(img,'rb') as file:
        data = file.read()
    data = resize_image(data)
    return data


# to convert any image to our required aspect ratio
def resize_image(img):
    img = Image.open(BytesIO(img))
    img_ratio = img.size[0] / float(img.size[1])
    ratio = 2.0/3.0 # Set image ratio here
    if ratio > img_ratio:
        box = (0, (img.size[1] * (1 - ratio)) / 2, img.size[0], (img.size[1] * (1 + ratio)) / 2)
        img = img.crop(box)
    elif ratio < img_ratio:
        box = ((img.size[0]  * (1 - ratio)) / 2, 0, (img.size[0] * (1 + ratio)) / 2, img.size[1])
        img = img.crop(box)
    img = img.resize((450,600))
    imgBlob = BytesIO()
    img.save(imgBlob, format='jpeg')
    imgBlob = imgBlob.getvalue()
    return imgBlob


# Database model
class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key = True)
    movie = db.Column(db.String(250), unique = True)
    year = db.Column(db.Integer)
    imdb = db.Column(db.Float)
    image = db.Column(db.LargeBinary)
    genre = db.Column(db.String(250))
    actors = db.Column(db.String(700))
    likes = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)
    summary = db.Column(db.String(500))
    addedBy = db.Column(db.String(120))
    movie_or_series = db.Column(db.String(100))

    def __init__(self, movie, image):
        self.movie = movie['movie']
        self.year = int(movie['year'])
        self.imdb = float(movie['imdb'])
        self.image = image
        # self.actors = movie.actors
        # self.likes = movie.likes
        # self.dislikes = movie.dislikes
        # self.summary = movie.summary
        self.addedBy = movie['addedBy']
        # self.movie_or_series = db.Column(db.String(100))

    def __repr__(self):
        return self.movie + ' was released in ' + str(self.year) + ' imdb : ' + str(self.imdb)



def create_db():
    db.create_all()

def drop_db():
    db.drop_all()

def create_table():
    Movie.__table__.create(db.engine)




# entering point for the program
if __name__ == "__main__":
    app.run(debug = True)