import pygame
import ui
import os
import random
import json
from datetime import datetime

pygame.init()

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PARTICLES = [
    os.path.join(BASE_PATH, "assets/particles/particle1.png"),
    os.path.join(BASE_PATH, "assets/particles/particle2.png"),
    os.path.join(BASE_PATH, "assets/particles/particle3.png"),
    os.path.join(BASE_PATH, "assets/particles/particle4.png"),
]
ASSETS = {
    "MENU_BG": os.path.join(BASE_PATH, "assets/backgrounds/main_menu.png"),
    "TUTORIAL_BG": os.path.join(BASE_PATH, "assets/backgrounds/tutorial.png"),
    "LIBRARY_BG": os.path.join(BASE_PATH, "assets/backgrounds/library.png"),
    "PLAYLIST_BG": os.path.join(BASE_PATH, "assets/backgrounds/playlists.png"),
    "USERS": os.path.join(BASE_PATH, "assets/users.json"),
    "PLAYLISTS": os.path.join(BASE_PATH, "assets/playlists.json"),
    "SONGS": os.path.join(BASE_PATH, "assets/song_list.json"),
}

class Scene:
    def __init__(self):
        self.next_scene = self
        self.ui_elements = []

    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)

    def update(self):
        for element in self.ui_elements:
            element.update()

    def render(self, screen):
        for element in self.ui_elements:
            element.draw(screen)


class MainMenu(Scene):
    def __init__(self):
        super().__init__()
        self.particles = []
        self.ui_elements = [
            (error_text:= ui.TextBox(850, 650, 500, 50, text="", background=False)),
            (sign_up:= ui.Button(825, 550, 225, 50, text="Sign Up", redirect="tutorial")),
            (log_in:= ui.Button(1150, 550, 225, 50, text="Log In", redirect="library")),
            (s_username:= ui.TextBox(825, 330, 225, 50, text="Username", editable=True, max_length=22)),
            (s_password:= ui.TextBox(825, 390, 225, 50, text="Password", editable=True, max_length=22)),
            (s_confirm_password:= ui.TextBox(825, 450, 225, 50, text="Confirm Password", editable=True, max_length=22)),
            (l_username:= ui.TextBox(1150, 330, 225, 50, text="Username", editable=True, max_length=22)),
            (l_password:= ui.TextBox(1150, 390, 225, 50, text="Password", editable=True, max_length=22)),
            ]
        self.error_text = error_text
        self.sign_up = sign_up
        self.log_in = log_in
        self.s_username = s_username
        self.s_password = s_password
        self.s_confirm_password = s_confirm_password
        self.l_username = l_username
        self.l_password = l_password

        self.error_text.text_colour = ui.COLOURS["RED"]
        self.error_text.font = pygame.font.Font(ui.ASSETS["BOLD"], 32)
        self.sign_up.bg_colour = ui.COLOURS["DARK_BLUE"]
        self.log_in.bg_colour = ui.COLOURS["DARK_BLUE"]

    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)
                if type(element) == ui.Button and element.active:
                    if element == self.sign_up:
                        info = {
                            'username': self.s_username.text,
                            'password': self.s_password.text,
                            'confirm_password': self.s_confirm_password.text,
                            'button_pressed': 'signup'
                        }
                        
                    elif element == self.log_in:
                        info = {
                            'username': self.l_username.text,
                            'password': self.l_password.text,
                            'button_pressed': 'login'
                        }

                    if (result := self.validate_login(info)) is True:
                        globals()["tutorial"].username = info['username']
                        globals()["library"].username = info['username']
                        globals()["playlist_maker"].username = info['username']
                        self.next_scene = globals()[element.redirect]
                    else:
                        self.error_text.text = result[1]

    def update(self):
        super().update()
        if len(self.particles) <= 4:
            self.particles.append(
                [
                    [450, 500], # position
                    (random.randint(5, 20) / 8, -2), # (x, y) velocity
                    random.randint(20, 100), # timer
                    pygame.image.load(random.choice(PARTICLES)), # image
                    (width := random.randint(32, 72), width) # size
                ]
            )

    def render(self, screen):
        screen.blit(pygame.image.load(ASSETS["MENU_BG"]), (0, 0))
        super().render(screen)
        particles_to_remove = []
        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 1
            if particle[2] <= 0:
                particles_to_remove.append(particle)
            else:
                screen.blit(
                    pygame.transform.scale(particle[3], particle[4]),
                    (particle[0][0], particle[0][1]),
                )

        for particle in particles_to_remove:
            self.particles.remove(particle)

    def validate_login(self, info):
        self.users = {}

        with open(ASSETS['USERS'], 'r') as f:
            self.users = json.load(f)

        if info['button_pressed'] == 'login':
            if info['username'] in self.users:
                if self.users[info['username']]['password'] == info['password']:
                    return True
            return (False, "Invalid username or password")
        
        elif info['button_pressed'] == 'signup':
            if info['username'] == 'Username' or info['password'] == 'Password':
                return (False, "Please fill in all fields")
            if info['username'] not in self.users:
                if info['password'] == info['confirm_password']:
                    self.users[info['username']] = {
                        'username': info['username'],
                        'password': info['password']
                    }
                else:
                    return (False, "Passwords do not match")
            else:
                return (False, "Username already exists")
            
            with open(ASSETS['USERS'], 'w') as f:
                json.dump(self.users, f)

        return True

