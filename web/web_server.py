from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

# ###############################
# HTML Endpoints
# ###############################
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/movies/", defaults={'page': 1, 'page_size': 10})
@app.route("/movies/<int:page>", defaults={'page_size': 10})
@app.route("/movies/<int:page>/<int:page_size>")
def movies(page, page_size):
    print(page_size)
    return render_template("movies.html", page=page, page_size=page_size, movies=get_movies_page(page, page_size))

@app.route("/about")
def about():
    return render_template("about.html")


# ###############################
# API Endpoints
# ###############################
@app.route("/api/movies/")
def get_movies():
    movies = pd.read_csv('data/movies_meta_data.csv', sep=';', engine='python')
    movies = movies.fillna('')  # replace NaN values with empty string
    movies = movies.sort_values(by=['Title']) # order movies by title
    return movies.to_dict(orient='records')

@app.route("/api/movies/title/")
def get_movie_titles():
    movies = pd.read_csv('data/movies_meta_data.csv', sep=';', engine='python')
    movies = movies.fillna('')  # replace NaN values with empty string
    movies = movies.sort_values(by=['Title']) # order movies by title
    movies = movies['Title']
    return movies.to_dict()

@app.route("/api/movies/page/<int:page>", defaults={'page_size': 10})
@app.route("/api/movies/page/<int:page>/<int:page_size>")
def get_movies_page(page, page_size):
    movies = pd.read_csv('data/movies_meta_data.csv', sep=';', engine='python')
    movies = movies.fillna('')  # replace NaN values with empty string
    movies = movies.sort_values(by=['Title']) # order movies by title
    return movies.iloc[page * page_size:(page+1) * page_size].to_dict(orient='records')

@app.route("/api/movies/<int:movie_id>")
def get_movie_by_id(movie_id):
    movies = pd.read_csv('data/movies_meta_data.csv', sep=';', engine='python')
    movies = movies.fillna('')  # replace NaN values with empty string
    movie = movies[movies['ml_movieId'] == movie_id]
    if movie.empty:
        return jsonify({'error': 'not found'}), 404
    return movie.to_dict(orient='records')

@app.route("/api/movies/<string:movie_title>")
def get_movie_by_title(movie_title):
    movies = pd.read_csv('data/movies_meta_data.csv', sep=';', engine='python')
    movies = movies.fillna('')  # replace NaN values with empty string
    movie = movies[movies['Title'] == movie_title]
    if movie.empty:
        return jsonify({'error': 'not found'}), 404
    return movie.to_dict(orient='records')


# ###############################
# Error Handler
# ###############################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html') # redirect to index.html

if __name__ == '__main__':
    app.run(debug=True)