import requests
import pandas as pd
from os.path import exists
import json

def get_meta_data(url: str):
    response = requests.request("GET", url)
    return response.status_code, response.text

def print_error(response: tuple, movie):
    print(f"Error fetching meta data for '{movie.ml_title}':")
    print(f">> Status code: {response[0]}")
    print(f">> Result: {response[1]}")

def save_not_found_movies(movies: list):
    print(f"\nNumber of movies not found: {len(movies)}")   
    if len(movies) > 0:
        print(f"Saving {len(movies)} not found movie(s) to '{not_found_file}'")
        not_found = pd.read_csv(not_found_file)
        new_not_found = pd.DataFrame(movies, columns=['ml_title'])
        if len(not_found) > 0:
            all_not_found = pd.concat([not_found, new_not_found]).drop_duplicates() # concat new not found movies with already not found movies
        else:
            all_not_found = new_not_found
        all_not_found.to_csv(not_found_file, index=False) # save all not found movies to csv file

if __name__ == "__main__":
    # read movies from movielens dataset
    ml_movies = pd.read_csv('data/movies.dat', sep='::', engine='python', names=['ml_movieId', 'ml_title', 'ml_genres'], encoding="ISO-8859-1")
    # Remove year from title and add it as a separate column
    ml_movies['ml_year'] = ml_movies['ml_title'].str.extract(r"\((\d{4})\)", expand=False)
    ml_movies['ml_title'] = ml_movies['ml_title'].str.replace(r"\s\(\d{4}\)","", regex=True)
    # Change titles with ',' and move part after ',' to the start of the title
    ml_movies['ml_title'] = ml_movies['ml_title'].apply(lambda x: ' '.join(x.split(',')[::-1]).strip())

    # read already fetched movies
    movies_file = 'data/movies_meta_data2.csv'
    if not exists(movies_file): # create file if not exists
        fetched_movies = pd.DataFrame(columns=['ml_movieId', 'ml_title', 'ml_genres', 'Title', 'Year', 'Rated', 'Released', 'Runtime', 'Genre', 'Director', 'Writer', 'Actors', 'Plot', 'Language', 'Country', 'Awards', 'Poster', 'Ratings', 'Metascore', 'imdbRating', 'imdbVotes', 'imdbID', 'Type', 'DVD', 'BoxOffice', 'Production', 'Website', 'Response'])
        fetched_movies.to_csv(movies_file, index=False, sep=';')
    fetched_movies = pd.read_csv(movies_file, delimiter=';') # read already fetched movies

    # read not found movies
    not_found_file = 'data/not_found_movies2.csv'
    if not exists(not_found_file): # create file if not exists
        not_found_movies = pd.DataFrame(columns=['ml_title'])
        not_found_movies.to_csv(not_found_file, index=False, sep=';')
    not_found_movies = pd.read_csv(not_found_file) # read already not found movies

    new_fetched_movies = [] # list of new fetched movies
    new_not_found = [] # list of movies not found
    response = [200, ""]
    index = 0

    while response[0] == 200 and index < len(ml_movies): # fetch meta data for all movies til error occurs
        ml_movie = ml_movies.iloc[index]

        if ml_movie.ml_title in fetched_movies['ml_title'].values or ml_movie.ml_title in not_found_movies['ml_title'].values: # check if movie is already fetched
            print(f"Already fetched meta data for '{ml_movie.ml_title}'")
            index += 1
        else: # fetch meta data for movie
            print(f"Fetching meta data for '{ml_movie.ml_title}'")
            movie_title = ml_movie.ml_title.replace(" ", "+") # replace spaces with + for url
            movie_year = ml_movie.ml_year
            # url = f"https://www.omdbapi.com/?t={movie_title}&apikey=aa348489" # API key with school mail
            url = f"https://www.omdbapi.com/?t={movie_title}&y={movie_year}&apikey=967eb8c6" # API key with private mail
            response = get_meta_data(url) # fetch meta data and save response
            if not response[0] == 200: # check if response is ok
                print_error(response, ml_movie)
                break   
            elif json.loads(response[1])['Response'] == "False": # check if movie was found
                print_error(response, ml_movie)
                new_not_found.append(ml_movie.ml_title)
            else: # save response
                movie_meta_data = pd.read_json(response[1], lines=True).iloc[0]
                movie_df = pd.concat([ml_movie, movie_meta_data], axis=0)
                new_fetched_movies.append(pd.DataFrame(movie_df).T)
            index += 1
            if index > 5:
                break

    # save not found movies to csv file
    save_not_found_movies(new_not_found)

    # save fetched movies to csv file
    print(f"Number of new fetched movies: {len(new_fetched_movies)}")
    if len(new_fetched_movies) > 0:
        print(f"Saving {len(new_fetched_movies)} fetched movie(s) to '{movies_file}'")
        new_movies = pd.concat(new_fetched_movies, ignore_index=True) # concat all new movies frames to one frame
        all_movies = pd.concat([fetched_movies, new_movies], ignore_index=True) # concat already fetched movies with new movies
        all_movies.to_csv(movies_file, index=False, sep=';')
        print(f"File saved! Total number of movies: {len(all_movies)}")
    else:
        print("No new movies fetched!")