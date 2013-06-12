from pygame.locals import *
from character import LoadPng, Character
import pygame
#import random as pyrandom
#import math
import sys

#odswierzanie
TARGET_FPS = 50
#krok czasowy
TIME_STEP = 1.0/TARGET_FPS
#rozdzielczosc
SCREEN_WIDTH=800
SCREEN_HEIGHT=600
#debugowanie
DEBUG_SPRITE=0

#dzwiek
FREQ = 44100   # same as audio CD
BITSIZE = -16  # unsigned 16 bit
CHANNELS = 2   # 1 == mono, 2 == stereo
BUFFER = 1024  # audio buffer size in no. of samples
FRAMERATE = 30 # how often to check if playback has finished


PI = 3.1416


def main():
    # Inicijalizacja obrazu
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    pygame.display.set_caption('The Game')
    tloimg,tlorect = LoadPng("gra_bg.png")
    screen.blit(tloimg,(0,0))
    hero = Character(screen.get_rect())
    allsprites = pygame.sprite.RenderPlain(hero)
    clock = pygame.time.Clock()

    active = 1
    while active:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))
                elif event.key == K_LEFT:
                    hero.move(-1)
                elif event.key == K_RIGHT:
                    hero.move(1)
                elif event.key == K_UP:
                    hero.jump()
            elif event.type == KEYUP:
                if event.key == K_LEFT:
                    hero.stop()
                elif event.key == K_RIGHT:
                    hero.stop()
            else:
                pass
                #player2.eventGet(event)
                #player1.eventGet(event)
        try:
            clock.tick(TARGET_FPS)
        except:
            pass
        allsprites.update()
        screen.blit(tloimg,(0,0))
        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
