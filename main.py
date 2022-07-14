from flask import Flask, render_template, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy

from os import environ
from config import *
from random import randint, sample
import base64

import utils
import json


# Defining app
app = Flask(__name__)



# SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
app.config.from_object(DevelopmentConfig)


# database 
db = SQLAlchemy(app)


# Home page
@app.route("/")
def index():
    option, movies = get_all_movies()

    return render_template("index.html",movies = movies, option = option)


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
        movies[i] = encode_image(movies[i])

    genre = ' '.join(genre)
    return render_template("genre.html",movies = movies, genre = genre)


# get a random movie 
@app.route("/random")
def random():
    id = get_random()
    return redirect("/movie/" + str(id))


# get a random movie through api
@app.route("/api/random")
def api_random():
    movie = get_random_movie()

    return convert_movie_to_json(movie)

@app.route("/api/genre/<genre>")
def api_random_in_genre(genre):
    movies = Movie.query.filter(Movie.genre.contains(genre)).all()
    length = len(movies)
    id = randint(0 ,length - 1)

    return convert_movie_to_json(movies[id])

# Genres page
@app.route('/api/genres')
def api_genres():
    l = list(db.session.query(Movie.genre).distinct())
    names = set()
    for i in l:
        genres = i[0].split('/')
        for genre in genres:
            names.add(genre)
    return json.dumps(list(names))

def convert_movie_to_json(movie):
    d = {}
    d["movie"] = movie.movie
    d["year"] = movie.year
    d["imdb"] = movie.imdb
    d["image"] = encode_image_to_str(movie.image)
    d["genre"] = movie.genre
    d["actors"] = movie.actors
    d["likes"] = movie.likes
    d["dislikes"] = movie.dislikes
    d["summary"] = movie.summary
    d["addedBy"] = movie.addedBy
    d["movie_or_series"] = movie.movie_or_series
    d["trailer"] = movie.trailer

    return json.dumps(d)


@app.route("/movie/<id>")
def movie(id):
    movie, similar = get_movie_by_id(id)
    return render_template("movie.html",movie = movie, similar = similar)


# get the contribute page
@app.route("/contribute", methods = ['GET'])
def contribute():
    return render_template("contribute.html", post = False)


# method for users to add a movie < Handle movie already exists error >
@app.route("/contribute", methods = ['POST'])
def contribute_post():
    image = utils.resize_image(request.files.get('image').read())
    d = dict(request.form)
    movie = Movie(d,image)
    db.session.add(movie)
    db.session.commit()
    return render_template("contribute.html", post = True)


# Contributors page
@app.route('/contributors')
def contributors():
    l = list(db.session.query(Movie.addedBy).distinct())
    names = [i[0] for i in l]
    return render_template('contributors.html',names = names)


#get all movies added by a user
@app.route("/user/<name>")
def user(name):
    movies = Movie.query.filter_by(addedBy = name).all()
    movies.sort(key = lambda x : x.movie)

    for i in range(len(movies)):
        movies[i] = encode_image(movies[i])

    return render_template("user.html",movies = movies, name = name)


# Genres page
@app.route('/genres')
def genres():
    l = list(db.session.query(Movie.genre).distinct())
    names = set()
    for i in l:
        genres = i[0].split('/')
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
        obj = Movie.query.filter_by(movie = d['movie']).one()
        db.session.delete(obj)
        db.session.commit()
        return render_template("admin.html", post = True)


# edit a movie
@app.route('/edit/<id>',methods = ['GET','POST'])
def edit(id):
    if request.method == "GET":
        return render_template("edit.html")
    elif request.method == "POST":
        movie = Movie.query.get(id)
        d = dict(request.form)
        image = request.files.get('image')
        if image:
            image = utils.resize_image(image.read())
            setattr(movie,'image',image)
            db.session.commit()
        else:
            for i in d.keys():
                if d[i] != None:
                    setattr(movie, i, d[i])
                    db.session.commit()
        return redirect("/movie/"+str(id))


# like a movie
@app.route('/like/<id>',methods = ['GET'])
def like(id):
    movie = Movie.query.get(id)
    setattr(movie, 'likes', movie.likes + 1)
    db.session.commit()
    return redirect("/movie/"+str(id))


# dislike a movie
@app.route('/dislike/<id>',methods = ['GET'])
def dislike(id):
    movie = Movie.query.get(id)
    setattr(movie, 'dislikes', movie.dislikes + 1)
    db.session.commit()
    return redirect("/movie/"+str(id))


# error handling
@app.errorhandler(404)
@app.errorhandler(500)
def not_found(error):

    id = get_random()
    movie, _ = get_movie_by_id(id)

    if error.code == 404:
        error_message = "Sorry, We can't find the resource you're looking for"
    else:
        error_message = "Sorry, We messed up"

    return render_template('error.html', error = error.code, error_message = error_message, movie = movie), error.code


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


# Helper methods
def get_all_movies():
    option = request.args.get('op')

    if option == 'all' or option == None:
        movies = Movie.query.all()
        movies.sort(key = lambda x : x.movie)

    elif option == "new":
        movies = Movie.query.all()
        movies.sort(key = lambda x : x.id, reverse = True)

    elif option == 'movies':
        movies = Movie.query.filter(Movie.movie_or_series != 'series').all()
        movies.sort(key = lambda x : x.movie)

    elif option == "sort_by_imdb":
        movies = Movie.query.all()
        movies.sort(key = lambda x : x.imdb, reverse = True)

    else:
        movies = Movie.query.filter_by(movie_or_series = 'series').all()
        movies.sort(key = lambda x : x.movie)
    

    for i in range(len(movies)):
        movies[i] = encode_image(movies[i])

    return option,movies

def get_movie_by_id(id):
    movie = Movie.query.get(id)
    
    if movie == None:
        abort(404)

    l = movie.genre.split('/')

    if len(l) == 1:
        similar = Movie.query.filter(Movie.genre.contains(l[0])).all()
    else:
        similar = Movie.query.filter((Movie.genre.contains(l[0])) | (Movie.genre.contains(l[1]))).all()

    similar.remove(movie)

    if len(similar) > 4:
        similar = sample(similar,4)

    for i in range(len(similar)):
        similar[i] = encode_image(similar[i])

    movie = encode_image(movie)
    return movie,similar

def get_random():
    movies = Movie.query.all()
    length = len(movies)
    id = randint(1,length)
    return id

def get_random_movie():
    movies = Movie.query.all()
    length = len(movies)
    id = randint(0 ,length - 1)
    return movies[id]

def encode_image(movie):
    movie.image = base64.b64encode(movie.image)
    movie.image = movie.image.decode('utf-8')

    return movie

def encode_image_to_str(image):
    image = base64.b64encode(image)
    image = image.decode('utf-8')

    return image

# def create_db():
#     db.create_all()

# def drop_db():
#     db.drop_all()

# def create_table():
#     Movie.__table__.create(db.engine)




# entering point for the program
if __name__ == "__main__":
    app.run(debug = True)