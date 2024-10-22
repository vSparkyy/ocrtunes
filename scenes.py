import pygame
import ui
import os
import random
import json
from datetime import datetime
from file_handler import handle_image_change

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
    "PLAYLIST_VIEW": os.path.join(BASE_PATH, "assets/backgrounds/playlist_viewer.png"),
    "PLAYLIST_INFO": os.path.join(BASE_PATH, "assets/backgrounds/playlist_info.png"),
    "SETTINGS_BG": os.path.join(BASE_PATH, "assets/backgrounds/settings.png"),
    "DEFAULT": os.path.join(BASE_PATH, "assets/images/default.png"),
    "BIN": os.path.join(BASE_PATH, "assets/images/bin.png"),
    "SORT": os.path.join(BASE_PATH, "assets/images/sort.png"),
    "CROSS": os.path.join(BASE_PATH, "assets/images/cross.png"),
    "CHANGE_IMG": os.path.join(BASE_PATH, "assets/images/change_image.png"),
    "EDIT": os.path.join(BASE_PATH, "assets/images/edit.png"),
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
                        self._reset()
                        if self.users[info['username']].get('ADMIN', {}):
                            self.next_scene = globals()["admin_panel"]
                        else:
                            # update username across all scenes
                            globals()["tutorial"].username = info['username']
                            globals()["library"].username = info['username']
                            globals()["playlist_maker"].username = info['username']
                            globals()["playlist_viewer"].username = info['username']
                            globals()["settings"].username = info['username']
                            self.next_scene = globals()[element.redirect]
                    else:
                        self.error_text.text = result[1]

    def update(self):
        super().update()
        # particle manager
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

    def _reset(self):
        self.l_username.text = "Username"
        self.l_password.text = "Password"
        self.s_username.text = "Username"
        self.s_password.text = "Password"
        self.s_confirm_password.text = "Confirm Password"

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
                json.dump(self.users, f, indent=4)

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
            (favourite_genre:= ui.DropDown(430, 440, 500, 45, options=["Afrobeats", "RNB", "Pop", "Rap"], selected="Favourite Genre")),
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
                            json.dump(users, f, indent=4)
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
            json.dump(users, f, indent=4)

