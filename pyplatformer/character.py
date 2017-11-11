from pygame import sprite, transform

from pyplatformer.config.const import GRAVITY
from pyplatformer.helpfun import load_image


class Character(sprite.Sprite):
    """Character class"""

    def __init__(self, area):
        sprite.Sprite.__init__(self)

        self.image_normal1_r, self.rect_sprite = load_image("normal.png")
        self.image_normal1_l = transform.flip(self.image_normal1_r, 1, 0)
        self.image_walk1_r, _ = load_image("walk1.png")
        self.image_walk1_l = transform.flip(self.image_walk1_r, 1, 0)
        self.image_walk2_r, _ = load_image("walk2.png")
        self.image_walk2_l = transform.flip(self.image_walk2_r, 1, 0)
        self.image_jump_r, _ = load_image("jump.png")
        self.image_jump_l = transform.flip(self.image_jump_r, 1, 0)

        self.image, self.rect = self.image_normal1_r, self.rect_sprite
        self.rect.midbottom = area.midbottom
        self.area = area
        self.status = "normal"
        self.x = self.rect.x
        self.y = self.rect.y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.orientation = "right"
        self.speed = 1
        self.speed_max = 5
        self.speed_increase = 0.2
        self.jump_speed = -20
        self.counter = 0

    def update(self):
        if self.status == "jump" or self.status == "double_jump":
            # gravity
            self.vel_y += GRAVITY

        if self.vel_x != 0.0 or self.vel_y != 0.0:
            self.rect.move_ip(self.vel_x * self.speed, self.vel_y)
            if self.vel_x != 0.0 and self.speed < self.speed_max:
                self.speed += self.speed_increase

        if self.vel_x != 0.0 and self.vel_y == 0.0:
            if self.counter > 10:
                self.counter = 0
                if self.orientation == "left":
                    if self.image == self.image_walk1_l:
                        self.image = self.image_walk2_l
                    else:
                        self.image = self.image_walk1_l

                if self.orientation == "right":
                    if self.image == self.image_walk1_r:
                        self.image = self.image_walk2_r
                    else:
                        self.image = self.image_walk1_r
            else:
                self.counter += 1

        # stop at the bottom
        if self.rect.bottom > self.area.bottom:
            self.rect.bottom = self.area.bottom
            self.vel_y = 0
            self.status = "normal"
            if self.orientation == "right":
                self.image = self.image_normal1_r
            else:
                self.image = self.image_normal1_l

    def move(self, vel_x):
        self.vel_x = vel_x
        self.turn()

    def turn(self):
        if self.vel_x < 0 and self.orientation == "right":
            self.orientation = "left"
            self.image = self.image_walk1_l
        elif self.vel_x > 0 and self.orientation == "left":
            self.orientation = "right"
            self.image = self.image_walk1_r

    def jump(self):
        if self.status != "double_jump":
            if self.status == "jump":
                self.status = "double_jump"
                self.vel_y = self.jump_speed
            else:
                self.status = "jump"
                if self.orientation == "right":
                    self.image = self.image_jump_r
                else:
                    self.image = self.image_jump_l
                self.vel_y = self.jump_speed

    def stop(self):
        self.vel_x = 0.0
        self.speed = 1
