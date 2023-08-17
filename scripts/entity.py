import pygame as pg

class Entity:
    GRAVITY = 0.5

    def __init__(self, game, pos, e_type, img=pg.Surface((16, 16)), speed=5) -> None:
        self.game = game
        self.img = img
        self.type = e_type
        self.rect = pg.FRect(pos[0], pos[1], *self.img.get_size())
        self.collide_rect = pg.FRect(*self.rect.topleft, *self.img.get_size())
        self.vel = [0, 0]
        self.move_right = False
        self.move_left = False
        self.move_up = False
        self.move_down = False
        self.facing_left = False
        self.walk_speed = speed
        
        self.terminal_vel = 6

        self.collidable = True
        self.grounded = False

    def update(self):
        self.vel[1] = min(self.terminal_vel, self.vel[1]+self.GRAVITY)

        self.move_up = self.vel[1] < 0
        self.move_down = self.vel[1] > 0

        if self.move_up or self.move_down:
            self.grounded = False

        grid_pos = self.get_grid_pos()
        grid_poss_to_check = [
            (grid_pos[0]-1, grid_pos[1]-1), (grid_pos[0], grid_pos[1]-1), (grid_pos[0]+1, grid_pos[1]-1),
            (grid_pos[0]-1, grid_pos[1]), grid_pos, (grid_pos[0]+1, grid_pos[1]),
            (grid_pos[0]-1, grid_pos[1]+1), (grid_pos[0], grid_pos[1]+1), (grid_pos[0]+1, grid_pos[1]+1)
            ]
        
        self.rect.y += self.vel[1]
        if self.collidable:
            for grid_poss in grid_poss_to_check:
                plat = self.game.bricks.get(grid_poss)
                if plat and self.rect.colliderect(plat.rect):
                    if self.move_up:
                        self.rect.top = plat.rect.bottom
                        self.vel[1] = 0
                    elif self.move_down:
                        self.rect.bottom = plat.rect.top
                        self.vel[1] = 0
                        self.grounded = True
        
        self.rect.x += self.vel[0]

        if self.collidable:
            for grid_poss in grid_poss_to_check:
                plat = self.game.bricks.get(grid_poss)
                if plat and self.rect.colliderect(plat.rect):
                    if self.move_right:
                        self.rect.right = plat.rect.left
                    elif self.move_left:
                        self.rect.left = plat.rect.right
        
    def show(self, img_offsetx=0):
        self.game.display.blit(pg.transform.flip(self.img, self.facing_left, False), (self.rect.topleft[0]-img_offsetx-round(self.game.offset[0]), self.rect.topleft[1]-round(self.game.offset[1])))
    
    def get_grid_pos(self):
        return (int(self.rect.x // self.game.TILE_SIZE), int(self.rect.y // self.game.TILE_SIZE))

