from utils.engine import *
import sys
import os
import random
import pygame
from pygame import draw, display, image, event, mixer, font, mouse

WIDTH = 400
HEIGHT = 400


class DinoStates:
    IDLE_BASE = 0
    IDLE = 3
    RUN_BASE = 3
    RUN = 13
    HIT_BASE = 13
    HIT = 17
    CROUCH_BASE = 17
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
    def __init__(self, args):
        GameItem.__init__(self)

        self.dino_types = ["doux", "mort", "tard", "vita"]
        self.dino_index = 0

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

        self.texture_index = 0
        self.texture_time = 0

        self.player_textures = []
        self.tile_textures = []

        self.score = 0
        self.coin = 0
        self.state = DinoStates.IDLE

        self.start = False

        self.icon_animation = GameAnimation()
        self.icon_animation.max_duration = 10
        self.icon_animation.vars.append(DinoStates.RUN_BASE)
        self.icon_animation.vars.append(DinoStates.RUN)
        self.icon_animation.vars.append(DinoStates.RUN_BASE)

        self.start_animation = GameAnimation()
        self.start_animation.max_duration = 50
        self.start_animation.vars.append(4)
        self.start_animation.vars.append(False)

        self.name_animation = GameAnimation()
        self.name_animation.max_duration = 50
        self.name_animation.vars.append(False)

        self.spacebase_animation = GameAnimation()
        self.spacebase_animation.max_duration = 600
        self.spacebase_animation.vars.append(True)

        self.x = (WIDTH - 150)/2
        self.y = (HEIGHT - 240)

        mouse.set_visible(0)

        self.load_dino(image.load(
            "./assets/DinoSprites - {0}.png".format(self.dino_types[self.dino_index])))
        self.load_tiles(image.load("./assets/Tileset.png"))

    def bool_animation_end(self, gameaniamtion):
        gameaniamtion.vars[0] = not gameaniamtion.vars[0]
        return True

    def int_animation_min(self, gameaniamtion):
        gameaniamtion.vars[0] -= 1
        if gameaniamtion.vars[0] < 0:
            gameaniamtion.vars[1] = not gameaniamtion.vars[1]
        return True

    def int_animation_add(self, gameaniamtion):
        gameaniamtion.vars[0] += 1
        if gameaniamtion.vars[0] >= gameaniamtion.vars[1]:
            gameaniamtion.vars[0] = gameaniamtion.vars[2]

        return True

    def load_tiles(self, image):
        for x in range(8):
            for y in range(6):
                tmp = pygame.Surface((16, 16))
                tmp = tmp.convert_alpha(tmp)
                tmp.blit(image, (0, 0), (x * 16, y * 16, 16, 16))

                if tmp.get_at((8, 8)) != (0, 0, 0, 255):
                    self.tile_textures.append(tmp)

    def load_dino(self, image):
        self.player_textures.clear()

        for x in range(24):
            tmp = pygame.Surface((24, 24))
            tmp = tmp.convert_alpha(tmp)
            tmp.blit(image, (0, 0), (x * 24, 0, 24, 24))

            for x in range(24):
                for y in range(24):
                    if tmp.get_at((x, y)) == (0, 0, 0, 255):
                        tmp.set_at((x, y), (0, 0, 0, 0))

            self.player_textures.append(tmp)

        pygame.display.set_icon(self.player_textures[0])

    def update(self, delta, input):
        if input.ismove():
            if not self.start:
                self.spacebase_animation.vars[0] = True
                self.spacebase_animation.time = 0

        if input.ispress(pygame.K_DOWN):
            if self.start:
                print("down")

        if input.ispress(pygame.K_SPACE):
            if not self.start:
                self.start = True
                self.start_animation.vars[1] = True
            else:
                pass
        
        if input.ispress(pygame.K_LEFT):
            if not self.start:
                self.name_animation.vars[0] = True
                self.name_animation.time = 0

                self.dino_index -= 1
                if self.dino_index < 0:
                    self.dino_index = len(self.dino_types)-1

                self.load_dino(image.load(
                            "./assets/DinoSprites - {0}.png".format(self.dino_types[self.dino_index])))

        if input.ispress(pygame.K_RIGHT):
            if not self.start:
                self.name_animation.vars[0] = True
                self.name_animation.time = 0

                self.dino_index += 1
                if self.dino_index >= len(self.dino_types):
                    self.dino_index = 0

                self.load_dino(image.load(
                    "./assets/DinoSprites - {0}.png".format(self.dino_types[self.dino_index])))

        self.update_player(delta)

        if self.spacebase_animation.vars[0]:
            self.spacebase_animation.update(
                delta, self.bool_animation_end)

        if self.name_animation.vars[0]:
            self.name_animation.update(delta, self.bool_animation_end)

        # print("\r UPS: {0}".format(
        #     int(1/(delta if delta != 0 else 1))), end='')

    def update_icon(self, delta):
        if self.icon_animation.update(delta, self.int_animation_add):
            pygame.display.set_icon(
                self.player_textures[self.icon_animation.vars[0]])
        # self.icon_time += delta * 100
        # if self.icon_time >= 10:
        #     self.icon_time = 0
        #     self.icon_index += 1

        #     if self.icon_index >= DinoStates.RUN:
        #         self.icon_index = DinoStates.RUN_BASE

    def update_player(self, delta):
        if self.start:
            self.update_icon(delta)

            if not self.start_animation.vars[1]:
                self.score += int(delta*100)
                speed = 150 * (delta/10)
            else:
                self.start_animation.update(delta, self.int_animation_min)
        else:
            self.texture_time += delta * 100
            if self.texture_time >= 10:
                self.texture_time = 0
                self.texture_index += 1

                if self.texture_index >= DinoStates.IDLE:
                    self.texture_index = DinoStates.IDLE_BASE

    def draw_menu(self, renderer):
        self.texture(renderer, self.player_textures[self.texture_index], [
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
                200, 50], 25, (30, 30, 30), True)

        self.text(renderer, "<", [
                  100, 200], 40, (30, 30, 30), True)
        self.text(renderer, ">", [
            250, 200], 40, (30, 30, 30), True)

        if self.name_animation.vars[0]:
            self.text(renderer, self.dino_types[self.dino_index].capitalize(), [
                170, 150], 25, (30, 30, 30), True)

    def draw(self, delta, renderer):
        self.texture(renderer, self.backgrounds[0], [0, 0], [400, 400])
        self.texture(renderer, self.backgrounds[1], [0, 0], [400, 400])
        self.texture(renderer, self.backgrounds[2], [0, 0], [400, 400])

        if self.start:
            if not self.start_animation.vars[1]:
                self.text(renderer, "Score {0}".format(self.score), [
                    10, 10], 25, (30, 30, 30), False)
                self.text(renderer, "Coin {0}".format(self.coin), [
                    10, 40], 20, (30, 30, 30), False)

            else:
                text_value = str(self.start_animation.vars[0])
                if self.start_animation.vars[0] == 0:
                    text_value = "GO"
                elif self.start_animation.vars[0] == 4:
                    text_value = "READY"
                self.text(renderer, text_value, [
                          200, 200], 90, (30, 30, 30))
        else:
            self.draw_menu(renderer)


class DinoController(GameController):
    def __init__(self):
        GameController.__init__(self)

    def update(self, delta, items):
        tmp = items.copy()
        return tmp


def main(args):
    game = GameMain(size=[WIDTH, HEIGHT], title="Dino Game")
    os.system('cls')

    game.input.save = False
    game.add_item(Dino(args))
    game.add_controller(DinoController())

    game.run(False)
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
