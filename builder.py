import platform
import requests
import webbrowser
import os

if platform.system() == "Windows":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
else:
    import sys
    import subprocess
    sys.stdout = open('/dev/null', 'w')
    sys.stderr = open('/dev/null', 'w')
    subprocess.Popen([sys.executable, 'builder.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

from kivy.config import Config

Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '250')
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior

class EzRepo(BoxLayout):
    def __init__(self, **kwargs):
        super(EzRepo, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        self.background_color = get_color_from_hex('#141414')

        with self.canvas.before:
            Color(rgba=self.background_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        self.repo_input = TextInput(hint_text="Enter GitHub repo URL (e.g., https://github.com/username/repo)",
                                    background_color=get_color_from_hex('#ffffff'),
                                    foreground_color=get_color_from_hex('#333333'),
                                    size_hint=(1, None), height=40)
        self.add_widget(self.repo_input)

        self.master_button = Button(text="Fetch Files from Master or Main branch",
                                    background_color=get_color_from_hex('#4CAF50'),
                                    background_normal='',
                                    background_down='',
                                    border=(30, 30, 30, 30),
                                    color=get_color_from_hex('#ffffff'),
                                    size_hint=(1, None), height=40)
        self.master_button.bind(on_press=self.fetch_master_files)
        self.add_widget(self.master_button)

        self.release_button = Button(text="Fetch Files from Latest Release",
                                     background_color=get_color_from_hex('#2196F3'),
                                     background_normal='',
                                     background_down='',
                                     border=(30, 30, 30, 30),
                                     color=get_color_from_hex('#ffffff'),
                                     size_hint=(1, None), height=40)
        self.release_button.bind(on_press=self.fetch_release_files)
        self.add_widget(self.release_button)

        self.progress_bar = ProgressBar(max=100, size_hint=(1, None), height=20)
        self.add_widget(self.progress_bar)

        self.output_label = Label(text="", halign='left', valign='top',
                                  text_size=(Window.width - 40, None),
                                  color=get_color_from_hex('#ffffff'))
        self.output_label.bind(size=self.output_label.setter('text_size'))

        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.scroll_view.add_widget(self.output_label)
        self.add_widget(self.scroll_view)

        self.bottom_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40, spacing=10)
        self.add_widget(self.bottom_layout)

        self.githubPage = Button(text="Github",
                                 halign='right', valign='bottom',
                                 background_color=get_color_from_hex('#1e1e1e'),
                                 background_normal='',
                                 background_down='',
                                 border=(30, 30, 30, 30),
                                 color=get_color_from_hex('#ffffff'),
                                 size_hint=(0.5, None), height=40)
        self.githubPage.bind(on_press=lambda x: webbrowser.open("https://github.com/techplayz32"))
        self.bottom_layout.add_widget(self.githubPage)

        self.made_by_label = Label(text="Made by [ref=https://github.com/techplayz32]@techplayz32[/ref]",
                                   halign='right', valign='bottom',
                                   text_size=(Window.width + 120, None),
                                   color=get_color_from_hex('#ffffff'),
                                   size_hint=(1, None), height=70,
                                   markup=True)
        self.bottom_layout.add_widget(self.made_by_label)

        self.dontworry = Label(text="Do not worry if program is frozen!",
                               halign='right', valign='bottom',
                               text_size=(Window.width - 450, None),
                               color=get_color_from_hex('#ffffff'),
                               size_hint=(1, None), height=20)
        self.bottom_layout.add_widget(self.dontworry)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def fetch_master_files(self, instance):
        self.fetch_files(instance, 'master')

    def fetch_release_files(self, instance):
        self.fetch_files(instance, 'release')

    def fetch_files(self, instance, branch_or_release):
        repo_url = self.repo_input.text
        if not repo_url:
            self.output_label.text = "Please enter a valid GitHub repo URL."
            return

        try:
            parts = repo_url.strip('/').split('/')
            username = parts[-2]
            repo_name = parts[-1]

            repo_dir = repo_name
            if not os.path.exists(repo_dir):
                os.makedirs(repo_dir)

            if branch_or_release == 'release':
                api_url = f"https://api.github.com/repos/{username}/{repo_name}/releases/latest"
                response = requests.get(api_url)
                response.raise_for_status()
                release_assets = response.json()['assets']
                files = [{'name': asset['name'], 'download_url': asset['browser_download_url']} for asset in release_assets]
                
                if all(asset['name'].endswith(('.zip', '.tar.gz')) for asset in release_assets):
                    self.output_label.text = "Only source code archives found. Fetching files from master or main branch instead."
                    branch_or_release = 'master'
                else:
                    files = release_assets

            if branch_or_release == 'master':
                api_url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
                response = requests.get(api_url)
                response.raise_for_status()
                files = response.json()

            total_files = len(files)
            self.progress_bar.max = total_files
            self.progress_bar.value = 0

            def download_file(file_url, file_name):
                if file_url is None:
                    self.output_label.text = f"Skipping file: {file_name} (no download URL)"
                    return
                try:
                    file_response = requests.get(file_url)
                    file_response.raise_for_status()
                    file_path = os.path.join(repo_dir, file_name)
                    with open(file_path, 'wb') as f:
                        f.write(file_response.content)
                except Exception as e:
                    self.output_label.text = f"Error downloading file {file_name}: {e}"

            def update_progress(dt):
                if self.progress_bar.value < total_files:
                    file = files[int(self.progress_bar.value)]
                    file_url = file.get('download_url')
                    file_name = file['name']
                    download_file(file_url, file_name)
                    self.progress_bar.value += 1
                    self.output_label.text = f"Downloaded: {file_name}"
                else:
                    Clock.unschedule(update_progress)
                    self.output_label.text = f"All files downloaded to directory: {repo_dir}"

            Clock.schedule_interval(update_progress, 0.1)

        except Exception as e:
            self.output_label.text = f"Error fetching files: {e}"

class EzRepoApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#141414')
        Window.size = (600, 250)
        return EzRepo()

if __name__ == '__main__':
    EzRepoApp().run()