from math import sqrt
from utils.engine import *
import sys
import os
import random
import pygame
from pymitter import EventEmitter
from pygame import draw, display, image, event, mixer, font, mouse

WIDTH = 400
HEIGHT = 400
gameDinoEvent = EventEmitter()


class DinoStates:
    IDLE_BASE = 0
    IDLE = 4

    RUN_BASE = 4
    RUN = 10

    JUMP_BASE = 10
    JUMP = 12

    HIT_BASE = 13
    HIT = 17

    JUMP_CROUCH_BASE = 17
    JUMP_CROUCH = 19

    CROUCH_BASE = 19
    CROUCH = 24


class TileIndex:
    LEFT_GRASS = 0
    LEFT_GROUND = 1
    LEFT_END = 2

    LEFT_TOP_WALL = 3
    LEFT_WALL = 4
    LEFT_END_WALL = 5

    GRASS = 6
    GROUND = 7
    GROUND_END = 8

    WALL_TOP = 9
    WALL_FILL = 10
    WALL_END = 11

    RIGHT_GRASS = 12
    RIGHT_GROUND = 13
    RIGHT_END = 14

    RIGHT_TOP_WALL = 15
    RIGHT_WALL = 16
    RIGHT_END_WALL = 17

    RIGHT_GRASS_END = 18
    RIGHT_GROUND_2 = 19
    RIGHT_GRASS_END_2 = 20

    RIGHT_WALL_CLEAN = 21
    RIGHT_WALL_CLEAN_FILL = 22
    RIGHT_WALL_CLEAN_2 = 23

    LEFT_GRASS_END = 24
    LEFT_GROUND_2 = 25
    LEFT_GRASS_END_2 = 26

    LEFT_WALL_CLEAN = 27
    LEFT_WALL_CLEAN_FILL = 28
    LEFT_WALL_CLEAN_2 = 29

    GROUND_TEXTURED = 30
    GROUND_TEXTURED_2 = 31
    GRASS_SINGLE_TEXT = 32

    BRICK_RIGHT_TOP = 33
    BRICK_RIGHT_MIDLE = 34
    BRICK_RIGHT = 35

    GROUND_TEXTURED_3 = 36
    GROUND_TEXTURED_4 = 37

    BRICK_MID_TOP = 38
    BRICK_MID_MIDLE = 39
    BRICK_MID = 40

    GROUND_TEXTURED_5 = 41

    BRICK_LEFT_TOP = 42
    BRICK_LEFT_MIDLE = 43
    BRICK_LEFT = 44