class Library(Scene):
    def __init__(self):
        super().__init__()
        self.songs = self._get_song_list()
        self.init = True
        self.redirected = True
        self.ui_elements = [
            (song_list:= ui.ItemList(180, 400, 750, 50, items=self.songs, max_items=7)),
            ui.TextBox(520, 350, 100, 50, text=f"Title{' '*35}Artist{' '*32}Genre{' '*30}Duration", background=False),
            ui.Button(0, 186, 200, 50, text="Home", background=False),
            ui.Button(0, 238, 200, 50, text="Make Playlist", background=False, redirect="playlist_maker"),
            ui.Button(0, 288, 200, 50, text="My Playlists", background=False, redirect="playlist_viewer"),
            ui.Button(0, 783, 200, 50, text="Settings", background=False, redirect="settings"),
            ui.Button(0, 833, 200, 50, text="Log Out", background=False, redirect="main_menu"),
            (sort_name:= ui.Button(255, 362, 50, 50, icon=ASSETS["SORT"], background=False)),
            (sort_length:= ui.Button(937, 362, 50, 50, icon=ASSETS["SORT"], background=False)),
            (afrobeats:= ui.Button(172, 170, 200, 100, text="Afrobeats", background=False)),
            (rap:= ui.Button(325, 170, 200, 100, text="Rap", background=False)),
            (pop:= ui.Button(475, 170, 200, 100, text="Pop", background=False)),
            (rnb:= ui.Button(630, 170, 200, 100, text="RNB", background=False)),
            (search:= ui.SearchBox(250, 18, 760, 60, reference=self._song_list, background=False)),
            (artist:= ui.TextBox(1055, 110, 300, 50, text="Artist", editable=True, max_length=22)),
            (genre:= ui.DropDown(1250, 170, 60, 40, options=["Afrobeats", "Pop", "RNB", "Rap"], selected="Genre")),
            (length:= ui.TextBox(1090, 170, 100, 40, text="Length(m)", editable=True, max_length=2)),
            (song_num:= ui.DropDown(1190, 170, 60, 40, options=[str(i) for i in range(1, 6)], selected="Songs")),
            (confirm:= ui.Button(1055, 415, 300, 30, text="Confirm")),
            (error_text:= ui.TextBox(240, 70, 760, 50, text="", background=False)),
            (playlists:= ui.ItemList(1080, 550, 250, 30, items=[], max_items=5, offset=12)),
            (artist2:= ui.TextBox(1080, 775, 250, 50, text="Artist", editable=True, max_length=22)),
            (success_text:= ui.TextBox(240, 70, 760, 50, text="", background=False)),
        ]
        self.artist = artist
        self.artist2 = artist2
        self.playlists = playlists
        self.confirm = confirm
        self.error_text = error_text
        self.success_text = success_text
        self.genre = genre
        self.length = length
        self.song_num = song_num
        self.sort_name = sort_name
        self.sort_length = sort_length
        self.afrobeats = afrobeats
        self.pop = pop
        self.rnb = rnb
        self.rap = rap
        self.genres = [self.afrobeats, self.pop, self.rnb, self.rap]
        self.song_list = song_list
        self.song_list.scene_colour = ui.COLOURS["WHITE"]
        self.search = search
        for element in self.ui_elements:
            if element in self.genres:
                element.font = pygame.font.Font(ui.ASSETS["BOLD"], 32)
            elif type(element) == ui.TextBox or type(element) == ui.Button:
                element.font = pygame.font.Font(ui.ASSETS["BOLD"], 20)
        
        self.error_text.text_colour = ui.COLOURS["RED"]
        self.success_text.text_colour = ui.COLOURS["GREEN"]
        self.error_text.font = pygame.font.Font(ui.ASSETS["BOLD"], 20)
        self.success_text.font = pygame.font.Font(ui.ASSETS["BOLD"], 20)
    
    def _generate_playlist(self):
        playlist = []

        num = int(self.song_num.selected) if self.song_num.selected != "Songs" else None
        genre = self.genre.selected if self.genre.selected != "Genre" else None
        length = min(max(int(self.length.text), 5), 20) if self.length.text != "Length(m)" else None
        artist = self.artist.text if self.artist.text != "Artist" else None

        with open(ASSETS['SONGS'], "r") as f:
            songs = json.load(f)
            random.shuffle(songs)

        if not any([genre, length, num, artist]):
            self.error_text.text = "Select either a maximum duration, a maximum number of songs, or an artist"
            return

        for song in songs:
            if artist and song['artist'].lower() != artist.lower():
                continue
            if genre and song['genre'] != genre:
                continue
            if length and self._parse_song_length(song) >= length:
                continue
            if num and len(playlist) >= num:
                break
            playlist.append(song)

        if artist and not playlist:
            self.error_text.text = "Artist not in song library"
            return

        return playlist
    
    def _sort_songs(self, by):
        formatted_songs = []
        for song in self.songs:
            split = song.split("  ")
            formatted_songs.append([s for s in split if s != '' and s != ' '])
        if by == "name":
            formatted_songs.sort()
        elif by == "length":
            formatted_songs.sort(key=lambda x: x[3].split(":")[0]*60 + x[3].split(":")[1])

        self.song_list.items = self._get_song_list(songs=formatted_songs)

    def _parse_song_length(self, song):
        minutes, seconds = song['length'].split(":")
        minutes, seconds = int(minutes), int(seconds)
        return minutes + seconds / 60

    def _get_song_list(self, songs=None):
        final_list = []
        space_width = ui.BUTTON_FONT.render(" ", True, (0, 0, 0)).get_width()

        if not songs:
            self._song_list = self._load_songs()
        else:
            self._song_list = [
                {
                    "name": song[0].strip(),
                    "artist": song[1].strip(),
                    "genre": song[2].strip(),
                    "length": song[3].strip()
                }
                for song in songs
            ]

        for song in self._song_list:
            entry = ""
            if type(song) == dict:
                song = song.values()
            for value in song:
                entry += value
                font_offset = ui.BUTTON_FONT.size(value)[0]
                entry += " " * ((space_width*45 - font_offset)//space_width)
            final_list.append(entry)

        return final_list
    
    def _load_songs(self):
        with open(ASSETS["SONGS"], "r") as f:
            return json.load(f)

    def _get_playlists(self):
        with open(ASSETS["PLAYLISTS"], "r") as f:
            return json.load(f)
    
    def _save_playlist(self, playlist):
        users = self._get_playlists()

        if self.username not in users:
            users[self.username] = {}

        length = len(users[self.username]) + 1
        while f"My Playlist #{length}" in users[self.username]:
            length += 1

        users[self.username][f"My Playlist #{length}"] = {}
        users[self.username][f"My Playlist #{length}"]["songs"] = playlist
        users[self.username][f"My Playlist #{length}"]["img"] = ASSETS["DEFAULT"]

        with open(ASSETS["PLAYLISTS"], "w") as f:
            json.dump(users, f, indent=4)

        globals()["playlist_viewer"].new = True

    def _export_playlist(self, playlist):
        num = 1
        path = os.path.join(BASE_PATH, f"export{num}.txt")
        while os.path.exists(path):
            num += 1
            path = os.path.join(BASE_PATH, f"export{num}.txt")
        with open(path, "w") as f:
            if self.playlists.selected:
                f.write(f"{self.playlists.selected}\n{'-'*len(self.playlists.selected)}\n\n")
            else:
                f.write(f"{self.artist2.text.title()}\n{'-'*len(self.artist2.text)}\n\n")
            for i, song in enumerate(playlist):
                f.write("\n".join(f"{key}: {value}" for key, value in song.items()))
                if i < len(playlist) - 1:
                    f.write("\n\n")

        self.playlists.selected = None
        self.artist2.text = self.artist2.org_text
        return num

    def _reset_playlists(self):
        if self.username not in self._get_playlists():
            self.playlists.items = []
            return
        self.playlists.items = self._get_playlists()[self.username].keys()
        self.playlists.dy = 0
        self.playlists.update_slider()

    def _get_artist_playlists(self):
        songs = self._load_songs()
        final = []
        for song in songs:
            if song['artist'].lower() == self.artist2.text.lower():
                final.append(song)
        return final

    def process_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.error_text.text = ""
                self.success_text.text = ""
            for element in self.ui_elements:
                element.handle_event(event)
                if type(element) == ui.Button and element.active:
                    if element == self.confirm:
                        playlist = self._generate_playlist()
                        if playlist:
                            self._save_playlist(playlist)
                            self.success_text.text = "Playlist Saved!"
                            self.genre.selected = "Genre"
                            self.length.text = "Length(m)"
                            self.song_num.selected = "Songs"
                            self.artist.text = "Artist"
                            self._reset_playlists()
                    if element.text == "Make Playlist":
                        globals()["playlist_maker"]._reset()
                    if element.redirect:
                        self.next_scene = globals()[element.redirect]
                        self.init = True
                    if element == self.sort_name:
                        self._sort_songs("name")
                    if element == self.sort_length:
                        self._sort_songs("length")

        if self.playlists.selected or (self.artist2.text != self.artist2.org_text and not self.artist2.active):
            if self.playlists.selected:
                playlist = self._get_playlists()[self.username][self.playlists.selected]['songs']
            else:
                playlist = self._get_artist_playlists()
            
            if playlist:
                path = self._export_playlist(playlist)
                self.success_text.text = f"Playlist exported to 'export{path}'!"
            else:
                self.error_text.text = "No songs found"
        
        for genre in self.genres:
            if genre.active and not self.search.active:
                globals()["playlist_maker"].filters.items[globals()["playlist_maker"].filters.items.index((genre.text, False))] = (genre.text, True)
                self.next_scene = globals()["playlist_maker"]
                globals()["playlist_maker"].filter_songs()
                break

    def update(self):
        super().update()
        selected_song = self.search.selected or self.song_list.selected
        if selected_song:
            if selected_song == self.search.selected:
                for song in self._song_list:
                    if song["name"] == selected_song[0]:
                        selected_song = globals()["playlist_maker"]._format_song_list([song])[0]
                        break
            globals()["playlist_maker"]._reset([selected_song])
            self.search.selected = None
            self.song_list.selected = None
            self.next_scene = globals()["playlist_maker"]

        if self.init:
            self._reset_playlists()
            self.init = False
        
    def render(self, screen):
        screen.blit(pygame.image.load(ASSETS["LIBRARY_BG"]), (0, 0))
        super().render(screen)

class PlaylistMaker(Scene):
    def __init__(self):
        super().__init__()
        self._song_list = self._load_songs()
        self.new_playlist = []
        self.other_songs = self._get_other_songs()
        
        self.ui_elements = [
            ui.Button(0, 186, 198, 50, text="Home", background=False, redirect="library"),
            ui.Button(0, 238, 200, 50, text="Make Playlist", background=False),
            ui.Button(0, 288, 200, 50, text="My Playlists", background=False, redirect="playlist_viewer"),
            ui.Button(0, 783, 200, 50, text="Settings", background=False, redirect="settings"),
            ui.Button(0, 833, 200, 50, text="Log Out", background=False, redirect="main_menu"),
            (error_text:= ui.TextBox(320, 180, 750, 50, text="", background=False)),
            (filters:= ui.Checkboxes(1125, 270, 200, 45, items=["Afrobeats", "Pop", "RNB", "Rap"], background=False)),
            (playlist:= ui.ItemList(220, 258, 750, 30, items=self.new_playlist, max_items=5, offset=12)),
            (other_songs:= ui.ItemList(220, 550, 750, 30, items=self.other_songs, max_items=5, offset=12)),
            (name:= ui.TextBox(320, 142, 750, 50, text="", editable=True, max_length=20, border_radius=0, background=False)),
            (filter_button:= ui.Button(1150, 600, 200, 50, text="Filter")),
            (artist:= ui.TextBox(1150, 470, 200, 50, text="Artist", editable=True, max_length=22)),
            (save:= ui.Button(445, 775, 400, 50, text="Save Playlist")),
        ]
        self.save = save
        self.error_text = error_text
        self.artist = artist
        self.artist.active_colour = ui.COLOURS["NAVY"]
        self.filter_button = filter_button
        self.other_songs = other_songs
        self.playlist = playlist
        self.name = name
        self.name.centred = False
        self.override = False
        self.filters = filters

        self._reset_initial_slider()

        self.save.bg_colour = ui.COLOURS["DARK_BLUE"]
        self.save.active_colour = ui.COLOURS["LIGHT_BLUE"]

        for element in self.ui_elements:
            if type(element) == ui.TextBox or type(element) == ui.Button:
                element.font = pygame.font.Font(ui.ASSETS["BOLD"], 20)
            elif type(element) == ui.ItemList:
                element.scene_colour = ui.COLOURS['LIGHT_BLUE']
                element.slider_colour = ui.COLOURS['DARK_BLUE']
                element.bg_colour = ui.COLOURS['CREAM']

        self.error_text.text_colour = ui.COLOURS["RED"]
        self.error_text.font = pygame.font.Font(ui.ASSETS["BOLD"], 32)

    def _reset_initial_slider(self):
        self.playlist.items = self._song_list
        self.playlist.dy = 0
        self.playlist.update_slider()
        self.playlist.items = self.new_playlist
        
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

        return self._format_song_list(self._song_list)
    
    def _format_song_list(self, song_list):
        final_list = []
        space_width = ui.BUTTON_FONT.render(" ", True, (0, 0, 0)).get_width()
        for song in song_list:
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
        self._reset()
        self._song_list = self._load_songs()
        selected_genres = [filter_[0] for filter_ in self.filters.items if filter_[1]]
        if selected_genres:
            self._song_list = [song for song in self._song_list if song["genre"] in selected_genres]
        if self.artist.text != "Artist":
            self._song_list = [song for song in self._song_list if song["artist"].lower() == self.artist.text.lower()]
        self.other_songs.items = self._get_other_songs()

    def _save_playlist(self):
        key = ["name", "artist", "genre", "length"]
        final = []

        with open(ASSETS["PLAYLISTS"], "r") as f:
            users = json.load(f)

        if self.username not in users:
            users[self.username] = {}

        if self.name.text in list(users[self.username].keys()) and not self.override:
            self.error_text.text = "Playlist name already exists"
        else:
            for item in self.new_playlist:
                song_dict = {}
                item = [x for x in item.split("  ") if x != '' and x != ' ']

                for i, val in enumerate(item):
                    song_dict[key[i]] = val
                final.append(song_dict)

                users[self.username][self.name.text] = {}
                users[self.username][self.name.text]['songs'] = final
                users[self.username][self.name.text]['img'] = ASSETS["DEFAULT"]
        
            with open(ASSETS["PLAYLISTS"], "w") as f:
                json.dump(users, f, indent=4)

            self.error_text.text = ""

        globals()["playlist_viewer"].new = True

    def _reset(self, new=None):
        if not new:
            new = []
        self.filters.items = [(filter_, False) for filter_ in ["Afrobeats", "Pop", "RNB", "Rap"]]
        self.new_playlist = new
        self.playlist.items = new
        self._song_list = self._load_songs()
        self._reset_initial_slider()
        self.other_songs.items = self._get_other_songs()
        self.other_songs.dy = 0
        self.other_songs.update_slider()
        self._get_user_playlists()
        self.name.org_text = self._get_playlist_num()
        self.name.text = self.name.org_text
        self.error_text.text = ""

    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)
                if element.active:
                    self.error_text.text = ""
                if type(element) == ui.Button and element.active:
                    if element.redirect:
                        self._reset()
                        self.next_scene = globals()[element.redirect]
                    if element == self.filter_button:
                        self.filter_songs()
                    if element == self.save:
                        if self.playlist.items:
                            self._save_playlist()
                            if self.error_text.text == "":
                                self._reset()
                                self.next_scene = globals()["library"]
                        else:
                            self.error_text.text = "Playlist is empty"
                
        if self.other_songs.selected:
            self.new_playlist.append(self.other_songs.selected)
            self.other_songs.selected = None
            self.playlist.items = self.new_playlist
            self.other_songs.items = self._get_other_songs()
            self.error_text.text = ""

        if self.playlist.selected:
            self.new_playlist.remove(self.playlist.selected)
            self.playlist.items = self.new_playlist
            self.playlist.selected = None
            self._song_list = self._load_songs()
            self.other_songs.items = self._get_other_songs()

    def update(self):
        super().update()
        self._get_user_playlists()
        if not self.override:
            self.name.org_text = self._get_playlist_num()
        self.other_songs.items = self._get_other_songs()

    def render(self, screen):
        screen.blit(pygame.image.load(ASSETS["PLAYLIST_BG"]), (0, 0))
        super().render(screen)

