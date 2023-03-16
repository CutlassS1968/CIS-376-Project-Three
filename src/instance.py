import pygame

from player import Player

from game import SCREEN_WIDTH
from game import SCREEN_HEIGHT


class WorldInstance:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.player = Player((640, 360))
        self.background = pygame.transform.scale(
            pygame.image.load("resources/background.png"),
            (SCREEN_WIDTH, SCREEN_HEIGHT))

    def run(self, dt: float):
        self.display_surface.fill('black')
        self.process_updates(dt)
        self.process_outputs(dt)

    def process_updates(self, dt: float):
        self.player.update(dt)

    def process_outputs(self, dt: float):
        self.draw()

    def draw(self):
        self.display_surface.blit(self.background, self.background.get_rect())
        self.display_surface.blit(self.player.image, self.player.rect)
