import pygame
import Box2D
from Box2D import *

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

        # Initialize b2 world
        self.world = b2World(gravity=(0, -10), doSleep=True)
        self.destructionListener = ObjectDestructionListener(test=self)
        self.world.destructionListener = self.destructionListener
        self.world.contactListener = self
        # todo: change?
        self.time_delta, self.time_draws = [], []

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


class ObjectDestructionListener(b2DestructionListener):
    """
    Move this to world instance?
    """

    def __init__(self, test, **kwargs):
        super(ObjectDestructionListener, self).__init__(**kwargs)
        self.test = test

    def delete(self, obj):
        if isinstance(obj, b2Joint):
            if self.test.mouseJoint == obj:
                self.test.mouseJoint = None
            else:
                self.test.JointDestroyed(obj)
        elif isinstance(obj, b2Fixture):
            self.test.FixtureDestroyed(obj)