class Tutorial(Scene):
    def __init__(self):
        super().__init__()
        self.input_rect = pygame.Rect(10, 90, 775, 775)
        self.animated = False
        self.ui_elements = [
            (error_text:= ui.TextBox(380, 20, 600, 50, text="", background=False)),
            (title:= ui.TextBox(622, 100, 200, 50, text="Tell us a bit about you...", background=False)),
            (submit:= ui.Button(380, 810, 300, 45, text="Submit", redirect="library")),
            ui.Button(695, 810, 300, 45, text="Back", redirect="main_menu"),
            (full_name:= ui.TextBox(380, 200, 600, 45, text="Full Name", editable=True, max_length=40)),
            (dob:= ui.TextBox(480, 280, 400, 45, text="Birthday (DD/MM/YYYY)", editable=True, max_length=10)),
            (favourite_artist:= ui.TextBox(430, 360, 500, 45, text="Favourite Artist", editable=True, max_length=40)),
            (favourite_genre:= ui.DropDown(430, 440, 500, 45, options=["Rock", "RNB", "Pop", "Rap"], selected="Favourite Genre")),
        ]
        
        self.full_name = full_name
        self.error_text = error_text
        self.dob = dob
        self.favourite_artist = favourite_artist
        self.favourite_genre = favourite_genre
        self.info_boxes = [self.full_name, self.dob, self.favourite_artist, self.favourite_genre]
        self.submit = submit
        self.title = title
        for element in self.ui_elements:
            element.active_colour = ui.COLOURS["VANILLA"]
            element.text_colour = ui.COLOURS["BLACK"]
            element.font = pygame.font.Font(ui.ASSETS["BOLD"], 32)
            element.bg_colour = ui.COLOURS["CREAM"]

        self.error_text.text_colour = ui.COLOURS["RED"]

    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)
                if type(element) == ui.Button and element.active:
                    if element == self.submit:
                        info = {
                            'full_name': self.full_name.text,
                            'dob': self.dob.text,
                            'favourite_artist': self.favourite_artist.text,
                            'favourite_genre': self.favourite_genre.selected,
                        }
                        if (result := self.validate_info(info)) is True:
                            self.next_scene = globals()[element.redirect]
                        else:
                            self.error_text.text = result[1]
                    else:
                        with open(ASSETS['USERS'], 'r') as f:
                            users = json.load(f)
                            users.pop(self.username)
                        with open(ASSETS['USERS'], 'w') as f:
                            json.dump(users, f)
                        self.next_scene = globals()[element.redirect]

    def update(self):
        super().update()

    def render(self, screen):
        screen.fill(ui.COLOURS["WHITE"])
        if not self.animated:
            self.animate(screen, [self.title])
            self.animate(screen, self.info_boxes)
        pygame.draw.rect(screen, ui.COLOURS["DARK_BLUE"], self.input_rect, 0, 10)
        super().render(screen)

    def animate(self, screen, elements):
        if not self.animated:
            while self.input_rect.x < (screen.get_width() - self.input_rect.width)//2 - 10:
                self.input_rect.x += 1
                screen.fill(ui.COLOURS["WHITE"])
                pygame.draw.rect(screen, ui.COLOURS["DARK_BLUE"], self.input_rect, 0, 25)
                pygame.display.update()
                pygame.time.delay(1)
        x = 0
        while x < 200:
            for element in elements:
                element.anti_aliasing = False
                element.txt_surface.set_alpha(x)
                element.draw(screen)
                pygame.display.update()
                element.anti_aliasing = True
            pygame.time.delay(25)
            x += 5
        self.animated = True

    def validate_info(self, info):
        try:
            info['dob'] = datetime.strptime(info['dob'], "%d/%m/%Y")
        except ValueError:
            return (False, "Invalid Date of Birth (DD/MM/YYYY)")
        if info['dob'] > datetime.now():
            return (False, "Invalid Date of Birth (DD/MM/YYYY)")
        else:
            info['dob'] = info['dob'].strftime("%d/%m/%Y")
        try:
            info['full_name'] = info['full_name'].split()
            if len(info['full_name']) < 2 or len(info['full_name']) > 3 or not all([name.isalpha() for name in info['full_name']]):
                raise Exception
        except:
            return (False, "Please enter a valid full name")
        if info['favourite_artist'] == 'Favourite Artist':
            return (False, "Please enter your favourite artist")
        if info['favourite_genre'] == 'Favourite Genre':
            return (False, "Please select your favourite genre")
        
        self.save_info(info)
        return True

    def save_info(self, info):
        with open(ASSETS['USERS'], 'r') as f:
            users = json.load(f)
        users[self.username].update(info)
        with open(ASSETS['USERS'], 'w') as f:
            json.dump(users, f)


