import os
import pygame

def LoadPng(name):
    """Ladowanie obrazow"""
    fullname = os.path.join('data', 'img', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        print 'Nie moge zaladowac obrazu:', fullname
        raise SystemExit, message
    return image, image.get_rect()
