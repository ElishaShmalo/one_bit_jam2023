import pygame as pg

class Brick:
    def __init__(self, game, pos) -> None:
        self.game = game
        self.rect = pg.Rect(pos[0]*self.game.TILE_SIZE, pos[1]*self.game.TILE_SIZE, self.game.TILE_SIZE, self.game.TILE_SIZE)
        self.img = pg.Surface((self.game.TILE_SIZE, self.game.TILE_SIZE))
        self.img.fill((255, 255, 255))
    def show(self):
        self.game.display.blit(self.img, (self.rect.x-round(self.game.offset[0]), self.rect.y-round(self.game.offset[1])))

