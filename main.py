#!/usr/bin/python3.5
""" GAME """
import sys
import random
from time import sleep
from collections import namedtuple
import numpy as np
import pygame
from player_inputs import PlayerInputs
from algo import *

SNAKE_PERIOD = 0.4
SIZE = width, height = 720, 600
BACKGROUND_COLOR = 0, 0, 0

pygame.init()


screen = pygame.display.set_mode(SIZE, pygame.DOUBLEBUF)

def _rand_col(b=8):
    return [random.getrandbits(b) for _ in range(3)]

Tile = namedtuple("Tile", field_names=["player", "type", "data"])




def create_snake(size, start_y, start_x):
    snake = [(start_x,y) for y in range(start_y, start_y + size)]
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
        board = self._board
        for y in range(board_size[1]):
            for x in range(board_size[0]):
                bg_color = _rand_col(5)
                if board.isFree(x,y):
                    pygame.draw.rect(self._buffer, bg_color, [x*s, self._buffer.get_height() - (y+1)*s, s, s])
                else:
                    pygame.draw.rect(self._buffer, self._state._players[board._tiles[x][y].player]._color, [x*s, self._buffer.get_height() - (y+1)*s, s, s])

        for player in self._state._players:
            for snake_bit in player._snake:
                x, y = snake_bit
                pygame.draw.rect(self._buffer, player._color, [x*s, self._buffer.get_height() - (y+1)*s, s, s])

            

        # draw buffer on screen
        screen.blit(self._buffer, [(screen.get_width()-self._buffer.get_width()) / 2,
            (screen.get_height()-self._buffer.get_height()) / 2])


class Player(object):

    def __init__(self):
        self._snake = create_snake(5, 23, 5)
        self._state = ""
        self._color = _rand_col()
        self._direction_vert = 0
        self._direction_horiz = 0
        self._direction = (0,-1)
        self._can_fall = True
        self._can_move = True

    def update(self):
        if not self._can_fall and not self._can_move:
            self._state = "dead"
    
    def revive(self, player_num):
        self._snake = create_snake(5, 20, player_num)
        self._state = ""
        self._direction = (0,-1)
        self._can_fall = True
        self._can_move = True


    def move(self):
        first = self._snake[0]
        translated = (first[0] + self._direction[0], first[1] + self._direction[1])
        del self._snake[-1]
        self._snake = [translated]+self._snake
    
    def nextSquareSnake(self):
        first = self._snake[0]
        return (first[0] + self._direction[0], first[1] + self._direction[1])

class Board(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self._size = (12, 24)
        self._tiles = np.zeros(self._size, dtype=object)

    def freeze(self, squares, player = -1, dtype = 0, data = None):
        for sq in squares:
            self._tiles[sq[0]][sq[1]] = Tile(player, dtype, data)

    def clear(self, i, j):
        self._tiles[i][j] = None

    def isFree(self, i, j):
        return not self._tiles[i][j]

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
            if direction != 0:
                player._direction_horiz += direction
                if player._direction_horiz != 0:
                    player._direction = (player._direction_horiz, 0)

            direction = 0
            if action.action == "down":
                direction = -1*[-1, 1][action.keydown]
            elif action.action == "up":
                direction = 1*[-1, 1][action.keydown]
            if direction != 0:
                player._direction_vert += direction
                if player._direction_vert != 0:
                    player._direction = (0, player._direction_vert)


        # Check if snakes can move
        all_snakes = [p._snake for p in self._players]
        for player in self._players:
            if player._can_move:
                future_head_pos = player.nextSquareSnake()
                collision = collide(self.board._size, [future_head_pos], lambda i,j:not self.board.isFree(i,j), allow_out_of_bounds=(0,0,0,0), floating_items=all_snakes)
                player._can_move = not collision
        # Make snakes move
        for player in self._players:
            if player._can_move:
                player.move()

        # Check if snakes can fall
        all_snakes = [p._snake for p in self._players] # we need to recreate this array, 'cause snake might have changed
        can_fall = canFall(all_snakes, self.board._size, lambda i,j:not self.board.isFree(i,j))
        for p in range(len(self._players)):
            self._players[p]._can_fall = can_fall[p]
        # Make snakes fall
        fall(all_snakes, can_fall)

        # player state
        for p in range(len(self._players)):
            player = self._players[p]
            player.update()
            if player._state == "dead":
                self.board.freeze(player._snake, p)
                player.revive(p)

        # Map
        component = connectedComponent(self.board._size, lambda i,j:0 if self.board.isFree(i,j) else self.board._tiles[i][j].player+1) 
        for b in range(len(component[0])):
            blocks = component[0][b]
            if blocks["size"] >= 13.37: # TODO sort components by size, remove biggest first
                removeConnectedComponent(b+1, self.board._size, self.board.clear, component[1])
                print("Player",blocks["grp"],"block size",blocks["size"],"-> destroyed",b+1)

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
