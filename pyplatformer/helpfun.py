from pathlib import Path
from typing import NamedTuple

import pygame

DEFAULT_IMAGE_PATH = Path("data", "img")

class ImageWithRect(NamedTuple):
    image: pygame.Surface
    rect: pygame.Rect


def load_image(name: str, image_dir_path: str | None = None) -> ImageWithRect:
    """Load image."""

    if image_dir_path is None:
        _path = DEFAULT_IMAGE_PATH / name
    else:
        _path = Path(image_dir_path, name)

    try:
        image = pygame.image.load(_path)
        converted_iamge = (
            image.convert() if image.get_alpha is None else image.convert_alpha()
        )
    except pygame.error as e:
        raise SystemExit("Failed to load image") from e
    return ImageWithRect(converted_iamge, image.get_rect())
