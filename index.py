import vlc
import time
from guy import Guy, http
from sys import platform
import os
import subprocess
import pywinctl as pwc
import pymonctl as pmon
import asyncio
import json

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
            loop = None

    # bring the chrome gui window to the front
    def bring_gui_front(self):
        global gui_window
        global is_hidden
        if (not is_hidden):
            gui_window.raiseWindow()

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
        self.get_running_async_loop().create_task(self.emit('change_chevron', 'down'))

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
                    'type': 'file',
                    'path': entry.path
                }
                files.append(file_item)
        return folders + files


open_chrome('http://127.0.0.1:9090')
app = index()
app.serve(port=9090, open=False)
