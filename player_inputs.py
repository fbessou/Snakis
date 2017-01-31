import pygame

class PlayerInputs:
    def __init__(self):
        self._mapping = [
                {pygame.K_d:"right", pygame.K_s:"down", pygame.K_q:"left"},
                {pygame.K_RIGHT:"right", pygame.K_DOWN:"down", pygame.K_LEFT:"left"}
                ]

    def read(self):
        inputs = []
        for event in pygame.event.get():
            keydown = False
            used = False
            if event.type == pygame.KEYDOWN:
                keydown = True
            if event.type == pygame.KEYUP or keydown:
                for player in range(len(self._mapping)):
                    if event.key in self._mapping[player]:
                        inputs.append((player, self._mapping[player][event.key], keydown))
                        used = True
            if not used:
                pygame.event.post(event)

        return inputs
