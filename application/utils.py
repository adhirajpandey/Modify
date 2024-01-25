from application.models import User, Song, Album, Playlist, PlaylistSong, RatingSong
from application.database import db
import os
import matplotlib.pyplot as plt


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


def get_filename():
    songs_images_dir = "static/images/songs"
    filenames = os.listdir(songs_images_dir)
    filenames = [int(filename[:-4]) for filename in filenames]

    max_num_filename = max(filenames)
    new_num_filename = max_num_filename + 1

    filename = songs_images_dir + "/" + str(new_num_filename) + ".jpg"

    return filename
    

def create_charts():
    songs = Song.query.all()
    song_ids = [song.id for song in songs]
    average_ratings = fetch_songs_average_ratings(song_ids)

    filename1 = "static/images/graphs/1.png"
    filename2 = "static/images/graphs/2.png"
    filename3 = "static/images/graphs/3.png"
    filename4 = "static/images/graphs/4.png"

    # chart 1 to show which song ids have the most ratings (song ids should be integers)
    song_ids = list(average_ratings.keys())
    ratings = list(average_ratings.values())

    plt.bar(song_ids, ratings)
    plt.xlabel("Song ID")
    plt.ylabel("Average Rating")

    # Set x-axis ticks to display as integers
    plt.xticks(song_ids, [int(song_id) for song_id in song_ids])

    plt.savefig(filename1)
    plt.clf()

    # chart 2 to show which user id has uploaded how many songs
    users = User.query.all()
    user_ids = [user.id for user in users]
    user_song_counts = {}
    for user_id in user_ids:
        user_song_counts[user_id] = len(Song.query.filter_by(user_id=user_id).all())

    user_ids = list(user_song_counts.keys())
    song_counts = list(user_song_counts.values())

    plt.bar(user_ids, song_counts)
    plt.xlabel("User ID")
    plt.ylabel("Number of Songs")

    # Set x-axis ticks to display as integers
    plt.xticks(user_ids, [int(user_id) for user_id in user_ids])

    plt.savefig(filename2)
    plt.clf()

    # chart 3 pie chart to show how many songs are flagged
    flagged_songs = Song.query.filter_by(flagged=1).all()
    flagged_songs_count = len(flagged_songs)

    non_flagged_songs = Song.query.filter_by(flagged=0).all()
    non_flagged_songs_count = len(non_flagged_songs)

    plt.pie([flagged_songs_count, non_flagged_songs_count], labels=["Flagged", "Not Flagged"], autopct='%1.1f%%')
    plt.savefig(filename3)
    plt.clf()

    # chart 4 pie chart to total number of songs in each genre
    albums = Album.query.all()
    genres = [album.genre for album in albums]

    genre_counts = {}
    for genre in genres:
        if genre in genre_counts:
            genre_counts[genre] += 1
        else:
            genre_counts[genre] = 1

    album_songs_count = {}
    for album in albums:
        album_songs_count[album.id] = len(Song.query.filter_by(album=album.id).all())

    album_ids = list(album_songs_count.keys())
    song_counts = list(album_songs_count.values())

    plt.pie(song_counts, labels=album_ids, autopct='%1.1f%%')
    plt.savefig(filename4)
    plt.clf()

    