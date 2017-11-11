import os
import pygame


def load_image(name):
    """Load image."""

    fullname = os.path.join('data', 'img', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as e:
        print('File load has failed:{}'.formt(fullname))
        raise SystemExit(e.message)
    return image, image.get_rect()