class PlaylistViewer(Scene):
    def __init__(self):
        self.username = None
        super().__init__()
        self.ui_elements = [
            ui.Button(0, 186, 198, 50, text="Home", background=False, redirect="library"),
            ui.Button(0, 238, 200, 50, text="Make Playlist", background=False, redirect="playlist_maker"),
            ui.Button(0, 288, 200, 50, text="My Playlists", background=False),
            ui.Button(0, 783, 200, 50, text="Settings", background=False, redirect="settings"),
            ui.Button(0, 833, 200, 50, text="Log Out", background=False, redirect="playlist_viewer"),
            (slide:=ui.PlaylistSlide(225, 80, 350, 250, items=self._get_playlists())),
            ui.TextBox(675, 20, 200, 50, text="My Playlists", background=False)
        ]
        self.pop_up_elements = [
            ui.ArbitraryRect(330, 125, 900, 700, colour=ui.COLOURS["WHITE"]),
            ui.Button(500, 140, 600, 50, text="", background=False, hover=ASSETS["EDIT"]),
            playlist_name:=(ui.TextBox(505, 140, 600, 50, text="", editable=True, max_length=20, background=False)),
            exit_button:=(ui.Button(1170, 125, 100, 100, icon=ASSETS["CROSS"])),
            song_length:=(ui.TextBox(505, 180, 200, 50, text="", background=False)),
            track_length:=(ui.TextBox(505, 210, 200, 50, text="", background=False)),
            songs:=(ui.ItemList(350, 350, 750, 50, items=[], max_items=6)),
            delete:=(ui.Button(570, 260, 50, 50, icon=ASSETS["BIN"])),
            edit:=(ui.Button(520, 260, 50, 50, icon=ASSETS["EDIT"])),
            image:=(ui.Button(350, 145, 150, 150, icon=ASSETS["DEFAULT"], hover=ASSETS["CHANGE_IMG"])),
            error_text:=(ui.TextBox(330, 290, 900, 50, text="", background=False)),
        ]

        self.playlist_name = playlist_name
        self.exit_button = exit_button
        self.error_text = error_text
        self.delete = delete
        self.image = image
        self.edit = edit
        self.song_length = song_length
        self.track_length = track_length
        self.songs = songs
        self.deactivated = False
        self.active_elements = self.ui_elements
        self.slide = slide
        self.slide.scene_colour = ui.COLOURS["WHITE"]
        self.new = True
        self.transparent_bg = pygame.Surface((1400, 900), pygame.SRCALPHA)
        self.tb_pos = (163, 0)

        for element in self.ui_elements:
            if type(element) == ui.TextBox or type(element) == ui.Button:
                element.font = pygame.font.Font(ui.ASSETS["BOLD"], 20)
                if element.text == "My Playlists" and type(element) == ui.TextBox:
                    element.font = pygame.font.Font(ui.ASSETS["BOLD"], 36)

        for element in self.pop_up_elements:
            if type(element) == ui.TextBox:
                element.centred = False
                element.font = pygame.font.Font(ui.ASSETS["REGULAR"], 25)
                if element == self.error_text:
                    element.text_colour = ui.COLOURS["RED"]
                    element.font = pygame.font.Font(ui.ASSETS["BOLD"], 25)
        self.playlist_name.font = pygame.font.Font(ui.ASSETS["BOLD"], 32)

    def _load_playlist(self):
        with open(ASSETS["PLAYLISTS"], "r") as f:
            return json.load(f)
        
    def _save_playlist(self, playlist):
        with open(ASSETS["PLAYLISTS"], "w") as f:
            json.dump(playlist, f, indent=4)

    def _get_playlists(self):
        self.users = self._load_playlist()
        if self.username not in self.users:
            return []
        return [ui.Playlist({playlist: vals}) for playlist, vals in self.users[self.username].items()]

    def process_input(self, events):
        for event in events:
            for element in self.active_elements:
                if self.deactivated and element not in self.pop_up_elements:
                    if element.rect.x in range(self.tb_pos[0], self.transparent_bg.get_width()-self.tb_pos[0]) and element.rect.y in range(self.tb_pos[1], self.transparent_bg.get_height()-self.tb_pos[1]):
                        continue

                element.handle_event(event)
                if element.active:
                    self.error_text.text = ""
                    if element == self.delete:
                        self.users[self.username].pop(self.playlist_name.text)
                        with open(ASSETS["PLAYLISTS"], "w") as f:
                            json.dump(self.users, f, indent=4)
                        self.slide.items = self._get_playlists()
                        self.deactivated = False
                        self.active_elements = self.ui_elements

                    if element == self.edit:
                        self.deactivated = False
                        self.active_elements = self.ui_elements
                        self.next_scene = globals()["playlist_maker"]
                        self.next_scene._reset(self.songs.items)
                        self.next_scene.name.text = self.playlist_name.text
                        self.next_scene.name.org_text = self.playlist_name.text
                        self.next_scene.override = True

                    if element == self.exit_button:
                        self.deactivated = False
                        self.active_elements = self.ui_elements

                    if element == self.image:
                        result = handle_image_change(self.username, os.path.join(BASE_PATH, "assets/user_images"), (150,150))
                        try:
                            pygame.image.load(result)
                            self._change_playlist_image(result)
                        except:
                            self.error_text.text = result
                else:
                    if element == self.playlist_name:
                        if self.playlist_name.text != self.playlist_name.org_text and self.playlist_name.text != "":
                            self._handle_name_change()

                if type(element) == ui.Button and element.active:
                    if element.redirect:
                        self.next_scene = globals()[element.redirect]
                            
        if self.slide.selected:
            self.deactivated = True
            self.temp = self.slide.selected
            self.active_elements = self.ui_elements + self.pop_up_elements
            self.handle_pop_up()

    def _change_playlist_image(self, img):
        self.users[self.username][self.playlist_name.text]["img"] = img
        self._save_playlist(self.users)
        self.image.update_icon(img)
        self.temp.update_image(img)
    
    def _handle_name_change(self):
        if self.playlist_name.text not in self.users[self.username]:
            self.users[self.username][self.playlist_name.text] = self.users[self.username].pop(self.old_name)
            self._save_playlist(self.users)
            self.slide.items = self._get_playlists()
            self.old_name = self.playlist_name.text
            self.playlist_name.org_text = self.playlist_name.text
            self.users = self._load_playlist()
        else:
            self.error_text.text = "Playlist name already exists"
            self.playlist_name.text = self.old_name
            self.playlist_name.org_text = self.old_name

    def _parse_song_length(self, song):
        minutes, seconds = map(int, song['length'].split(":"))
        return minutes + seconds / 60
    
    def _format_songs(self, songs):
        final_list = []
        space_width = ui.BUTTON_FONT.render(" ", True, (0, 0, 0)).get_width()
        for song in songs:
            entry = ""
            for value in song.values():
                entry += value
                font_offset = ui.BUTTON_FONT.size(value)[0]
                entry += " " * ((space_width*45 - font_offset)//space_width)
            final_list.append(entry)

        return final_list

    def handle_pop_up(self):
        self.info = self.slide.selected.old_info
        playlist_name = list(self.info.keys())[0]
        self.playlist_name.text = playlist_name
        self.old_name = playlist_name
        self.playlist_name.org_text = playlist_name

        songs = self.info[playlist_name]['songs']
        self.song_length.text = f"Total Songs: {len(songs)}"
        total_length = round(sum(self._parse_song_length(song) for song in songs))
        self.track_length.text = f"Total Length: {total_length} minutes"
        self.songs.items = self._format_songs(songs)

        img_path = self.info[playlist_name]['img']
        if not os.path.exists(img_path):
            img_path = ASSETS["DEFAULT"]
            self.users[self.username][playlist_name]["img"] = img_path
            self._save_playlist(self.users)

        self.image.update_icon(img_path)
        self.songs.dy = 0
        self.songs.update_slider()
        self.slide.selected = None

    def update(self):
        if self.new:
            self.slide.items = self._get_playlists()
            self.slide.dy = 0
            self.slide.update_slider()
            self.new = False
        for element in self.active_elements:
            element.update()

    def render(self, screen):
        screen.blit(pygame.image.load(ASSETS["PLAYLIST_VIEW"]), (0, 0))
        super().render(screen)
        if self.deactivated:
            pygame.draw.rect(self.transparent_bg, (168, 182, 250, 200), self.transparent_bg.get_rect())
            screen.blit(self.transparent_bg, self.tb_pos) 
            for element in self.pop_up_elements:
                element.draw(screen)

class Settings(Scene):
    def __init__(self):
        super().__init__()
        self.ui_elements = [
            ui.Button(0, 186, 198, 50, text="Home", background=False, redirect="library"),
            ui.Button(0, 238, 200, 50, text="Make Playlist", background=False, redirect="playlist_maker"),
            ui.Button(0, 288, 200, 50, text="My Playlists", background=False, redirect="playlist_viewer"),
            ui.Button(0, 783, 200, 50, text="Settings", background=False),
            ui.Button(0, 833, 200, 50, text="Log Out", background=False, redirect="main_menu"),
            (change_username:= ui.TextBox(180, 225, 300, 50, max_length=22, editable=True)),
            (change_password:= ui.TextBox(180, 345, 300, 50, max_length=22, editable=True)),
            (confirm_password:= ui.TextBox(180, 465, 300, 50, max_length=22, editable=True)),
            (submit:= ui.Button(775, 825, 600, 50, text="Submit")),
            (confirm:= ui.Button(185, 825, 550, 50, text="Confirm")),
            (delete_account:= ui.Button(470, 120, 250, 30, text="DELETE ACCOUNT")),
            (fav_artist:= ui.TextBox(775, 230, 300, 50, editable=True, max_length=22)),
            (fav_genre:= ui.DropDown(775, 340, 300, 50, options=["Afrobeats", "Pop", "RNB", "Rap"])),
            (error_text:= ui.TextBox(180, 530, 750, 50, background=False)),
            (success_text:= ui.TextBox(180, 530, 750, 50, background=False)),
        ]

        self.init = True

        self.change_username = change_username
        self.change_password = change_password
        self.confirm_password = confirm_password
        self.confirm = confirm
        self.submit = submit
        self.delete_account = delete_account
        self.fav_artist = fav_artist
        self.fav_genre = fav_genre
        self.error_text = error_text
        self.success_text = success_text

        for element in self.ui_elements:
            if type(element) == ui.Button:
                element.font = pygame.font.Font(ui.ASSETS["BOLD"], 20)

        self.error_text.text_colour = ui.COLOURS["RED"]
        self.success_text.text_colour = ui.COLOURS["GREEN"]
        self.error_text.font = pygame.font.Font(ui.ASSETS["BOLD"], 32)
        self.success_text.font = pygame.font.Font(ui.ASSETS["BOLD"], 32)
        self.error_text.centred = False
        self.success_text.centred = False

        self.delete_account.bg_colour = ui.COLOURS["RED"]

    def _get_user_info(self):
        with open(ASSETS['USERS'], 'r') as f:
            return json.load(f)

    def _dump_user_info(self, users):
        with open(ASSETS['USERS'], 'w') as f:
            json.dump(users, f, indent=4)

    def _save_info(self, info):
        users = self._get_user_info()
        users[self.username].update(info)
        self._dump_user_info(users)

    def _update_username(self):
        users = self._get_user_info()
        users[self.change_username.text] = users.pop(self.username)
        self._dump_user_info(users)
        self.username = self.change_username.text
        self.change_username.org_text = self.username

    def _get_account_preferences(self):
        users = self._get_user_info()
        return users[self.username]["favourite_artist"], users[self.username]["favourite_genre"]

    def _delete_account(self):
        users = self._get_user_info()
        users.pop(self.username)
        self._dump_user_info(users)

    def _validate_username(self, username):
        if not username:
            return (False, "Please enter a username")
        if username == self.username:
            return (True, "")
        if username in self._get_user_info():
            return (False, "Username already exists")
        return (True, "")
        
    def validate_password(self):
        if not self.change_password.text:
            return (True, "UNCHANGED")
        if self.change_password.text != self.confirm_password.text:
            return (False, "Passwords do not match")
        return (True, "")

    def process_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.error_text.text = ""
                self.success_text.text = ""
            for element in self.ui_elements:
                element.handle_event(event)
                if type(element) == ui.Button and element.active:
                    if element.redirect:
                        self.next_scene = globals()[element.redirect]
                        self.init = True
                    if element == self.confirm:
                        username = self.change_username.text
                        user_outcome = self._validate_username(username)
                        pass_outcome = self.validate_password()
                        if user_outcome[0] and pass_outcome[0]:
                            new_password = self.change_password.text if pass_outcome[1] != "UNCHANGED" else self._get_user_info()[self.username]["password"]
                            self._save_info({"username": username, "password": new_password})
                            self._update_username()
                            self.success_text.text = "Account updated!"
                            self.change_password.text = ""
                            self.confirm_password.text = ""
                        else:
                            self.error_text.text = user_outcome[1] if not user_outcome[0] else pass_outcome[1]

                    if element == self.submit:
                        fav_artist = self.fav_artist.text
                        fav_genre = self.fav_genre.selected
                        self._save_info({"favourite_artist": fav_artist, "favourite_genre": fav_genre})
                        self.success_text.text = "Preferences saved!"

                    if element == self.delete_account:
                        self._delete_account()
                        self.next_scene = globals()["main_menu"]

    def update(self):
        super().update()
        if self.init:
            self.fav_artist.text, self.fav_genre.selected = self._get_account_preferences()
            self.fav_artist.org_text = self.fav_artist.text
            self.change_username.text = self.username
            self.change_username.org_text = self.username
            self.init = False

    def render(self, screen):
        screen.blit(pygame.image.load(ASSETS["SETTINGS_BG"]), (0, 0))
        super().render(screen)

class Admin(Scene):
    def __init__(self):
        super().__init__()
        averages = self._get_average_lengths()
        self.ui_elements = [
            ui.TextBox(25, 50, 300, 300, text="Afrobeats"),
            ui.TextBox(375, 50, 300, 300, text="Pop"),
            ui.TextBox(725, 50, 300, 300, text="RNB"),
            ui.TextBox(1075, 50, 300, 300, text="Rap"),
            ui.TextBox(25, 400, 300, 50, text=f"Average Track Length: {averages['Afrobeats']}min"),
            ui.TextBox(375, 400, 300, 50, text=f"Average Track Length: {averages['Pop']}min"),
            ui.TextBox(725, 400, 300, 50, text=f"Average Track Length: {averages['RNB']}min"),
            ui.TextBox(1075, 400, 300, 50, text=f"Average Track Length: {averages['Rap']}min"),
            ui.Button(600, 600, 200, 50, text="Log out", background=True, redirect="main_menu"),
        ]

        for element in self.ui_elements:
            if element.text in ["Afrobeats", "Pop", "RNB", "Rap"]:
                element.font = pygame.font.Font(ui.ASSETS["BOLD"], 50)

    def _get_average_lengths(self):
        averages = {}
        with open(ASSETS["SONGS"], "r") as f:
            songs = json.load(f)
            for genre in ["Afrobeats", "Pop", "RNB", "Rap"]:
                songs_for_genre = []
                for song in songs:
                    if song['genre'] == genre:
                        songs_for_genre.append(song)
                total = sum(self._parse_song_length(song) for song in songs_for_genre)
                average = round(total / len(songs_for_genre), 2)
                averages[genre] = average

        return averages
    
    def _parse_song_length(self, song):
        minutes, seconds = song['length'].split(":")
        minutes, seconds = int(minutes), int(seconds)
        return minutes + seconds / 60

    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)
                if type(element) == ui.Button and element.active:
                    if element.redirect:
                        self.next_scene = globals()[element.redirect]

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
    "playlist_viewer": PlaylistViewer(),
    "settings": Settings(),
    "admin_panel": Admin()
})