class Dino(GameItem):
    def __init__(self, args: list[str]):
        GameItem.__init__(self)

        self.dino_types = ["doux", "mort", "tard", "vita"]
        self.dino_index = 0
        self.mario_mode = False

        if len(args) >= 1:
            if os.path.exists("./assets/DinoSprites - {0}.png".format(args[0])):
                i = 0
                for t in self.dino_types:
                    if t == args[0]:
                        self.dino_index = i
                    i += 1
            elif int(args[0]) >= 0 and int(args[0]) < 4:
                self.dino_index = int(args[0])

        self.decors = image.load("./assets/Decors.png")
        self.backgrounds = [
            image.load("./assets/BG1.png"),
            image.load("./assets/BG2.png"),
            image.load("./assets/BG3.png")
        ]

        self.player_textures = []
        self.tile_textures = []

        self.score = 0
        self.coin = 0
        self.game_speed = 350
        self.game_time = 0
        self.state = DinoStates.IDLE
        self.state_base = DinoStates.IDLE_BASE

        self.start = False

        self.init_animation = GameAnimation()
        self.init_animation.max_duration = 320
        self.init_animation.vars.append(True)

        self.player_animation = GameAnimation()
        self.player_animation.max_duration = 10
        self.player_animation.vars.append(self.state_base)
        self.player_animation.vars.append(self.state)
        self.player_animation.vars.append(self.state_base)

        self.icon_animation = GameAnimation()
        self.icon_animation.max_duration = 10
        self.icon_animation.vars.append(DinoStates.RUN_BASE)
        self.icon_animation.vars.append(DinoStates.RUN)
        self.icon_animation.vars.append(DinoStates.RUN_BASE)

        self.start_animation = GameAnimation()
        self.start_animation.max_duration = 95
        self.start_animation.vars.append(4 if not self.mario_mode else 3)
        self.start_animation.vars.append(False)

        self.name_animation = GameAnimation()
        self.name_animation.max_duration = 50
        self.name_animation.vars.append(False)

        self.spacebase_animation = GameAnimation()
        self.spacebase_animation.max_duration = 600
        self.spacebase_animation.vars.append(True)

        self.circles_animation = GameAnimation()
        self.circles_animation.max_duration = 100
        self.circles_animation.vars.append(True)

        self.score_animation = GameAnimation()
        self.score_animation.max_duration = 4
        self.score_animation.vars.append(False)
        self.score_animation.vars.append(25)
        self.score_animation.vars.append(30)
        self.score_animation.vars.append(25)

        self.x = (WIDTH - 150)/2
        self.y = (HEIGHT - 240)

        self.move_x = 0
        self.move_back_x = 0
        self.move_back_x2 = 0

        self.tilesize = 40
        self.margin = 150
        self.player_size = 80
        self.player_margin = 10

        self.rnd_box = []
        self.rnd_box_max = 0
        self.move_x_val = 0
        self.game_time = time.time()

        self.tree = Tree()
        self.coins = [Coin(WIDTH*2), Coin(WIDTH)]
        
        self.show_circles = True
        self.sound_active = True

        self.circles_id = 0
        self.circles: list[CircleTouch] = []
        self.circle_song = mixer.Sound("./music/circle.wav")

        self.circle_btn= MenuSwitchButton(
                (10,10),
                (image.load("./assets/btn_2.png"),image.load("./assets/btn_3.png")),
                [30,30],
                True)
        self.sound_btn = MenuSwitchButton(
                (WIDTH- 40,10),
                (image.load("./assets/btn_0.png"),
                 image.load("./assets/btn_1.png")),
                [30,30],
                True)

        mouse.set_visible(0)

        self.load_dino(image.load(
            "./assets/DinoSprites - {0}.png".format(self.dino_types[self.dino_index])))
        self.load_tiles(image.load("./assets/Tileset.png"))

        self.play_intro_sound()
        self.select_sound = mixer.Sound("./music/select.mp3")
        self.s_coin = mixer.Sound("./music/coin.mp3")

#
# Animation update
#
    def bool_int_animation_add(self, gameaniamtion: GameAnimation):
        gameaniamtion.vars[1] += 1
        if gameaniamtion.vars[1] >= gameaniamtion.vars[2]:
            gameaniamtion.vars[0] = not gameaniamtion.vars[0]
            gameaniamtion.vars[1] = gameaniamtion.vars[3]
        return True

    def bool_animation_end(self, gameaniamtion: GameAnimation):
        gameaniamtion.vars[0] = not gameaniamtion.vars[0]
        return True

    def start_animation_min(self, gameaniamtion: GameAnimation):
        gameaniamtion.vars[0] -= 1
        if gameaniamtion.vars[0] < 0:
            gameaniamtion.vars[1] = not gameaniamtion.vars[1]
            self.start_game_play()
        return True

    def int_animation_add(self, gameaniamtion: GameAnimation):
        gameaniamtion.vars[0] += 1
        if gameaniamtion.vars[0] >= gameaniamtion.vars[1]:
            gameaniamtion.vars[0] = gameaniamtion.vars[2]

        return True


#
# Load sprites
#


    def load_tiles(self, image: pygame.Surface):
        for x in range(8):
            for y in range(6):
                tmp = pygame.Surface((16, 16))
                tmp = tmp.convert_alpha(tmp)
                tmp.fill((0, 0, 0, 0))
                tmp.blit(image, (0, 0), (x * 16, y * 16, 16, 16))

                if tmp.get_at((8, 8)) != (0, 0, 0, 255):
                    self.tile_textures.append(tmp)

    def load_dino(self, image: pygame.Surface):
        self.player_textures.clear()

        for x in range(24):
            tmp = pygame.Surface((24, 24))
            tmp = tmp.convert_alpha(tmp)
            tmp.fill((0, 0, 0, 0))
            tmp.blit(image, (0, 0), (x * 24, 0, 24, 24))

            self.player_textures.append(tmp)

        pygame.display.set_icon(self.player_textures[0])


