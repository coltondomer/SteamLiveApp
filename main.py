import os
from kivy.config import Config

# Fixes potential multitouch/mouse conflicts on Android
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window
import webbrowser  # For the Game ID link

# --- STEAM COLOR PALETTE ---
S_DARK_BG = (0.1, 0.12, 0.15, 1)
S_ROW_BG = (0.15, 0.18, 0.22, 1)
S_BLUE = (0.1, 0.6, 1, 1)
S_TEXT_DIM = (0.6, 0.65, 0.7, 1)

# --- DATA ---
ALL_GAMES = [
    {"name": "Counter-Strike 2", "id": "730"}, {"name": "Dota 2", "id": "570"},
    {"name": "PUBG", "id": "578080"}, {"name": "Apex Legends", "id": "1172470"},
    {"name": "GTA V", "id": "271590"}, {"name": "Baldur's Gate 3", "id": "1086940"},
    {"name": "Rust", "id": "252490"}, {"name": "Warframe", "id": "230410"}
]


class SteamButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*(S_BLUE if self.state == 'normal' else (0.05, 0.4, 0.8, 1)))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8, ])


class LibraryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*S_DARK_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="STEAM LIBRARY", font_size='28sp', bold=True, size_hint_y=None, height=60))

        # --- CUSTOM ID SECTION ---
        id_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.custom_id_input = TextInput(
            hint_text='Enter App ID (e.g. 440)', multiline=False,
            background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1, 1, 1, 1)
        )
        add_btn = SteamButton(text="TRACK ID", size_hint_x=0.4)
        add_btn.bind(on_release=self.track_custom_id)

        id_layout.add_widget(self.custom_id_input)
        id_layout.add_widget(add_btn)
        layout.add_widget(id_layout)

        # Link to find IDs
        link_lbl = Button(text="[color=199aff][u]Find more Game IDs here[/u][/color]",
                          markup=True, background_color=(0, 0, 0, 0), size_hint_y=None, height=30)
        link_lbl.bind(on_release=lambda x: webbrowser.open("https://steamdb.info/graph/"))
        layout.add_widget(link_lbl)

        # Search Bar
        self.search_input = TextInput(
            hint_text='Search library...', size_hint_y=None, height=50,
            multiline=False, background_color=(0.12, 0.14, 0.18, 1),
            foreground_color=(1, 1, 1, 1), cursor_color=S_BLUE
        )
        self.search_input.bind(text=self.on_search)
        layout.add_widget(self.search_input)

        self.scroll = ScrollView()
        self.game_list = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.game_list.bind(minimum_height=self.game_list.setter('height'))
        self.scroll.add_widget(self.game_list)
        layout.add_widget(self.scroll)

        self.add_widget(layout)
        self.refresh_list("")

    def track_custom_id(self, instance):
        val = self.custom_id_input.text.strip()
        if val.isdigit():
            self.go_to_detail({"name": f"App ID: {val}", "id": val})

    def _update_bg(self, instance, value):
        self.bg_rect.size = value

    def on_search(self, instance, value):
        self.refresh_list(value.lower())

    def refresh_list(self, filter_text):
        self.game_list.clear_widgets()
        for game in ALL_GAMES:
            if filter_text in game['name'].lower():
                row = BoxLayout(size_hint_y=None, height=80, padding=10)
                with row.canvas.before:
                    Color(*S_ROW_BG)
                    RoundedRectangle(pos=row.pos, size=row.size, radius=[10, ])

                lbl = Label(text=f"[b]{game['name']}[/b]\n[size=12sp]ID: {game['id']}[/size]", markup=True,
                            halign='left', size_hint_x=0.7)
                lbl.bind(size=lbl.setter('text_size'))

                btn = SteamButton(text="VIEW", size_hint_x=0.3)
                btn.bind(on_release=lambda x, g=game: self.go_to_detail(g))

                row.add_widget(lbl)
                row.add_widget(btn)
                self.game_list.add_widget(row)

    def go_to_detail(self, game):
        self.manager.get_screen('detail').target_game = game
        self.manager.current = 'detail'


class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_game = None
        self.history = []
        with self.canvas.before:
            Color(*S_DARK_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.layout = BoxLayout(orientation='vertical', padding=0, spacing=10)
        self.banner = AsyncImage(source="", size_hint_y=None, height=220, allow_stretch=True, keep_ratio=False)

        info_box = BoxLayout(orientation='vertical', padding=[20, 0, 20, 0], spacing=5)
        self.title_label = Label(text="", font_size='24sp', bold=True, halign='center')
        self.count_label = Label(text="---", font_size='55sp', color=S_BLUE, bold=True)
        self.sub_label = Label(text="PLAYERS ONLINE", font_size='12sp', color=S_TEXT_DIM)

        info_box.add_widget(self.title_label)
        info_box.add_widget(self.sub_label)
        info_box.add_widget(self.count_label)

        self.graph_box = BoxLayout(size_hint_y=0.4, padding=20)
        back_btn = Button(text="BACK TO LIBRARY", size_hint_y=None, height=60, background_color=S_ROW_BG)
        back_btn.bind(on_release=self.go_back)

        self.layout.add_widget(self.banner)
        self.layout.add_widget(info_box)
        self.layout.add_widget(self.graph_box)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        self.banner.source = f"https://cdn.akamai.steamstatic.com/steam/apps/{self.target_game['id']}/header.jpg"
        self.title_label.text = self.target_game['name'].upper()
        self.history = []
        Clock.schedule_interval(self.fetch_data, 2)

    def on_leave(self):
        Clock.unschedule(self.fetch_data)

    def fetch_data(self, dt):
        url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={self.target_game['id']}"
        UrlRequest(url, on_success=self.update_ui, on_error=self.on_network_fail, on_failure=self.on_network_fail)

    def on_network_fail(self, request, error):
        self.count_label.text = "OFFLINE"

    def update_ui(self, request, result):
        try:
            count = result['response'].get('player_count', 0)
            self.count_label.text = f"{count:,}"
            self.history.append(count)
            if len(self.history) > 30: self.history.pop(0)
            # Simple line drawing logic here or custom widget
        except:
            self.count_label.text = "ERROR"

    def go_back(self, instance):
        self.manager.current = 'library'


class SteamApp(App):
    def build(self):
        Window.bind(on_keyboard=self.on_key)
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(LibraryScreen(name='library'))
        sm.add_widget(DetailScreen(name='detail'))
        return sm

    def on_key(self, window, key, *args):
        if key == 27:  # Android Back Button
            if self.root.current == 'detail':
                self.root.current = 'library'
                return True
            return False


if __name__ == '__main__':
    SteamApp().run()
