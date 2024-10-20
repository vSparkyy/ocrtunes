import pygame
import math
import os

pygame.init()

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
COLOURS = {
    "LIGHT_BLUE": (179, 197, 251),
    "DARK_BLUE": (97, 122, 247),
    "NAVY": (46, 74, 92),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "WHITE": (242, 245, 254),
    "BLACK": (0, 0, 0),
    "CREAM": (250, 235, 214),
    "VANILLA": (254, 253, 211)
}
ASSETS = {
    "BOLD": os.path.join(BASE_PATH, "assets/fonts/CorporativeSansRdAlt-Bold.ttf"),
    "REGULAR": os.path.join(BASE_PATH, "assets/fonts/CorporativeSansRdAlt-Medium.ttf"),
    "TICK": os.path.join(BASE_PATH, "assets/images/tick.png"),
    "BASE_PLAYLIST_IMG": os.path.join(BASE_PATH, "assets/images/default.png"),
    "PLAYLIST_INFO": os.path.join(BASE_PATH, "assets/images/playlist_info.png")
}
BUTTON_FONT = pygame.font.Font(ASSETS["REGULAR"], 20)

class UIElement:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.font = BUTTON_FONT
        self.active = False
        self.bg_colour = COLOURS["LIGHT_BLUE"]
        self.active_colour = COLOURS["DARK_BLUE"]
        self.current_colour = self.bg_colour

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active

    def update(self):
        self.current_colour = self.active_colour if self.active else self.bg_colour

    def draw(self, screen):
        pygame.draw.rect(screen, self.current_colour, self.rect, 0, 5)

