from pygame import font

class Score:
    """Is used to render the score of the game.
    Can be used for other text as well."""
    def __init__(self, font_name, cont, pos, font_size=40, colour="black") -> None:
        self.colour = colour
        self.font = font.SysFont(font_name, font_size)
        self.text = self.font.render(str(cont), True, colour)
        self.tRect = self.text.get_rect()
        self.tRect.center = pos

    def update(self, content) -> None:
        """Update the text of the Score"""
        self.text = self.font.render(str(content), True, self.colour)
