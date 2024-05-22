import pygame


class CTagStar:
    def __init__(self, blink_rate: float, color: pygame.Color)->None:
        self.blink_rate = blink_rate
        self.color = color