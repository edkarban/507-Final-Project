import requests
import json
import webbrowser
import matplotlib.pyplot as plt

import secrets as secrets
from requests_oauthlib import OAuth1

#SPOTIFY AUTHENTICATION

client_key = secrets.SPOTIFY_CLIENT_KEY
client_secret = secrets.SPOTIFY_CLIENT_SECRET

AUTH_URL = 'https://accounts.spotify.com/api/token'

auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': client_key,
    'client_secret': client_secret,
})

auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']
headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}


# GLOBAL VARIABLES
artist_id = ''
artist_JSON = {}


# SEARCH AND RETURN

def artist_getid():


    #Function Variables
    global artist_id
    ret_query_list = []
    selection = ''

    #Search and return results
    search_q = input('What Artist Would You Like To Search For?\n')
    while len(search_q) == 0:
        search_q = input('Please enter an artist name: \n')
    search_q = search_q.replace(' ', '+')

    data = requests.get(f'https://api.spotify.com/v1/search?query={search_q}&limit=10&type=artist', headers=headers)
    data = data.json()

    for i in data['artists']['items']:
        ret_query_list.append(i['name'])


    #Return ID if only one item is returned
    if len(ret_query_list) == 1:
        artist_id = data['artists']['items'][0]['id']

    #Select item if multiple items returned
    if len(ret_query_list) >= 1:
        print('\nHere are the artists that are the closest match for your search:\n')
        for i in ret_query_list:
            print(f'{(ret_query_list.index(i) + 1)}: {i}\n')
        selection = input('Please select the number of the artist you wanted to search for from the above list: ')
        while selection.isnumeric() == False:
            for i in ret_query_list:
                print(f'{(ret_query_list.index(i) + 1)}: {i}\n')
            selection = input('Please only input a number no greater than 10 from the above list in numeric format (i.e. "1", "7"): ')
            continue
        while int(selection) not in range(1,11):
            for i in ret_query_list:
                print(f'{(ret_query_list.index(i) + 1)}: {i}\n')
            selection = input('Please only input a number no greater than 10 from the above list in numeric format (i.e. "1", "7"): ')
            continue

        else:
            artist_id = data['artists']['items'][int(selection.strip()) - 1]['id']
            artist_name = data['artists']['items'][int(selection.strip()) - 1]['name']
            print(f'You\'ve selected "{artist_name}"!\n')


def artist_search(id_no):
    global artist_JSON
    artist_JSON = requests.get(f'https://api.spotify.com/v1/artists/{id_no}', headers=headers)
    artist_JSON = artist_JSON.json()


def artist_print():

    name = artist_JSON['name']
    genres = artist_JSON['genres']
    followers = artist_JSON['followers']['total']
    popularity = artist_JSON['popularity']

    if len(genres) == 1:
        print(f'{name} makes {genres[0]} music and has {followers} spotify followers\n')
    elif len(genres) >= 2:
        genres = (', '.join(genres))
        print(f'{name} makes music that can be described as {genres} music and has {followers} spotify followers\n')
    print(f'This artist has a overall popularity rating of {popularity} out of 100\n')


def artist_options():

    name = artist_JSON['name']

    user_input = input(f'''\n\nWhat would you like to do next?
    1 - Get a list of {name}'s albums.
    2 - Get a list of {name}'s most popular tracks (in the U.S.).
    3 - Get a list of {name}'s related artists.
    4 - Get in depth analysis of this artists {name}'s most popular tracks compared to the most popular tracks in the US.
    5 - Launch {name}'s spotify page in your browser.
    6 - Display some of the album artwork for {name} in your browser.
    7 - Check to see if there are any mentions of {name} on twitter.
    8 - Search for a different artist.
    ''')

    while user_input.isnumeric() == False:
        user_input = input('Please only input a number from 1 - 8 from the above list in numeric format (i.e. "1", "7"): ')
        continue
    while int(user_input) not in range(1,9):
        user_input = input('Please only input a number from 1 - 8 from the above list in numeric format (i.e. "1", "7"): ')
        continue

    return int(user_input)

