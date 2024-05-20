from pygame import font

class Score:
    def __init__(self, font_name, cont, pos, font_size=40, colour="black") -> None:
        self.colour = colour
        self.font = font.SysFont(font_name, font_size)
        self.text = self.font.render(str(cont), True, colour)
        self.tRect = self.text.get_rect()
        self.tRect.center = pos

    def update(self, cont):
        self.text = self.font.render(str(cont), True, self.colour)

