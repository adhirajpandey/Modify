from application.models import User, Song, Album, Playlist, PlaylistSong, RatingSong
from application.database import db


def input_validation(username, password):
    MIN_LENGTH = 5
    if username == "" or password == "":
        return False
    elif len(username) < MIN_LENGTH or len(password) < MIN_LENGTH:
        return False
    else:
        return True


def fetch_song_average_rating(song_id):
    ratings = RatingSong.query.filter_by(song_id=song_id).all()
    sum = 0
    for rating in ratings:
        sum += rating.rating

    if len(ratings) == 0:
        return 0
    else:
        return sum / len(ratings)


def fetch_songs_average_ratings(song_ids):
    ratings = {}
    for song_id in song_ids:
        ratings[song_id] = RatingSong.query.filter_by(song_id=song_id).all()
    
    average_ratings = {}
    for song_id in ratings:
        sum = 0
        for rating in ratings[song_id]:
            sum += rating.rating

        if len(ratings[song_id]) == 0:
            average_ratings[song_id] = 0
        else:
            average_ratings[song_id] = sum / len(ratings[song_id])

    return average_ratings