def option_1():
    name = artist_JSON['name']

    artist_albums = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}/albums', headers=headers)
    artist_albums = artist_albums.json()

    print(f'Here is a list of {name}\'s albums:\n')
    for i in artist_albums['items']:
        album = i['name']
        track_count = i['total_tracks']
        print(f'"{album}", with a total of {track_count} tracks')


def option_2():
    name = artist_JSON['name']

    top_tracks = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US', headers=headers)
    top_tracks = top_tracks.json()

    print(f'Here is a list of {name}\'s most popular tracks:\n')

    for i in top_tracks['tracks']:
        track = i['name']
        album = i['album']['name']
        print(f'"{track}" from the album {album}')

def option_3():
    name = artist_JSON['name']

    related_artists = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}/related-artists', headers=headers)
    related_artists = related_artists.json()

    print(f'Artists that are similar to {name} include:\n')

    for i in related_artists['artists']:
        print(i['name'])

def option_4():

    #Variables
    popular_tracks = []
    popular_track_features = {}
    artists_tracks = []
    artists_track_features = {}
    track_string = ''

    #Build a list of Popular Track IDs
    data = requests.get(f'https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF/tracks', headers=headers)
    data = data.json()
    for i in data['items']:
        popular_tracks.append(i['track']['id'])

    #Build a list of Artist Track IDs
    data = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US', headers=headers)
    data = data.json()

    for i in data['tracks']:
        artists_tracks.append(i['id'])

    #Request for track features and build 2x JSON objects
    for i in popular_tracks:
        track_string += i
        track_string += ','
    track_string = track_string[:-1]

    data = requests.get(f'https://api.spotify.com/v1/audio-features?ids={track_string}', headers=headers)
    popular_track_features = data.json()
    popular_track_features['audio_features'] = list(filter(None, popular_track_features['audio_features']))

    for i in artists_tracks:
        track_string += i
        track_string += ','
    track_string = track_string[:-1]

    data = requests.get(f'https://api.spotify.com/v1/audio-features?ids={track_string}', headers=headers)
    artists_track_features = data.json()
    artists_track_features['audio_features'] = list(filter(None, artists_track_features['audio_features']))




    #Visualization Variables

    pop_danceability = []
    art_danceability = []
    pop_energy = []
    art_energy = []
    pop_speechiness = []
    art_speechiness = []
    pop_instrumentalness = []
    art_instrumentalness = []
    pop_loudness = []
    art_loudness = []
    pop_acousticness = []
    art_acousticness = []
    pop_valence = []
    art_valence = []
    pop_tempo = []
    art_tempo = []

    #Artists Track features lists for visualization

    for i in popular_track_features['audio_features']:
        pop_danceability.append(i['danceability'])

    for i in popular_track_features['audio_features']:
        pop_energy.append(i['energy'])

    for i in popular_track_features['audio_features']:
        pop_speechiness.append(i['speechiness'])

    for i in popular_track_features['audio_features']:
        pop_instrumentalness.append(i['instrumentalness'])

    for i in popular_track_features['audio_features']:
        pop_loudness.append(i['loudness'])

    for i in popular_track_features['audio_features']:
        pop_acousticness.append(i['acousticness'])

    for i in popular_track_features['audio_features']:
        pop_valence.append(i['valence'])

    for i in popular_track_features['audio_features']:
        pop_tempo.append(i['tempo'])

    #Artists Track features lists for visualization

    for i in artists_track_features['audio_features']:
        art_danceability.append(i['danceability'])

    for i in artists_track_features['audio_features']:
        art_energy.append(i['energy'])

    for i in artists_track_features['audio_features']:
        art_speechiness.append(i['speechiness'])

    for i in artists_track_features['audio_features']:
        art_instrumentalness.append(i['instrumentalness'])

    for i in artists_track_features['audio_features']:
        art_loudness.append(i['loudness'])

    for i in artists_track_features['audio_features']:
        art_acousticness.append(i['acousticness'])

    for i in artists_track_features['audio_features']:
        art_valence.append(i['valence'])

    for i in artists_track_features['audio_features']:
        art_tempo.append(i['tempo'])


    #Visualization

    fig, axs = plt.subplots(2, 2, figsize = (10, 10))

    axs[0,0].scatter(x=art_danceability, y=art_energy, c='red', alpha=.5)
    axs[0,0].scatter(x=pop_danceability, y=pop_energy, c='black', alpha=1)
    axs[0,0].set_title('Danceability vs Energy')
    axs[0,0].set_xlabel('Danceability')
    axs[0,0].set_ylabel('Energy')

    axs[0,1].scatter(x=art_speechiness, y=art_instrumentalness, c='red', alpha=.5)
    axs[0,1].scatter(x=pop_speechiness, y=pop_instrumentalness, c='black', alpha=1)
    axs[0,1].set_title('Speechiness vs Instrumentalness')
    axs[0,1].set_xlabel('Speechiness')
    axs[0,1].set_ylabel('Instrumentalness')

    axs[1,0].scatter(x=art_loudness, y=art_acousticness, c='red', alpha=.5)
    axs[1,0].scatter(x=pop_loudness, y=pop_acousticness, c='black', alpha=1)
    axs[1,0].set_title('Loundness vs Acousticness')
    axs[1,0].set_xlabel('Loundness')
    axs[1,0].set_ylabel('Acousticness')

    axs[1,1].scatter(x=art_valence, y=art_tempo, c='red', alpha=.5)
    axs[1,1].scatter(x=pop_valence, y=pop_tempo, c='black', alpha=1)
    axs[1,1].set_title('Positivity vs Tempo')
    axs[1,1].set_xlabel('Positivity')
    axs[1,1].set_ylabel('Tempo')

    fig.legend(labels=['Popular US Tracks', 'Artist Top Tracks'], loc='upper center')
    plt.tight_layout()
    plt.show()



