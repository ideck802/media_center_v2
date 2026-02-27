import re
import os
from pathlib import Path

app = None

def set_app_instance(app_instance):
    global app
    app = app_instance


def get_watched_name(name, type = None):
    if (type == 's'):
        # if its a season
        return name.lower().replace('season ', 's')
    elif (type == 'e'):
        # if its an episode
        if match := re.search(r'.*?e(\d+).*', name.lower()):
            return 'e' + match.group(1)
    else:
        # if any other, like movie or show
        return os.path.splitext(name.lower())[0].replace(' ', '-').replace("'", '')


def get_parent(path, ancestor = 0):
    path = Path(path)
    if (ancestor == 'self'):
        return path.name
    else:
        return path.parents[ancestor].name


def set_season_watch(path, watched, set_all):
    name = get_parent(path, 'self')

    show = get_watched_name(get_parent(path))
    season = get_watched_name(name, 's')

    # make season and show entries if they don't exist
    app.watched_list.setdefault(show, {}) \
            .setdefault(season, {})
    
    app.watched_list[show][season]['watched'] = watched
    
    if (set_all):
        # set all episodes in season to watched/unwatched
        episodes = app.read_folder(path)
        for ep in episodes:
            app.watched_list[show][season][get_watched_name(ep['name'], 'e')] = watched

    if (watched):
        seasons = app.read_folder(str(Path(path).parent))
        set_show = True

        # if setting season to watched, and all seasons are watched, set the show to watched too
        for sson in app.watched_list[show].keys():
            if (sson != 'watched'):
                stored = sum(
                    1 for item in app.watched_list[show]
                    if 'watched' not in item
                )
                if ('watched' not in app.watched_list[show][sson]):
                    set_show = False
                elif ((app.watched_list[show][sson]['watched'] != True) or
                    stored != len(seasons)):
                    print(app.watched_list[show][sson]['watched'])
                    set_show = False
        if (set_show):
            print('setting show')
            set_show_watch(str(Path(path).parent), True, False)
    else:
        # if unwatching a season, unwatch the show too
        app.watched_list[show]['watched'] = False


def set_episode_watch(path, watched, set_all):
    name = get_parent(path, 'self')

    show = get_watched_name(get_parent(path, 1))
    season = get_watched_name(get_parent(path), 's')

    # make season and show entries if they don't exist
    app.watched_list.setdefault(show, {}) \
            .setdefault(season, {})
    
    # set episode watched status
    app.watched_list[show][season][get_watched_name(name, 'e')] = watched

    # if setting episode to watched
    if (watched):
        episode_keys = [
            k for k in app.watched_list[show][season]
            if k.startswith("e") and k[1:].isdigit()
        ]
        # check if all episodes in season are watched
        if (all(app.watched_list[show][season][k] is True for k in episode_keys)):
            # and all episodes are in the saved data
            episodes = app.read_folder(str(Path(path).parent))
            stored = sum(
                1 for item in app.watched_list[show][season]
                if 'watched' not in item
            )
            if (stored == len(episodes)):
                # set season to watched
                set_season_watch(str(Path(path).parent), True, False)
    else:
        # if unwatching an episode, unwatch the season too
        app.watched_list[show][season]['watched'] = False


def set_show_watch(path, watched, set_all):
    name = get_parent(path, 'self')

    # set show watched status
    app.watched_list[get_watched_name(name)]['watched'] = watched

    if (set_all):
        # if setting show to watched, set all seasons and episodes to watched too
        seasons = app.read_folder(path)
        for sson in seasons:
            if (sson['type'] == 'folder'):
                set_season_watch(sson['path'], watched, set_all)

async def set_watched(path, watched=True):
    name = get_parent(path, 'self')

    if ('season' in name.lower()):
        # if its a season
        set_season_watch(path, watched, True)
    elif ('season' in get_parent(path).lower()):
        # if its an episode
        set_episode_watch(path, watched, False)
    elif (Path(path).suffix):
        # if its a movie file
        app.watched_list[get_watched_name(name)] = watched
    else:
        # if its the root show folder
        set_show_watch(path, watched, True)
    app.save_watched()
    await app.emit('draw_browse', str(Path(path).parent).replace('\\', '/'))