#!/usr/bin/python3.5
""" GAME """
import sys
import random
from time import sleep
from collections import namedtuple
import numpy as np
import pygame
from player_inputs import PlayerInputs

SNAKE_PERIOD = 0.8
SIZE = width, height = 720, 600
BACKGROUND_COLOR = 0, 0, 0

pygame.init()


screen = pygame.display.set_mode(SIZE, pygame.DOUBLEBUF)

def _rand_col():
    return [random.getrandbits(8) for _ in range(3)]

Tile = namedtuple("Tile", field_names=["player", "type", "data"])




def create_snake(size, start_y):
    x = 6
    snake = [(x,y) for y in range(start_y, start_y + size)]
    return snake

class BoardRenderer(object):

    def __init__(self, board, state):
        self._state = state
        self._board = board
        self._seed = random.random()
        self.resize((screen.get_width(), screen.get_height()))

    def resize(self, dimensions):
        global screen
        board_size = self._board._size
        self._scale = int(dimensions[1] / board_size[1])
        self._buffer = pygame.Surface((self._scale*board_size[0], self._scale*board_size[1]))
        #screen = pygame.display.set_mode(dimensions, pygame.RESIZABLE|pygame.DOUBLEBUF)


    def render(self, screen):
        board_size = self._board._size
        random.seed(self._seed)
        s = self._scale
        for y in range(board_size[1]):
            for x in range(board_size[0]):
                pygame.draw.rect(self._buffer, _rand_col(), [x*s, self._buffer.get_height() - (y+1)*s, s, s])

        for player in self._state._players:
            for snake_bit in player._snake:
                x, y = snake_bit
                pygame.draw.rect(self._buffer, player._color, [x*s, self._buffer.get_height() - (y+1)*s, s, s])

            

        # draw buffer on screen
        screen.blit(self._buffer, [(screen.get_width()-self._buffer.get_width()) / 2,
            (screen.get_height()-self._buffer.get_height()) / 2])


class Player(object):

    def __init__(self):
        self._snake = create_snake(5, 20)
        self._state = None
        self._color = _rand_col()
        self._direction = 0

    def update(self):
        first = self._snake[0]
        translated = (first[0]+self._direction, first[1] - (not self._direction))
        del self._snake[-1]
        self._snake = [translated]+self._snake

class Board(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self._size = (12, 24)
        self._tiles = np.zeros(self._size, dtype=object)

class RoundState(object):
    def __init__(self, player_inputs):
        self.player_inputs = player_inputs

        self._players = [Player() for _ in range(2)]
        self.board = Board()
        self._renderer = BoardRenderer(self.board, self)

    def loop(self):
        while 1:
            self._update()
            self._render()
            sleep(SNAKE_PERIOD)


    def _update(self):
        actions = self.player_inputs.read()
        for action in actions:
            print(action)
            player = self._players[action.player]
            direction = 0
            if action.action == "left":
                direction = -1*[-1, 1][action.keydown]
            elif action.action == "right":
                direction = 1*[-1, 1][action.keydown]
            player._direction += direction


        for player in self._players:
            player.update()

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE: self._renderer.resize((event.w, event.h))
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: sys.exit() 


    def _render(self):
        self._clear()
        self._renderer.render(screen)

        #pygame.draw.circle(screen, BLUE, [x,y], s)
        pygame.display.flip()


    def _clear(self):
        screen.fill(BACKGROUND_COLOR)

def main():
    player_inputs = PlayerInputs()
    game = RoundState(player_inputs)
    game.loop()
if __name__ == "__main__":
    main()
