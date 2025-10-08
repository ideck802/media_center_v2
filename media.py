import vlc
import os
import time
from sys import platform
import threading
import pywinctl as pwc
if platform == 'win32':
    from ctypes import windll
from pynput import keyboard
import asyncio

app_instance = None

playing = 'nothing'

def set_app_instance(app):
    global app_instance
    app_instance = app

# initialize vlc backend and establish playlist variable
vlc_inst = vlc.Instance()
media_player = vlc_inst.media_player_new()
media_list_player = vlc_inst.media_list_player_new()
playlist = vlc_inst.media_list_new()
media_list_player.set_media_list(playlist)
media_list_player.set_media_player(media_player)

def toggle_taskbar(act):
    if (act == 'hide'):
        windll.user32.ShowWindow(windll.user32.FindWindowA(b'Shell_TrayWnd', None), 0)
    elif (act == 'show'):
        windll.user32.ShowWindow(windll.user32.FindWindowA(b'Shell_TrayWnd', None), 9)

def btn_input():
    global pos_same_count
    pos_same_count = -2

listener = keyboard.Listener(on_press=btn_input)
listener.start()

def watch_mouse():
    global is_hidden
    global pos_same_count
    time.sleep(5)
    xpos = 0
    ypos = 0
    pos_same_count = 0
    is_hidden = False
    while True:
        if (playing == 'video'):
            # get cursor current position
            mousepos = pwc.getMousePos()
            # if in the same position as last check count up
            if (xpos == mousepos.x and ypos == mousepos.y):
                pos_same_count += 1
            # otherwise if has moved reset count and show the gui window
            else:
                pos_same_count = 0
            
            if (pos_same_count <= 0 and is_hidden):
                #show gui window
                print('show gui')
                app_instance.bring_gui_front()
                is_hidden = False
            # bookmark postition
            xpos = mousepos.x
            ypos = mousepos.y
            # when not moved for long enough (hence the counter) hide the gui window
            # (only when a video is playing)
            if (pos_same_count == 2):
                #hide gui window
                app_instance.bring_vid_front()
                is_hidden = True
        time.sleep(1)

mouse_thread = mouse_thread = threading.Thread(target=watch_mouse)
mouse_thread.start()

def renderProgPass(event):
    asyncio.run_coroutine_threadsafe(app_instance.renderProgBar(), app_instance.main_loop)

def render_playing_notif(event):
    asyncio.run_coroutine_threadsafe(app_instance.render_playing_notif(), app_instance.main_loop)

vlc_event_manager = media_player.event_manager()
vlc_event_manager.event_attach(vlc.EventType.MediaPlayerTimeChanged, renderProgPass)
vlc_event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, render_playing_notif)

def clear_playlist():
    global playlist
    playlist = vlc_inst.media_list_new()
    media_list_player.set_media_list(playlist)

def handle_media(path, action):
    if ('play' in action):
        media_list_player.stop()
        clear_playlist()
    if (os.path.isdir(path)):
        filetype = None
        for file in sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name)):
            if file.is_file():
                filetype = os.path.splitext(file.name)[1][1:].lower()
                playlist.add_media(vlc_inst.media_new(file.path))
        if (not playing in ['audio', 'video']):
            start_player(filetype)
    else:
        playlist.add_media(vlc_inst.media_new(path))
        if (not playing in ['audio', 'video']):
            ext = os.path.splitext(path)[1][1:].lower()
            start_player(ext)

def start_player(filetype):
    global playing
    if filetype in ['mp3', 'wav', 'flac', 'aac', 'ogg']:
        playing = 'audio'
        media_list_player.play()
    elif filetype in ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'm4v']:
        media_list_player.play()
        time.sleep(1)  # wait a moment for VLC to start
        media_player.set_fullscreen(False)
        app_instance.move_vlc_window()
        app_instance.shrink_gui()
        playing = 'video'
        media_player.set_fullscreen(True)
        app_instance.bring_gui_front()
        toggle_taskbar('hide')

def get_playlist():
    media_files = []
    cur_playing_media = get_curr_media().get_mrl()
    if (cur_playing_media != None):
        for i in range(playlist.count()):
            media = playlist.item_at_index(i)
            if (media.get_mrl() == cur_playing_media):
                is_playing = True
                timeAt = round(media_player.get_time()/1000)
            else:
                is_playing = False
                timeAt = 0
            media_info = {
                'name': os.path.splitext(media.get_meta(vlc.Meta.Title))[0],
                'path': media.get_mrl(),
                'isPlaying': is_playing,
                'time': timeAt
            }
            media_files.append(media_info)
        return media_files
    else:
        return []

def get_curr_media():
    try:
        return media_player.get_media()
    except:
        return None


def ctl_player(action):
    global playing
    if action == 'play':
        media_list_player.play()
        if (playing == 'video' or playing == 'paused_vid'):
                playing = 'video'
                toggle_taskbar('hide')
        return 'play'
    elif action == 'pause':
        player_state = media_player.get_state()
        if (player_state == vlc.State.Playing):
            media_list_player.pause()
            if (playing == 'video'):
                playing = 'paused_vid'
            else:
                playing = 'paused_aud'
            app_instance.bring_gui_front()
            toggle_taskbar('show')
            return 'pause'
        else:
            media_list_player.play()
            if (playing == 'video' or playing == 'paused_vid'):
                playing = 'video'
                toggle_taskbar('hide')
            return 'play'
    elif action == 'stop':
        media_list_player.stop()
        playing = 'nothing'
        toggle_taskbar('show')
        app_instance.expand_gui()
        return 'pause'
    elif action == 'next':
        media_list_player.next()
        return 'play'
    elif action == 'prev':
        media_list_player.previous()
        return 'play'