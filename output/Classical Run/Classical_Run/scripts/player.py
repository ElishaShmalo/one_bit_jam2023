import pygame as pg
from .entity import Entity


class Player(Entity):
    MAX_BLINK_SPEED = 35
    def __init__(self, game, pos, img, speed=5) -> None:
        super().__init__(game, pos, "player", img, speed)
        self.rect.size = (10, 16)
        self.can_jump = True
        self.jumps = 2
        self.air_time = 0
        self.walk_speed = 3

        self.terminal_vel = 5

        self.blink_cooldown = 0
        self.blinking = 0
        self.blink_dir = 0
        self.blink_speed = 20

        self.score = 0
    
    def update(self):
        super().update()

        if not self.grounded:
            self.air_time += 1
        else:
            self.air_time = 0
            self.reset_jumps()
        if self.air_time > 15:
            self.can_jump = False
        
        if self.blinking > 0:
            self.vel[0] = self.blink_speed * self.blink_dir
            self.rect.y -= self.vel[1]
        elif self.blinking == 0:
            self.vel[1] = -4
            self.air_time = -5
        else:
            self.vel[0] = self.walk_speed * (-self.move_left + self.move_right)
        self.blink_cooldown = max(0, self.blink_cooldown-1)
        self.blinking = max(-1, self.blinking - 1)

        if self.rect.y > self.game.HEIGHT + 5 * self.game.TILE_SIZE:
            self.game.sounds["die"].play()
            self.game.update_high_score()
            self.game.reset()
        
    
    def reset_jumps(self):
        self.can_jump = True
        self.jumps = 2

    def jump(self):
        if self.can_jump or self.jumps == 1:
            self.game.sounds["jump"].play()
            self.jumps -= 1
            self.vel[1] = -11
    
    def blink(self):
        if self.blink_cooldown == 0:
            self.game.sounds["dash"].play()
            self.blink_cooldown = 60
            self.blinking = 3
            self.blink_dir = (-self.facing_left + (not self.facing_left))
    
    def show(self):
        super().show(3)
        score_txt : pg.Surface = self.game.fonts["player_score"].render(f"{round(self.score)}", False, (255, 255, 255))
        self.game.display.blit(score_txt, (self.game.WIDTH // 2 - score_txt.get_width() // 4, 5))
        # pg.draw.rect(self.game.display, "red", self.rect, 1)

