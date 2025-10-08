import time
from guy import Guy, http
from sys import platform
import os
import subprocess
import pywinctl as pwc
import pymonctl as pmon
import asyncio
import json
import media
import datetime
import vlc

def open_chrome(url):
    if platform == 'win32':
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        command = [chrome_path, '--new-window', '--app=' + url]
    
    elif platform == "linux":
        # Use 'google-chrome' or 'chromium-browser' depending on install
        for chrome_cmd in ['google-chrome', 'chromium-browser', 'chromium']:
            if subprocess.call(['which', chrome_cmd], stdout=subprocess.DEVNULL) == 0:
                command = [chrome_cmd, '--new-window', '--app=' + url]
                break
        else:
            raise FileNotFoundError("Chrome/Chromium not found on Linux system.")
    
    else:
        raise OSError("Unsupported operating system.")

    subprocess.Popen(command)

is_shrunk = False

is_hidden = False

class index(Guy):

    async def init(self):
        global is_hidden
        global monitor
        global gui_window
        is_hidden = False
        print('test')
        media.set_app_instance(self)
        self.main_loop = self.get_running_async_loop()
        # get handle of the chrome window running the gui
        time.sleep(1)
        gui_window = pwc.getWindowsWithTitle('Media Center Deluxe')[0]
        display = gui_window.getDisplay()[0]
        monitor = pmon.findMonitorWithName(display)
        if (monitor == None):
            monitor = pmon.getAllMonitors()[0]
        # make sure window is in expanded mode
        self.expand_gui()
        #self.shrink_gui()
        self.load_settings()
        # initialize js and pass it the settings
        await self.js.init(self.settings)

    # get the current running async loop, or None if there isn't one
    def get_running_async_loop(self):
        try:
            loop = asyncio.get_running_loop()
            return loop
        except RuntimeError:  # 'RuntimeError: There is no current event loop...'
            return None

    # bring the chrome gui window to the front
    def bring_gui_front(self):
        global gui_window
        global is_hidden
        print(is_hidden)
        if (not is_hidden):
            gui_window.raiseWindow()

    def bring_vid_front(self):
        print('bring vid front')
        #if (media.playing == 'video'):
        #    vid_window = self.find_vlc_vid_window()
        #    if (vid_window != None):
        #        vid_window.raiseWindow()
        global gui_window
        gui_window.lowerWindow()

    # return whether the gui is in shrunk mode or not, for use in js
    def get_shrunk_status(self):
        global is_shrunk
        return is_shrunk

    # toggle between shrunk and expanded gui, while storing the state
    def toggle_gui(self):
        global is_shrunk
        if (is_shrunk):
            self.expand_gui()
        else:
            self.shrink_gui()

    # shrink the gui to a single strip showing only the media controls
    def shrink_gui(self):
        global gui_window
        global is_shrunk
        global monitor
        is_shrunk = True
        # rect(x, y, right, bottom)
        gui_window.rect = monitor.rect
        gui_window.height = 110
        if (platform == 'win32'):
            gui_window.bottom = monitor.workarea[3]
        elif (platform == 'linux'):
            # TODO adjust height and add padding
            gui_window.bottom = monitor.rect[3]
        self.bring_gui_front()
        self.get_running_async_loop().create_task(self.emit('change_chevron', 'up'))

    # expand the gui window to full screen
    def expand_gui(self):
        global is_shrunk
        global is_shrunk
        global monitor
        is_shrunk = False
        # rect(x, y, right, bottom)
        if (platform == 'win32'):
            gui_window.rect = monitor.workarea
        elif (platform == 'linux'):
            # TODO add padding around for title bar
            gui_window.rect = monitor.rect
        self.bring_gui_front()
        media.btn_input()
        self.get_running_async_loop().create_task(self.emit('change_chevron', 'down'))

    def find_vlc_vid_window(self):
        vlc_window = None
        while vlc_window == None:
            try:
                vlc_window = pwc.getWindowsWithTitle('vlc', condition=pwc.Re.CONTAINS, flags=pwc.Re.IGNORECASE)[0]
            except:
                time.sleep(1)
        return vlc_window

    def move_vlc_window(self):
        global monitor
        vid_window = self.find_vlc_vid_window()
        if (vid_window != None):
            vid_window.restore()
            print('moving vlc window')
            if (platform == 'win32'):
                vid_window.rect = monitor.workarea
            elif (platform == 'linux'):
                # TODO add padding around for title bar
                vid_window.rect = monitor.rect

    # load settings from ini file
    def load_settings(self):
        ini_file = open('./saved_lists/settings.ini', 'r')
        contents = ini_file.read()
        ini_file.close()
        data = json.loads(contents)
        self.settings = data

    # save settings to ini file
    def save_settings(self):
        print('need to add')

    # read the contents of a folder and return them as a list, with folders first
    def read_folder(self, path):
        folders = []
        files = []
        for entry in sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name)):
            if entry.is_dir():
                folder_item = {
                    'name': entry.name,
                    'type': 'folder',
                    'path': entry.path
                }
                folders.append(folder_item)
            else:
                file_item = {
                    'name': entry.name,
                    'type': os.path.splitext(entry.name)[1][1:],  # get file extension without dot
                    'path': entry.path
                }
                files.append(file_item)
        return folders + files
    
    async def handle_media(self, path, action):
        media.handle_media(path, action)
        time.sleep(0.5) # wait a moment for vlc to start playing
        await self.render_playing_notif()

    async def ctl_player(self, action):
        await self.emit('change_playpause', media.ctl_player(action))
    
    async def renderProgBar(self):
        len = str(datetime.timedelta(milliseconds=media.media_player.get_length()))[:-7]
        pos = round(media.media_player.get_position() * 100, 3)
        time_at = str(datetime.timedelta(milliseconds=media.media_player.get_time()))[:-7]
        await self.emit('render_prog', len, pos, time_at)
        await asyncio.sleep(0.5) # throttle updates to twice a second

    async def render_playing_notif(self):
        curr_media = self.get_curr_media()
        name = os.path.splitext(curr_media.get_meta(vlc.Meta.Title))[0]
        await self.emit('render_playing_notif', name)

    def get_playlist(self):
        return media.get_playlist()
        
    def get_curr_media(self):
        return media.get_curr_media()


open_chrome('http://127.0.0.1:9090')
app = index()
app.serve(port=9090, open=False)
