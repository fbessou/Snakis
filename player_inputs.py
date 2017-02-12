import pygame
from collections import namedtuple

PlayerInput = namedtuple("PlayerInput",field_names=["player","action","keydown"])

class PlayerInputs:
    def __init__(self):
        self._mapping = [
                { # Player 
                    pygame.K_d:"right",
                    pygame.K_s:"down",
                    pygame.K_q:"left",
                    pygame.K_z:"up"
                },
                { # Player 1
                    pygame.K_RIGHT:"right",
                    pygame.K_DOWN:"down",
                    pygame.K_LEFT:"left",
                    pygame.K_UP:"up"
                }
        ]

    def read(self):
        inputs = []
        unused_events = []
        while True:
            event = pygame.event.poll()
            if event.type == pygame.NOEVENT:
                break

            keydown = False
            used = False
            if event.type == pygame.KEYDOWN:
                keydown = True
            if event.type == pygame.KEYUP or keydown:
                for player in range(len(self._mapping)):
                    if event.key in self._mapping[player]:
                        inputs.append(PlayerInput(player, self._mapping[player][event.key], keydown))
                        used = True
            if not used:
                unused_events.append(event)

        for event in unused_events:
            pygame.event.post(event)

        return inputs
