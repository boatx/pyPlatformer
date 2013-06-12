import pygame
from helpfun import LoadPng

class Character(pygame.sprite.Sprite):
    """character class"""
    def __init__(self,area):
        pygame.sprite.Sprite.__init__(self)
        self.image_normal1, self.rect_normal1 = LoadPng("normal.png")
        self.image_normal2, self.rect_normal2 = LoadPng("normal1.png")
        self.image_walk1, self.rect_walk1 = LoadPng("walk1.png")
        self.image_walk2, self.rect_walk2 = LoadPng("walk2.png")
        self.image_jump, self.rect_jump = LoadPng("jump.png")
        self.image, self.rect = self.image_normal1, self.rect_normal1
        self.rect.midbottom = area.midbottom
        self.area=area
        self.status="normal"
        self.x = self.rect.x
        self.y = self.rect.y
        self.vel_x=0.0
        self.vel_y=0.0
        self.orientation = 1
        self.speed=4
        self.speed_max=9
        self.speed_increase=0.5

    def update(self):
        if self.status == "jump" or self.status == "double_jump":
            #gravity
            self.vel_y +=2

        if  self.vel_x != 0.0 or self.vel_y != 0.0:
            self.rect.move_ip(self.vel_x * self.speed,self.vel_y)
            if self.vel_x != 0.0 and self.speed < self.speed_max:
                self.speed += self.speed_increase
        if self.rect.bottom > self.area.bottom:
            self.rect.bottom = self.area.bottom
            self.vely = 0
            self.status="normal"
            self.image = self.image_normal1


    def move(self,vel_x):
        if self.status == "normal":
            self.status == "walk1"
        elif self.status == "walk1":
            self.status == "walk2"
        elif self.status == "walk2":
            self.status == "walk1"
        if vel_x < 0 and self.orientation == 1:
            self.orientation = 0
            self.image = pygame.transform.flip(self.image,1,0)
        elif vel_x > 0 and self.orientation == 0:
            self.orientation = 1
            self.image = pygame.transform.flip(self.image,1,0)

        self.vel_x = vel_x

    def jump(self):
        if self.status != "double_jump":
            if self.status == "jump":
                self.status = "double_jump"
                self.vel_y = -20
            else:
                self.status="jump"
                self.image = self.image_jump
                self.vel_y = -20

    def stop(self):
        self.vel_x=0.0
        self.speed=1
