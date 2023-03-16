import pygame


from game import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("resources/player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2(0, 0)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 400

    def key_inputs(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def move(self, dt: float):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        if self.pos.x < self.image.get_width() / 2:
            self.pos.x = self.image.get_width() / 2
        if self.pos.x > SCREEN_WIDTH - self.image.get_width() / 2:
            self.pos.x = SCREEN_WIDTH - self.image.get_width() / 2
        self.rect.centerx = self.pos.x

        self.pos.y += self.direction.y * self.speed * dt
        if self.pos.y < self.image.get_height() / 2:
            self.pos.y = self.image.get_height() / 2
        if self.pos.y > SCREEN_HEIGHT - self.image.get_height() / 2:
            self.pos.y = SCREEN_HEIGHT - self.image.get_height() / 2
        self.rect.centery = self.pos.y

    def update(self, dt: float):
        self.key_inputs()
        self.move(dt)
