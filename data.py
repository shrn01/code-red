import sqlite3

def get_db_connection():
    conn = sqlite3.connect('movies.db')
    return (conn)

def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS movies (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, release_date TEXT, imdb REAL, image TEXT);
    ''')
    conn.commit()
    conn.close()
    return


def add_movie(movie):
    conn = get_db_connection()
    cur = conn.cursor()
    l = cur.execute("SELECT name FROM movies WHERE name = ?",(movie[0],)).fetchall()
    if not l:
        cur.execute('''
        INSERT INTO movies(name, release_date, imdb, image) VALUES (?,?,?,?);
        ''', movie)
    conn.commit()
    conn.close()
    return

def get_all_movies():   
    conn = get_db_connection()
    cur = conn.cursor()
    l = cur.execute("SELECT name, release_date, imdb, image FROM movies").fetchall()
    conn.close()
    return l

def get_movie(conn,name):
    cur = conn.cursor()
    l = cur.execute("SELECT name, release_date, imdb, image FROM movies WHERE name = ?",(name,)).fetchall()
    return l

def delete_entry(name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    DELETE FROM movies WHERE name = ?
    ''',(name,))
    conn.commit()
    conn.close()
    return

def update():
    pass

