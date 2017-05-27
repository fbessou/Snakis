#!/usr/bin/python3.5
""" GAME """
import sys
import random
from time import sleep
from collections import namedtuple
import numpy as np
import pygame
from player_inputs import PlayerInputs
from snake_image import *
from day_and_night import DayAndNight
from algo import *
import math
import os
import colorsys

FONTS_DIR = os.path.join("assets", "fonts")
IMAGES_DIR = os.path.join("assets", "images")

GAME_TICK_PERIOD = 200
INITIAL_SNAKE_LENGTH = 4
MINIMUM_CLUSTER_SIZE = INITIAL_SNAKE_LENGTH*3
SIZE = width, height = 720, 900
BACKGROUND_COLOR = 0, 0, 0

pygame.init()
pygame.font.init()
score_font = pygame.font.Font(os.path.join(FONTS_DIR, "Binz.ttf"), 27)


screen = pygame.display.set_mode(SIZE, pygame.DOUBLEBUF)


def _rand_col(s=1, v=1):
    r,g,b = colorsys.hsv_to_rgb(random.random(), s, v) #[random.getrandbits(b) for _ in range(3)]
    return (r*255,g*255,b*255)

Tile = namedtuple("Tile", field_names=["player", "type", "shape"])


def create_snake(size, start_y, start_x):
    snake = [(start_x,y) for y in range(start_y, start_y + size)]
    return snake

class Particle(object):
    def update(self):
        pass
    def isAlive(self):
        return True
    def render(self, screen):
        pass