class Library(Scene):
    def __init__(self):
        super().__init__()
        self.songs = self._get_song_list()
        self.ui_elements = [
            (song_list:= ui.ItemList(180, 400, 750, 50, items=self.songs, max_items=7)),
            ui.TextBox(520, 350, 100, 50, text=f"Title{' '*35}Artist{' '*32}Genre{' '*30}Duration", background=False),
            ui.Button(0, 186, 200, 50, text="Make Playlist", background=False, redirect="playlist_maker"),
            ui.Button(0, 238, 200, 50, text="My Playlists", background=False),
            ui.Button(0, 783, 200, 50, text="Settings", background=False),
            ui.Button(0, 833, 200, 50, text="Log Out", background=False, redirect="main_menu"),
            (search:= ui.SearchBox(250, 18, 760, 60, reference=self._song_list, background=False)),
            (rock:= ui.Button(172, 170, 200, 100, text="Rock", background=False)),
            (rap:= ui.Button(325, 170, 200, 100, text="Rap", background=False)),
            (pop:= ui.Button(475, 170, 200, 100, text="Pop", background=False)),
            (rnb:= ui.Button(630, 170, 200, 100, text="RNB", background=False)),
        ]
        self.rock = rock
        self.pop = pop
        self.rnb = rnb
        self.rap = rap
        self.genres = [self.rock, self.pop, self.rnb, self.rap]
        self.song_list = song_list
        self.song_list.scene_colour = (242, 245, 254)
        self.search = search
        for element in self.ui_elements:
            if element in self.genres:
                element.font = pygame.font.Font(ui.ASSETS["BOLD"], 32)
            elif type(element) == ui.TextBox or type(element) == ui.Button:
                element.font = pygame.font.Font(ui.ASSETS["BOLD"], 20)
        
    def _get_song_list(self):
        final_list = []
        space_width = ui.BUTTON_FONT.render(" ", True, (0, 0, 0)).get_width()

        with open(ASSETS["SONGS"], "r") as f:
            self._song_list = json.load(f)

        for song in self._song_list:
            entry = ""
            for value in song.values():
                entry += value
                font_offset = ui.BUTTON_FONT.size(value)[0]
                entry += " " * ((space_width*45 - font_offset)//space_width)
            final_list.append(entry)

        for song in self._song_list:
            song.pop("genre", None)
            song.pop("length", None)

        self._song_list.sort(key=lambda x: x["name"])

        return final_list

    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)
                if type(element) == ui.Button and element.active:
                    if element.text == "Make Playlist":
                        globals()["playlist_maker"].filter_songs()
                    if element.redirect:
                        self.next_scene = globals()[element.redirect]
        
        for genre in self.genres:
            if genre.active:
                globals()["playlist_maker"].filters.items[globals()["playlist_maker"].filters.items.index((genre.text, False))] = (genre.text, True)
                self.next_scene = globals()["playlist_maker"]
                globals()["playlist_maker"].filter_songs()
                break

    def update(self):
        super().update()
        selected_song = self.search.selected or self.song_list.selected
        if selected_song:
            globals()["playlist_maker"].new_playlist.append(selected_song)
            self.search.selected = None
            self.song_list.selected = None
            self.next_scene = globals()["playlist_maker"]
        

    def render(self, screen):
        screen.blit(pygame.image.load(ASSETS["LIBRARY_BG"]), (0, 0))
        super().render(screen)

