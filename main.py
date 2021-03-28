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
from random import randint
# import sys
# import time

# Defining app
app = Flask(__name__)


# SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
app.config.from_object(DevelopmentConfig)


# database 
db = SQLAlchemy(app)


# Home page
@app.route("/")
def index():
    option = request.args.get('op')
    # db.session.query(Movie).filter(Movie.movie == "Harry Potter").update({Movie.movie_or_series : "film series"})
    # db.session.commit()
    # print(type(option))
    # c = time.time()
    if option == 'all' or option == None:
        movies = Movie.query.all()
        movies.sort(key = lambda x : x.movie)
        # print(type(movies[0].movie_or_series))
    elif option == "new":
        movies = Movie.query.all()
        movies.sort(key = lambda x : x.id, reverse = True)
    elif option == 'movies':
        movies = Movie.query.filter(Movie.movie_or_series != 'series').all()
        movies.sort(key = lambda x : x.movie)
    else:
        movies = Movie.query.filter_by(movie_or_series = 'series').all()
        movies.sort(key = lambda x : x.movie)
    
    # print(movies)
    # a = time.time()
    # print((a-c), ' s to get queries')
    # b = time.time()
    # print((b-a)* 1000,' ms to sort')
    for i in range(len(movies)):
        # print(movies[i])
        movies[i].image = base64.b64encode(movies[i].image)
        movies[i].image = movies[i].image.decode('utf-8')
        # print(movies[i].image)
    return render_template("index.html",movies = movies, option = option)

#get all movies added by a user
@app.route("/user/<name>")
def user(name):
    movies = Movie.query.filter_by(addedBy = name).all()
    movies.sort(key = lambda x : x.movie)
    for i in range(len(movies)):
        # print(movies[i])
        movies[i].image = base64.b64encode(movies[i].image)
        movies[i].image = movies[i].image.decode('utf-8')
        # print(movies[i].image)
    return render_template("user.html",movies = movies, name = name)

#get all movies in a genre
@app.route("/genre/<genre>")
def genre(genre):
    genre = genre.split(' ')
    if len(genre) == 1:
        movies = Movie.query.filter(Movie.genre.contains(genre[0])).all()
    else:
        movies = Movie.query.filter((Movie.genre.contains(genre[0])) | (Movie.genre.contains(genre[1]))).all()
    movies.sort(key = lambda x : x.movie)
    for i in range(len(movies)):
        # print(movies[i])
        movies[i].image = base64.b64encode(movies[i].image)
        movies[i].image = movies[i].image.decode('utf-8')
        # print(movies[i].image)
    genre = ' '.join(genre)
    return render_template("genre.html",movies = movies, genre = genre)

# get a random movie < broken right now >
@app.route("/random")
def random():
    movies = Movie.query.all()
    length = len(movies)
    i = randint(0,length)
    movie = movies[i]
    l = movie.genre.split('/')
    similar = Movie.query.filter(Movie.genre.contains(l[0])).all()
    # print(movie.movie_or_series)
    similar.remove(movie)
    if len(similar) > 4:
        similar = similar[:4]
    for i in range(len(similar)):
        similar[i].image = base64.b64encode(similar[i].image)
        similar[i].image = similar[i].image.decode('utf-8')
    # print(type(movie.image))
    movie.image = base64.b64encode(movie.image)
    movie.image = movie.image.decode('utf-8')
    return render_template("movie.html",movie = movie, similar = similar)

@app.route("/movie/<id>")
def movie(id):
    movie = Movie.query.get(id)
    l = movie.genre.split('/')
    similar = Movie.query.filter(Movie.genre.contains(l[0])).all()
    # print(movie.movie_or_series)
    similar.remove(movie)
    if len(similar) > 4:
        similar = similar[:4]
    for i in range(len(similar)):
        similar[i].image = base64.b64encode(similar[i].image)
        similar[i].image = similar[i].image.decode('utf-8')
    # print(type(movie.image))
    movie.image = base64.b64encode(movie.image)
    movie.image = movie.image.decode('utf-8')
    return render_template("movie.html",movie = movie, similar = similar)