def option_5():
    url5 = artist_JSON['external_urls']['spotify']
    webbrowser.open(url5, new=2)

def option_6():

    artist_albums = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}/albums', headers=headers)
    artist_albums = artist_albums.json()

    for i in artist_albums['items']:
        url6 = i['images'][0]['url']
        webbrowser.open(url6, new=2)

def option_7():
    tw_client_key = secrets.TWITTER_API_KEY
    tw_client_secret = secrets.TWITTER_API_SECRET
    tw_access_token = secrets.TWITTER_ACCESS_TOKEN
    tw_access_token_secret = secrets.TWITTER_ACCESS_TOKEN_SECRET

    oauth = OAuth1(tw_client_key,
            client_secret=tw_client_secret,
            resource_owner_key=tw_access_token,
            resource_owner_secret=tw_access_token_secret)


    name = artist_JSON['name']
    name_hash = name.replace(' ','')
    baseurl = "https://api.twitter.com/1.1/search/tweets.json"
    hashtag = f"#{name_hash}"
    count = 50
    params = {'q':hashtag, 'count':count}

    tweet_data = requests.get(baseurl, params=params, auth=oauth)
    tweet_data = tweet_data.json()

    print(f'Here is a list of 50 tweets that mention {name}')
    for i in tweet_data['statuses']:
        tweeter = i['user']['name']
        print('\n----------------------------------\n')
        print(f'User "{tweeter}" wrote:')
        print(i['text'])


def function_loop1():
    artist_getid()
    artist_search(artist_id)
    artist_print()

def function_loop2():
    while True:
        option = artist_options()
        if option == 8:
            break
        elif option != 8:
            if option == 1:
                option_1()
            elif option == 2:
                option_2()
            elif option == 3:
                option_3()
            elif option == 4:
                option_4()
            elif option == 5:
                option_5()
            elif option == 6:
                option_6()
            elif option == 7:
                option_7()
            continue

def function_loop():
    while True:
        function_loop1()
        function_loop2()
        continue


if __name__ == "__main__":
    function_loop()