class PlaylistMaker(Scene):
    def __init__(self):
        super().__init__()
        self._song_list = self._load_songs()
        self.new_playlist = []
        self.other_songs = self._get_other_songs()
        self.username = "Sparky"
        self.ui_elements = [
            ui.Button(0, 188, 200, 50, text="Home", background=False, redirect="library"),
            ui.Button(0, 238, 200, 50, text="My Playlists", background=False),
            ui.Button(0, 783, 200, 50, text="Settings", background=False),
            ui.Button(0, 833, 200, 50, text="Log Out", background=False, redirect="main_menu"),
            (filters:= ui.Checkboxes(1125, 270, 200, 45, items=["Rock", "Pop", "RNB", "Rap"], background=False)),
            (playlist:= ui.ItemList(220, 270, 750, 30, items=self.new_playlist, max_items=4)),
            (other_songs:= ui.ItemList(220, 550, 750, 30, items=self.other_songs, max_items=4)),
            (name:= ui.TextBox(320, 142, 750, 50, text="", editable=True, max_length=40, border_radius=0, background=False)),
            (filter_button:= ui.Button(1150, 600, 200, 50, text="Filter")),
            (artist:= ui.TextBox(1150, 470, 200, 50, text="Artist", editable=True, max_length=22)),
            (save:= ui.Button(445, 775, 400, 50, text="Save Playlist")),
        ]
        self.save = save
        self.artist = artist
        self.filter_button = filter_button
        self.other_songs = other_songs
        self.playlist = playlist
        self.name = name
        self.name.centred = False
        self.filters = filters

        self.save.bg_colour = ui.COLOURS["DARK_BLUE"]
        self.save.active_colour = ui.COLOURS["LIGHT_BLUE"]

        for element in self.ui_elements:
            if type(element) == ui.TextBox or type(element) == ui.Button:
                element.font = pygame.font.Font(ui.ASSETS["BOLD"], 20)
            elif type(element) == ui.ItemList:
                element.offset = 12
                element.scene_colour = ui.COLOURS['LIGHT_BLUE']
                element.slider_colour = ui.COLOURS['DARK_BLUE']
                element.bg_colour = ui.COLOURS['CREAM']
        
    def _load_songs(self):
        with open(ASSETS["SONGS"], "r") as f:
            return json.load(f)

    def _get_user_playlists(self):
        with open(ASSETS["PLAYLISTS"], "r") as f:
            users = json.load(f)
            if self.username not in users:
                self.user_playlists = {}
            else:
                self.user_playlists = users[self.username]

    def _get_other_songs(self):
        for song in self._song_list:
            for value in self.new_playlist:
                if song["name"] == value.split("  ")[0]:
                    self._song_list.remove(song)

        final_list = []
        space_width = ui.BUTTON_FONT.render(" ", True, (0, 0, 0)).get_width()
        for song in self._song_list:
            entry = ""
            for value in song.values():
                entry += value
                font_offset = ui.BUTTON_FONT.size(value)[0]
                entry += " " * ((space_width*45 - font_offset)//space_width)
            final_list.append(entry)

        return final_list

    def _get_playlist_num(self):
        length = len(self.user_playlists) + 1
        while True:
            if f"My Playlist #{length}" not in self.user_playlists:
                return f"My Playlist #{length}"
            else:
                length += 1

    def filter_songs(self):
        self._song_list = self._load_songs()
        selected_genres = [filter_[0] for filter_ in self.filters.items if filter_[1]]
        if selected_genres:
            self._song_list = [song for song in self._song_list if song["genre"] in selected_genres]
        if self.artist.text != "Artist":
            self._song_list = [song for song in self._song_list if song["artist"] == self.artist.text]
        self.other_songs.items = self._get_other_songs()
        self.other_songs.update_slider()

    def _save_playlist(self):
        key = ["name", "artist", "genre", "length"]
        final = []

        with open(ASSETS["PLAYLISTS"], "r") as f:
            users = json.load(f)

        if self.username not in users:
            users[self.username] = {}

        for item in self.playlist.items:
            song_dict = {}
            item = [x for x in item.split("  ") if x != '' and x != ' ']

            for i, val in enumerate(item):
                song_dict[key[i]] = val
            final.append(song_dict)

            users[self.username][self.name.text] = final

        with open(ASSETS["PLAYLISTS"], "w") as f:
            json.dump(users, f)

    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)
                if type(element) == ui.Button and element.active:
                    if element.redirect:
                        self.filters.items = [(filter_, False) for filter_ in ["Rock", "Pop", "RNB", "Rap"]]
                        self.new_playlist = []
                        self.playlist.items = self.new_playlist
                        self._song_list = self._load_songs()
                        self.other_songs.items = self._get_other_songs()
                        self.next_scene = globals()[element.redirect]
                    if element == self.filter_button:
                        self.filter_songs()
                    if element == self.save:
                        if self.playlist.items:
                            self._save_playlist()
                            self.next_scene = globals()["library"]
                
        if self.other_songs.selected:
            self.new_playlist.append(self.other_songs.selected)
            self.other_songs.selected = None
            self.playlist.items = self.new_playlist
            self.playlist.update_slider()
            self.other_songs.items = self._get_other_songs()
            self.other_songs.update_slider()

        if self.playlist.selected:
            self.new_playlist.remove(self.playlist.selected)
            self.playlist.items = self.new_playlist
            self.playlist.selected = None
            self.playlist.update_slider()
            self._song_list = self._load_songs()
            self.other_songs.items = self._get_other_songs()
            self.other_songs.update_slider()

    def update(self):
        super().update()
        self._get_user_playlists()
        self.name.org_text = self._get_playlist_num()
        self.other_songs.items = self._get_other_songs()

    def render(self, screen):
        screen.blit(pygame.image.load(ASSETS["PLAYLIST_BG"]), (0, 0))
        super().render(screen)

