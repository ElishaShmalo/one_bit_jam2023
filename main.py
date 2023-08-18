import pygame as pg
import sys
import random as rn

from scripts.player import Player
from scripts.brick import Brick
import os

class Game:
    TILE_SIZE = 16
    SCREEN_WIDTH = 28 * TILE_SIZE *2
    SCREEN_HEIGHT = 17 * TILE_SIZE * 2
    WIDTH = SCREEN_WIDTH // 2
    HEIGHT = SCREEN_HEIGHT // 2
    FPS = 60
    MAX_OFFSET_SPEED = 4
    def __init__(self) -> None:
        pg.init()
        pg.mixer.init()
        pg.font.init()
        self.win = pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pg.SCALED, vsync=1)
        pg.display.set_caption("Classical Run")
        pg.display.set_icon(pg.image.load("assets\\graphics\\general\\icon.ico"))
        self.display = pg.Surface((self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT/2), pg.SRCALPHA)
        self.clock = pg.time.Clock()

        self.sounds = {
            "jump": pg.mixer.Sound("assets/sounds/jump.wav"),
            "die": pg.mixer.Sound("assets/sounds/die.wav"),
            "dash": pg.mixer.Sound("assets/sounds/dash.wav"),
        }
        pg.mixer.music.load("assets/sounds/bg_sound.mp3")
        pg.mixer.music.set_volume(0.15)
        self.sounds["jump"].set_volume(0.07)
        self.sounds["dash"].set_volume(0.1)
        self.sounds["die"].set_volume(0.1)

        self.imgs = {
            "player_idle": pg.image.load("assets\\graphics\\player\\idle\\1.png").convert()
        }        
        for key in self.imgs:
            self.imgs[key].set_colorkey(0)
        #     self.imgs[key].set_colorkey((255, 255, 255))
        self.fonts = {
            "player_score": pg.font.Font(None, 30),
            "instructions": pg.font.Font(None, 21),
            "high score": pg.font.Font(None, 17),
        }

        with open("utils/high_score.txt", "r") as f:
            self.high_score = int(f.read())
        self.high_score_txt = self.fonts["high score"].render(f"High Score: {self.high_score}", False, (255, 255, 255))

        self.instruction_dist = 50 - 8 # grid
        self.instructions = {
            (self.TILE_SIZE * 8, 25): self.fonts["instructions"].render("Use the ARROW keys to move, jump and quick-fall.", False, (255, 255, 255)),
            (self.TILE_SIZE * (8 + self.instruction_dist), 25): self.fonts["instructions"].render("Just FYI, you have a double jump :D", False, (255, 255, 255)),
            (self.TILE_SIZE * (8 + (2 * self.instruction_dist)), 25): self.fonts["instructions"].render("Oh! And you can dash with SPACE.", False, (255, 255, 255)),
            (self.TILE_SIZE * (8 + (3 * self.instruction_dist)), 25): self.fonts["instructions"].render("Double Oh! You can jump out of your dash if you haven't jumped yet and you time it right.", False, (255, 255, 255)),
            (self.TILE_SIZE * (8 + (4 * self.instruction_dist)), 25): self.fonts["instructions"].render("NOW RUN!!", False, (255, 255, 255)),
        }

        self.reset()

    
    def reset(self):
        self.running = True

        self.offset = [0, 0]

        self.bricks = {
            (1, 15): Brick(self, (1, 15)),
        }
        for i in range(1, 12):
            self.bricks[(i, 15)] = Brick(self, (i, 15))
        for i in range(15, 23):
            self.bricks[(i, 10)] = Brick(self, (i, 10))
        self.platform_types = {
            "square": {"shape": [(0, 0), (1, 0), (0, 1), (1, 1)],},
            "big_square": {"shape": [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)],},
            "hill": {"shape": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (1, -1), (2, -1), (3, -1), (2, -2),],},
            # "tower": {"shape": [(0, 0),*[(1, i) for i in range(-7, 7)], (2, 0)], },
            "ramp": {"shape": [(0, 0), (1, 0), (1, -1), (2, -1), (2, -2),]},
            "fliped_ramp": {"shape": [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2),]},
            "pit": {"shape": [(0, 0), (2, 0), *[(i, 1) for i in range(3)]], }
        }
        self.spawn_platform((27*self.TILE_SIZE, 5*self.TILE_SIZE), "square")

        self.make_platforms(3)

        self.player = Player(self, (299, 143), self.imgs["player_idle"], 5)
        self.spawn_plat_every = 2.5 # sec
        self.spawn_plat_timer = self.spawn_plat_every * self.FPS 
        self.offset_speed = 0.75

        self.high_score_txt = self.fonts["high score"].render(f"High Score: {self.high_score}", False, (255, 255, 255))

    def quit(self):
        pg.mixer.quit()
        pg.font.quit()
        pg.quit()
        sys.exit()

    def run(self):
        pg.mixer.music.play(-1)
        while self.running:
            self.clock.tick(self.FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    self.update_high_score()
                    self.quit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.player.jump()
                    elif event.key == pg.K_RIGHT:
                        self.player.move_right = True
                        self.player.move_left = False
                        self.player.facing_left = False
                        self.player.vel[0] = self.player.walk_speed
                    elif event.key == pg.K_LEFT:
                        self.player.move_right = False
                        self.player.move_left = True
                        self.player.facing_left = True
                        self.player.vel[0] = -self.player.walk_speed
                    elif event.key == pg.K_SPACE:
                        self.player.blink()
                    elif event.key == pg.K_DOWN:
                        self.player.sinking = True
                        self.player.vel[1] = max(0, self.player.vel[1])

                elif event.type == pg.KEYUP:
                    if event.key == pg.K_RIGHT:
                        if not self.player.move_left:
                            self.player.move_right = False
                            self.player.vel[0] = 0
                    elif event.key == pg.K_LEFT:
                        if not self.player.move_right:
                            self.player.move_left = False
                            self.player.vel[0] = 0
                    elif event.key == pg.K_DOWN:
                        self.player.sinking = False
                        
            self.update()
            self.draw()
    
    def update(self):
        self.offset[0] += self.offset_speed
        if self.offset_speed < self.MAX_OFFSET_SPEED:
            self.player.blink_speed = min(self.player.blink_speed + 0.0001, self.player.MAX_BLINK_SPEED)
            self.offset_speed = min(self.offset_speed + 0.00025, self.MAX_OFFSET_SPEED)
            self.player.walk_speed =  max(self.player.walk_speed, round(self.offset_speed) + 2)
        self.player.score += self.offset_speed / (0.5*self.FPS)
        
        self.spawn_plat_every = max(1.75, self.spawn_plat_every - 0.0005)
        self.player.update()

        bricks_to_remove = []
        for brick in self.bricks:
            if (brick[0] * self.TILE_SIZE) - self.offset[0] < -2*self.TILE_SIZE:
                bricks_to_remove.append(brick)
        for brick in bricks_to_remove:
            del self.bricks[brick] 
        
        if len(self.instructions) > 0:
            isnt_to_remove = []
            for inst in self.instructions:
                if inst[0] + self.instructions[inst].get_width() - self.offset[0] < -2 * self.TILE_SIZE:
                    isnt_to_remove.append(inst)
            for inst in isnt_to_remove:
                del self.instructions[inst] 
        
        self.spawn_plat_timer -= 1
        if self.spawn_plat_timer <= 0:
            self.spawn_plat_timer = round(self.spawn_plat_every, 3) * self.FPS
            self.make_platforms(2)
            self.make_platforms(1)
        
        if round(self.player.score) == self.high_score:
            self.high_score_txt = self.fonts["high score"].render(f"NEW HIGH SCORE!", False, (255, 255, 255))
    
    def spawn_platform(self, loc, p_type):
        grid_loc = [int(loc[0]//self.TILE_SIZE), int(loc[1]//self.TILE_SIZE)]
        grid_locs = [[grid_loc[0]+rel_location[0], grid_loc[1]+rel_location[1]] for rel_location in self.platform_types[p_type]["shape"]]
        while any(tuple(try_loc) in list(self.bricks) for try_loc in grid_locs):
            grid_loc[0] += 2
            grid_locs = [[grid_loc[0]+rel_location[0], grid_loc[1]+rel_location[1]] for rel_location in self.platform_types[p_type]["shape"]]
        for rel_location in self.platform_types[p_type]["shape"]:
            self.bricks[(grid_loc[0]+rel_location[0], grid_loc[1]+rel_location[1])] = Brick(self, (grid_loc[0]+rel_location[0], grid_loc[1]+rel_location[1]))
    
    def update_high_score(self):
        if round(self.player.score) > self.high_score:
            self.high_score = round(self.player.score)
            with open("utils/high_score.txt", "w") as f:
                f.write(str(round(self.player.score)))

    def make_platforms(self, num=1):
        section_sizes = self.WIDTH // (num)
        for i in range(num):
            plat_type = rn.choice(list(self.platform_types.keys()))
            loc = [rn.randint(int(self.offset[0]+self.WIDTH) + (section_sizes * i), int(self.offset[0]+(self.WIDTH)) + (section_sizes * (i+1))), rn.randint(self.HEIGHT//2.5, self.HEIGHT)]
            if plat_type == "tower":
                loc[1] = self.HEIGHT // 2
            elif plat_type == "pit":
                loc[1] = max(min(self.HEIGHT - 2*self.TILE_SIZE, loc[1]), self.TILE_SIZE * 2)
            elif plat_type == "ramp" or plat_type == "hill":
                loc[1] = max(min(self.HEIGHT - self.TILE_SIZE, loc[1]), 4*self.TILE_SIZE)
            elif plat_type == "square" or plat_type == "big_square":
                loc[1] = max(min(self.HEIGHT-2*self.TILE_SIZE, loc[1]), 2*self.TILE_SIZE)
            self.spawn_platform(loc, plat_type)

    def draw(self):
        self.win.fill(0)
        self.display.fill((0, 0, 0))

        for plat in self.bricks.values():
            plat.show()

        for loc in self.instructions:
            self.display.blit(self.instructions[loc], (loc[0] - self.offset[0], loc[1]))

        self.player.show()

        self.display.blit(self.high_score_txt, (5, 5))
        
        self.win.blit(pg.transform.scale2x(self.display), (0, 0))
        pg.display.update()

if __name__ == "__main__":
    application_path = os.path.dirname(sys.executable)
    game = Game()
    game.run()
