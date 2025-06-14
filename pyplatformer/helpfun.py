import os

import pygame


def load_image(name, image_dir_path=None):
    """Load image."""

    if image_dir_path is None:
        fullname = os.path.join("data", "img", name)
    else:
        fullname = os.path.join(image_dir_path, name)

    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as e:
        print("File load has failed:{}".format(fullname))
        raise SystemExit(e.message)
    return image, image.get_rect()