#
# Play Sound Effects
#
    def switch_sound(self):
        mixer.Sound("./music/song_active.mp3").play()
    
    def start_walk_songs(self):
        if self.sound_active:
            walk1 = mixer.Sound("./music/walk1.wav")
            walk1.set_volume(0.2)

            walk2 = mixer.Sound("./music/walk2.wav")
            walk2.set_volume(0.2)

            for i in range(3):
                walk = mixer.Sound("./music/walk{0}.wav".format(i+1))
                if walk == 2:
                    walk.set_volume(0.3)
                else:
                    walk.set_volume(0.2)

                mixer.Channel(4+i).play(walk, -1)

    def play_intro_sound(self):
        if self.sound_active:
            s_intro = mixer.Sound("./music/intro.wav")
            mixer.Channel(2).play(s_intro)

    def play_coin_song(self):
        if self.sound_active:
            self.s_coin.set_volume(0.3)
            mixer.Channel(1).play(self.s_coin)

    def set_mario_mode(self):
        self.mario_mode = True
        self.start_animation.vars[0] = 3
        coin = mixer.Sound("./music/coin.mp3")
        coin.set_volume(0.5)
        if self.sound_active:
            coin.play()


#
# Game start event
#


    def start_game_counter(self):
        self.start = True
        self.start_animation.vars[1] = True
        # mixer.music.load("./music/walk1.wav")
        # mixer.music.set_volume(0.5)
        # mixer.music.play(-1)

        for i in range(6):
            self.rnd_box.append([
                int(random.randint(1, (WIDTH//self.tilesize))),
                int(random.randint(0, (self.margin//self.tilesize)))
            ])
            self.rnd_box_max = max(self.rnd_box_max, self.rnd_box[-1][0])

        self.change_state(DinoStates.RUN, DinoStates.RUN_BASE)
        if self.sound_active:
            if self.mario_mode:
                mario_start = mixer.Sound("./music/start.wav")
                mario_start.set_volume(0.5)
                mixer.Channel(3).play(mario_start)
            else:
                mixer.Channel(3).play(mixer.Sound("./music/go.mp3"))

        gameDinoEvent.emit("game.inputsave")

    def start_game_play(self):
        mouse.set_visible(1)
        mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

        self.start_walk_songs()


#
# Update Game
#


    def update(self, delta: float, input: GameInput):
        if not self.init_animation.vars[0]:
            self.menu_selection_update(delta, input)

            if self.start:

                if input.ispress(pygame.K_DOWN):
                    if self.state != DinoStates.CROUCH:
                        self.change_state(DinoStates.CROUCH,
                                          DinoStates.CROUCH_BASE)
                elif self.state == DinoStates.CROUCH:
                    self.change_state(DinoStates.RUN, DinoStates.RUN_BASE)

            self.update_player(delta, input)

        if self.spacebase_animation.vars[0]:
            self.spacebase_animation.update(
                delta, self.bool_animation_end)

        if self.name_animation.vars[0]:
            self.name_animation.update(delta, self.bool_animation_end)

        if self.init_animation.vars[0]:
            self.init_animation.update(delta, self.bool_animation_end)

        # print("\r UPS: {0}".format(
        #     int(1/(delta if delta != 0 else 1))), end='')

    def update_icon(self, delta: float):
        if self.icon_animation.update(delta, self.int_animation_add):
            pygame.display.set_icon(
                self.player_textures[self.icon_animation.vars[0]])

    def update_player(self, delta: float, input: GameInput):
        if self.start:
            self.update_icon(delta)
            if not self.start_animation.vars[1]:

                self.tree.update(delta, self)
                for c in self.coins:
                    c.update(delta, self)

                if self.show_circles:
                    for c in self.circles:
                        c.update(delta, input)

                self.game_time += delta * 10
                if self.game_time >= 80:
                    self.score += 1
                    self.game_time = 0
                    self.game_speed += 50

                self.move_x_val = self.game_speed * (delta/10)
                self.move_x -= self.move_x_val

                self.move_back_x -= self.game_speed * (1/2) * (delta/10)
                self.move_back_x2 -= self.game_speed * (3/4) * (delta/10)

                if self.move_back_x <= -WIDTH:
                    self.move_back_x = 0
                if self.move_back_x2 <= -WIDTH:
                    self.move_back_x2 = 0
                if self.move_x <= -WIDTH:
                    self.move_x = 0

                self.player_animation.update(delta, self.int_animation_add)
                self.circles_animation.update(delta, self.bool_animation_end)

                if self.score_animation.vars[0]:
                    self.score_animation.update(
                        delta, self.bool_int_animation_add)

                if self.show_circles:
                    if len(self.circles) != 0:
                        circ_index = 0
                        while True:
                            if self.circles[circ_index].delete:
                                if self.circles[circ_index].point:
                                    self.score += 10

                                    if self.circles[circ_index].circle_id == self.circles_id:
                                        self.score += 10

                                    self.score_animation.vars[0] = True
                                del self.circles[circ_index]
                                circ_index -= 1

                            circ_index += 1
                            if circ_index >= len(self.circles):
                                break

                    if self.circles_animation.vars[0]:
                        self.circles_animation.vars[0] = False

                        if self.circles_id >= 100:
                            self.circles.clear()
                            self.circles_id = 0
                            if self.sound_active:
                                xp = mixer.Sound("./music/xp.wav")
                                xp.set_volume(0.4)
                                mixer.Channel(2).play(xp)
                        else:
                            if len(self.circles) < 3:
                                positions = []
                                for c in self.circles:
                                    positions.append([c.x,c.y,True])

                                def generate_position(pos):
                                    margin_w = 100
                                    margin_h = 100
                                    res = [random.randint(margin_w, WIDTH),
                                        random.randint(margin_h, HEIGHT), False]
                                    if len(pos) == 0:
                                        return res
                                    valid = False
                                    while not valid:
                                        for p in pos:
                                            dx = p[0] - res[0]
                                            dy = p[1] - res[1]
                                            distance = sqrt(dx * dx + dy * dy)
                                            
                                            if distance < CircleTouch.base_radius*2:
                                                res = [random.randint(margin_w, WIDTH),
                                                    random.randint(margin_h, HEIGHT), False]
                                            else:
                                                valid = True
                                    return res

                                for k in range(3 - len(self.circles)):
                                    positions.append(generate_position(positions))

                                for position in positions:
                                    if not position[2]:
                                        self.circles_id += 1
                                        self.circles.append(CircleTouch(
                                            self.circles_id, position, self.circle_song if self.sound_active else None))
                i = 0
                for c in self.coins:
                    if self.x >= c.x+50:
                        del self.coins[i]
                        self.coin += 1
                        self.play_coin_song()
                        i -= 1
                    i += 1

                if len(self.coins) != 2:
                    for k in range(2 - len(self.coins)):
                        self.coins.append(
                            Coin(random.randint(0, (WIDTH*3) + (self.game_speed * 2))))
            else:
                self.start_animation.update(delta, self.start_animation_min)
        else:
            self.player_animation.update(delta, self.int_animation_add)

    def menu_selection_update(self, delta: float, input: GameInput):
        if not self.start:
            diff = self.circle_btn.button_active
            self.circle_btn.update(delta,input)
            if diff != self.circle_btn.button_active:
                self.show_circles = self.circle_btn.button_active
                if self.sound_active:
                    self.switch_sound()

            diff = self.sound_btn.button_active
            self.sound_btn.update(delta,input)
            if diff != self.sound_btn.button_active:
                self.sound_active = self.sound_btn.button_active
                self.switch_sound()

            if self.sound_btn.in_surface(mouse.get_pos(), self.sound_btn.size[0]*3) or self.circle_btn.in_surface(mouse.get_pos(), self.circle_btn.size[0]*3):
                mouse.set_visible(1)
                mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                mouse.set_visible(0)

            if input.ispress(pygame.K_m):
                self.set_mario_mode()
            if input.ispress(pygame.K_SPACE):
                self.start_game_counter()
            if input.ispress(pygame.K_LEFT):
                self.name_animation.vars[0] = True
                self.name_animation.time = 0

                self.dino_index -= 1
                if self.dino_index < 0:
                    self.dino_index = len(self.dino_types)-1
                if self.sound_active:
                    self.select_sound.play()
                self.load_dino(image.load(
                    "./assets/DinoSprites - {0}.png".format(self.dino_types[self.dino_index])))

            if input.ispress(pygame.K_RIGHT):

                self.name_animation.vars[0] = True
                self.name_animation.time = 0

                self.dino_index += 1
                if self.dino_index >= len(self.dino_types):
                    self.dino_index = 0
                if self.sound_active:
                    self.select_sound.play()
                self.load_dino(image.load(
                    "./assets/DinoSprites - {0}.png".format(self.dino_types[self.dino_index])))
            if input.ismove():
                self.spacebase_animation.vars[0] = True
                self.spacebase_animation.time = 0

    def change_state(self, state: DinoStates, base: DinoStates):
        self.state = state
        self.state_base = base

        self.player_animation.vars[0] = self.state_base
        self.player_animation.vars[1] = self.state
        self.player_animation.vars[2] = self.state_base


#
# Draw Game
#


    def draw_menu(self, renderer: pygame.Surface):
        self.texture(renderer, self.player_textures[self.player_animation.vars[0]], [
            self.x, self.y], [100, 100])

        for x in range((WIDTH+100) // 70):
            self.texture(renderer, self.tile_textures[TileIndex.GRASS], [
                x * 70, HEIGHT - 150], [70, 70])
            self.texture(renderer, self.tile_textures[TileIndex.GROUND_TEXTURED], [
                x * 70, HEIGHT - 80], [70, 70])
            self.texture(renderer, self.tile_textures[TileIndex.GROUND_TEXTURED], [
                x * 70, HEIGHT - 10], [70, 70])

        if self.spacebase_animation.vars[0]:
            self.text(renderer, "Press [SPACE] to start the game", [
                200, 70], 25, (30, 30, 30), True)

        self.text(renderer, "<", [
                  100, 200], 40, (30, 30, 30), True)
        self.text(renderer, ">", [
            250, 200], 40, (30, 30, 30), True)

        self.circle_btn.draw(renderer)
        self.sound_btn.draw(renderer)

        if self.name_animation.vars[0]:
            self.text(renderer, self.dino_types[self.dino_index].capitalize(), [
                170, 150], 25, (30, 30, 30), True)

    def draw_game(self, renderer: pygame.Surface, delta: float):
        for x in range((WIDTH//self.tilesize)*2):
            self.texture(renderer, self.tile_textures[TileIndex.GRASS], [
                x * self.tilesize + self.move_x, HEIGHT - self.margin], [self.tilesize, self.tilesize])

            for y in range((self.margin//self.tilesize)+1):
                self.texture(renderer, self.tile_textures[TileIndex.GROUND_TEXTURED], [
                    x * self.tilesize + self.move_x, HEIGHT - (y * self.tilesize)], [self.tilesize, self.tilesize])

        for i in self.rnd_box:
            self.texture(renderer,
                         self.tile_textures[TileIndex.GROUND_TEXTURED_2],
                         [i[0] * self.tilesize + self.move_x,
                          HEIGHT - (i[1] * self.tilesize)],
                         [self.tilesize, self.tilesize])

            self.texture(renderer,
                         self.tile_textures[TileIndex.GROUND_TEXTURED_2],
                         [(i[0] + (WIDTH//self.tilesize)) * self.tilesize +
                          self.move_x, HEIGHT - (i[1] * self.tilesize)],
                         [self.tilesize, self.tilesize])

        self.tree.draw(delta, renderer)
        for c in self.coins:
            c.draw(delta, renderer)

        self.texture(renderer, self.player_textures[self.player_animation.vars[0]], [
                     30, HEIGHT - (self.margin + self.player_size-self.player_margin)], [self.player_size, self.player_size])
        if self.show_circles:
            for c in self.circles:
                c.draw(delta, renderer,self.circles_id)

    def draw(self, delta: float, renderer: pygame.Surface):
        if self.init_animation.vars[0]:
            color_value = (self.init_animation.time * 255 /
                           self.init_animation.max_duration)
            renderer.fill((color_value, color_value, color_value))
            self.text(renderer, "Dino", [
                200, 200], 150, (255, 255, 255))
        else:
            self.texture(renderer, self.backgrounds[0], [0, 0], [400, 400])

            if self.start:
                if not self.start_animation.vars[1]:
                    self.texture(renderer, self.backgrounds[1], [
                        0 + self.move_back_x, 0], [400, 400])
                    self.texture(renderer, self.backgrounds[1], [
                        WIDTH + self.move_back_x, 0], [400, 400])

                    self.texture(renderer, self.backgrounds[2], [
                        WIDTH + self.move_back_x2, 0], [400, 400])
                    self.texture(renderer, self.backgrounds[2], [
                        0 + self.move_back_x2, 0], [400, 400])


                    self.text(renderer, "Score {0}".format(self.score), [
                        10, 10], self.score_animation.vars[1], (30, 30, 30), False)

                    self.text(renderer, "Coin {0}".format(self.coin), [
                        10, 40], 20, (30, 30, 30), False)

                    self.draw_game(renderer, delta)
                else:
                    self.texture(renderer, self.backgrounds[1], [
                        0, 0], [400, 400])
                    self.texture(renderer, self.backgrounds[2], [
                        0, 0], [400, 400])

                    text_value = str(self.start_animation.vars[0])
                    if self.start_animation.vars[0] == 0:
                        text_value = "GO"
                    elif self.start_animation.vars[0] == 4:
                        text_value = "READY"
                    self.text(renderer, text_value, [
                        200, 200], 90, (30, 30, 30))
            else:
                self.texture(renderer, self.backgrounds[1], [
                    0, 0], [400, 400])
                self.texture(renderer, self.backgrounds[2], [
                    0, 0], [400, 400])

                self.draw_menu(renderer)


class MenuSwitchButton(GameItem):

    def __init__(self,position: Tuple[int, int],states:Tuple[pygame.Surface,pygame.Surface],size:list[int]=[50,50],active:bool = False,key = None):
        GameItem.__init__(self)
        self.button_active = active
        
        self.x = position[0]
        self.y = position[1]
        self.size = size
        
        self.key_action = None
        if key != None:
            self.key_action = key
            

        self.sprites.append(states[0])
        self.sprites.append(states[1])

    def draw(self, renderer: pygame.Surface):
        if self.button_active:
            self.texture(renderer,self.sprites[0],[self.x,self.y],self.size)
        else:
            self.texture(renderer,self.sprites[1],[self.x,self.y],self.size)



    def update(self, delta: float, input: GameInput):

        if input.isclicked() and self.in_surface(mouse.get_pos(),self.size[0]):
            self.button_active = not self.button_active

        if self.key_action != None:
            if input.ispress(self.key_action):
                self.button_active = not self.button_active

    def in_surface(self, pos: Tuple[int, int],size:int) -> bool:
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        distance = sqrt(dx * dx + dy * dy)

        if distance < size:
            return True
        return False

class CircleTouch(GameItem):
    base_radius = 60 # 80
    click_radius = 20 # 30
    text_size = 20 # 40

    def __init__(self, circle_id=1, position=[0, 0],song = None):
        GameItem.__init__(self)

        self.circle_id = circle_id
        self.x = position[0]
        self.y = position[1]

        self.sound = None
        if song != None:
            self.sound:mixer.Sound = song
            self.sound.set_volume(0.3)

        self.radius = self.base_radius
        self.time = random.randint(0,30)
        self.end_time = random.randint(40, 80) + self.time
        self.delete = False
        self.point = False

    def circle_rgba(self, renderer: pygame.Surface, color: Tuple[int, int, int, int], center: Tuple[int, int], radius: int, width: int):
        target = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
        circle = pygame.Surface(target.size, pygame.SRCALPHA)

        draw.circle(circle, color, (radius, radius), radius, width)
        renderer.blit(circle, target)

    def draw(self, delta: float, renderer: pygame.Surface,current_id: int):
        if not self.delete:
            self.circle_rgba(renderer, (40, 40, 40, 150),
                             (self.x, self.y), self.radius+30, 2)

            color = (40, 40, 40, 150)
            if current_id == self.circle_id:
                color = (255, 138, 5, 150)
                if self.in_surface(mouse.get_pos()):
                    color = (255, 180, 5, 150)
            elif self.in_surface(mouse.get_pos()):
                color = (100,100,100,150)

            self.circle_rgba(renderer, color,
                             (self.x, self.y), self.click_radius, 80)

            self.text(renderer, str(self.circle_id), [
                      self.x, self.y], self.text_size, (200, 200, 200))

    def update(self, delta: float, input: GameInput):
        if not self.delete:
            self.time += delta * 10
            self.radius = self.base_radius - ((self.time*self.base_radius)/self.end_time)

            if self.time >= self.end_time:
                self.delete = True
                
            if input.isclicked() and self.in_surface(mouse.get_pos()):
                
                self.delete = True
                self.point = True
                if self.sound != None:
                    mixer.Channel(3).play(self.sound)
                

    def in_surface(self, pos: Tuple[int, int]) -> bool:
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        distance = sqrt(dx * dx + dy * dy)

        if distance < self.click_radius:
            return True
        return False


class Coin(GameItem):
    def __init__(self, x: int):
        GameItem.__init__(self)
        tmp = image.load("./assets/MonedaD.png")

        self.coin_animation = GameAnimation()
        self.coin_animation.max_duration = 10

        self.coin_animation.vars.append(0)
        self.coin_animation.vars.append(5)
        self.coin_animation.vars.append(0)

        self.y = HEIGHT - 190
        self.x = WIDTH + random.randint(x, WIDTH+x)

        for x in range(5):
            sprite = pygame.Surface((16, 16))
            sprite = sprite.convert_alpha(sprite)
            sprite.fill((0, 0, 0, 0))
            sprite.blit(tmp, (0, 0), (x * 16, 0, 16, 16))
            self.sprites.append(sprite)

    def __str__(self):
        return "x={0} y={1} animation_index={2}".format(self.x, self.y, self.coin_animation.vars[0])

    def draw(self, delta: float, renderer: pygame.Surface):
        self.texture(renderer, self.sprites[self.coin_animation.vars[0]], [
                     self.x, self.y], [30, 30])

    def update(self, delta: float, dino: Dino):
        self.x -= dino.game_speed * (delta/10)
        if (self.x + self.sprites[0].get_width()*2) < 0:
            self.x = WIDTH + random.randint(0, dino.game_speed * 1.5)

        self.coin_animation.update(delta, self.int_animation_add)

    def int_animation_add(self, gameaniamtion):
        gameaniamtion.vars[0] += 1
        if gameaniamtion.vars[0] >= gameaniamtion.vars[1]:
            gameaniamtion.vars[0] = gameaniamtion.vars[2]

        return True


class Tree(GameItem):
    def __init__(self):
        GameItem.__init__(self)
        self.sprite = pygame.Surface((112, 112))
        self.sprite = self.sprite.convert_alpha(self.sprite)
        self.sprite.fill((0, 0, 0, 0))

        self.sprite.blit(image.load("./assets/Decors.png"),
                         (0, 0), (0, 0, 112, 112))
        self.x = WIDTH + random.randint(0, 300)
        self.y = HEIGHT - 350

    def draw(self, delta: float, renderer: pygame.Surface):
        self.texture(renderer, self.sprite, [
                     self.x, self.y], [200, 200])

    def update(self, delta: float, dino: Dino):
        self.x -= dino.game_speed * (delta/10)
        if (self.x + self.sprite.get_width()*2) < 0:
            self.x = WIDTH + random.randint(0, 300)


class GameConsole:
    def __init__(self, game: GameMain):
        self.game = game
        self.active = True
        self.livedebug = False

    def run(self):
        threading.Thread(target=self.start).start()

    def getDino(self) -> Dino:
        return self.game.gameItems[0]

    def print_help(self):
        print("Commands List\n")

        print("__System__")
        print("\techo (str...")
        print("\thelp")
        print("\tclear")
        print("\texit")
        print("\tstart")

        print("__Debug__")
        print("\tvar_names")
        print("\tvar_live <name> <duration>")
        print("\tdebug [live]")

        print("__Dino__")
        print("\ttime")
        print("\tmenu_select")
        print("\tcoin")
        print("\tcircle")
        print("\tsound")
        print("\tscore")

        print("__Console__")
        print("\t$ = execute the last input")
        print("\t?$ = get the last input")
        print("\t@ = get input histoiry")
        print("\t?@ = clear input histoiry")
        


    def interaction(self, s: str):
        parts = s.split(" ")
        dino = self.getDino()
        
        if len(parts) >= 1:
            cmd = parts[0]
            if cmd == "echo":
                for p in parts[1:]:
                    print(p, end=' ')
                print("")
            elif cmd == "help":
                self.print_help()
            elif cmd == "clear":
                os.system('cls')
            elif cmd == "sound":
                dino.sound_active = not dino.sound_active
            elif cmd == "circle":
                dino.show_circles = not dino.show_circles
            elif cmd == "exit":
                self.active = False
            elif cmd == "var_names":
                vars = [attr for attr in dir(dino) if not callable(
                        getattr(dino, attr)) and not attr.startswith("__")]

                for var in vars:
                    print(var, type(getattr(dino, var)))
            elif cmd == "start":
                os.system("{0} {1} {2}".format(sys.executable,
                          __file__, " ".join(sys.argv[1:])))
            elif cmd == "var_live" and len(parts) >= 3:
                self.live_duration(parts[1], float(parts[2]))
            elif cmd == "var_get" and len(parts) >= 2:
                name = parts[1]
                try:
                    value = getattr(dino, name)
                    if type(value) is list:
                        print("{0} (len={2}){1}".format(name, "".join(
                            ["\n"+str(item) for item in value]), len(value)))
                    else:
                        print("{0} = {1}".format(name, value))
                except:
                    print("\"{0}\" not found".format(name))
            elif cmd == "menu_select":
                print(dino.dino_types[dino.dino_index])
            elif cmd == "time":
                print("{0}s".format(time.time() - dino.game_time))
            elif cmd == "coin":
                print("Coins: {0}".format(dino.coin))
            elif cmd == "score":
                print("Score: {0}".format(dino.score))
            elif cmd == "debug":
                if len(parts) >= 2 and parts[1] == "live":
                    self.livedebug = True
                else:
                    vars = [attr for attr in dir(dino) if not callable(
                        getattr(dino, attr)) and not attr.startswith("__")]

                    for var in vars:
                        value = getattr(dino, var)
                        t = type(value)
                        if t == int or t == str or t == float or t == bool:
                            print("{0} = {1}".format(var, value))

    def live_duration(self, name: str, s_duration: float):
        dino = self.getDino()
        start = time.time()
        while True:
            if time.time() - start > s_duration:
                break

            os.system("cls")
            try:
                value = getattr(dino, name)
                if type(value) is list:
                    print("{0} (len={2}){1}".format(name, "".join(
                        ["\n"+str(item) for item in value]), len(value)))
                else:
                    print("{0} = {1}".format(name, value))
            except:
                print("\"{0}\" not found".format(name))
                break
            time.sleep(0.1)

    def live(self):
        dino = self.getDino()
        vars = [attr for attr in dir(dino) if not callable(
            getattr(dino, attr)) and not attr.startswith("__")]

        valid = []
        for var in vars:
            t = type(getattr(dino, var))
            if t == int or t == str or t == float or t == bool:
                valid.append(var)

        while self.active and self.game.active:
            os.system('cls')
            # sys.stdout.write("\r")
            for var in valid:
                sys.stdout.write("{0}={1}\n".format(var, getattr(dino, var)))
            sys.stdout.write("\n")
            sys.stdout.flush()

            time.sleep(0.01)

    def start(self):
        save_input = [""]
        actions = ["@","?@","$","?$"]
        
        while self.active and self.game.active:
            if self.livedebug:
                self.live()
            else:
                user_input = str(input(">"))
                if user_input in actions:
                    if user_input == "@":
                        for inp in save_input:
                            print(inp)
                    elif user_input == "?@":
                        save_input.clear()
                        save_input.append("")
                    elif user_input == "$":
                        self.interaction(save_input[-1])
                    elif user_input == "?$":
                        print(save_input[-1])
                else:
                    save_input.append(user_input)
                    self.interaction(save_input[-1])


def main(args: list[str]):
    game = GameMain(size=[WIDTH, HEIGHT], title="Dino Game")
    console = GameConsole(game)

    os.system('cls')

    game.input.save = False

    @gameDinoEvent.on("game.inputsave")
    def onsave():
        game.input.save = not game.input.save

    game.add_item(Dino(args))

    console.run()
    game.run(False)
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
