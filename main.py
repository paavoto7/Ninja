from os import listdir
import random

import pygame

from menu import menu
from Score import Score

FPS = 60
SCREEN_BOTTOM = 810
SCREEN_WIDTH = 926
SCORE = 0
LIVES = 5
ACTION = pygame.event.custom_type()

images = {}
images["fruits"] = []
filenames = listdir("./assets/")
def load_images():
    for imagename in filenames:
        if "fruit" in imagename:
            images["fruits"].append((pygame.image.load(f"./assets/{imagename}").convert_alpha(),
                                     imagename[0:-4].strip("_fruit")))
        else:
            images[imagename[0:-4]] = pygame.image.load(f"./assets/{imagename}").convert_alpha()


class Fruit(pygame.sprite.Sprite):
    def __init__(self, image: pygame.surface.Surface, position, *groups) -> None:
        super().__init__(*groups)
        self.image = image[0]
        self.name = image[1]
        self.rect = self.image.get_rect(center=position)
    
    def update(self):
        self.rect.y += 5
        if self.rect.y >= SCREEN_BOTTOM:
            global LIVES
            LIVES -= 1
            self.kill()


class Sliced(pygame.sprite.Sprite):
    def __init__(self, whole: Fruit, order, *groups) -> None:
        super().__init__(*groups)
        self.image = images[f"{whole.name}_{order}"]
        self.order = order
        self.rect = self._set_rect(whole)
        self.velx = 0
        self.vely = 0

    def _set_rect(self, whole):
        if self.order == 1:
            return self.image.get_rect(topright=whole.rect.midbottom)
        else:
            return self.image.get_rect(topleft=whole.rect.midbottom)
    
    def update(self):
        self.velx += -0.5 if self.order == 1 else 0.5
        self.vely += 1
        self.rect.x += self.velx
        self.rect.y += self.vely
        if self.rect.y >= SCREEN_BOTTOM:
            self.kill()


class Katana(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.image = images["katana"]
        #self.rect = self.image.get_rect(center=(100, 100))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.mask.get_rect()
        self.pos = pygame.Vector2((100,100))
        self.sound = pygame.mixer.Sound("./sounds/Recording.wav")
        self.sound.set_volume(0.2)

    def update(self):
        heading = pygame.mouse.get_pos() - self.pos
        self.pos += heading
        self.rect.bottomright = self.pos

        angle = (SCREEN_WIDTH / 180) * (self.rect.x / 100)
        self.image = pygame.transform.rotate(images["katana"], angle)

"""
class Trail(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.image = pygame.Surface((200, 200), pygame.SRCALPHA)
        #self.image.fill()
        self.rect = self.image.get_rect(center=(200,200))
        self.pos = pygame.Vector2((100,100))
        pygame.draw.line(self.image, (255,255,255,200), self.pos[0], self.pos[1])
        self.sound = pygame.mixer.Sound("./sounds/Recording.wav")
        self.sound.set_volume(0.2)

    def update(self):
        heading = pygame.mouse.get_pos() - self.pos
        self.pos += heading * 0.7
        self.rect.midtop = self.pos
"""

def fruit_generator(group, width):
    image = images["fruits"][random.randint(0, len(images["fruits"])-1)]
    position = (random.randint(0, width), 0)
    Fruit(image, position, group)


def generate_sliced(whole, group):
    
    Sliced(whole, 1, group)
    Sliced(whole, 2, group)


def quit(screen, clock, fruits, sliced, game_over=False):
    global LIVES, SCORE
    SCORE = 0
    LIVES = 5
    fruits.empty()
    sliced.empty()
    return menu(screen, clock, FPS, images["shoji"], game_over)


def main():
    global SCORE, LIVES

    pygame.init()
    pygame.mixer.init()
    #screen_size = (pygame.display.Info().current_w, SCREEN_BOTTOM)
    screen_size = (SCREEN_WIDTH, SCREEN_BOTTOM)
    screen = pygame.display.set_mode(screen_size, pygame.SCALED)
    center = (screen.get_width() / 2, screen.get_height() / 2)
    clock = pygame.time.Clock()
    load_images()

    fruits = pygame.sprite.Group()
    sliced = pygame.sprite.Group()
    katanaGroup = pygame.sprite.GroupSingle()

    katana = Katana(katanaGroup)
    #katana = Trail(katanaGroup)
    score = Score("impact", SCORE, (100, 100), 100, "white")

    # Does it update the time???
    pygame.time.set_timer(ACTION, int(500 - SCORE**1.05))

    running = menu(screen, clock, FPS, images["shoji"])

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = quit(screen, clock, fruits, sliced)
            if event.type == ACTION:
                fruit_generator(fruits, screen.get_width())
        
        if LIVES == 0:
            running = quit(screen, clock, fruits, sliced, game_over=True)
        
        if collided := pygame.sprite.spritecollideany(katana, fruits):
            SCORE += 1
            katana.sound.play()
            generate_sliced(collided, sliced)
            collided.kill()
        score.update(SCORE)
        
        screen.fill("black")
        screen.blit(images["shoji"], (0,0))
        [screen.blit(images["heart"], (images["heart"].get_width() * i, 10)) for i in range(LIVES)]

        screen.blit(score.text, score.tRect)

        fruits.update()
        fruits.draw(screen)
        katanaGroup.update()
        katanaGroup.draw(screen)
        sliced.draw(screen)
        sliced.update()

        pygame.display.flip()

        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
