#!/usr/bin/python3.5
""" GAME """
import sys
import random
from time import sleep
from collections import namedtuple
import numpy as np
import pygame
from player_inputs import PlayerInputs
print(pygame.__file__)
pygame.init()

SIZE = width, height = 720, 600
SPEED = [2, 2]
BLACK = 0, 0, 0
BLUE = 0, 20, 255

screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)

def _rand_col():
    return [random.getrandbits(8) for _ in range(3)]

Tile = namedtuple("Tile", field_names=["player", "type", "data"])

class Board(object):
    def __init__(self):
        self._size = (12, 24)
        self._tiles = np.zeros(self._size, dtype=object)
        self._scale = int(height / self._size[1])
        self._buffer = pygame.Surface((self._scale*self._size[0], self._scale*self._size[1]))
        self._seed = random.random()

    def render(self):
        random.seed(self._seed)
        s = self._scale
        for y in range(self._size[1]):
            for x in range(self._size[0]):
                pygame.draw.rect(self._buffer, _rand_col(), [x*s, self._buffer.get_height() - (y+1)*s, s, s])

        # draw buffer on screen
        screen.blit(self._buffer, [(screen.get_width()-self._buffer.get_width()) / 2,
            (screen.get_height()-self._buffer.get_height()) / 2])

class RoundState(object):
    def __init__(self, player_inputs):
        self.player_inputs = player_inputs
        self.players = []
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: sys.exit() 

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
