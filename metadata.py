import os
import requests
import time
import json

tmdb_api_key = '7367e424c44bfc1f6fa68e01e9c7e575'

app_instance = None

def set_app_instance(app):
    global app_instance
    app_instance = app

def search_tmdb(media_type, file_name, id = False, num_results = 1):
    # if id is provided, make url with id
    if (id):
        if (media_type == 'movie'):
            url = 'https://api.themoviedb.org/3/movie/' + file_name
            params = {'api_key': tmdb_api_key, 'language': 'en-US'}
        elif (media_type == 'show'):
            url = 'https://api.themoviedb.org/3/tv/' + file_name
            params = {'api_key': tmdb_api_key, 'language': 'en-US'}
    # otherwise, make url with file name
    else:
        file_name = os.path.splitext(file_name)[0].lower().translate(dict.fromkeys(map(ord, u',\'')))
        # if name has a year, make url search with title and year
        if (file_name[-4:].isdigit()):
            year = file_name[-4:]
            file_name = file_name[:-5]

            if (media_type == 'movie'):
                url = 'https://api.themoviedb.org/3/search/movie'
                params = {'api_key': tmdb_api_key, 'language': 'en-US', 'query': file_name, 'primary_release_year': year}
            elif (media_type == 'show'):
                url = 'https://api.themoviedb.org/3/search/tv'
                params = {'api_key': tmdb_api_key, 'language': 'en-US', 'query': file_name, 'primary_release_year': year}
        # otherwise, make url search with title only
        else:
            if (media_type == 'movie'):
                url = 'https://api.themoviedb.org/3/search/movie'
                params = {'api_key': tmdb_api_key, 'language': 'en-US', 'query': file_name}
            elif (media_type == 'show'):
                url = 'https://api.themoviedb.org/3/search/tv'
                params = {'api_key': tmdb_api_key, 'language': 'en-US', 'query': file_name}

    # make API request

    #print(url + str(params))
    response = requests.get(url, params).json()

    correct_movie = None
    print("|" + file_name + "|")
    print(response)

    # if a name, not id, is provided, we are searching and must check
    if (not id):
        # if a search result matches the file name exactly use that metadata
        # (must check if movie or show because of tmdb dict names)
        if (media_type == 'movie'):
            for movie in response['results']:
                movie_name = movie['original_title'].translate(dict.fromkeys(map(ord, u',\':*?<>|'))).lower()
                if (movie_name == file_name):
                    correct_movie = movie
                    break
                else:
                    continue
        elif (media_type == 'show'):
            for show in response['results']:
                show_name = show['original_name'].translate(dict.fromkeys(map(ord, u',\':*?<>|'))).lower()
                if (show_name == file_name):
                    correct_movie = show
                    break
                else:
                    continue

    time.sleep(0.1)

    # if looking for more than one result, return all
    if (num_results > 1 and not id):
        if (len(response['results']) == 0):
            return None
        else:
            return response['results'][:(num_results+1)]
    # otherwise give the perfect match (if found)
    elif (not correct_movie == None):
        print(correct_movie)
        return correct_movie
    # otherwise return first found
    else:
        try:
            if (id):
                return response
            else:
                if (len(response['results']) == 0):
                    return None
                else:
                    return response['results'][0]
        except:
            return None
        
# get a list of all files in a folder and subfolders
def scan_files(path):
    files = []
    for item in app_instance.read_folder(path):
        if (item['type'] == 'folder'):
            files += scan_files(item['path'])
        else:
            files.append(item)
    return files

def read_file(file_path):
    file = open(file_path, 'r', encoding='utf8')
    data = json.loads(file.read())
    file.close()
    return data

def write_file(file_path, data, bytes = False):
    if (bytes):
        with open(file_path, 'wb') as file:
            file.write(data)
            file.close()
    else:
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(data)
            file.close()