class PlaylistViewer(Scene):
    def __init__(self):
        super().__init__()
        self.ui_elements = [
            ui.TextBox(0, 0, 200, 50, text="Add to Favourites", background=False),
            ui.TextBox(0, 0, 200, 50, text="Remove from Favourites", background=False),
            ui.Button(0, 0, 200, 50, text="Back"),
        ]

    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)

    def update(self):
        super().update()

    def render(self, screen):
        super().render(screen)

class Settings(Scene):
    def __init__(self):
        super().__init__()
        self.ui_elements = [
            ui.TextBox(0, 0, 200, 50, text="Settings", background=False, editable=False),
            ui.TextBox(0, 0, 200, 50, text="Change Username", max_length=22),
            ui.TextBox(0, 0, 200, 50, text="Change Password", max_length=22),
            ui.TextBox(0, 0, 200, 50, text="Confirm Password", max_length=22),
            ui.Button(0, 0, 200, 50, text="Delete Account", redirect="main_menu"),
            ui.Button(0, 0, 200, 50, text="Back", redirect="library"),
            ui.DropDown(0, 0, 200, 50, options=["Rock", "Pop", "RNB", "Rap"], selected="Favourite Genre"),
            ui.TextBox(0, 0, 200, 50, text="Favourite Artist", max_length=40),
        ]

    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)

    def update(self):
        super().update()

    def render(self, screen):
        super().render(screen)