class ScoreParticle(Particle):
    def __init__(self, position, text, color = (255,255,255), font = score_font, maxDuration = 10):
        self._position = position
        self._text = text
        self._maxDuration = maxDuration
        self._age = 0
        self._alive = True
        self._font = font
        self._color = color

    def update(self):
        self._age += 1
        if self._age > self._maxDuration:
            self._alive = False
        self._position = (self._position[0], self._position[1] - 1)

    def isAlive(self):
        return self._alive

    def render(self, screen):
        alpha = int(min(1.0, 2 - 2 * self._age / self._maxDuration) * 255)
        color = (self._color[0], self._color[1], self._color[2], alpha)
        img = self._font.render(self._text, 1, color)
        screen.blit(img, (self._position[0] - img.get_width() // 2, self._position[1] - img.get_height() // 2))
        

class Particles(object):
    def __init__(self):
        self._particles = []

    def update(self):
        newParticles = []
        for p in self._particles:
            p.update()
            if p.isAlive():
                newParticles.append(p)
        self._particles = newParticles

    def addParticle(self, particle):
        self._particles.append(particle)

    def render(self, screen):
        for p in self._particles:
            p.render(screen)

class BoardRenderer(object):

    def __init__(self, board, state):
        self._state = state
        self._board = board
        self._seed = random.random()
        self.resize((screen.get_width(), screen.get_height()))

    def resize(self, dimensions):
        board_size = self._board._size
        self._scale = dimensions[1] / (board_size[1]+0.5)
        self._buffer = pygame.Surface((
            self._scale * ((board_size[0]-1) * math.cos(math.pi/6) + 1),
            self._scale*board_size[1]
        ))


    def render(self, screen):
        board_size = self._board._size
        #random.seed(self._seed)
        s = self._scale
        r = int(s / 5)
        board = self._board
        self._buffer.fill((0, 0, 0))
        for y in range(board_size[1]):
            for x in range(board_size[0]):
                bg_color = _rand_col(0.3, 0.2)
                pos = board.getTileCenterPosition(x,y,s)
                if board.isFree(x,y):
                     pygame.draw.circle(self._buffer, bg_color, pos, r)
                elif board._tiles[x][y].player >= 0:
                    player = board._tiles[x][y].player
                    shape = board._tiles[x][y].shape
                    img = self._state._imageFactory.getSnakeImages()[player][shape]
                    rect = img.get_rect()
                    rect.center = pos
                    self._buffer.blit(img, rect) 

        
        for p in range(len(self._state._players)):
            player = self._state._players[p]
            for i in range(len(player._snake)):
                x, y = player._snake[i]
                shape = player._shapes[i]
                pos = board.getTileCenterPosition(x,y,s)
                #if player._state != "frozen" and i == 0: # draw head
                    #pygame.draw.circle(self._buffer, player._color, pos, int(r*0.75))
                #else:
                    #pygame.draw.circle(self._buffer, player._color, pos, r)
                img = self._state._imageFactory.getSnakeImages()[p][shape]
                rect = img.get_rect()
                rect.center = pos
                self._buffer.blit(img, rect) 

        # Draw particles
        self._state._particles.render(self._buffer)

        # draw buffer on screen
        screen.blit(self._buffer, [(screen.get_width()-self._buffer.get_width()),
            (screen.get_height()-self._buffer.get_height()) / 2])

        for i in range(len(self._state._players)):
            player = self._state._players[i]
            score = score_font.render("Player "+str(i)+": "+str(player._score), 1, player._color, (0,0,0))
            screen.blit(score, (MINIMUM_CLUSTER_SIZE/2, MINIMUM_CLUSTER_SIZE*(i*2+1)))


class Player(object):

    def __init__(self, board):
        self._color = _rand_col()
        self._score = 0
        self.revive(board)
        #self._snakeImages = SnakeImage(self._color, IMAGES_DIR+"/snake_%s_%s.png")
    
    def update(self):
        if not self._can_fall and not self._can_move:
            self._state = "dead"
        elif not self._can_move:
            self._state = "frozen"
    
    def revive(self, board):
        freeTilesCount = sum(board.isFree(i, board._size[1]-1) for i in range(board._size[0]))
        x_respawn = int(random.random() * freeTilesCount)
        j = 0
        for i in range(board._size[0]):
            j += board.isFree(i, board._size[1]-1)
            if j-1 == x_respawn:
                x_respawn = i
                break

        self._snake = create_snake(INITIAL_SNAKE_LENGTH, board._size[1]-1, x_respawn)
        self._shapes = [(3,3)]*INITIAL_SNAKE_LENGTH
        self._state = ""
        self._direction = 3
        self._can_fall = True
        self._can_move = True

    def score(self, block_size):
        self._score += block_size #int((((block_size-MINIMUM_CLUSTER_SIZE)/INITIAL_SNAKE_LENGTH) * 10)) #**2 + MINIMUM_CLUSTER_SIZE / INITIAL_SNAKE_LENGTH) * 10);

    def move(self):
        translated = self.nextSquareSnake()
        shape = (self._shapes[0][0], self._direction)
        new_shape = (self._direction, -1)
        del self._snake[-1]
        del self._shapes[-1]
        if self._shapes:
            self._shapes[-1] = (-1, self._shapes[-1][1])
            self._shapes[0] = shape
        self._snake = [translated]+self._snake
        self._shapes = [new_shape]+self._shapes
    
    def nextSquareSnake(self):
        first = self._snake[0]
        return (first[0] + hexa_transition[first[0]&1][self._direction][0],
                first[1] + hexa_transition[first[0]&1][self._direction][1])

class Board(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self._size = (13, 19)
        self._tiles = np.zeros(self._size, dtype=object)
        centerX = self._size[0] // 2
        for x in range(self._size[0]):
            for y in range(self._size[1]):
                if y < (1+abs(x-centerX))//2:
                    self._tiles[x][y] = Tile(-1, 0, None)
                else:
                    self._tiles[x][y] = None


    def getTileCenterPosition(self, i,j, diameter):
        cos30 = math.cos(math.pi/6)
        odd = i&1
        offsetX = diameter/2
        offsetY = diameter/2
        totalHeight = diameter * (self._size[1] + 0.5)
        return (int(offsetX + i*diameter*cos30 + 0.5),
               int(totalHeight - (offsetY + ((1-odd)*0.5 + j)*diameter) + 0.5))

    def freeze(self, squares, player = -1, shapes = [], dtype = 0):
        for i in range(len(squares)):
            sq = squares[i]
            if 0 <= sq[0] < self._size[0] and 0 <= sq[1] < self._size[1]:
                self._tiles[sq[0]][sq[1]] = Tile(player, dtype, shape=shapes[i] if shapes else None)

    def clear(self, i, j):
        if self._tiles[i][j] == None or self._tiles[i][j].player >= 0 or self._tiles[i][j].type != 0:
            self._tiles[i][j] = None

    def isFree(self, i, j):
        return not self._tiles[i][j]

class RoundState(object):
    def __init__(self, player_inputs):
        self.player_inputs = player_inputs

        self.board = Board()
        self._players = [Player(self.board) for _ in range(2)]
        self._particles = Particles()
        self._renderer = BoardRenderer(self.board, self)
        colors = [p._color for p in self._players]
        self._imageFactory = DayAndNight(IMAGES_DIR+"/snake_%s_%s.png", colors)
        while not self._imageFactory.imagesReady():
            pygame.time.wait(100)

    def loop(self):
        while 1:
            self._update()
            self._render()
            pygame.time.wait(GAME_TICK_PERIOD)


    def _update(self):
        actions = self.player_inputs.read()
        mv=[
                {"right":5,"left":1},
                {"right":0,"up":0,"down":2,"left":2},
                {"up":1,"left":1,"down":3,"right":3},
                {"left":2,"right":4},
                {"down":3,"left":3,"up":5,"right":5},
                {"down":4,"right":4,"left":0,"up":0}
        ]
        onlyOneMovePerPlayer={}
        for action in actions:
            player = self._players[action.player]
            if action.action in mv[player._direction] and action.keydown:
                onlyOneMovePerPlayer[action.player] = mv[player._direction][action.action]
        for p in onlyOneMovePerPlayer:
            self._players[p]._direction = onlyOneMovePerPlayer[p]

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
                self.board.freeze(player._snake, p, shapes=player._shapes)
                player.revive(self.board)

        # Map
        component = connectedComponent(self.board._size, lambda i,j:0 if self.board.isFree(i,j) else self.board._tiles[i][j].player+1) 
        # score with block explosion and collateral damage
        for b in range(len(component[0])):
            blocks = component[0][b]
            if blocks["size"] >= MINIMUM_CLUSTER_SIZE:
                extraCount = countAdjancentConnectedComponent(b+1, self.board._size, lambda i,j: not self.board.isFree(i,j), component[1])
                self._players[blocks["grp"]-1].score(blocks["size"]+extraCount)

        # remove exploded blocks, and add particles
        def clearAndParticle(p, i, j):
            if component[1][i][j] != 0:
                self._particles.addParticle(ScoreParticle(self.board.getTileCenterPosition(i,j, self._renderer._scale), "+1", self._players[p]._color))
                self.board.clear(i,j)

        for b in range(len(component[0])):
            blocks = component[0][b]
            if blocks["size"] >= MINIMUM_CLUSTER_SIZE:
                removeConnectedComponent(b+1, self.board._size, lambda i,j: clearAndParticle(component[0][b]["grp"]-1, i, j), component[1])

        self._particles.update()

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE: self._renderer.resize((event.w, event.h))
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: sys.exit() 


    def _render(self):
        self._clear()
        self._renderer.render(screen)

        pygame.display.flip()


    def _clear(self):
        screen.fill(BACKGROUND_COLOR)

def main():
    player_inputs = PlayerInputs()
    game = RoundState(player_inputs)
    game.loop()
if __name__ == "__main__":
    main()