# ADD ERRORING OUT FROM NO INTERNET OR ECT
def dwnload_metadata(media_type, path):
    if (media_type == 'movie'):
        # get the movies in the path
        movies = scan_files(path)

        # loop through each movie file
        for movie in movies:
            path_start = './static/cached_metadata/movies/' + movie['name']
            # check if metadata is already cached
            if (os.path.isfile(path_start + '_txt.json')):
                saved_metadata = read_file(path_start + '_txt.json')
                # get the new metadata from tmdb using id, since it's already cached
                new_metadata = search_tmdb('movie', saved_metadata['id'], True)
            else:
                # get the new metadata from tmdb using file name
                new_metadata = search_tmdb('movie', movie['name'])

            # if metadata exists for the movie, download it to the cache
            if (not new_metadata == None):
                img_data = requests.get('https://image.tmdb.org/t/p/w500' + new_metadata['poster_path']).content
                write_file(path_start + '_img.jpg', img_data, True)

                # store and write the text metadata to the cache file
                new_metadata = "{\"title\": \"" + new_metadata['original_title'] + "\",\"date\": \"" + new_metadata['release_date'] + "\",\"id\": \"" + str(new_metadata['id']) + "\",\"desc\": \"" + new_metadata['overview'].replace('"', '\\"').replace('\n', '\\n').replace('\u200b', ' ') + "\"}"
                write_file(path_start + '_txt.json', new_metadata)

    elif (media_type == 'show'):
        # get the shows in the path
        for show in app_instance.read_folder(path):
            if (show['type'] == 'folder'):
                if (not 'season' in show['name'].lower()):

                    path_start = './static/cached_metadata/shows/' + show['name'] + '/'
                    # check if metadata is already cached
                    if (os.path.isfile(path_start + 'txt.json')):
                        saved_metadata = read_file(path_start + 'txt.json')
                        # get the new metadata from tmdb using id, since it's already cached
                        new_metadata = search_tmdb('show', saved_metadata['id'], True)
                    else:
                        os.makedirs(path_start)
                        # get the new metadata from tmdb using file name
                        new_metadata = search_tmdb('show', show['name'])
                        if (not new_metadata == None):
                            new_metadata = search_tmdb('show', str(new_metadata['id']), True)

                    # if metadata exists for the movie, download it to the cache
                    if (not new_metadata == None):
                        if (not new_metadata['poster_path'] == None):
                            img_data = requests.get('https://image.tmdb.org/t/p/w500' + new_metadata['poster_path']).content
                            write_file(path_start + 'img.jpg', img_data, True)

                        # store and write the text metadata to the cache file
                        to_write = "{\"title\": \"" + new_metadata['original_name'] + "\",\"date\": \"" + new_metadata['first_air_date'] + "\",\"id\": \"" + str(new_metadata['id']) + "\",\"desc\": \"" + new_metadata['overview'].replace('"', '\\"').replace('\n', '\\n').replace('\u200b', ' ') + "\"}"
                        write_file(path_start + 'txt.json', to_write)

                        for season in new_metadata['seasons']:
                            # make sure the folder is made for the season
                            os.makedirs(path_start + 'season_' + str(season['season_number']), exist_ok=True)
    
                            if (not season['poster_path'] == None):
                                img_data = requests.get('https://image.tmdb.org/t/p/w500' + season['poster_path']).content
                                write_file(path_start + 'season_' + str(season['season_number']) + '/img.jpg', img_data, True)
    
                            # store and write the text metadata to the cache file
                            to_write = "{\"title\": \"" + season['name'] + "\",\"id\": \"" + str(season['id']) + "\",\"desc\": \"" + season['overview'].replace('"', '\\"').replace('\n', '\\n').replace('\u200b', ' ') + "\"}"
                            write_file(path_start + 'season_' + str(season['season_number']) + '/txt.json', to_write)
    
    
                            url = 'https://api.themoviedb.org/3/tv/' + str(new_metadata['id']) + '/season/' + str(season['season_number'])
                            params = {'api_key': tmdb_api_key, 'language': 'en-US'}
    
                            response = requests.get(url, params).json()
                            for episode in response['episodes']:
                                if (not episode['still_path'] == None):
                                    img_data = requests.get('https://image.tmdb.org/t/p/w500' + episode['still_path']).content
                                    write_file(path_start + 'season_' + str(season['season_number']) + '/' + str(episode['episode_number']) + '_img.jpg', img_data, True)
    
                                # store and write the text metadata to the cache file
                                to_write = "{\"title\": \"" + episode['name'] + "\",\"id\": \"" + str(episode['episode_number']) + "\",\"desc\": \"" + season['overview'].replace('"', '\\"').replace('\n', '\\n').replace('\u200b', ' ') + "\"}"
                                write_file(path_start + 'season_' + str(season['season_number']) + '/' + str(episode['episode_number']) + '_txt.json', to_write)

                        