class UITest(Scene):
    def __init__(self):
        super().__init__()
        placeholder = [
    {
        "name": "Me N my Kup",
        "artist": "Ken Carson",
        "genre": "Rap",
        "length": "3:55"
    },
    {
        "name": "Breathe",
        "artist": "Yeat",
        "genre": "Rap",
        "length": "2:51"
    },
    {
        "name": "90210",
        "artist": "Travis Scott",
        "genre": "Rap",
        "length": "5:40"
    },
    {
        "name": "Miss The Rage",
        "artist": "Trippie Red",
        "genre": "Rap",
        "length": "3:57"
    },
    {
        "name": "levitating",
        "artist": "Dua Lipa",
        "genre": "Pop",
        "length": "3:41"
    },
    {
        "name": "Just Dance",
        "artist": "Lady Gaga",
        "genre": "Pop",
        "length": "4:02"
    },
    {
        "name": "Smooth Criminal",
        "artist": "Michael Jackson",
        "genre": "Pop",
        "length": "4:12"
    },
    {
        "name": "Kill Bill",
        "artist": "SZA",
        "genre": "Pop",
        "length": "2:36"
    },
    {
        "name": "Easy on me",
        "artist": "Adele",
        "genre": "Pop",
        "length": "3:46"
    },
    {
        "name": "Unnamed1",
        "artist": "Sade",
        "genre": "RNB",
        "length": "0:00"
    },
    {
        "name": "Unnamed2",
        "artist": "Usher",
        "genre": "RNB",
        "length": "0:00"
    },
    {
        "name": "Nights",
        "artist": "Frank Ocean",
        "genre": "RNB",
        "length": "0:00"
    },
    {
        "name": "Unnamed3",
        "artist": "Prince",
        "genre": "RNB",
        "length": "0:00"
    },
    {
        "name": "Unnamed4",
        "artist": "Rich Amiri",
        "genre": "RNB",
        "length": "0:00"
    },
    {
        "name": "Unnamed5",
        "artist": "Foo Fighters",
        "genre": "Rock",
        "length": "0:00"
    },
    {
        "name": "Unnamed6",
        "artist": "Led Zeppelin",
        "genre": "Rock",
        "length": "0:00"
    },
    {
        "name": "Unnamed7",
        "artist": "Nirvana",
        "genre": "Rock",
        "length": "0:00"
    },
    {
        "name": "Unnamed8",
        "artist": "Radiohead",
        "genre": "Rock",
        "length": "0:00"
    },
    {
        "name": "505",
        "artist": "Arctic Monkeys",
        "genre": "Rock",
        "length": "0:00"
    }
]
        for song in placeholder:
            song.pop("genre", None)
            song.pop("length", None)
        self.ui_elements = [
            ui.Button(100, 100, 200, 50, text="Button 1"),
            ui.TextBox(100, 300, 200, 50, text="Text Box 1", editable=True),
            ui.TextBox(300, 300, 100, 50, text="Title", background=False),
            (item_list:= ui.ItemList(700, 30, 500, 25, items=["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6", "Item 7", "Item 8", "Item 9", "Item 10"], max_items=7)),
            ui.DropDown(100, 500, 200, 50, options=["Option 1", "Option 2", "Option 3", "Option 4", "Option 5", "Option 6", "Option 7", "Option 8", "Option 9", "Option 10"]),
            ui.SearchBox(500, 100, 700, 50, reference=placeholder, background=False),
            ui.Checkboxes(500, 200, 200, 50, items=["Checkbox 1", "Checkbox 2", "Checkbox 3", "Checkbox 4"], background=False),
        ]

    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)

    def update(self):
        super().update()

    def render(self, screen):
        screen.fill(ui.COLOURS["WHITE"])
        super().render(screen)



globals().update({
    "main_menu": MainMenu(),
    "library": Library(),
    "tutorial": Tutorial(),
    "playlist_maker": PlaylistMaker(),
})