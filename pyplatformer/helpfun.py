import os
from typing import NamedTuple

import pygame


class ImageWithRect(NamedTuple):
    image: pygame.Surface
    rect: pygame.Rect


def load_image(name: str, image_dir_path: str | None = None) -> ImageWithRect:
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
        raise SystemExit("Failed to load image") from e
    return ImageWithRect(image, image.get_rect())
