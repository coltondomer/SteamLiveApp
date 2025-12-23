import os, json, webbrowser
from kivy.config import Config

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
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window

# --- CONFIG & COLORS ---
STEAM_API_KEY = "971102DF95C8FE478AE652ACFD430764"

S_DARK_BG = (0.1, 0.12, 0.15, 1)
S_ROW_BG = (0.15, 0.18, 0.22, 1)
S_BLUE = (0.1, 0.6, 1, 1)
S_TEXT_DIM = (0.6, 0.65, 0.7, 1)
S_ONLINE = (0.4, 0.8, 0.4, 1)

STORAGE_FILE = "userdata.json"

# --- EXPANDED 20-GAME LIST ---
DEFAULT_GAMES = [
    {"name": "Counter-Strike 2", "id": "730"}, {"name": "Dota 2", "id": "570"},
    {"name": "PUBG: BATTLEGROUNDS", "id": "578080"}, {"name": "Apex Legends", "id": "1172470"},
    {"name": "GTA V", "id": "271590"}, {"name": "Baldur's Gate 3", "id": "1086940"},
    {"name": "Rust", "id": "252490"}, {"name": "Warframe", "id": "230410"},
    {"name": "Destiny 2", "id": "1085660"}, {"name": "Elden Ring", "id": "1245620"},
    {"name": "Team Fortress 2", "id": "440"}, {"name": "Helldivers 2", "id": "553850"},
    {"name": "Monster Hunter: World", "id": "582010"}, {"name": "Stardew Valley", "id": "294100"},
    {"name": "Palworld", "id": "1623730"}, {"name": "Dead by Daylight", "id": "381210"},
    {"name": "Terraria", "id": "105600"}, {"name": "Rainbow Six Siege", "id": "359550"},
    {"name": "Cyberpunk 2077", "id": "1091500"}, {"name": "Black Myth: Wukong", "id": "2358720"}
]


def load_data():
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"favorites": [], "friends": []}


def save_data(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f)


# --- CUSTOM UI WIDGETS ---
class SteamButton(Button):
    def __init__(self, bg_color=S_BLUE, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.custom_color = bg_color
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*(self.custom_color if self.state == 'normal' else (0.05, 0.4, 0.8, 1)))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8, ])


# --- SCREENS ---
class LibraryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*S_DARK_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=lambda i, v: setattr(self.bg_rect, 'size', v))

        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        main_layout.add_widget(Label(text="STEAM DASHBOARD", font_size='24sp', bold=True, size_hint_y=None, height=50))

        nav = BoxLayout(size_hint_y=None, height=45, spacing=10)
        nav.add_widget(SteamButton(text="GAMES", on_release=lambda x: self.refresh_list("")))
        nav.add_widget(SteamButton(text="FRIENDS", bg_color=S_ROW_BG,
                                   on_release=lambda x: setattr(self.manager, 'current', 'friends')))
        main_layout.add_widget(nav)

        id_box = BoxLayout(size_hint_y=None, height=45, spacing=10)
        self.id_input = TextInput(hint_text='App ID', multiline=False, background_color=(0.12, 0.14, 0.18, 1),
                                  foreground_color=(1, 1, 1, 1))
        add_btn = SteamButton(text="TRACK ID", size_hint_x=0.3, on_release=self.add_custom)
        id_box.add_widget(self.id_input);
        id_box.add_widget(add_btn)
        main_layout.add_widget(id_box)

        self.scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, size_hint_y=None, spacing=12)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        main_layout.add_widget(self.scroll)
        self.add_widget(main_layout)

    def on_enter(self):
        self.refresh_list("")

    def add_custom(self, instance):
        val = self.id_input.text.strip()
        if val.isdigit(): self.go_to_detail({"name": f"App ID: {val}", "id": val})

    def refresh_list(self, filter_text):
        self.list_layout.clear_widgets()
        data = load_data()
        display_list = DEFAULT_GAMES + [g for g in data['favorites'] if g not in DEFAULT_GAMES]
        for game in display_list:
            row = BoxLayout(size_hint_y=None, height=100, spacing=10, padding=5)
            with row.canvas.before:
                Color(*S_ROW_BG);
                RoundedRectangle(pos=row.pos, size=row.size, radius=[10, ])
            img_url = f"https://cdn.akamai.steamstatic.com/steam/apps/{game['id']}/capsule_184x69.jpg"
            row.add_widget(AsyncImage(source=img_url, size_hint_x=None, width=150, allow_stretch=True))
            info = Label(text=f"[b]{game['name']}[/b]\n[size=12sp]ID: {game['id']}[/size]", markup=True, halign='left',
                         valign='middle')
            info.bind(size=info.setter('text_size'))
            row.add_widget(info)
            btn = SteamButton(text="VIEW", size_hint_x=None, width=80)
            btn.bind(on_release=lambda x, g=game: self.go_to_detail(g))
            row.add_widget(btn)
            self.list_layout.add_widget(row)

    def go_to_detail(self, game):
        self.manager.get_screen('detail').target_game = game
        self.manager.current = 'detail'


class FriendsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*S_DARK_BG);
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=lambda i, v: setattr(self.bg, 'size', v))

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="FRIENDS STATUS", font_size='24sp', bold=True, size_hint_y=None, height=50))

        add_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.friend_input = TextInput(hint_text='SteamID64 (17 digits)', multiline=False)
        btn = SteamButton(text="ADD", size_hint_x=0.3, on_release=self.add_friend)
        add_box.add_widget(self.friend_input);
        add_box.add_widget(btn)
        layout.add_widget(add_box)

        self.friends_list = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.friends_list.bind(minimum_height=self.friends_list.setter('height'))
        scroll = ScrollView();
        scroll.add_widget(self.friends_list)
        layout.add_widget(scroll)

        layout.add_widget(SteamButton(text="BACK", size_hint_y=None, height=50,
                                      on_release=lambda x: setattr(self.manager, 'current', 'library')))
        self.add_widget(layout)

    def on_enter(self):
        self.refresh_friends()
        Clock.schedule_interval(self.refresh_friends, 20)

    def on_leave(self):
        Clock.unschedule(self.refresh_friends)

    def add_friend(self, x):
        fid = self.friend_input.text.strip()
        if len(fid) == 17 and fid.isdigit():
            data = load_data()
            if fid not in data['friends']:
                data['friends'].append(fid);
                save_data(data);
                self.refresh_friends()

    def refresh_friends(self, *args):
        data = load_data()
        if not data['friends']: return
        ids = ",".join(data['friends'])
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={ids}"
        UrlRequest(url, on_success=self.draw_friends)

    def draw_friends(self, req, res):
        self.friends_list.clear_widgets()
        players = res.get('response', {}).get('players', [])
        for p in players:
            row = BoxLayout(size_hint_y=None, height=80, padding=10, spacing=10)
            status_color = S_ONLINE if p.get('personastate', 0) > 0 else S_TEXT_DIM
            if p.get('gameextrainfo'): status_color = S_BLUE
            with row.canvas.before:
                Color(*S_ROW_BG);
                RoundedRectangle(pos=row.pos, size=row.size, radius=[10, ])

            row.add_widget(AsyncImage(source=p.get('avatar'), size_hint_x=None, width=60))
            name = p.get('personaname', 'Unknown User')
            game_text = p.get('gameextrainfo', 'Online' if p.get('personastate', 0) > 0 else 'Offline')
            row.add_widget(Label(text=f"[b]{name}[/b]\n[size=12sp]{game_text}[/size]", markup=True, halign='left'))

            dot_box = BoxLayout(size_hint_x=None, width=40)
            with dot_box.canvas:
                Color(*status_color);
                Ellipse(pos=(self.width - 65, row.y + 30), size=(15, 15))
            row.add_widget(dot_box)
            self.friends_list.add_widget(row)


class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_game = None
        with self.canvas.before:
            Color(*S_DARK_BG);
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=lambda i, v: setattr(self.bg, 'size', v))

        layout = BoxLayout(orientation='vertical', spacing=15)
        self.banner = AsyncImage(source="", size_hint_y=None, height=220, allow_stretch=True, keep_ratio=False)
        self.title_label = Label(text="", font_size='28sp', bold=True, halign='center')
        self.count_label = Label(text="---", font_size='60sp', color=S_BLUE, bold=True)
        self.sub_label = Label(text="PLAYERS ONLINE", font_size='14sp', color=S_TEXT_DIM)

        btn_box = BoxLayout(size_hint_y=None, height=60, spacing=10, padding=10)
        self.fav_btn = SteamButton(text="FAVORITE", bg_color=(0.3, 0.3, 0.3, 1), on_release=self.toggle_favorite)
        back_btn = SteamButton(text="BACK", bg_color=S_ROW_BG,
                               on_release=lambda x: setattr(self.manager, 'current', 'library'))
        btn_box.add_widget(self.fav_btn);
        btn_box.add_widget(back_btn)

        layout.add_widget(self.banner);
        layout.add_widget(self.title_label)
        layout.add_widget(self.sub_label);
        layout.add_widget(self.count_label)
        layout.add_widget(btn_box);
        self.add_widget(layout)

    def on_enter(self):
        self.banner.source = f"https://cdn.akamai.steamstatic.com/steam/apps/{self.target_game['id']}/header.jpg"
        self.title_label.text = self.target_game['name'].upper()
        data = load_data()
        is_fav = any(g['id'] == self.target_game['id'] for g in data['favorites'])
        self.fav_btn.text = "FAVORITED" if is_fav else "FAVORITE"
        self.fav_btn.custom_color = S_BLUE if is_fav else (0.3, 0.3, 0.3, 1)
        Clock.schedule_interval(self.fetch, 5)

    def on_leave(self):
        Clock.unschedule(self.fetch)

    def fetch(self, dt):
        url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={self.target_game['id']}"
        UrlRequest(url, on_success=self.update_ui)

    def update_ui(self, req, res):
        count = res['response'].get('player_count', 0)
        self.count_label.text = f"{count:,}"

    def toggle_favorite(self, x):
        data = load_data()
        ids = [g['id'] for g in data['favorites']]
        if self.target_game['id'] in ids:
            data['favorites'] = [g for g in data['favorites'] if g['id'] != self.target_game['id']]
        else:
            data['favorites'].append(self.target_game)
        save_data(data);
        self.on_enter()


class SteamApp(App):
    def build(self):
        Window.bind(on_keyboard=self.on_key)
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(LibraryScreen(name='library'))
        sm.add_widget(FriendsScreen(name='friends'))
        sm.add_widget(DetailScreen(name='detail'))
        return sm

    def on_key(self, w, k, *a):
        if k == 27: self.root.current = 'library'; return True
        return False


if __name__ == '__main__': SteamApp().run()
