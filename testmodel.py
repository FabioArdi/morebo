import argparse
import os
import numpy as np
import tensorflow_datasets as tfds
import tensorflow_recommenders as tfrs
import plotly.graph_objs as go
import datapane as dp


USER_FEATURES = ["user_id", "sex", "occupation", "age"]


class MovieLensTrainer:

    def __init__(self, num_epochs, embedding_dim, layer_sizes, additional_feature_sets, retrain):
        self.num_epochs = num_epochs
        self.embedding_dim = embedding_dim
        self.layer_sizes = layer_sizes
        self.additional_feature_sets = additional_feature_sets
        self.retrain = retrain

        self.ratings = None
        self.movies = None
        self.unique_movie_titles = None
        self.all_ratings = None
        self.dataset = None

        self.rating_weight = 0.5
        self.timestamp_weight = 0.5
        self.user_id_weight = 1.0

    def _load_data(self):
        self.ratings = tfds.load("movielens/100k-ratings", split="train")
        self.movies = tfds.load("movielens/100k-movies", split="train")

        self.unique_movie_titles = np.unique([movie["title"].numpy().decode("utf-8") for movie in self.movies])
        self.unique_movie_titles = np.array([x.lower() for x in self.unique_movie_titles])
        self.all_ratings = self.ratings.map(lambda x: {k: x[k] for k in ("user_id", "movie_title", "user_rating")})
        self.dataset = self.all_ratings.batch(512)

    def _build_rating_model(self):
        movie_title_lookup = tf.keras.Sequential([
            tf.keras.layers.experimental.preprocessing.StringLookup(
                vocabulary=self.unique_movie_titles, mask_token=None),
            tf.keras.layers.Embedding(len(self.unique_movie_titles) + 1, self.embedding_dim)
        ])

        user_id_lookup = tf.keras.Sequential([
            tf.keras.layers.experimental.preprocessing.StringLookup(mask_token=None),
            tf.keras.layers.Embedding(len(self.ratings.batch(1_000_000).map(lambda x: x["user_id"]).unique()) + 1,
                                      self.embedding_dim)
        ])

        user_model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(self.embedding_dim)
        ])

        timestamp_model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(self.embedding_dim)
        ])

        rating_model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(16, activation="relu"),
            tf.keras.layers.Dense(1)
        ])

        ratings = self.ratings.map(lambda x: {"movie_title": x["movie_title"],
                                              "user_id": x["user_id"],
                                              "user_rating": x["user_rating"],
                                              "timestamp": x["timestamp"]})

        user_features = ratings.batch(1_000_000).map(lambda x: x["user_id"])
        user_id_lookup.fit(user_features)
        user_model_input = tf.keras.Input(shape=(1,), name="user_id")
        user_model_output = user_model(user_id_lookup(user_model_input))

        timestamp_features = ratings.batch(1_000_000).map(lambda x: x["timestamp"])
        standard_timestamp = tfrs.layers.Standardization()(timestamp_features)
        timestamp_model_input = tf.keras.Input(shape=(
