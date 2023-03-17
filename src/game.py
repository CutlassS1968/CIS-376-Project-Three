import pygame
import sys

from instance import *


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

FRAME_RATE = 60


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Project Three')
        self.clock = pygame.time.Clock()
        self.instance = WorldInstance()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            dt = self.clock.tick(FRAME_RATE) / 1000
            self.instance.step(dt)
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