class Button(UIElement):
    def __init__(self, x, y, width, height, text='', background=True, redirect=None, icon=None, hover=None, hover_pos="DEFAULT"):
        super().__init__(x, y, width, height)
        self.hover_colour = None
        self.hover_pos = (self.rect.x, self.rect.y) if hover_pos == "DEFAULT" else hover_pos
        self.icon = pygame.image.load(icon) if icon else None
        try:
            self.hover = pygame.image.load(hover)
        except:
            self.hover = None
            if hover:
                self.hover_colour = hover

        self.redirect = redirect
        self.hovering = False
        self.text = text
        self.background = background
        self.text_colour = COLOURS["WHITE"] if self.background else COLOURS["BLACK"]

    def update_icon(self, icon):
        self.icon = pygame.image.load(icon)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if self.hover_colour or self.hover:
                    self.hovering = True
            else:
                self.hovering = False

    def update(self):
        self.txt_surface = self.font.render(self.text, True, self.text_colour)
        self.current_colour = self.active_colour if self.active else self.bg_colour
        if self.hovering and self.hover_colour:
            self.current_colour = self.hover_colour
        self.active = False
        width = max(self.width, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        if not self.icon:
            if self.background:
                pygame.draw.rect(screen, self.current_colour, self.rect, 0, 25)
            screen.blit(self.txt_surface, (self.rect.x + (self.rect.width - self.txt_surface.get_width()) // 2, self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))
        else:
            screen.blit(self.icon, (self.rect.x, self.rect.y))

        if self.hovering and self.hover:
            screen.blit(self.hover, self.hover_pos)

class TextBox(UIElement):
    def __init__(self, x, y, width, height, text='', max_length=float('inf'), background=True, editable=False, border_radius=5):
        super().__init__(x, y, width, height)
        self.background = background
        self.border_radius = border_radius
        self.max_length = max_length
        self.text_colour = COLOURS["WHITE"] if self.background else COLOURS["BLACK"]
        self.text = self.org_text = text
        self.editable = editable
        self.centred = True
        self.anti_aliasing = True

    def handle_event(self, event):
        if self.editable:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    if self.text:
                        self.text = ''
                    self.active = not self.active
                else:
                    self.active = False
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    elif event.key != pygame.K_RETURN and len(self.text) < self.max_length:
                        self.text += event.unicode
                    elif event.key == pygame.K_RETURN:
                        self.active = False

    def update(self):
        if not self.active and not self.text:
            self.text = self.org_text
        self.txt_surface = self.font.render(self.text, self.anti_aliasing, self.text_colour)
        self.current_colour = self.active_colour if self.active else self.bg_colour

    def draw(self, screen):
        if self.background:
            pygame.draw.rect(screen, self.current_colour, self.rect, 0, self.border_radius)
        screen.blit(self.txt_surface, (self.rect.x + ((self.rect.width - self.txt_surface.get_width()) // 2 if self.centred else 20) , self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))

class SearchBox(TextBox):
    def __init__(self, x, y, width, height, text='Search', max_length=float('inf'), reference=[], background=True, max_items=10):
        super().__init__(x, y, width, height, text, max_length, background, editable=True)
        self.max_items = max_items
        self.items = reference
        self.search_rects = []
        self.selected = None
        self.centred = False
    
    def handle_event(self, event):
        if not self.active:
            self.selected = None

        for item, rect in self.search_rects:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect.collidepoint(event.pos) and self.active:
                    self.selected = item

        super().handle_event(event)

    def update(self):
        super().update()
    
    def draw(self, screen):
        super().draw(screen)
        if self.active:
            self._get_search_rects()
            for item, rect in self.search_rects:
                pygame.draw.rect(screen, self.bg_colour, rect)
                pygame.draw.rect(screen, COLOURS["BLACK"], rect, 1)
                txt_surface = self.font.render(item[0], True, self.text_colour)
                screen.blit(txt_surface, (rect.x + 20, rect.y + (rect.height - txt_surface.get_height()) // 2))

    def _get_search_results(self):
        items = [list(item.values()) for item in self.items]
        return [item for item in items if any(self.text.lower() in i.lower() for i in item)]

    def _get_search_rects(self):
        self.search_rects = []
        for i, item in enumerate(self._get_search_results()):
            if len(self.search_rects) == self.max_items:
                break
            rect = pygame.Rect(self.x, self.y + self.height * (i + 1), self.width, self.height)
            self.search_rects.append((item, rect))
    
class DropDown(UIElement):
    def __init__(self, x, y, width, height, options, selected=None):
        super().__init__(x, y, width, height)
        self.options = options
        self.selected = selected or options[0]
        self.text_colour = COLOURS["WHITE"]
        self.get_option_rects()

    def handle_event(self, event):
        super().handle_event(event)
        if self.active:
            for _, rect in self.option_rects:
                if rect.collidepoint(event.pos):
                    self.selected, self.listed_options[self.option_rects.index((_, rect))] = self.listed_options[self.option_rects.index((_, rect))], self.selected
                    self.active = False

    def update(self):
        self.dd_colour = self.bg_colour
        self.txt_surface = self.font.render(self.selected, True, self.text_colour)
        self.current_colour = self.active_colour if self.active else self.bg_colour
        self.get_option_rects()

    def draw(self, screen):
        pygame.draw.rect(screen, self.current_colour, self.rect, 0, 5)
        screen.blit(self.txt_surface, (self.rect.x + (self.rect.width - self.txt_surface.get_width()) // 2, self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))
        if self.active:
            for option, rect in self.option_rects:
                pygame.draw.rect(screen, self.dd_colour, rect, 0, 5)
                txt_surface = self.font.render(option, True, self.text_colour)
                screen.blit(txt_surface, (rect.x + (rect.width - txt_surface.get_width()) // 2, rect.y + (rect.height - txt_surface.get_height()) // 2))

    def get_option_rects(self):
        self.option_rects = []
        self.listed_options = self.options.copy()
        if self.selected in self.listed_options:
            self.listed_options.remove(self.selected)
            self.listed_options.sort()
        for i, option in enumerate(self.listed_options):
            rect = pygame.Rect(self.x, self.y + self.height * (i + 1), self.width, self.height)
            self.option_rects.append((option, rect))
        
class ItemList(UIElement):
    def __init__(self, x, y, width, height, items, max_items=4, offset=20):
        super().__init__(x, y, width, height)
        self.items = items
        self.font = BUTTON_FONT
        self.slider_colour = COLOURS["LIGHT_BLUE"]
        self.bg_colour = COLOURS["DARK_BLUE"]
        self.current_colour = self.bg_colour
        self.active_colour = self.slider_colour
        self.text_colour = COLOURS["BLACK"]
        self.scene_colour = COLOURS["WHITE"]
        self.offset = offset
        self.max_items = max_items
        self.selected = None
        self.dy = 0
        self.old_y = 0
        self.max_height = (self.height+self.offset) * self.max_items 
        self.active = False
        self.update_slider()
        self.get_item_rects()
        self.top_rect = pygame.Rect(self.x, self.y-self.height, self.width, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.y+self.max_height-self.offset, self.width, self.height)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        buttons = pygame.mouse.get_pressed()
        if buttons[0]:
            if self.slider_rect.collidepoint(mouse_pos):
                self.active = True
                self.active_colour = self.bg_colour
            
        else:
            self.active = False
            self.active_colour = self.slider_colour
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for item, rect, on_screen in self.item_rects:
                if rect.collidepoint(event.pos) and on_screen:
                    self.selected = item
            if self.slider_rect.collidepoint(event.pos):
                self.old_y = mouse_pos[1]
        
        if self.active:
            dy = mouse_pos[1] - self.old_y
            if self.slider_rect.y + dy >= self.y and self.slider_rect.y + dy + self.slider_rect.height <= self.y + self.max_height:
                self.dy -= dy
                self.slider_rect.y += dy
                self.old_y = mouse_pos[1]
    
    def update_slider(self):
        total_height = (self.height + self.offset) * len(self.items)
        height = min(self.max_height, total_height)
        if total_height > self.max_height:
            height -= 10 * (len(self.items)-self.max_items)
        self.slider_rect = pygame.Rect(self.x + self.width + self.offset, self.y, 20, height)

    def update(self):
        pixel_offset = self.dy / 10 * (self.height + self.offset)
        self.get_item_rects(pixel_offset)

    def draw(self, screen):
        pygame.draw.rect(screen, self.active_colour, self.slider_rect, 0, 25)
        for item, rect, on_screen in self.item_rects:
            if rect.y + self.height < self.y + self.max_height + self.offset and rect.y + self.height > self.y:
                self.item_rects[self.item_rects.index((item, rect, on_screen))] = (item, rect, True)
                pygame.draw.rect(screen, self.current_colour, rect, 0, 25)
                txt_surface = self.font.render(item, True, self.text_colour)
                screen.blit(txt_surface, (rect.x + 20, rect.y + (rect.height - txt_surface.get_height()) // 2))

        pygame.draw.rect(screen, self.scene_colour, self.top_rect)
        pygame.draw.rect(screen, self.scene_colour, self.bottom_rect)

    def get_item_rects(self, dy=0):
        self.item_rects = []
        for i, item in enumerate(self.items):
            rect = pygame.Rect(self.x, self.y + (self.height + self.offset) * i + dy, self.width, self.height)
            self.item_rects.append((item, rect, False))

class Checkboxes(UIElement):
    def __init__(self, x, y, width, height, items, background=True):
        super().__init__(x, y, width, height)
        self.items = items
        self.items = list(zip(self.items, [False] * len(self.items)))
        self.font = BUTTON_FONT
        self.tick = pygame.image.load(ASSETS["TICK"])
        self.checkbox_colour = COLOURS["LIGHT_BLUE"]
        self.text_colour = COLOURS["BLACK"]
        self.selected = []
        self.background = background
        self.get_checkbox_rects()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for item, _, checkbox_rect in self.checkbox_rects:
                if checkbox_rect.collidepoint(event.pos):
                    new_item = (item[0], not item[1])
                    self.items[self.items.index(item)] = new_item

    def update(self):
        super().update()
        self.get_checkbox_rects()

    def draw(self, screen):
        for item, rect, checkbox_rect in self.checkbox_rects:
            if self.background:
                pygame.draw.rect(screen, self.bg_colour, rect, 0, 25)
            txt_surface = self.font.render(item[0], True, self.text_colour)
            checkbox_rect.y = rect.y + (rect.height - txt_surface.get_height()) // 2
            pygame.draw.rect(screen, self.checkbox_colour, checkbox_rect, 0, 5)
            if item[1]:
                screen.blit(self.tick, (checkbox_rect.x, checkbox_rect.y))
            screen.blit(txt_surface, (rect.x + 20, rect.y + (rect.height - txt_surface.get_height()) // 2))

    def get_checkbox_rects(self):
        self.checkbox_rects = []
        for i, item in enumerate(self.items):
            rect = pygame.Rect(self.x, self.y + self.height * i, self.width, self.height)
            checkbox_rect = pygame.Rect(self.x + 200, rect.y, 32, 32)
            self.checkbox_rects.append((item, rect, checkbox_rect))

class Playlist():
    def __init__(self, info={}):
        self.info = info
        self.old_info = info
        self.rect = None
        self.colour = COLOURS["LIGHT_BLUE"]
        self.text_colour = COLOURS["BLACK"]
        self.font = BUTTON_FONT
        self.active = False
        self._process_info()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active

    def _process_info(self):
        for v in self.info.values():
            for k, val in v.items():
                if k == "img":
                    try:
                        self.image = pygame.image.load(val)
                    except:
                        self.image = pygame.image.load(ASSETS["BASE_PLAYLIST_IMG"])
                elif k == "songs":
                    self.info = {
                        "Name": list(self.info.keys())[0],
                        "Songs": str(len(val)),
                        "Track Length": self._get_song_duration(val)+" minutes"
                    }

    def _get_song_duration(self, songs):
        total_minutes = sum(int(song['length'].split(":")[0]) for song in songs)
        total_seconds = sum(int(song['length'].split(":")[1]) for song in songs)
        total = total_minutes + total_seconds / 60
        return str(round(total))

    def update_rect(self, rect):
        self.rect = rect
    
    def update_image(self, img):
        self.image = pygame.image.load(img)

    def get_text(self):
        self.txt = "\n".join([f"{k}: {v}" for k, v in self.info.items()])
        lines = self.txt.split('\n')
        self.text_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        y_offset = self.rect.height - len(lines) * self.font.get_height() - 5
        for line in lines:
            line_surface = self.font.render(line, True, self.text_colour)
            self.text_surface.blit(line_surface, (0, y_offset))
            y_offset += line_surface.get_height()

    def draw(self, screen):
        pygame.draw.rect(screen, COLOURS["LIGHT_BLUE"], self.rect, 0, 25)
        screen.blit(self.text_surface, (self.rect.x + 20, self.rect.y + (self.rect.height - self.text_surface.get_height()) // 2))
        screen.blit(self.image, (self.rect.x+20, self.rect.y+20))

    def __len__(self):
        return len(self.info)

class PlaylistSlide(ItemList):
    def __init__(self, x, y, width, height, max_len=3, max_height=3, items=[]):
        self.max_len = max_len
        super().__init__(x, y, width, height, items, max_items=max_height)
        if not all(type(item) == Playlist for item in items):
            raise Exception
        
        self.max_height = (self.height+self.offset) * self.max_items
        
        self.top_rect.width = (self.width+self.offset) * self.max_len
        self.bottom_rect.width = (self.width+self.offset) * self.max_len
        
        self.update_slider()

    def handle_event(self, event):
        for item in self.items:
            item.handle_event(event)

        mouse_pos = pygame.mouse.get_pos()
        buttons = pygame.mouse.get_pressed()
        if buttons[0]:
            if self.slider_rect.collidepoint(mouse_pos):
                self.active = True
                self.active_colour = self.bg_colour
            
        else:
            self.active = False
            self.active_colour = self.slider_colour
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for item in self.items:
                if item.rect.collidepoint(event.pos):
                    self.selected = item
            if self.slider_rect.collidepoint(event.pos):
                self.old_y = mouse_pos[1]
        
        if self.active:
            dy = mouse_pos[1] - self.old_y
            if self.slider_rect.y + dy >= self.y and self.slider_rect.y + dy + self.slider_rect.height <= self.y + self.max_height:
                self.dy -= dy
                self.slider_rect.y += dy
                self.old_y = mouse_pos[1]

    def update(self):
        super().update()
        pixel_offset = self.dy / 10 * (self.height + self.offset)
        self.get_item_rects(pixel_offset)
        for item in self.items:
            item.get_text()

    def draw(self, screen):
        pygame.draw.rect(screen, self.active_colour, self.slider_rect, 0, 25)
        for item in self.items:
            if item.rect.y < self.y + self.max_height + self.offset and item.rect.y + self.height > self.y:
                item.draw(screen)

        pygame.draw.rect(screen, self.scene_colour, self.top_rect)
        pygame.draw.rect(screen, self.scene_colour, self.bottom_rect)

    def update_slider(self):
        total_height = (self.height + self.offset) * math.ceil((len(self.items)/self.max_len))
        height = min(self.max_height, total_height)
        x_offset = (self.rect.width + self.offset) * self.max_len
        if total_height > self.max_height:
            height -= 10 * (math.ceil(len(self.items)/self.max_len)-self.max_items)
        self.slider_rect = pygame.Rect(self.x + x_offset, self.y, 20, height)

    def get_item_rects(self, dy=0):
        x_offset = 0
        y_offset = 0
        for item in self.items:
            rect = pygame.Rect(self.x + (self.width + self.offset) * x_offset, (self.y + ((self.height + self.offset) * y_offset)) + dy, self.width, self.height)
            item.update_rect(rect)
            if x_offset == self.max_len - 1:
                x_offset = 0
                y_offset += 1
            else:
                x_offset += 1

class ArbitraryRect(UIElement):
    def __init__(self, x, y, width, height, colour=COLOURS["LIGHT_BLUE"], border_radius=5):
        super().__init__(x, y, width, height)
        self.border_radius = border_radius
        self.colour = colour

    def handle_event(self, event):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect, 0, self.border_radius)