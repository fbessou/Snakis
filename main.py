""" GAME """
import sys, pygame
from time import sleep
pygame.init()

SIZE = width, height = 320, 240
SPEED = [2, 2]
BLACK = 0, 0, 0
BLUE = 0, 20, 255

screen = pygame.display.set_mode(SIZE)
x = 19
y = 20
s = 17
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    
    x+=SPEED[0]
    y+=SPEED[1]
    if x-s< 0 or x+s > width:
        SPEED[0] = -SPEED[0]
    if y-s < 0 or y+s > height:
        SPEED[1] = -SPEED[1]

    screen.fill(BLACK)
    pygame.draw.circle(screen, BLUE, [x,y], s)
    pygame.display.flip()
    sleep(0.016)
    
