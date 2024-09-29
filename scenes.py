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
    "USERS": os.path.join(BASE_PATH, "assets/users.json"),
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
            (error_text:= ui.TextBox(850, 650, 500, 50, text="", editable=False, background=False)),
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
        self.ui_elements = [
            ui.Button(100, 100, 200, 50, text="Back", redirect="main_menu"),
        ]

    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)
                if type(element) == ui.Button and element.active:
                    self.next_scene = globals()[element.redirect]

    def update(self):
        super().update()

    def render(self, screen):
        screen.fill(ui.COLOURS["WHITE"])
        super().render(screen)

    def validate_info(self, info):
        pass
        # try:
        #     info['dob'] = datetime.strptime(info['dob'], "%d/%m/%y")
        # except ValueError:
        #     return (False, "Invalid Date of Birth (DD/MM/YY)")
        # if info['dob'] > datetime.now():
        #     return (False, "Invalid Date of Birth (DD/MM/YY)")
        # try:
        #     info['full_name'] = info['full_name'].split()
        #     if len(info['full_name']) < 2 or len(info['full_name']) > 3 or not all([name.isalpha() for name in info['full_name']]):
        #         raise Exception
        # except:
        #     return (False, "Please enter a valid full name")
    


class Library(Scene):
    def __init__(self):
        super().__init__()
        self.ui_elements = [
            ui.Button(100, 100, 200, 50, text="Back", redirect="main_menu"),
        ]
    
    def process_input(self, events):
        for event in events:
            for element in self.ui_elements:
                element.handle_event(event)
                if type(element) == ui.Button and element.active:
                    self.next_scene = globals()[element.redirect]

    def update(self):
        super().update()

    def render(self, screen):
        screen.fill(ui.COLOURS["WHITE"])
        super().render(screen)


globals().update({
    "main_menu": MainMenu(),
    "library": Library(),
    "tutorial": Tutorial()
})