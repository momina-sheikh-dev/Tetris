import sys
import pygame as pg
import math
import random
import pathlib
import pygame.freetype as ft

vec = pg.math.Vector2

FPS = 60
FIELD_COLOR = (48, 39, 32)
BG_COLOR = (24, 89, 117)

SPRITE_DIR_PATH = "C:\\Users\\Momina\\Downloads"
FONT_PATH = "C:\\Users\\Momina\\Downloads\\FREAKSOFNATUREMASSIVE.ttf"

ANIM_TIME_INTERVAL = 500 #milliseconds
FAST_ANIM_TIME_INTERVAL =15

TILE_SIZE = 30
FIELD_SIZE = FIELD_W, FIELD_H = 12, 21
FIELD_RES = FIELD_W * TILE_SIZE, FIELD_H * TILE_SIZE

FIELD_SCALE_W ,FIELD_SCALE_H = 1.7, 1.0
WIN_RES = WIN_W, WIN_H= FIELD_RES[0]* FIELD_SCALE_W, FIELD_RES[1]* FIELD_SCALE_H

INIT_POS_OFFSET = vec(FIELD_W // 2-1,0)
NEXT_POS_OFFSET = vec(FIELD_W*1.3, FIELD_H*0.45)
MOVE_DIRECTIONS = {'left': vec(-1,0), 'right': vec(1,0), 'down': vec(0,1)}
TETROMINOES = {
    'T': [(0, 0), (-1, 0), (1, 0), (0, -1)],
    'O': [(0, 0), (0, -1), (1, 0), (1, -1)],
    'J': [(0, 0), (-1, 0), (0, -1), (0, -2)],
    'L': [(0, 0), (1, 0), (0, -1), (0, -2)],
    'I': [(0, 0), (0, 1), (0, -1), (0, -2)],
    'S': [(0, 0), (-1, 0), (0, -1), (1, -1)],
    'Z': [(0, 0), (1, 0), (0, -1), (-1, -1)]
}

class App:
    def __init__(self):
        pg.init()
        pg.display.set_caption('Tetris')
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.set_timer()
        self.images = self.load_images()
        self.tetris = Tetris(self)
        self.text= Text(self)

    

    def load_images(self):
        files = [item for item in pathlib.Path(SPRITE_DIR_PATH).rglob('*.png') if item.is_file()]
        images = [pg.image.load(file).convert_alpha() for file in files]
        images = [pg.transform.scale(image, (TILE_SIZE, TILE_SIZE)) for image in images]
        return images
        print(files)

    def set_timer(self):
        self.user_event = pg.USEREVENT + 0
        self.fast_user_event = pg.USEREVENT + 1
        self.anim_trigger = False
        self.fast_anim_trigger = False
        pg.time.set_timer(self.user_event, ANIM_TIME_INTERVAL)
        pg.time.set_timer(self.fast_user_event, FAST_ANIM_TIME_INTERVAL)

    def update(self):
        self.tetris.update()
        self.clock.tick(FPS)

    def draw(self):
        self.screen.fill(color=BG_COLOR)
        self.screen.fill(color= FIELD_COLOR, rect=(0,0,*FIELD_RES))
        self.tetris.draw()
        self.text.draw()
        pg.display.flip()

    def check_events(self):
        self.anim_trigger = False
        self.fast_anim_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                self.tetris.control(pressed_key= event.key)
            elif event.type == self.user_event:
                self.anim_trigger = True
            elif event.type == self.fast_user_event:
                self.fast_anim_trigger = True

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()

class Text:
    def __init__(self,app):
        self.app= app
        self.font = ft.Font(FONT_PATH)

        
    def draw(self):
        self.font.render_to(self.app.screen,(WIN_W* 0.635, WIN_H*0.02),
                            text='TETRIS', fgcolor='white', size=TILE_SIZE*1.65,
                            bgcolor='black')
        self.font.render_to(self.app.screen,(WIN_W* 0.65, WIN_H*0.17),
                            text='NEXT', fgcolor='orange', size=TILE_SIZE*1.4,
                            bgcolor='black')
        self.font.render_to(self.app.screen,(WIN_W* 0.65, WIN_H*0.67),
                            text='SCORE', fgcolor='orange', size=TILE_SIZE*1.4,
                            bgcolor='black')
        self.font.render_to(self.app.screen,(WIN_W* 0.68, WIN_H*0.8),
                            text=f'{self.app.tetris.score}', fgcolor='white', size=TILE_SIZE*1.8)

    
class Tetris:
    def __init__(self, app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self,current = False)
        self.speed_up = False

        self.score=0
        self.full_lines = 0
        self.points_per_lines = {0:0, 1:100, 2:300, 3:700, 4:1500}

    def get_score(self):
        self.score+= self.points_per_lines[self.full_lines]
        self.full_lines = 0

    def check_full_lines(self):
        row = FIELD_H-1
        for y in range(FIELD_H-1,-1,-1):
            for x in range(FIELD_W):
                self.field_array[row][x] = self.field_array[y][x]
                if self.field_array[y][x]:
                    self.field_array[row][x].pos = vec(x,y)

            if sum(map(bool, self.field_array[y]))<FIELD_W:
                row-=1
            else:
                 for x in range(FIELD_W):
                     self.field_array[row][x].alive = False
                     self.field_array[row][x]= 0

                 self.full_lines += 1
                

    def put_tetromino_blocks_in_array(self):
        for block in self.tetromino.blocks:
            x,y = int(block.pos.x), int(block.pos.y)
            self.field_array[y][x] = block

    def get_field_array(self):
        return[[0 for x in range(FIELD_W)] for y in range(FIELD_H)]

    def is_game_over(self):
        if self.tetromino.blocks[0].pos.y == INIT_POS_OFFSET[1]:
            pg.time.wait(550)
            return True

    def check_tetromino_landing(self):
        if self.tetromino.landing:
            if self.is_game_over():
                self.__init__(self.app)
            else:
                self.speed_up = False
                self.put_tetromino_blocks_in_array()
                self.next_tetromino.current = True
                self.tetromino = self.next_tetromino
                self.next_tetromino = Tetromino(self, current=False)

    def control(self,pressed_key):
        if pressed_key == pg.K_LEFT:
            self.tetromino.move(direction = 'left')
        elif pressed_key == pg.K_RIGHT:
            self.tetromino.move(direction = 'right')
        elif pressed_key == pg.K_UP:
            self.tetromino.rotate()
        elif pressed_key == pg.K_DOWN:
            self.speed_up = True

    def draw_grid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, (0, 0, 0), (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    def update(self):
        trigger = [self.app.anim_trigger, self.app.fast_anim_trigger][self.speed_up]
        if trigger:
            self.check_full_lines()
            self.tetromino.update()
            self.check_tetromino_landing()
            self.get_score()
        self.sprite_group.update()

    def draw(self):
        self.draw_grid()
        self.sprite_group.draw(self.app.screen)
        


class Block(pg.sprite.Sprite):
    def __init__(self, tetromino, pos):
        self.tetromino = tetromino
        self.pos = vec(pos) + INIT_POS_OFFSET
        self.next_pos = vec(pos) + NEXT_POS_OFFSET
        self.alive = True

        super().__init__(tetromino.tetris.sprite_group)
        self.image = tetromino.image
        #self.image = pg.Surface([TILE_SIZE, TILE_SIZE])
        #pg.draw.rect(self.image,'yellow',(1,1, TILE_SIZE -2,TILE_SIZE -2), border_radius =8)
        self.rect = self.image.get_rect()

        self.sfx_image = self.image.copy()
        self.sfx_image.set_alpha(110)
        self.sfx_speed = random.uniform(0.2,0.6)
        self.sfx_cycles = random.randrange(6,8)
        self.cycle_counter = 0

    def sfx_end_time(self):
        if self.tetromino.tetris.app.anim_trigger:
            self.cycle_counter +=1
            if self.cycle_counter > self.sfx_cycles:
                self.cycle_counter = 0
                return True

    def sfx_run(self):
        self.image = self.sfx_image
        self.pos.y -= self.sfx_speed
        self.image = pg.transform.rotate(self.image, pg.time.get_ticks()* self.sfx_speed)

    def is_alive(self):
        if not self.alive:
            if not self.sfx_end_time():
                self.sfx_run()
            else:
                self.kill()

    def rotate(self, pivot_pos):
        translated = self.pos - pivot_pos
        rotated = translated.rotate(90)
        return rotated + pivot_pos

    def set_rect_pos(self):
        pos = [self.next_pos, self.pos][self.tetromino.current]
        self.rect.topleft = pos*TILE_SIZE
        #self.rect.topleft = (self.pos.x * TILE_SIZE, self.pos.y * TILE_SIZE)
        
    def update(self):
        self.is_alive()
        self.set_rect_pos()

    def is_collide(self, pos):
        x,y = int(pos.x), int(pos.y)
        if 0<= x < FIELD_W and y< FIELD_H and (
            y<0 or not self.tetromino.tetris.field_array[y][x]):
            return False
        return True

class Tetromino:
    def __init__(self, tetris, current=True):
        self.tetris = tetris
        self.shape = random.choice(list(TETROMINOES.keys()))
        self.image = random.choice(tetris.app.images)
        self.blocks = [Block(self, pos) for pos in TETROMINOES[self.shape]]
        self.landing = False
        self.current = current

    def rotate(self):
        pivot_pos = self.blocks[0].pos
        new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]
        if not self.is_collide(new_block_positions):
            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]

    def is_collide(self, block_positions):
        return any(map(Block.is_collide, self.blocks, block_positions))

    def move(self,direction):
        move_direction = MOVE_DIRECTIONS[direction]
        new_block_positions = [block.pos + move_direction for block in self.blocks]
        is_collide = self.is_collide(new_block_positions)

        if not is_collide:
            for block in self.blocks:
                block.pos += move_direction
        elif direction == 'down':
            self.landing = True

    def update(self):
        self.move(direction = 'down')
        #pg.time.wait(200)


if __name__ == '__main__':
    app = App()
    app.run()
