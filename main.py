import os, json, webbrowser, random
import certifi # Critical for Android SSL
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window
from kivy.metrics import sp
from plyer import notification

# --- ANDROID SYSTEM FIXES ---
# Fix 1: Force Python to use Certifi certificates for Steam API
os.environ['SSL_CERT_FILE'] = certifi.where()

def get_data_path():
    # Fix 2: Redirect storage to app-specific folder on Android
    try:
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), "userdata.json")
    except ImportError:
        return "userdata.json"

STORAGE_FILE = get_data_path()
STEAM_API_KEY = "971102DF95C8FE478AE652ACFD430764"

# --- CONFIG & COLORS ---
S_DARK_BG = (0.08, 0.1, 0.12, 1)
S_ROW_BG = (0.12, 0.15, 0.18, 1)
S_BLUE = (0.1, 0.6, 1, 1)
S_UP = (0.2, 0.9, 0.4, 1)
S_DOWN = (0.9, 0.2, 0.2, 1)
S_TEXT_DIM = (0.6, 0.65, 0.7, 1)
S_SALE = (0.7, 0.8, 0.2, 1)
S_ONLINE = (0.4, 0.8, 0.4, 1)

DEFAULT_GAMES = [
    {"name": "Counter-Strike 2", "id": "730"}, {"name": "Dota 2", "id": "570"},
    {"name": "PUBG", "id": "578080"}, {"name": "Apex Legends", "id": "1172470"},
    {"name": "GTA V", "id": "271590"}, {"name": "Baldur's Gate 3", "id": "1086940"},
    {"name": "Rust", "id": "252490"}, {"name": "Warframe", "id": "230410"}
]

def load_data():
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r') as f: return json.load(f)
    except: pass
    return {"favorites": [], "friends": [], "notified_sales": []}

def save_data(data):
    try:
        with open(STORAGE_FILE, 'w') as f: json.dump(data, f)
    except: pass

# --- UI COMPONENTS ---
class ProGraph(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.points = []
        self.trend_color = S_BLUE
        self.label_y = Label(text="LIVE", size_hint_x=None, width=sp(80), font_size=sp(11), color=S_TEXT_DIM, bold=True)
        self.canvas_area = BoxLayout()
        self.add_widget(self.label_y)
        self.add_widget(self.canvas_area)
        self.canvas_area.bind(pos=self.redraw, size=self.redraw)

    def update_points(self, val):
        jitter = random.randint(-max(1, val // 8000), max(1, val // 8000))
        new_val = val + jitter
        if len(self.points) > 0:
            self.trend_color = S_UP if new_val > self.points[-1] else S_DOWN
        self.points.append(new_val)
        if len(self.points) > 60: self.points.pop(0)
        self.label_y.text = f"{new_val:,}\nNOW"
        self.label_y.color = self.trend_color
        self.redraw()

    def redraw(self, *args):
        self.canvas_area.canvas.before.clear()
        self.canvas_area.canvas.after.clear()
        with self.canvas_area.canvas.before:
            Color(0.15, 0.18, 0.22, 1)
            Line(rectangle=(self.canvas_area.x, self.canvas_area.y, self.canvas_area.width, self.canvas_area.height), width=1.2)
        if len(self.points) < 2: return
        p_min, p_max = min(self.points), max(self.points)
        p_range = p_max - p_min if p_max != p_min else 1
        with self.canvas_area.canvas.after:
            Color(*self.trend_color)
            w, h = self.canvas_area.size
            x_step = w / (len(self.points) - 1)
            coords = []
            for i, p in enumerate(self.points):
                norm_y = ((p - p_min) / p_range) * (h * 0.7) + (h * 0.15)
                coords.extend([self.canvas_area.x + (i * x_step), self.canvas_area.y + norm_y])
            Line(points=coords, width=sp(2.5), joint='round')

class BigSteamButton(Button):
    def __init__(self, bg_color=S_BLUE, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''; self.background_color = (0, 0, 0, 0)
        self.custom_color = bg_color; self.font_size = sp(16); self.bold = True
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*(self.custom_color if self.state == 'normal' else (0.1, 0.5, 0.9, 1)))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[sp(10)])

# --- SCREENS ---
class LibraryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.view_mode = "GAMES"
        with self.canvas.before:
            Color(*S_DARK_BG); self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=lambda i, v: setattr(self.bg, 'size', v))
        main = BoxLayout(orientation='vertical', padding=sp(15), spacing=sp(10))
        self.trending_label = Label(text="TRENDING: [color=1ac3ff]FETCHING...[/color]", markup=True, size_hint_y=None, height=sp(30), font_size=sp(12))
        main.add_widget(self.trending_label)
        main.add_widget(Label(text="STEAM LIVE DASHBOARD", font_size=sp(28), bold=True, size_hint_y=None, height=sp(50)))
        nav = BoxLayout(size_hint_y=None, height=sp(60), spacing=sp(5))
        for t in ["GAMES", "WISHLIST", "FRIENDS"]:
            btn = BigSteamButton(text=t, bg_color=S_ROW_BG if t != "GAMES" else S_BLUE)
            btn.on_release = (lambda x=t: self.switch_tab(x))
            nav.add_widget(btn)
        main.add_widget(nav)
        self.list_layout = GridLayout(cols=1, size_hint_y=None, spacing=sp(8))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.list_layout)
        main.add_widget(scroll)
        self.add_widget(main)

    def switch_tab(self, tab):
        if tab == "FRIENDS": self.manager.current = 'friends'
        else: self.view_mode = tab; self.refresh_list()

    def on_enter(self): self.refresh_list(); self.update_trending()

    def update_trending(self):
        UrlRequest("https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=730",
                   on_success=lambda r, res: setattr(self.trending_label, 'text', f"TRENDING: [color=1ac3ff]Counter-Strike 2 ({res['response'].get('player_count', 0):,} playing)[/color]"))

    def refresh_list(self):
        self.list_layout.clear_widgets()
        data = load_data()
        display = data['favorites'] if self.view_mode == "WISHLIST" else DEFAULT_GAMES
        for g in display:
            row = BoxLayout(size_hint_y=None, height=sp(90), spacing=sp(10), padding=sp(5))
            with row.canvas.before:
                Color(*S_ROW_BG); RoundedRectangle(pos=row.pos, size=row.size, radius=[sp(8)])
            row.add_widget(AsyncImage(source=f"https://cdn.akamai.steamstatic.com/steam/apps/{g['id']}/capsule_184x69.jpg", size_hint_x=None, width=sp(140)))
            row.add_widget(Label(text=f"{g['name']}", bold=True, halign='left'))
            row.add_widget(BigSteamButton(text="STATS", size_hint_x=None, width=sp(80), on_release=lambda x, game=g: self.go_detail(game)))
            self.list_layout.add_widget(row)

    def go_detail(self, game):
        self.manager.get_screen('detail').target_game = game
        self.manager.current = 'detail'

