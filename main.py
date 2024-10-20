import pygame
import scenes
import sys

WIDTH, HEIGHT = (1400, 900)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OCRtunes")
pygame.init()
pygame.key.set_repeat(250, 50)

clock = pygame.time.Clock()
current_scene = scenes.PlaylistViewer()

while True:
    clock.tick(60)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    current_scene.process_input(events)
    current_scene.update()
    current_scene.render(WIN)
    pygame.display.update()

    next_scene = current_scene.next_scene
    if next_scene is not current_scene:
        current_scene.next_scene = current_scene
        current_scene = next_scene