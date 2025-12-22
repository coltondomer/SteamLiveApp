import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.image import AsyncImage  # New: For web images
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
from kivy.graphics import Color, Line, RoundedRectangle, SmoothLine, Rectangle
import webbrowser

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

        self.search_input = TextInput(
            hint_text='Search games...', size_hint_y=None, height=50,
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
                    self.row_rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[10, ])
                row.bind(pos=self._update_row_rect, size=self._update_row_rect)

                lbl = Label(text=f"[b]{game['name']}[/b]\n[size=12sp]ID: {game['id']}[/size]", markup=True,
                            halign='left', size_hint_x=0.7)
                lbl.bind(size=lbl.setter('text_size'))

                btn = SteamButton(text="VIEW", size_hint_x=0.3)
                btn.bind(on_release=lambda x, g=game: self.go_to_detail(g))

                row.add_widget(lbl)
                row.add_widget(btn)
                self.game_list.add_widget(row)

    def _update_row_rect(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*S_ROW_BG)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[10, ])

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

        # --- TOP BANNER IMAGE ---
        self.banner = AsyncImage(
            source="",
            size_hint_y=None, height=220,
            allow_stretch=True, keep_ratio=False
        )

        # --- GAME INFO SECTION ---
        info_box = BoxLayout(orientation='vertical', padding=[20, 0, 20, 0], spacing=5)
        self.title_label = Label(text="", font_size='32sp', bold=True, halign='center')
        self.count_label = Label(text="---", font_size='55sp', color=S_BLUE, bold=True)
        self.sub_label = Label(text="PLAYERS ONLINE", font_size='12sp', color=S_TEXT_DIM)

        info_box.add_widget(self.title_label)
        info_box.add_widget(self.sub_label)
        info_box.add_widget(self.count_label)

        # --- GRAPH ---
        self.graph_box = BoxLayout(size_hint_y=0.4, padding=20)

        # --- BACK BUTTON ---
        back_btn = Button(text="BACK TO LIBRARY", size_hint_y=None, height=60, background_color=S_ROW_BG)
        back_btn.bind(on_release=self.go_back)

        self.layout.add_widget(self.banner)
        self.layout.add_widget(info_box)
        self.layout.add_widget(self.graph_box)
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def on_enter(self):
        # Update Banner via Steam CDN
        self.banner.source = f"https://cdn.akamai.steamstatic.com/steam/apps/{self.target_game['id']}/header.jpg"
        self.title_label.text = self.target_game['name'].upper()
        self.history = []
        Clock.schedule_interval(self.fetch_data, 1)

    def on_leave(self):
        Clock.unschedule(self.fetch_data)
        self.banner.source = ""  # Clear to save memory

    def fetch_data(self, dt):
        url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={self.target_game['id']}"
        UrlRequest(url, on_success=self.update_ui)

    def update_ui(self, request, result):
        try:
            count = result['response'].get('player_count', 0)
            self.count_label.text = f"{count:,}"
            self.history.append(count)
            if len(self.history) > 30: self.history.pop(0)
            self.draw_graph()
        except:
            pass

    def draw_graph(self):
        self.graph_box.canvas.clear()
        if len(self.history) < 2: return
        with self.graph_box.canvas:
            Color(*S_BLUE)
            h_min, h_max = min(self.history), max(self.history)
            y_range = max(h_max - h_min, 5)
            points = []
            w_step = self.graph_box.width / 29
            for i, val in enumerate(self.history):
                x = self.graph_box.x + (i * w_step)
                y = self.graph_box.y + ((val - h_min) / y_range) * (self.graph_box.height * 0.8)
                points.extend([x, y])
            SmoothLine(points=points, width=2)

    def go_back(self, instance):
        self.manager.current = 'library'


class SteamApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(LibraryScreen(name='library'))
        sm.add_widget(DetailScreen(name='detail'))
        return sm


if __name__ == '__main__':
    SteamApp().run()