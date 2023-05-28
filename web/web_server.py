from flask import Flask, render_template, jsonify, request
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

@app.route("/api/model/pearson/", methods=['POST'])
def get_pearson_predictions():
    # get payload from request
    payload = request.get_json(force=True)
    user_id = payload['userId']
    movie_ratings = payload['ratings']

    # load similarity matrix
    similary_matrix = pd.read_csv('data/similarity.csv', sep=',', engine='python', index_col=0)

    # get predictions
    similar_movies = pd.DataFrame()
    for movie in movie_ratings:
        similar_score = similary_matrix[movie['movieTitle']]*(movie['rating']-2.5)
        similar_score = similar_score.sort_values(ascending=False)
        similar_movies = similar_movies.append(similar_score, ignore_index=True)

    # order movies by score
    sorted_movies = similar_movies.sum().sort_values(ascending=False).head(15)
    sorted_movies_list = sorted_movies.reset_index().rename(columns={'index': 'movieTitle', 0: 'rating'}).to_dict(orient='records')

    # Exclude movies that user has already rated
    movie_titles = [movie['movieTitle'] for movie in movie_ratings]
    sorted_movies_list = [movie for movie in sorted_movies_list if movie['Title'] not in movie_titles]
    return sorted_movies_list 


# ###############################
# Error Handler
# ###############################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html') # redirect to index.html

if __name__ == '__main__':
    app.run(debug=True)