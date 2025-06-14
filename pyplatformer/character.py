from collections import defaultdict
from enum import IntEnum
from typing import NamedTuple, TypedDict
from uuid import uuid1

from pygame import Rect, Surface, sprite, transform

from pyplatformer.config.const import GRAVITY
from pyplatformer.helpfun import load_image


class Orientation(IntEnum):
    LEFT = -1
    RIGHT = 1


class State(IntEnum):
    NORMAL = 1
    JUMP = 2
    DOUBLE_JUMP = 3
    WALK = 4


class CharacterImages(NamedTuple):
    images: dict[State, dict[Orientation, Surface | list[Surface]]]
    rect: Rect


class CharacterDict(TypedDict):
    id: str
    state: State
    orientation: Orientation
    rect: list[int]


def change_img_orientation(
    img: Surface, orientation: Orientation = Orientation.LEFT
) -> Surface:
    return transform.flip(img, orientation.value, False)  # type: ignore


class CharacterLogic:
    """Character class"""

    DEFAULT_SPEED = 1.0

    def __init__(
        self,
        area: Rect,
        rect: Rect | None = None,
        obj_id: str | None = None,
    ) -> None:
        super().__init__()
        self.area = area
        self.state = State.NORMAL
        self.orientation = Orientation.RIGHT
        self.rect = rect
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.speed = self.DEFAULT_SPEED
        self.speed_max = 5
        self.speed_increase = 0.2
        self.jump_speed = -20
        self.obj_id = obj_id or str(uuid1())

    def dump(self) -> dict:
        return {
            "id": self.obj_id,
            "state": self.state,
            "orientation": self.orientation,
            "rect": list(self.rect or []),
        }

    @property
    def is_in_air(self) -> bool:
        return self.state in (State.JUMP, State.DOUBLE_JUMP)

    def update(self) -> None:
        if not self.rect:
            raise ValueError("No rect")
        if self.is_in_air:
            # gravity
            self.vel_y += GRAVITY

        if self.vel_x != 0.0 or self.vel_y != 0.0:
            self.rect.move_ip(self.vel_x * self.speed, self.vel_y)
            if self.vel_x != 0.0 and self.speed < self.speed_max:
                self.speed += self.speed_increase

        # stop at the bottom
        if self.rect.bottom > self.area.bottom:
            self.rect.bottom = self.area.bottom
            self.vel_y = 0
            self.state = State.NORMAL if self.vel_x == 0 else State.WALK

    def move(self, vel_x: float | int) -> None:
        self.vel_x = vel_x
        self.turn()
        self.counter = 0
        if not self.is_in_air:
            self.state = State.WALK

    def turn(self) -> None:
        if self.vel_x < 0 and self.orientation == Orientation.RIGHT:
            self.orientation = Orientation.LEFT
        elif self.vel_x > 0 and self.orientation == Orientation.LEFT:
            self.orientation = Orientation.RIGHT

    def jump(self) -> None:
        if self.state == State.DOUBLE_JUMP:
            return
        if self.state == State.JUMP:
            self.state = State.DOUBLE_JUMP
            self.vel_y = self.jump_speed
        else:
            self.state = State.JUMP
            self.vel_y = self.jump_speed

    def stop(self) -> None:
        self.vel_x = 0.0
        self.speed = self.DEFAULT_SPEED
        if not self.is_in_air:
            self.state = State.NORMAL


# TODO fix use composition
class Character(CharacterLogic, sprite.Sprite):  # type: ignore
    """Character class"""

    COUNTER_DIVIDER = 10
    DEFAULT_SPEED = 1.0

    def __init__(self, area: Rect, obj_id: str | None = None):
        super().__init__(area=area, obj_id=obj_id)
        self.images, self.rect = self.load_images()
        self.image = self.images[self.state][self.orientation]  # type: ignore
        self.rect.midbottom = area.midbottom
        self.counter = 0

    def load_images(self) -> CharacterImages:
        images: defaultdict[State, dict[Orientation, Surface | list[Surface]]] = (
            defaultdict(dict)
        )
        img, rect = load_image("normal.png")
        images[State.NORMAL][Orientation.RIGHT] = img
        images[State.NORMAL][Orientation.LEFT] = change_img_orientation(img)

        img, _ = load_image("jump.png")
        images[State.JUMP][Orientation.RIGHT] = img
        images[State.JUMP][Orientation.LEFT] = change_img_orientation(img)
        images[State.DOUBLE_JUMP] = images[State.JUMP]

        img1, _ = load_image("walk1.png")
        img2, _ = load_image("walk2.png")
        images[State.WALK][Orientation.RIGHT] = [img1, img2]
        images[State.WALK][Orientation.LEFT] = [
            change_img_orientation(img1),
            change_img_orientation(img2),
        ]

        return CharacterImages(images, rect)

    def update_image(self) -> None:
        image = self.images[self.state][self.orientation]

        if isinstance(image, list):
            image = self.select_frame(image)

        self.image = image

    def select_frame(self, image: list[Surface]) -> Surface:
        if self.counter == self.COUNTER_DIVIDER * len(image):
            self.counter = 0
        index = self.counter // self.COUNTER_DIVIDER
        self.counter += 1
        return image[index]

    def update(self) -> None:
        super().update()
        self.update_image()