# method for users to add a movie 
@app.route("/contribute", methods = ['GET', 'POST'])
def contribute():
    if request.method == "GET":
        return render_template("contribute.html", post = False)
    elif request.method == "POST":
        image = resize_image(request.files.get('image').read())
        d = dict(request.form)
        # print(d)
        movie = Movie(d,image)
        db.session.add(movie)
        db.session.commit()
        return render_template("contribute.html", post = True)


# Contributors page
@app.route('/contributors')
def contributors():
    l = list(db.session.query(Movie.addedBy).distinct())
    names = []
    for i in l:
        names.append(i[0])
    return render_template('contributors.html',names = names)


# Genres page
@app.route('/genres')
def genres():
    l = list(db.session.query(Movie.genre).distinct())
    names = set()
    for i in l:
        genres = i[0].replace('/',' ').split(' ')
        for genre in genres:
            names.add(genre)
    return render_template('genres.html',genres = names)


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

# @app.route('/api')
# def api():
#     movies = db.session.query(Movie).update({Movie.movie_or_series : "movie"})
#     return "done"

# convert a image to blob and return
def to_blob():
    with open('D:/Desktop/spider.jpg','rb') as file:
        data = file.read()
    data = resize_image(data)
    return


# to convert any image to our required aspect ratio
def resize_image(img):
    img = Image.open(BytesIO(img))
    img_ratio = img.size[0] / img.size[1]
    # print(img.size[0],img.size[1])
    ratio = 3.0/4.0 # Set image ratio here
    # print(img_ratio,ratio)
    if ratio > img_ratio:
        box = (0, (img.size[1] - img.size[0]/ratio) / 2, img.size[0], (img.size[1] + img.size[0]/ratio) / 2)
        img = img.crop(box)
        # print("Crop 1")
    elif ratio < img_ratio:
        box = ((img.size[0] - img.size[1] * ratio) / 2, 0, ((img.size[0] + img.size[1] * ratio)) / 2, img.size[1])
        img = img.crop(box)
        # print("Crop 2")
    # print(img.size[0],img.size[1])
    img = img.resize((450,600))
    # img.show()
    imgBlob = BytesIO()
    img.save(imgBlob, format='jpeg')
    imgBlob = imgBlob.getvalue()
    # print(sys.getsizeof(imgBlob))
    return imgBlob


# Database model
class Movie(db.Model):
    __tablename__ = "movies"
    id      = db.Column(db.Integer, primary_key = True)
    movie   = db.Column(db.String(450), unique = True)
    year    = db.Column(db.Integer)
    imdb    = db.Column(db.Float)
    image   = db.Column(db.LargeBinary)
    genre   = db.Column(db.String(250))
    actors  = db.Column(db.String(700))
    likes   = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)
    summary = db.Column(db.String(700))
    addedBy = db.Column(db.String(120))
    movie_or_series = db.Column(db.String(100))
    trailer = db.Column(db.String(700))

    def __init__(self, movie, image):
        self.movie = movie['movie']
        self.year = int(movie['year'])
        self.imdb = float(movie['imdb'])
        self.image = image
        # self.actors = movie.actors
        self.likes = 0
        self.dislikes = 0
        # self.summary = movie.summary
        self.addedBy = movie['addedBy']
        self.movie_or_series = movie['movie_or_series']
        self.genre = movie['genre']
        self.trailer = movie['trailer']

    def __repr__(self):
        return self.movie + ' was released in ' + str(self.year) + ' imdb : ' + str(self.imdb) + " is a " + self.movie_or_series
    
    # def __lt__(self,other):
    #     return self.movie < other.movie

def create_db():
    db.create_all()

def drop_db():
    db.drop_all()

def create_table():
    Movie.__table__.create(db.engine)




# entering point for the program
if __name__ == "__main__":
    app.run(debug = True)