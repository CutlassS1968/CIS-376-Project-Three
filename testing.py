import sys
import math

from Box2D import *
import pygame


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


class Main:
    def __init__(self):
        # init pygame
        pygame.init()
        pygame.display.set_mode((1280, 720))
        self.display_surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()

        # Create the world
        self.gravity = b2Vec2(0.0, -1000.0)
        self.world = b2World(gravity=self.gravity)

        # Create a ground
        # self.ground = WOGround(world=self.world, pos=(0.0, -10.0), width=100, height=20)

        # # Create a ground box
        # self.groundBodyDef = b2BodyDef()
        # self.groundBodyDef.position = (0.0, -10.0)
        # self.groundBody = self.world.CreateBody(self.groundBodyDef)
        # self.groundBox = b2PolygonShape()
        # # takes half width and half height, so ground is 100 units wide and 20 units tall
        # self.groundBox.SetAsBox(100.0, 10.0)
        # self.groundBody.CreateFixture(shape=self.groundBox, density=0.0)

        self.ground = self.world.CreateBody(
            shapes=b2PolygonShape(
                vertices=[(-100, -10), (-100, 0), (100, 0),  (100, -10)]
            )
        )

        # Now that we have a ground body, we can use the same technique to create a dynamic body
        # self.bodyDef = b2BodyDef()
        # self.bodyDef.type = b2_dynamicBody
        # self.bodyDef.position = (0.0, 40.0)
        # self.body = self.world.CreateBody(self.bodyDef)
        #
        # self.dynamicBox = b2PolygonShape()
        # self.dynamicBox.SetAsBox(10.0, 10.0)
        #
        # self.fixtureDef = b2FixtureDef()
        # self.fixtureDef.shape = self.dynamicBox
        # self.fixtureDef.density = 1.0
        # self.fixtureDef.friction = 0.3
        # self.body.CreateFixture(defn=self.fixtureDef)

        self.dynamic_bodies = []

        # Alternate dynamic body creation
        self.body = self.world.CreateDynamicBody(
            position=(0.0, 200.0),
            fixtures=b2FixtureDef(
                shape=b2PolygonShape(box=(1, 2)),
                density=2.0,
                friction=0.1
            )
        )

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            dt = self.clock.tick(60) / 1000
            self.inputs()
            self.update(dt)
            self.draw()

    def inputs(self):
        keys = pygame.key.get_pressed()
        # if keys[pygame.K_s]:
        #     self.body.ApplyLinearImpulse(b2Vec2(0.0, -1000.0), self.body.position, True)
        # if keys[pygame.K_w]:
        #     self.body.ApplyLinearImpulse(b2Vec2(0.0, 1000.0), self.body.position, True)
        if keys[pygame.K_a]:
            self.body.ApplyLinearImpulse(b2Vec2(-1000.0, 0.0), self.body.position, True)
        if keys[pygame.K_d]:
            self.body.ApplyLinearImpulse(b2Vec2(100.0, 0.0), self.body.position, True)
        if keys[pygame.K_SPACE]:
            self.body.ApplyLinearImpulse(b2Vec2(0.0, 100000.0), self.body.position, True)

    def update(self, dt: float):
        time_step = dt
        velocityIterations = 6
        positionIterations = 2
        self.world.Step(time_step, velocityIterations, positionIterations)
        position = self.body.position
        angle = self.body.angle
        # print(f"{position.x} {position.y} {angle}")

    def draw(self):
        # TODO: not drawing y correctly
        self.display_surface.fill((0, 0, 0))
        for body in self.world.bodies:
            for fixture in body.fixtures:
                # get the position & angle of transform
                transform = body.transform
                trans_pos = transform.position
                trans_angle = transform.angle
                # get the vertices of the fixture
                fix_verts = fixture.shape.vertices
                # rotate vertices from transform angle around body origin (0, 0)
                # angle = trans_angle * (math.pi / 180)
                # # set to 0, 0 since the origin should be 0, 0 for the fixtures relative to the body
                # # TODO: might not be rotating properly
                # center = (0, 0)
                # rotated_verts = []
                # for vert in fix_verts:
                #     rx = math.cos(angle) * (vert[0] - center[0]) - math.sin(angle) * (vert[1] - center[1]) + center[0]
                #     ry = math.sin(angle) * (vert[0] - center[0]) - math.cos(angle) * (vert[1] - center[1]) + center[1]
                #     rotated_verts.append((rx, ry))
                rotated_verts = self.rotate_point_list((0, 0), fix_verts, trans_angle)
                # translate vertices from position to world space
                world_verts = []
                for vert in rotated_verts:
                    nx = vert[0] + trans_pos.x
                    ny = vert[1] + trans_pos.y
                    world_verts.append((nx, ny))
                # translate vertices from world space to screen space
                screen_verts = []
                for vert in world_verts:
                    screen_verts.append(self.convert_b2s(vert))
                pygame.draw.polygon(self.display_surface, (255, 255, 255), screen_verts, 1)

        # self.display_surface.fill((0, 0, 0))
        # # you can get a list of bodies in the world with b2World.bodies
        # c = 0
        # for body in self.world.bodies:
        #     # transform = body.transform
        #     for fixture in body.fixtures:
        #         shape = fixture.shape
        #         # todo: can put logic for checking body type here
        #         vertices = shape.vertices
        #         world_verts = []
        #         for vert in vertices:
        #             world_verts.append(self.convert_b2s(vert))
        #         pygame.draw.polygon(self.display_surface, (255, 0, 0), world_verts)
        # print(c)
        #
        # for fixture in self.body.fixtures:
        #     # get the position & angle of transform
        #     transform = self.body.transform
        #     trans_pos = transform.position
        #     trans_angle = transform.angle
        #     # get the vertices of the fixture
        #     fix_verts = fixture.shape.vertices
        #     # rotate vertices from transform angle around body origin (0, 0)
        #     angle = trans_angle * (math.pi / 180)
        #     # set to 0, 0 since the origin should be 0, 0 for the fixtures relative to the body
        #     # TODO: might not be rotating properly
        #     center = (0, 0)
        #     rotated_verts = []
        #     for vert in fix_verts:
        #         rx = math.cos(angle) * (vert[0] - center[0]) - math.sin(angle) * (vert[1] - center[1]) + center[0]
        #         ry = math.sin(angle) * (vert[0] - center[0]) - math.cos(angle) * (vert[1] - center[1]) + center[1]
        #         rotated_verts.append((rx, ry))
        #     # translate vertices from position to world space
        #     world_verts = []
        #     for vert in rotated_verts:
        #         nx = vert[0] + trans_pos.x
        #         ny = vert[1] + trans_pos.y
        #         world_verts.append((nx, ny))
        #     # translate vertices from world space to screen space
        #     screen_verts = []
        #     for vert in world_verts:
        #         screen_verts.append(self.convert_b2s(vert))
        #     pygame.draw.polygon(self.display_surface, (0, 255, 0), screen_verts)
        pygame.display.flip()

    def rotate_point_list(self, origin, points, angle):
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


    def convert_b2s(self, pos):
        return 10 * (pos[0]) + SCREEN_WIDTH / 2, 10 * (-1 * pos[1]) + SCREEN_HEIGHT - 10


if __name__ == '__main__':
    main = Main()
    main.run()
