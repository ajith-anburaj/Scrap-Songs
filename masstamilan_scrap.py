import urllib.request
from multiprocessing import Pool
from bs4 import BeautifulSoup
import pickle


class Scrap:

    base_url = 'https://www.masstamilan.com'

    def get_page_soup(self, url):

        req = urllib.request.Request(url, headers={'User-Agent': "Mozilla"})
        try:
            page = urllib.request.urlopen(req)
            return BeautifulSoup(page, 'html.parser')
        except Exception as e:
            print(url, e)
            return False

    def get_movie_index(self, page):

        movie_index_scrap = page.find('div', attrs={'class': 'bolda'})
        movie_index = list()
        for movie in movie_index_scrap:
            if movie.__class__.__name__ != "NavigableString":
                movie_index.append((movie.text, movie["href"]))
        return movie_index

    def get_movies(self, movie_index):

        movies_list = []
        page = movie_index[1]
        print(page)
        while True:
            page = self.get_page_soup(page)
            movies = page.find_all('div', attrs={'class': 'botitem'})
            for movie in movies:
                movies_list.append((movie.h1.text, movie.a['href']))
            next_page = page.find('span', attrs={'class': 'next'})
            if next_page:
                page = self.base_url + next_page.a['href']
                print(page)
            else:
                break
        return movies_list

    def get_songs_list(self, movie):
        page = self.get_page_soup(movie[1])
        try:
            songs_list = page.find('table', attrs={'id': 'tlist'}).find_all('tr')[1:]
            songs = dict()
            songs['movie'] = movie[0]
            songs['songs'] = list()
            for song in songs_list:
                musics = songs['songs']
                try:
                    links = song.find_all('a', attrs={'class': 'dlink anim'})
                    if len(links) == 0:
                        print(song)
                    zip = page.find('h2', attrs={'class': 'ziparea normal'}).find_all('a')
                    musics.append({
                        'name': song.a.text if song.a else str(song.h2.string),
                        'singers': song.find('span', attrs={'itemprop': 'byArtist'}).text,
                        'downloads': song.find('span', attrs={'class': 'dl-count'}).text,
                        '128_link': {'link': self.base_url + links[0]['href'] if len(links) > 0 else '',
                                     'size': links[0].text if len(links) > 0 else ''},
                        '320_link': {'link': self.base_url + links[1]['href'] if len(links) > 1 else '',
                                     'size': links[1].text if len(links) > 1 else ''},
                        '128_zip': {'link': zip[0]['href'] if len(zip) > 0 else '',
                                    'size': zip[0].text if len(zip) > 0 else ''},
                        '320_zip': {'link': zip[1]['href'] if len(zip) > 1 else '',
                                    'size': zip[1].text if len(zip) > 1 else ''},
                    })
                    songs['songs'] = musics
                except Exception as e:
                    print(e, movie[0], "not processed", song, song.find_all('a', attrs={'class': 'dlink anim'}))
            print(songs['movie'])
            return songs
        except Exception as e:
            print(movie, e, 'not processed')


def multi_process_movie(movie_index):
    scrap = Scrap()
    return scrap.get_movies(movie_index)

def multi_process_song(movie):
    scrap = Scrap()
    return scrap.get_songs_list(movie)


if __name__ == '__main__':
    scrap = Scrap()
    page = scrap.get_page_soup('https://www.masstamilan.com/movie-index')
    movie_index = scrap.get_movie_index(page)
    p = Pool(20)
    movies_list = p.map(multi_process_movie, movie_index)
    pickle.dump(movies_list, open('movies_list.pickle', 'wb'))
    songs = []
    for movies in movies_list:
        song = p.map(multi_process_song, movies)
        songs += song
    pickle.dump(songs, open('songs_list.pickle', 'wb'))
    p.close()
    p.join()
