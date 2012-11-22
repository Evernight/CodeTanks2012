import sys
import pygame
from GamePhysics import MAX_DISTANCE
from Geometry import get_unit_corners, Vector
from MyUtils import debug_dump_load

pygame.init()

#create the screen
window = pygame.display.set_mode((1280, 800))

#draw a line - see http://www.pygame.org/docs/ref/draw.html for more
def draw_unit(unit):
    c1, c2, c3, c4 = get_unit_corners(unit)
    pygame.draw.line(window, (255, 255, 255), (c1.x, c1.y), (c2.x, c2.y))
    pygame.draw.line(window, (255, 255, 255), (c2.x, c2.y), (c3.x, c3.y))
    pygame.draw.line(window, (255, 255, 255), (c3.x, c3.y), (c4.x, c4.y))
    pygame.draw.line(window, (255, 255, 255), (c4.x, c4.y), (c1.x, c1.y))

def draw_tank(tank):
    draw_unit(tank)

    b = tank.angle + tank.turret_relative_angle
    e = Vector(1, 0)
    q = e.rotate(b)

    tank_v = Vector(tank.x, tank.y)
    hit_v = tank_v + MAX_DISTANCE * q

    pygame.draw.line(window, (255, 0, 0), (tank.x, tank.y), (hit_v.x, hit_v.y))

data = debug_dump_load("3")

for unit in data["units"]:
    draw_unit(unit)

for tank in data["tanks"]:
    draw_tank(tank)

#draw it to the screen
pygame.display.flip()

#input handling (somewhat boilerplate code):
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        else:
            #print event
            pass