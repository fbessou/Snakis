import pygame

class PlayerInputs:
    def __init__(self):
        mapping = [
                {pygame.K_d:"right", pygame.K_s:"down", pygame.K_q:"left"},
                {pygame.K_RIGHT:"right", pygame.K_DOWN:"down", pygame.K_LEFT:"left"}
                ]

    def read(self):
        inputs = []
        for event in pygame.event.get():
            keydown = False
            if event.type == pygame.KEYDOWN:
                keydown = True
            if event.type == pygame.KEYUP or keydown:
                for player in range(len(mapping)):
                    if event.key in mapping[player]:
                        inputs.append((player, mapping[player][event.key], keydown))

        return inputs
