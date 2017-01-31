""" GAME """
import sys, pygame
import random
from time import sleep
from player_inputs import PlayerInputs
pygame.init()

SIZE = width, height = 720, 600
SPEED = [2, 2]
BLACK = 0, 0, 0
BLUE = 0, 20, 255

screen = pygame.display.set_mode(SIZE)
x = 19
y = 20
s = 17
def _rand_col():
    return [ random.getrandbits(8) for _ in range(3)]

class Board(object):
    def __init__(self):
        self._size = (12,24)

    def render(self):
        random.seed(0)
        w = width/self._size[0]
        h = height/self._size[1]
        w = min(w,h)
        h = min(w,h)
        for y in range(self._size[1]):
            for x in range(self._size[0]):
                pygame.draw.rect(screen, _rand_col(), [x*w, height - (y+1)*h, w, h])

class RoundState(object):
    def __init__(self, player_inputs):
        self.player_inputs = player_inputs
        self.player1_color = 16, 32, 53
        self.player2_color = 112, 125, 32
        self.board = Board()
    
    def loop(self):
        while 1:
            self._update()
            self._render()
            sleep(0.016)


    def _update(self):
        actions = self.player_inputs.read()
        for action in actions:
            print(action)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        
        #x+=SPEED[0]
        #y+=SPEED[1]
        #if x-s< 0 or x+s > width:
        #    SPEED[0] = -SPEED[0]
        #if y-s < 0 or y+s > height:
        #    SPEED[1] = -SPEED[1]
        
    def _render(self):
        self._clear()
        self.board.render()
        #pygame.draw.circle(screen, BLUE, [x,y], s)
        pygame.display.flip()

    def _clear(self):
        screen.fill(BLACK)

def main():
    player_inputs = PlayerInputs() 
    game = RoundState(player_inputs)
    game.loop()
if __name__ == "__main__":
    main()
