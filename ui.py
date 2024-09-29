import pygame
import os

pygame.init()

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
COLOURS = {
    "LIGHT_BLUE": (179, 197, 251),
    "DARK_BLUE": (97, 122, 247),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
}
ASSETS = {
    "BOLD": os.path.join(BASE_PATH, "assets/fonts/CorporativeSansRdAlt-Bold.ttf"),
    "REGULAR": os.path.join(BASE_PATH, "assets/fonts/CorporativeSansRdAlt-Medium.ttf"),
}
BUTTON_FONT = pygame.font.Font(ASSETS["REGULAR"], 20)


class UIElement:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass


class Button(UIElement):
    def __init__(self, x, y, width, height, text='', border_width=0, redirect=None):
        super().__init__(x, y, width, height)
        self.redirect = redirect
        self.text = text
        self.bg_colour = COLOURS["LIGHT_BLUE"]
        self.text_colour = COLOURS["WHITE"]
        self.active = False
        self.font = BUTTON_FONT
        self.txt_surface = self.font.render(text, True, self.text_colour)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True

    def update(self):
        self.active = False
        width = max(self.width, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_colour, self.rect, 0, 25)
        screen.blit(self.txt_surface, (self.rect.x + (self.rect.width - self.txt_surface.get_width()) // 2, self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))


class TextBox(UIElement):
    def __init__(self, x, y, width, height, text='', max_length=float('inf'), background=True, editable=False):
        super().__init__(x, y, width, height)
        self.background = background
        self.max_length = max_length
        self.bg_colour = COLOURS["LIGHT_BLUE"]
        self.text_colour = COLOURS["WHITE"]
        self.text = self.org_text = text
        self.font = BUTTON_FONT
        self.editing = False
        self.editable = editable

    def handle_event(self, event):
        if self.editable:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    if self.text:
                        self.text = ''
                    self.editing = not self.editing
                else:
                    self.editing = False
            if event.type == pygame.KEYDOWN:
                if self.editing:
                    if event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    elif event.key != pygame.K_RETURN and len(self.text) < self.max_length:
                        self.text += event.unicode
                    elif event.key == pygame.K_RETURN:
                        self.editing = False

    def update(self):
        if not self.editing and not self.text:
            self.text = self.org_text
        self.txt_surface = self.font.render(self.text, True, self.text_colour)
        self.bg_colour = COLOURS['DARK_BLUE'] if self.editing else COLOURS['LIGHT_BLUE']

    def draw(self, screen):
        if self.background:
            pygame.draw.rect(screen, self.bg_colour, self.rect, 0, 5)
        screen.blit(self.txt_surface, (self.rect.x + (self.rect.width - self.txt_surface.get_width()) // 2, self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))