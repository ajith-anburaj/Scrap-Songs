import pickle
import re
import requests
import os
from multiprocessing import Pool

def get_songs(albums):
    songs = []
    for album in albums:
        if album:
            for song in album['songs']:
                try:
                    # songs.append((song['name'].strip('\n'), int(song['downloads']),
                    #               song['320_link']['link'] if song['320_link']['link'] != '' else song['128_link']['link'],
                    #               float(re.search(r'\(.*\)', song['320_link']['size']).group(0)[1:-4])
                    #               if song['320_link']['link'] != '' else
                    #               float(re.search(r'\(.*\)', song['128_link']['size']).group(0)[1:-4])))
                    songs.append((song['name'].strip('\n'), int(song['downloads']),
                                  song['128_link']['link'],
                                  float(re.search(r'\(.*\)', song['128_link']['size']).group(0)[1:-4])))
                except Exception as e:
                    #print(e, song)
                    continue
    return songs


def top_albums(albums, limit):
    print(albums[0:5])


def top_songs(albums, limit, quality):
    songs = get_songs(albums)
    songs = sorted(songs, key=lambda song: song[1], reverse=True)
    return songs[0:limit]


def download_songs(song):
    if not os.path.exists('songs/' + song[0] + '.mp3'):
        data = requests.get(song[2])
        with open('songs/' + song[0] + '.mp3', 'wb') as f:
            f.write(data.content)
    print(song[0], ' done')

if __name__ == '__main__':
    movies = pickle.load(open('movies_list.pickle', 'rb'))
    total_movies = 0
    for movie in movies:
        total_movies += len(movie)
    songs = pickle.load(open('songs_list.pickle', 'rb'))
    top_songs = top_songs(songs, 1500, 0)
    total_size = 0
    # for song in top_songs:
    #     print(song)
    #     total_size += song[3]
    # print(total_size)
    p = Pool(16)
    p.map(download_songs, top_songs)
    p.close()
    p.join()
    # download_songs(top_songs=top_songs)
    # top_albums = top_albums(songs, 100)