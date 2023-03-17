import math
import platform

import pygame
import Box2D
from Box2D import *


from game import SCREEN_WIDTH
from game import SCREEN_HEIGHT


VELOCITY_ITERATIONS = 6
POSITION_ITERATIONS = 2
PIXELS_PER_METER = 40

SYSTEM_FILE_PREFIX = "" if platform.system() == "Windows" else "../"

DRAW_DEBUG = False

# Sound from: https://freesound.org/people/ShaneF91/sounds/386572/

def rotate_point_list(origin, points, angle):
    s = math.sin(angle)
    c = math.cos(angle)
    r_points = []
    for p in points:
        px = p[0]
        py = p[1]
        px -= origin[0]
        py -= origin[1]
        rx = px * c - py * s
        ry = px * s + py * c
        nx = rx + origin[0]
        ny = ry + origin[1]
        r_points.append((nx, ny))
    return r_points


def convert_w2s(pos):
    return (PIXELS_PER_METER * (pos[0])) + (SCREEN_WIDTH / 2), PIXELS_PER_METER * (-1 * pos[1]) + SCREEN_HEIGHT


def distance(p, q):
    return math.sqrt((q[0] - p[0])**2 + (q[1] - p[1])**2)


class WorldInstance:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.background = pygame.transform.scale(
            pygame.image.load(f"{SYSTEM_FILE_PREFIX}resources/background.png"),
            (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.world_objects = []

        # Setup Box2d
        self.gravity = b2Vec2(0.0, -1.6)
        contact_listener = WorldContactListener()
        self.world = b2World(gravity=self.gravity, contactListener=contact_listener)

        # Create ground
        ground_width = SCREEN_WIDTH / PIXELS_PER_METER
        ground_height = SCREEN_HEIGHT / PIXELS_PER_METER
        print(ground_width, ground_height)
        # 1 / 8 ratio for height/width
        # 1280x160 for ground
        self.ground = DrawableWorldObject(
            self.world.CreateBody(
                position=(0.0, ground_height / 16),
                fixtures=b2FixtureDef(shape=b2PolygonShape(box=(ground_width / 2, ground_height / 16)))
            ),
            pygame.image.load(f"{SYSTEM_FILE_PREFIX}resources/ground.png")
        )

        # Create screen borders
        self.world.CreateBody(
            shapes=b2LoopShape(vertices=[
                ((SCREEN_WIDTH / PIXELS_PER_METER)/2, -(SCREEN_HEIGHT / PIXELS_PER_METER)),
                ((SCREEN_WIDTH / PIXELS_PER_METER)/2, (SCREEN_HEIGHT / PIXELS_PER_METER)),
                (-(SCREEN_WIDTH / PIXELS_PER_METER)/2, (SCREEN_HEIGHT / PIXELS_PER_METER)),
                (-(SCREEN_WIDTH / PIXELS_PER_METER)/2, -(SCREEN_HEIGHT / PIXELS_PER_METER))
            ])
        )

        # Create player
        self.player = Player(
            self.world.CreateDynamicBody(
                position=(0.0, 5.0),
                fixtures=b2FixtureDef(
                    shape=b2PolygonShape(box=(0.286, 0.5)),
                    density=50.0,
                    friction=1,
                    restitution=0.5
                ),
                fixedRotation=True
            ),
            pygame.image.load(f"{SYSTEM_FILE_PREFIX}resources/player.png")
        )

        self.platforms = []
        self.gen_platforms()

    def gen_platforms(self):
        self.platforms.append(DrawableWorldObject(
            self.world.CreateStaticBody(
                position=(0.0, 10.0),
                fixtures=b2FixtureDef(shape=b2PolygonShape(box=(1, .555)))
            ),
            pygame.image.load(f"{SYSTEM_FILE_PREFIX}resources/platform.png")
        ))
        self.platforms.append(DrawableWorldObject(
            self.world.CreateStaticBody(
                position=(8.0, 5.0),
                fixtures=b2FixtureDef(shape=b2PolygonShape(box=(1, .555)))
            ),
            pygame.image.load(f"{SYSTEM_FILE_PREFIX}resources/platform.png")
        ))
        self.platforms.append(DrawableWorldObject(
            self.world.CreateStaticBody(
                position=(-10.0, 7.0),
                fixtures=b2FixtureDef(shape=b2PolygonShape(box=(1, .555)))
            ),
            pygame.image.load(f"{SYSTEM_FILE_PREFIX}resources/platform.png")
        ))
        self.platforms.append(DrawableWorldObject(
            self.world.CreateStaticBody(
                position=(-5.0, 13.0),
                fixtures=b2FixtureDef(shape=b2PolygonShape(box=(1, .555)))
            ),
            pygame.image.load(f"{SYSTEM_FILE_PREFIX}resources/platform.png")
        ))
        self.platforms.append(DrawableWorldObject(
            self.world.CreateStaticBody(
                position=(14.0, 13.0),
                fixtures=b2FixtureDef(shape=b2PolygonShape(box=(1, .555)))
            ),
            pygame.image.load(f"{SYSTEM_FILE_PREFIX}resources/platform.png")
        ))

    def step(self, dt: float):
        self.process_inputs()
        self.process_updates(dt)
        self.process_outputs(dt)

    def process_inputs(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            if not self.player.jump_cooldown:
                self.player.body.ApplyLinearImpulse(b2Vec2(-2.0, 0.0), self.player.body.position, True)
        if keys[pygame.K_d]:
            if not self.player.jump_cooldown:
                self.player.body.ApplyLinearImpulse(b2Vec2(2.0, 0.0), self.player.body.position, True)
        if keys[pygame.K_SPACE]:
            if not self.player.jump_cooldown:
                self.player.remove_jump()
                self.player.body.ApplyLinearImpulse(b2Vec2(0.0, 75.0), self.player.body.position, True)
        if keys[pygame.K_LSHIFT]:
            if not self.player.smash_cooldown:
                self.player.remove_smash()
                self.player.body.ApplyLinearImpulse(b2Vec2(0.0, -75.0), self.player.body.position, True)

    def process_updates(self, dt: float):
        # Update physics engine
        self.world.Step(dt, VELOCITY_ITERATIONS, POSITION_ITERATIONS)

    def process_outputs(self, dt: float):
        self.draw()
        # print(self.player.body.position)

    def draw(self):
        self.display_surface.fill('black')
        self.display_surface.blit(self.background, self.background.get_rect())

        self.ground.draw()
        self.player.draw()
        for plat in self.platforms:
            plat.draw()
        if DRAW_DEBUG:
            for body in self.world.bodies:
                transform = body.transform
                for fixture in body.fixtures:
                    # rotate fixture vertices around transform's angle
                    r_verts = rotate_point_list((0, 0), fixture.shape.vertices, transform.angle)
                    # translate vertices to transform's world position
                    w_verts = [(v[0] + transform.position.x, v[1] + transform.position.y) for v in r_verts]
                    # translate vertices to screen coordinates
                    s_verts = [convert_w2s(v) for v in w_verts]
                    # draw shape
                    pygame.draw.polygon(self.display_surface, (255, 255, 255), s_verts, 1)
                    # print(s_verts)
        pygame.display.flip()


class DrawableWorldObject:
    def __init__(self, body, image):
        self.body = body
        self.image = image

        self.body_width = 0
        self.body_height = 0
        self.gen_dims()

    def gen_dims(self):
        for fixture in self.body.fixtures:
            transform = self.body.transform
            t_pos = (transform.position.x, transform.position.y)
            # rotate fixture vertices around transform's angle
            r_verts = rotate_point_list((0, 0), fixture.shape.vertices, transform.angle)
            # translate vertices to transform's world position
            w_verts = [(v[0] + t_pos[0], v[1] + t_pos[1]) for v in r_verts]
            # translate vertices to screen coordinates
            s_verts = [convert_w2s(v) for v in w_verts]

            # get width and height of box
            self.body_width = distance(s_verts[0], s_verts[1])
            self.body_height = distance(s_verts[0], s_verts[3])

    def draw(self):
        # box format:
        # tl tr br bl
        display_surface = pygame.display.get_surface()
        transform = self.body.transform
        t_pos = (transform.position.x, transform.position.y)
        # scale image to body size
        w_image = pygame.transform.scale(self.image, (self.body_width, self.body_height))
        # rotate image to body angle
        r_image = pygame.transform.rotate(w_image, transform.angle * (180 / math.pi))
        # move image to body screen position
        s_pos = convert_w2s(t_pos)
        s_rect = r_image.get_rect(center=w_image.get_rect(center=s_pos).center)
        # draw image
        display_surface.blit(r_image, s_rect)
        # pygame.draw.circle(display_surface, (255, 0, 0), s_pos, 3)
        # pygame.draw.rect(display_surface, (255, 0, 0), s_rect, 1)


class Player(DrawableWorldObject):
    def __init__(self, body, image):
        super().__init__(body, image)
        self.body.userData = self
        self.jump_cooldown = False
        self.smash_cooldown = False
        self.jump_sound = pygame.mixer.Sound(f"{SYSTEM_FILE_PREFIX}resources/jump.wav")
        self.smash_sound = pygame.mixer.Sound(f"{SYSTEM_FILE_PREFIX}resources/smash.wav")

    def start_contact(self):
        self.refresh_jump()
        self.refresh_smash()

    def end_contact(self):
        pass

    def refresh_smash(self):
        print("refresh_smash")
        self.smash_cooldown = False

    def refresh_jump(self):
        print("refresh_jump")
        self.jump_cooldown = False

    def remove_smash(self):
        print("remove_smash")
        self.smash_cooldown = True

    def remove_jump(self):
        print("remove_jump")
        self.jump_sound.play()
        self.jump_cooldown = True


# https://www.iforce2d.net/b2dtut/collision-callbacks
class WorldContactListener(b2ContactListener):
    """
    Calls contact methods for objects when colliding (if that object has a given method)
    """
    def BeginContact(self, contact):
        # check if fixture a was player
        bodyUserData = contact.fixtureA.body.userData
        if bodyUserData:
            bodyUserData.start_contact()

        bodyUserData = contact.fixtureB.body.userData
        if bodyUserData:
            bodyUserData.start_contact()

    def EndContact(self, contact):
        bodyUserData = contact.fixtureA.body.userData
        if bodyUserData:
            bodyUserData.end_contact()

        bodyUserData = contact.fixtureA.body.userData
        if bodyUserData:
            bodyUserData.end_contact()