class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_game = None; self.session_peak = 0
        layout = BoxLayout(orientation='vertical', spacing=sp(10), padding=sp(12))
        with self.canvas.before:
            Color(*S_DARK_BG); self.bg = Rectangle(pos=self.pos, size=self.size)
        self.banner = AsyncImage(size_hint_y=None, height=sp(170), allow_stretch=True, keep_ratio=False)
        self.title_label = Label(text="", font_size=sp(24), bold=True)
        self.stats_box = Label(text="Calculating...", color=S_TEXT_DIM, size_hint_y=None, height=sp(30), markup=True)
        self.price_label = Label(text="...", font_size=sp(22), color=S_SALE, bold=True)
        self.graph = ProGraph(size_hint_y=None, height=sp(180))
        layout.add_widget(self.banner); layout.add_widget(self.title_label)
        layout.add_widget(self.stats_box); layout.add_widget(self.price_label)
        layout.add_widget(self.graph)
        btn_row = BoxLayout(size_hint_y=None, height=sp(45), spacing=sp(10))
        btn_row.add_widget(BigSteamButton(text="NEWS", bg_color=(0.2, 0.25, 0.3, 1), on_release=lambda x: webbrowser.open(f"https://store.steampowered.com/news/app/{self.target_game['id']}")))
        btn_row.add_widget(BigSteamButton(text="ACHIEVEMENTS", bg_color=(0.2, 0.25, 0.3, 1), on_release=lambda x: webbrowser.open(f"https://steamcommunity.com/stats/{self.target_game['id']}/achievements")))
        layout.add_widget(btn_row)
        layout.add_widget(BigSteamButton(text="STORE PAGE", bg_color=(0.1, 0.4, 0.7, 1), size_hint_y=None, height=sp(55), on_release=lambda x: webbrowser.open(f"https://store.steampowered.com/app/{self.target_game['id']}")))
        footer = BoxLayout(size_hint_y=None, height=sp(60), spacing=sp(10))
        self.fav_btn = BigSteamButton(text="WISHLIST", on_release=self.toggle_fav)
        footer.add_widget(self.fav_btn)
        footer.add_widget(BigSteamButton(text="BACK", bg_color=S_ROW_BG, on_release=lambda x: setattr(self.manager, 'current', 'library')))
        layout.add_widget(footer)
        self.add_widget(layout)

    def on_enter(self):
        self.banner.source = f"https://cdn.akamai.steamstatic.com/steam/apps/{self.target_game['id']}/header.jpg"
        self.title_label.text = self.target_game['name'].upper()
        self.graph.points = []; self.session_peak = 0
        data = load_data()
        is_fav = any(g['id'] == self.target_game['id'] for g in data['favorites'])
        self.fav_btn.text = "★ IN WISHLIST" if is_fav else "☆ ADD TO WISHLIST"
        self.fav_btn.custom_color = S_BLUE if is_fav else S_ROW_BG
        Clock.schedule_interval(self.fetch_loop, 3.0)

    def on_leave(self): Clock.unschedule(self.fetch_loop)

    def fetch_loop(self, *args):
        UrlRequest(f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={self.target_game['id']}", on_success=self.update_stats)
        UrlRequest(f"https://store.steampowered.com/api/appdetails?appids={self.target_game['id']}", on_success=self.update_price)

    def update_stats(self, req, res):
        count = res['response'].get('player_count', 0)
        if count > self.session_peak: self.session_peak = count
        self.graph.update_points(count)
        sentiment = "[color=44ff44]Positive[/color]" if count > 50000 else "[color=ffff44]Steady[/color]"
        self.stats_box.text = f"Sentiment: {sentiment} | Peak: [b]{self.session_peak:,}[/b]"

    def update_price(self, req, res):
        try:
            d = res[str(self.target_game['id'])]['data']
            p = d['price_overview']['final_formatted'] if not d['is_free'] else "FREE"
            self.price_label.text = p
        except: self.price_label.text = "N/A"

    def toggle_fav(self, x):
        data = load_data()
        if any(g['id'] == self.target_game['id'] for g in data['favorites']):
            data['favorites'] = [g for g in data['favorites'] if g['id'] != self.target_game['id']]
        else: data['favorites'].append(self.target_game)
        save_data(data); self.on_enter()

class FriendsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*S_DARK_BG); Rectangle(pos=self.pos, size=Window.size)
        layout = BoxLayout(orientation='vertical', padding=sp(15), spacing=sp(15))
        layout.add_widget(Label(text="FRIEND ACTIVITY", font_size=sp(26), bold=True, size_hint_y=None, height=sp(50)))
        box = BoxLayout(size_hint_y=None, height=sp(55), spacing=sp(10))
        self.f_input = TextInput(hint_text="Steam ID", multiline=False, background_color=(1, 1, 1, 0.1), foreground_color=(1, 1, 1, 1))
        box.add_widget(self.f_input)
        box.add_widget(BigSteamButton(text="ADD", size_hint_x=0.25, on_release=self.add_friend))
        layout.add_widget(box)
        self.f_list = GridLayout(cols=1, size_hint_y=None, spacing=sp(10))
        self.f_list.bind(minimum_height=self.f_list.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.f_list)
        layout.add_widget(scroll)
        layout.add_widget(BigSteamButton(text="BACK", bg_color=S_ROW_BG, size_hint_y=None, height=sp(60), on_release=lambda x: setattr(self.manager, 'current', 'library')))
        self.add_widget(layout)

    def on_enter(self): self.refresh_friends()

    def add_friend(self, x):
        name = self.f_input.text.strip()
        UrlRequest(f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={STEAM_API_KEY}&vanityurl={name}",
                   on_success=lambda r, res: self.save_id(res['response'].get('steamid')))

    def save_id(self, sid):
        if sid:
            data = load_data()
            if sid not in data['friends']: data['friends'].append(sid); save_data(data); self.refresh_friends()

    def refresh_friends(self):
        data = load_data()
        if data['friends']:
            UrlRequest(f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={','.join(data['friends'])}", on_success=self.draw)

    def draw(self, req, res):
        self.f_list.clear_widgets()
        for p in res.get('response', {}).get('players', []):
            row = BoxLayout(size_hint_y=None, height=sp(80), padding=sp(5), spacing=sp(10))
            with row.canvas.before:
                Color(*S_ROW_BG); RoundedRectangle(pos=row.pos, size=row.size, radius=[sp(8)])
            row.add_widget(AsyncImage(source=p.get('avatarfull'), size_hint_x=None, width=sp(70)))
            status = p.get('gameextrainfo', "Online" if p['personastate'] > 0 else "Offline")
            btn = Button(text=f"{p['personaname']}\n[size=12]{status}[/size]", markup=True, background_color=(0, 0, 0, 0), halign='left')
            btn.bind(on_release=lambda x, url=p['profileurl']: webbrowser.open(url))
            row.add_widget(btn)
            self.f_list.add_widget(row)

class SteamApp(App):
    def build(self):
        # Fix 3: Solicit permissions on Android startup
        if os.name == 'posix':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.INTERNET, Permission.POST_NOTIFICATIONS, Permission.VIBRATE])
            except ImportError: pass

        sm = ScreenManager(transition=FadeTransition(duration=0.25))
        sm.add_widget(LibraryScreen(name='library')); sm.add_widget(DetailScreen(name='detail'))
        sm.add_widget(FriendsScreen(name='friends'))
        return sm

if __name__ == '__main__': SteamApp().run()
