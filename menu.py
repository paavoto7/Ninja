import pygame

from Score import Score

class Button:
    def __init__(self, image, pos=(0,0)) -> None:
        self.image = image
        self.rect = self.image.get_rect(midtop=pos)

    def pressed(self, coordinate):
        if self.rect.collidepoint(coordinate):
            return True


def menu(screen, clock, FPS, bg, game_over=False):

    on_pause = True
    center = (screen.get_width() / 2, screen.get_height() / 2)

    banana = pygame.image.load("./assets/banana_fruit.png").convert_alpha()
    button = Button(banana, (center[0], center[1]))

    rect = pygame.Rect(0, 0, 700, 700)
    rect.center = center

    while on_pause:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    on_pause = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.pressed(pygame.mouse.get_pos()):
                    on_pause = False
            if event.type == pygame.QUIT:
                exit()
        screen.fill("black")
        screen.blit(bg, (0, 0))
        
        """if beginning:
            if len(grounds) < 2:
                Ground(grounds)
            screen.blit(bg, (0, 0))
            grounds.draw(screen)
            grounds.update()
            screen.blit(player.image, player.rect)
            screen.blit(button.image, button.rect)"""


        if game_over:
            center = screen.get_width() / 2, screen.get_height() / 2
            over = Score("impact", "Game Over", center, 100, "white")
            screen.blit(over.text, over.tRect)

        screen.blit(button.image, button.rect)
        pygame.display.flip()
        clock.tick(FPS)

    return True