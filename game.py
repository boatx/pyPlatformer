import sys

import pygame
from pygame.locals import KEYDOWN, KEYUP, K_ESCAPE, K_LEFT, K_RIGHT, K_UP, QUIT

from character import load_image, Character
from config.settings import SCREEN_HEIGHT, SCREEN_WIDTH, TARGET_FPS


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("The Game")
    bg_img, bg_rect = load_image("gra_bg.png")
    screen.blit(bg_img, (0, 0))
    hero = Character(screen.get_rect())
    all_sprites = pygame.sprite.RenderPlain(hero)
    clock = pygame.time.Clock()

    while True:
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

        clock.tick(TARGET_FPS)

        all_sprites.update()
        screen.blit(bg_img, (0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
