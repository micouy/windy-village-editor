from __future__ import division
import Tkinter as tk
from Tkinter import *
from threading import Timer
import json
import pygame
from pygame import *
import random
import math
import os


##### EDITOR COMPONENTS #####


class FramesManager(object):
    def __init__(self, control, width, height):
        self.control = control
        self.root = tk.Tk()
        self.root.minsize(width = width + 200, height = height)
        self.frame = Frame(self.root)
        self.frame.grid_columnconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(1, weight = 1)
        self.frame.pack()
        self.rightDoc = RightDoc(self)
        self.gameFrame = GameFrame(self, width, height)

    def update(self):
        self.root.update()


class WidgetManager(object):
    def __init__(self, parent, row, column):
        self.parent = parent
        self.control = parent.control
        self.root = parent.root
        self.frame = Frame(self.parent.frame)
        self.frame.grid(row = row, column = column)


class RightDoc(WidgetManager):
    def __init__(self, parent):
        self.parent = parent
        self.control = parent.control
        self.root = parent.root
        self.frame = Frame(self.parent.frame)
        self.frame.grid(row = 0, column = 1, ipadx = 10, ipady = 10, sticky = N)
        self.controlMenu = ControlMenu(self)
        self.addBlockDoc = AddBlockMenu(self)


class GameFrame(WidgetManager):
    def __init__(self, parent, width, height):
        super(GameFrame, self).__init__(parent, 0, 0)
        self.frame = Frame(self.parent.frame, width = width, height = height)
        self.frame.grid(column = 0, row = 0)
        os.environ['SDL_WINDOWID'] = str(self.frame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'

class ControlMenu(WidgetManager):
    def __init__(self, parent):
        super(ControlMenu, self).__init__(parent, 0, 0)
        self.mode = 'play'
        self.frame.grid_columnconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(1, weight = 1)
        self.mode_button = Button( self.frame, text = 'Play', command = lambda: self.changeMode())
        self.mode_button.grid(row = 0, column = 0, sticky = W + E)

    def changeMode(self):
        if self.mode == 'preview':
            mode = 'preview'
            self.mode = 'play'
            self.mode_button['text'] = 'Play'
        elif self.mode == 'play':
            mode = 'play'
            self.mode = 'preview'
            self.mode_button['text'] = 'Preview'
        self.control.changeMode(mode)


class AddBlockMenu(WidgetManager):
    def __init__(self, parent):
        super(AddBlockMenu, self).__init__(parent, 1, 0)
        self.x_entry = LabelEntry(self.frame, 'x: ', 0, 0)
        self.y_entry = LabelEntry(self.frame, 'y: ', 1, 0)
        self.z_entry = LabelEntry(self.frame, 'z: ', 2, 0)
        self.width_entry = LabelEntry(self.frame, 'width: ', 3, 0)
        self.height_entry = LabelEntry(self.frame, 'height: ', 4, 0)
        self.depth_entry = LabelEntry(self.frame, 'depth: ', 5, 0)

        self.addBlock_button = Button(self.frame, text = 'Add block', command = lambda: self.addBlock())
        self.addBlock_button.grid(row = 6, columnspan = 2, pady = 2)

        self.response_label = Label(self.frame, text = '')
        self.response_label.grid(row = 7, columnspan = 2, sticky = W, pady = 2)

    def addBlock(self):
        x = self.x_entry.get()
        y = self.y_entry.get()
        z = self.z_entry.get()
        width = self.width_entry.get()
        height = self.height_entry.get()
        depth = self.depth_entry.get()

        if x.isdigit() and y.isdigit() and width.isdigit() and int(width) > 0 and height.isdigit() and int(height) > 0:
            self.control.addBlock(int(x), int(y), int(width), int(height))
            self.x_entry.delete()
            self.y_entry.delete()
            self.width_entry.delete()
            self.height_entry.delete()
            self.response_label.config(text = 'Block added')
        else:
            self.response_label.config(text = 'Enter correct values')


class LabelEntry(object):
    def __init__(self, parent, text, row, column, width = 10):
        self.label = Label(parent, text = text)
        self.label.grid(row = row, column = column, sticky = W, pady = 2)
        self.entry = Entry(parent, width = width)
        self.entry.grid(row = row, column = column + 1, pady = 2)

    def get(self):
        return self.entry.get()

    def delete(self):
        self.entry.delete(0, 'end')

##### EDITOR #####


class Control(object):
    def __init__(self, width, height):
        self.mode = 'preview'
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.frames = FramesManager(self, width, height)

        self.game = Game(self, width, height)
        self.current = self.game.current
        self.sprites = self.current.sprites
        self.done = False

    def changeMode(self, mode):
        self.mode = mode
        self.game.changeMode(mode)

    def run(self):
        while not self.done:
            self.frames.update()
            self.game.update()

##### GAME #####


class Rectangle(object):
    def __init__(self, x = 0, y = 0, width = 0, height = 0):
        self.x = x
        self.y = y
        self.width = abs(width)
        self.height = abs(height)


class Vector2d(object):
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y


class Vector(object):
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z

    def add(self, a):
        self.x += a.x
        self.y += a.y
        self.z += a.z

    def mult(self, a):
        if a.isidgit():
            self.x *=  a
            self.y *=  a
            self.z *=  a
        else:
            self.x *=  a.x
            self.y *=  a.y
            self.z *=  a.z


class Mouse(object):
    def __init__(self, game):
        self.lastPressed = 0
        self.game = game
        self.debug = game.debug
        self.screen = game.screen
        self.camera = game.camera
        self.clock = game.clock
        self.x, self.y = mouse.get_pos()
        self.delta = Vector2d()
        self.pressed_pos = Vector2d()
        self.selection = Rectangle()
        self.selected = []
        self.dragging = False
        self.moved = False
        self.shift = False
        self.alt = False
        self.up = True
        self.down = False
        self.released = False
        self.pressed = False
        self.info = {'isDown': False, 'isUp': True}

    def initialise(self):
        self.current = self.game.current
        self.sprites = self.current.sprites

    def select(self, sprite):
        sprite.selected = True
        if not sprite in self.selected:
            self.selected.append(sprite)

    def deselect(self, sprite = None):
        if not sprite:
            for sprite in self.selected:
                sprite.selected = False
            self.selected = []
        else:
            sprite.selected = False
            self.selected.remove(sprite)

    def preview(self):
        self.shift = False
        self.alt = False
        self.ctrl = False
        self.pressed = False
        self.released = False

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                self.info['isDown'] = True
                self.info['isUp'] = False
            elif event.type == MOUSEBUTTONUP:
                self.info['isDown'] = False
                self.info['isUp'] = True

        if key.get_mods() & KMOD_SHIFT:
            self.shift = True
        if key.get_mods() & KMOD_ALT:
            self.alt = True
        if key.get_mods() & KMOD_CTRL:
            self.ctrl = True

        self.delta.x, self.delta.y = mouse.get_pos()
        self.delta.x -= self.x
        self.delta.y -= self.y
        self.x, self.y = mouse.get_pos()

        k = pygame.key.get_pressed()
        if not k[K_SPACE]:
            if self.up:
                if self.info['isDown']:
                    self.up = False
                    self.down = True
                    self.pressed = True

            if self.down:
                if self.info['isUp']:
                    self.down = False
                    self.up = True
                    self.released = True

            if self.released:
                self.pressed_pos.x = self.pressed_pos.y = None

            if self.up:
                self.dragging = False

            if self.down:
                if self.x != self.pressed_pos.x or self.y != self.pressed_pos.y:
                    self.moved = True

            if self.pressed:
                clickedSelected = False
                self.pressed_pos.x, self.pressed_pos.y = self.x, self.y
                self.moved = False
                self.dragging = False
                toSelect = []

                for sprite in self.sprites:
                    if (sprite.x - self.camera.x < self.x
                        and sprite.x + sprite.width - self.camera.x > self.x
                        and sprite.z - sprite.y - sprite.height - self.camera.y < self.y
                        and sprite.z - sprite.y + sprite.depth - self.camera.y > self.y):
                        if not sprite in toSelect:
                            toSelect.append(sprite)

                if len(toSelect) > 0:
                    self.dragging = True
                    toSelect.sort(displayingOrder)
                    if toSelect[-1] in self.selected:
                        clickedSelected = True
                    if not self.shift and not clickedSelected:
                        self.deselect()
                        toSelect[-1].selected = True
                        self.select(toSelect[-1])
                    # if self.shift:
                    #     toSelect[-1].selected = True
                    #     self.select(toSelect[-1])
                else:
                    if not self.shift and not clickedSelected:
                        self.deselect()

                    # if self.lastPressed < getTime() < self.lastPressed + 150:
                    #     self.game.addBlock(self.x + self.camera.x, 0, self.y + self.camera.y, 50, 50, 50)
                self.lastPressed = getTime()

            if not self.dragging and self.down:
                if self.pressed_pos.x and self.pressed_pos.y:
                    self.selection.x = min(self.x, self.pressed_pos.x)
                    self.selection.y = min(self.y, self.pressed_pos.y)
                    self.selection.width = abs(self.x - self.pressed_pos.x)
                    self.selection.height = abs(self.y - self.pressed_pos.y)

            if self.released:
                self.selection.x = None
                self.selection.y = None
                self.selection.width = None
                self.selection.height = None

            if self.selection.width > 0 and self.selection.height > 0 and self.selection.x and self.selection.y:
                for sprite in self.sprites:
                    if not (self.selection.x > sprite.x + sprite.width - self.camera.x
                        or self.selection.x + self.selection.width < sprite.x - self.camera.x
                        or self.selection.y > sprite.z + sprite.depth - sprite.y - self.camera.y
                        or self.selection.y + self.selection.height < sprite.z - sprite.y - sprite.height - self.camera.y):
                        self.select(sprite)
                    elif sprite in self.selected and not self.shift:
                        self.deselect(sprite)

            else:
                if len(self.selected) == 1:
                    sprite = self.selected[0]
                    if self.down:
                        self.debug.text('x: %s' % sprite.x, x = self.x + 10 + self.camera.x, y = self.y + self.camera.y)
                        self.debug.text('y: %s' % sprite.y, x = self.x + 10 + self.camera.x, y = self.y + 20 + self.camera.y)
                        self.debug.text('z: %s' % sprite.z, x = self.x + 10 + self.camera.x, y = self.y + 40 + self.camera.y)
        else:
            self.camera.x -= self.delta.x
            self.camera.y -= self.delta.y

    def update(self):
        self.delta.x, self.delta.y = mouse.get_pos()
        self.delta.x -= self.x
        self.delta.y -= self.y
        self.x, self.y = mouse.get_pos()

    def get(self):
        return {'up': self.up, 'down': self.down, 'released': self.released, 'pressed': self.pressed_pos}

    def draw(self):
        if self.selection.width and self.selection.height:
            selectionRectangle = Surface((self.selection.width, self.selection.height))
            selectionRectangle.fill((0, 100, 155))
            selectionRectangle.set_alpha(50)
            self.screen.blit(selectionRectangle, (self.selection.x, self.selection.y))
            pygame.draw.rect(self.screen, (100, 150, 255), (self.selection.x, self.selection.y, self.selection.width, self.selection.height), 1)


class Debug(object):
    def __init__(self, game):
        self.font = pygame.font.SysFont('monospace', 20)
        self.game = game
        self.width = 200
        self.height = 20
        self.x = 50
        self.y = 50
        self.screen = game.screen
        self.toWrite = []
        self.toDraw = []
        self.font.set_bold(True)

    def text(self, *args, **kwargs):
        args = list(args)
        if len(args) == 0:
            return
        x = None
        y = None
        static = False
        if 'x' in kwargs:
            if isinstance(kwargs['x'], (int, float)):
                x = kwargs['x']
        if 'y' in kwargs:
            if isinstance(kwargs['y'], (int, float)):
                y = kwargs['y']

        self.toWrite.append({'text': (', ').join([str(a) for a in args]), 'x': x, 'y': y})

    def point(self, x, y):
        self.toDraw.append({'type': 'point', 'x': x, 'y': y})

    def all(self):
        queue = [text['text'] for text in self.toWrite if text['x'] == None]

        if len(queue) > 0:
            max_len = max([len(str(text)) for text in queue])
            if max_len * 14 > 200:
                self.width = max_len * 14
            self.height = len(queue) * 20 + 24
            bg = Surface((self.width, self.height))
            bg.fill((0, 0, 0))
            bg.set_alpha(100)
            label = self.font.render('debug: ', 1, (255, 255, 255))
            self.screen.blit(bg, (self.x, self.y))
            self.screen.blit(label, (self.x + 2, self.y + 2))

            for index, text in enumerate(queue):
                if isinstance(text, list):
                    label = self.font.render((', ').join([str(w) for w in text]), 1, (255, 255, 255))
                else:
                    label = self.font.render(str(text), 1, (255, 255, 255))
                self.screen.blit(label, (self.x + 2, self.y + index * 20 + 22))

        withPos = [text for text in self.toWrite if text['x'] != None]

        for text in withPos:
            label = self.font.render(str(text['text']), 1, (255, 255, 255))
            bg = Surface((len(str(text['text'])) * 14, 20))
            bg.fill((0, 0, 0))
            bg.set_alpha(100)
            # self.screen.blit(bg, (text['x'] + self.camera.x, text['y'] + self.camera.y))
            # self.screen.blit(label, (text['x'] + self.camera.x, text['y'] + self.camera.y))
            self.screen.blit(bg, (text['x'] - self.camera.x, text['y'] - self.camera.y))
            self.screen.blit(label, (text['x'] - self.camera.x, text['y'] - self.camera.y))
            # self.screen.blit(bg, (text['x'], text['y']))
            # self.screen.blit(label, (text['x'], text['y']))

        # for shape in self.toDraw:
        #     if shape['type'] == 'point':
        #         if hasattr(self, 'camera'):
        #             pygame.draw.ellipse(self.screen, (0, 0, 0), (shape['x'] - self.camera.x, shape['y'] - self.camera.y, 4, 4))
        #         else:
        #             pygame.draw.ellipse(self.screen, (0, 0, 0), (shape['x'], shape['y'], 4, 4))

        self.toWrite = []
        # self.toDraw = []

# todo:
# assets manager:
#     . stores assets (one image?)
#     . draws sprites
#     . is managed by game, not by level

class SceneManager(object):
    def __init__(self, game):
        self.game = game
        self.path = game.path + '/assets'
        self.primaryImages = []

    def initialise(self):
        self.sprites = self.game.current.sprites
        self.camera = self.game.camera
        self.debug = self.game.debug
        self.screen = self.game.screen

    def loadPrimaryImage(self, **kwargs):
        imageData = {}
        if 'index' in kwargs:
            index = str(kwargs['index'])
            imageData['image'] = pygame.image.load('{}/images/level_{}.png'.format(self.path, index))
            imageData['fileName'] = 'level_' + index
        elif 'fileName' in kwargs:
            fileName = kwargs['fileName']
            imageData['image'] = pygame.image.load('{}/images/{}.png'.format(self.path, index))
            imageData['fileName'] = fileName
        self.primaryImages.append(imageData)

    def clearCache(self):
        self.primaryImages = []
        self.images = []

    def draw(self):
        self.sprites.sort(displayingOrder)
        for sprite in self.sprites:
            spriteInfo = sprite.getInfo()
            surface = pygame.Surface((spriteInfo['width'], spriteInfo['height'] + spriteInfo['depth']))
            # if 'image' in spriteInfo:
            #     image = self.find(spriteInfo['image'])
            # else:
            pygame.draw.rect(surface, (spriteInfo['color'].r + 20, spriteInfo['color'].g + 20, spriteInfo['color'].b + 20), (0, 0, spriteInfo['width'], spriteInfo['depth']))
            pygame.draw.rect(surface, (spriteInfo['color'].r, spriteInfo['color'].g, spriteInfo['color'].b), (0, spriteInfo['depth'], spriteInfo['width'], spriteInfo['height']))

            self.screen.blit(surface, (spriteInfo['x'] - self.camera.x, spriteInfo['z'] - spriteInfo['y'] - spriteInfo['height'] - self.camera.y))

            if spriteInfo['selected']:
                # c = (0, 100, 155)
                # warningRectangle = pygame.Surface((spriteInfo['width'], spriteInfo['height'] + spriteInfo['depth']))
                # warningRectangle.fill(c)
                # warningRectangle.set_alpha(50)
                # surface.blit(warningRectangle, (0, 0))
                pygame.draw.rect(self.screen, (100, 150, 255), (spriteInfo['x'] - self.camera.x, spriteInfo['z'] - spriteInfo['y'] - spriteInfo['height'] - self.camera.y, spriteInfo['width'], spriteInfo['height'] + spriteInfo['depth']), 1)


class Game(object):
    def __init__(self, control, width, height):
        pygame.init()
        pygame.display.init()

        self.path = control.path
        self.width = width
        self.height = height
        self.fps = 60
        self.control = control
        self.mode = 'preview'
        self.gravity = 2400

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.assetsManager = SceneManager(self)
        self.debug = Debug(self)
        self.camera = Camera(self)
        self.mouse = Mouse(self)

        self.current = Level(self, 1)
        self.current.initialise(1)
        self.mouse.initialise()
        self.assetsManager.initialise()
        self.debug.mouse = self.mouse

    def addBlock(self, x, y, z, width, height, depth):
        Dynamic(self, x, y, z, width, height, depth)

    def changeMode(self, mode):
        if mode == 'preview':
            self.mouse.initialise()
            self.mode = mode
            self.current.reset()
        elif mode == 'play':
            self.mode = mode
            self.current.save()

    def getKeys(self):
        self.keys = pygame.key.get_pressed()

    def changeState(self, connection):
        self.debug.camera = None
        index, entrance = connection
        self.current = Level(self, index)
        self.current.initialise(entrance)

    # def preview(self):
    #
    #     self.current.draw()
    #     self.debug.all()
    #
    # def play(self):
    #     self.current.draw()

    def update(self):
        k = pygame.key.get_pressed()
        if k[K_ESCAPE]:
            exit()

        self.screen.fill((255, 255, 255))
        if self.mode == 'preview':
            self.mouse.preview()
            self.current.preview()
            self.mouse.draw()
        elif self.mode == 'play':
            self.mouse.update()
            self.getKeys()
            self.current.update()
        self.assetsManager.draw()
        self.debug.all()
        pygame.display.update()
        self.clock.tick(self.fps)


class Level(object):
    def __init__(self, game, index):
        self.game = game
        self.screen = game.screen
        self.assetsManager = game.assetsManager
        self.debug = game.debug
        self.camera = game.camera
        self.index = index
        self.time = 0
        self.sprites = []
        self.statics = []
        self.dynamics = []
        self.entrances = []

    def initialise(self, entranceIndex):
        level_json = open(self.game.path + '/levels/level_1/level.json', 'r')
        self.data = json.load(level_json)
        level_json.close()

        animations_path = self.game.path + '/assets/animations.json'
        animations_json = open(animations_path, 'r')
        self.animations = json.load(animations_json)
        animations_json.close()

        self.debug.camera = self.camera
        self.assetsManager.loadPrimaryImage(index = self.index)
        self.sprites = []
        self.statics = []
        self.dynamics = []
        self.entrances = []

        for spriteData in self.data['sprites']:
            sprite = globals()[spriteData['class']](self.game, **spriteData['arguments'])
            if 'animationSet' in spriteData:
                sprite.animation = AnimationManager(sprite, spriteData['animationSet'])

        player = {}

        for entrance in self.entrances:
            if entrance.index == entranceIndex:
                player['y'] = entrance.y

                if entrance.direction == 1:
                    player['x'] = entrance.x
                    player['z'] = entrance.z - 60
                elif entrance.direction == 2:
                    player['x'] = entrance.x + entrance.width + 10
                    player['z'] = entrance.z
                elif entrance.direction == 3:
                    player['x'] = entrance.x
                    player['z'] = entrance.z + entrance.depth + 10
                elif entrance.direction == 4:
                    player['x'] = entrance.x - 60
                    player['z'] = entrance.z

                self.player = Player(self.game, player['x'], player['y'], player['z'])
                self.dynamics.append(self.player)
                self.camera.follow(self.player.focusSpot)
                break

    def getTime(self):
        return self.time

    def reset(self):
        for sprite in self.sprites:
            sprite.initialise()
        self.time = 0

    def save(self):
        for sprite in self.sprites:
            sprite.selected = False
            sprite.save()

    def preview(self):
        for sprite in self.sprites:
            sprite.preview()
        # k = pygame.key.get_pressed()
        # if k[K_o]:
        #     self.save()

    def update(self):
        self.time += 1 / self.game.fps
        self.player.getKeys()
        self.player.updateFocusSpot()
        self.camera.update()
        for sprite in self.sprites:
            sprite.preupdate()

        for dynamic in self.dynamics:
            dynamic.velocity.y -= self.game.gravity / self.game.fps

        self.sprites.sort(key = lambda sprite: sprite.y)

        for dynamic in self.dynamics:
            dynamic.collide()

        for sprite in self.statics + self.dynamics + self.entrances:
            sprite.update()

        self.player.checkIfAlive()

    def draw(self):
        self.sprites.sort(displayingOrder)
        for sprite in self.sprites:
            sprite.draw()


class Camera(object):
    def __init__(self, game):
        self.game = game
        self.debug = game.debug
        self.width = game.width
        self.height = game.height
        self.x = 0
        self.y = 0
        self.followed = None

    def goTo(self, x, y):
        self.x = x
        self.y = y

    def follow(self, point):
        self.followed = point

    def unfollow(self):
        self.followed = None

    def update(self):
        if self.followed:
            self.x = self.followed.x - self.width / 2
            self.y = self.followed.y - self.height / 2


# class Plane(object):
#     def __init__(self, game, x, y, z, width, height, image):
#         super(Plane, self).__init__()


class Cube(object):
    def __init__(self, x, y, z, width, height, depth):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth

class Delay(object):
    def __init__(self, animationManager, length, animationName):
        self.animationManager = animationManager
        self.game = animationManager.game
        self.playAfter = animationName
        self.index = 0
        self.length = length

    def reset(self):
        self.index = 0

    def update(self):
        if self.index > self.length * self.game.fps:
            self.animationManager.play(self.playAfter)
            self.animationManager.playing.remove(self)
        else:
            self.index += 1


class Animation(object):
    def __init__(self, animationManager, data):
        self.animationManager = animationManager
        self.game = animationManager.game
        self.sprite = animationManager.sprite
        self.name = data['name']
        self.sequence = data['sequence']
        self.looped = data['looped']
        self.length = len(self.sequence)
        self.index = 0
        self.current = self.sequence[0]

    def reset(self):
        self.index = 0

    def update(self):
        if self.index > self.length - 1:
            self.index = 0
        self.current = self.sequence[self.index]
        self.index += 1


class Move(object):
    def __init__(self, animationManager, data):
        self.animationManager = animationManager
        self.game = animationManager.game
        self.sprite = animationManager.sprite
        self.name = data['name']
        self.sequence = data['sequence']
        self.looped = data['looped']
        self.length = sum([frame['time'] for frame in self.sequence])
        if data['playOnInit']:
            self.playOnInit = True
        self.index = 0
        self.current = self.sequence[0]
        self.previous = self.sequence[-1]

    def reset(self):
        self.index = 0

    def update(self):
        if self.index >= self.length:
            self.index = 0
            if not self.looped:
                if hasattr(self, 'playAfter'):
                    self.animationManager.play(self.playAfter)
                self.animationManager.playing.remove(self)
                return
        length = 0
        for frame in self.sequence:
            length += frame['time']
            if length > self.index:
                self.current = frame
                self.previous = self.sequence[self.sequence.index(frame) - 1]
                break

        if 'x' in self.current:
            self.sprite.velocity.x = (self.current['x'] - (self.sprite.x - self.sprite.original['x'])) / (length - self.index) * self.game.fps
        if 'y' in self.current:
            self.sprite.velocity.y = (self.current['y'] - (self.sprite.y - self.sprite.original['y'])) / (length - self.index) * self.game.fps
        if 'z' in self.current:
            self.sprite.velocity.z = (self.current['z'] - (self.sprite.z - self.sprite.original['z'])) / (length - self.index) * self.game.fps

        self.index += 1


class AnimationManager(object):
    def __init__(self, sprite, animationInfo):
        self.game = sprite.game
        self.path = self.game.path
        self.debug = sprite.debug
        self.sprite = sprite
        self.all = []
        self.playing = []
        animations_json = open(self.path + '/assets/animations.json', 'r')
        data = json.load(animations_json)
        animations_json.close()
        for animationSet in data:
            if animationSet['name'] == animationInfo['name']:
                for animation in animationSet['moves']:
                    self.all.append(Move(self, animation))
                    if animation['playOnInit']:
                        if 'delay' in animationInfo:
                            self.delay = Delay(self, animationInfo['delay'], animation['name'])
                            self.playing.append(self.delay)
                        else:
                            self.play(animation['name'])

    def reset(self):
        self.playing = []
        for animation in self.all:
            animation.reset()
            if animation.playOnInit and not hasattr(self, 'delay'):
                self.play(animation.name)
        if hasattr(self, 'delay'):
            self.delay.reset()
            self.playing.append(self.delay)

    def getTime(self):
        return self.sprite.level.getTime()

    def find(self, animationName):
        for animation in self.all:
            if animation.name == animationName:
                return animation

    def getInfo(self):
        return {'info': 'takie se info'}

    def play(self, animationName):
        animation = self.find(animationName)
        if animation and animation not in self.playing:
            self.playing.append(animation)

    def stop(self, animationName):
        animation = self.find(animationName)
        if animation and animation in self.playing:
            self.playing.remove(animation)

    def update(self):
        self.sprite.velocity.x = 0
        self.sprite.velocity.y = 0
        self.sprite.velocity.z = 0
        for animation in self.playing:
            animation.update()


class Sprite(object):
    def __init__(self, game, **kwargs):
        self.game = game
        self.debug = game.debug
        self.screen = game.screen
        self.level = game.current
        self.mouse = game.mouse
        self.camera = self.level.camera

        self.x, self.y, self.z = kwargs['x'], kwargs['y'], kwargs['z']
        self.width, self.height, self.depth = kwargs['width'], kwargs['height'], kwargs['depth']
        self.original = {

            'x': self.x,
            'y': self.y,
            'z': self.z,
            'width': self.width,
            'height': self.height,
            'depth': self.depth
        }
        # self.virtual = Vector(x, y, z)
        # self.children = []
        # self.parent = None
        self.selected = False
        self.color = pygame.Color(random.randint(0, 225), random.randint(0, 225), random.randint(0, 225))
        self.overlapping = False

        if 'image' in kwargs:
            self.image = {
                'x': kwargs['image']['x'],
                'y': kwargs['image']['y']
            }

        self.level.sprites.append(self)

    def getInfo(self):
        info = {
            'x': self.x, 'y': self.y, 'z': self.z,
            'width': self.width, 'height': self.height, 'depth': self.depth,
            'color': self.color, 'selected': self.selected
        }
        if hasattr(self, 'image'):
            info['image'] = self.image
        return info

    def preview(self):
        self.overlapping = False
        for sprite in self.level.sprites:
            if not (sprite.x + sprite.width <= self.x
                and sprite.x >= self.x + self.width
                and sprite.y + sprite.height <= self.y
                and sprite.y >= self.y + self.height
                and sprite.z + sprite.depth <= self.z
                and sprite.z >= self.z + self.depth):
                self.overlapping = True

        if not self.mouse.dragging:
            self.distance = Vector2d((self.mouse.x - self.x), (self.mouse.y - (self.z - self.y)))

        elif self.selected:
            if self.mouse.ctrl:
                if self.mouse.alt:
                    self.y = int(50 * round(float(-self.mouse.y + self.distance.y + self.z) / 50))
                else:
                    self.x = int(50 * round(float(self.mouse.x - self.distance.x) / 50))
                    self.z = int(50 * round(float(self.mouse.y - self.distance.y + self.y) / 50))
            else:
                if self.mouse.alt:
                    self.y = -self.mouse.y + self.distance.y + self.z
                else:
                    self.x = self.mouse.x - self.distance.x
                    self.z = self.mouse.y - self.distance.y + self.y

    def preupdate(self):
        if hasattr(self, 'animation'):
            self.animation.update()
        # if self.parent:
        #     self.x = self.virtual.x + self.parent.x
        #     self.y = self.virtual.y + self.parent.y
        #     self.z = self.virtual.z + self.parent.z


    def initialise(self):
        self.overlapping = False
        self.x = self.original['x']
        self.y = self.original['y']
        self.z = self.original['z']
        if hasattr(self, 'animation'):
            self.animation.reset()

    def save(self):
        self.original['x'] = self.x
        self.original['y'] = self.y
        self.original['z'] = self.z
        self.original['width'] = self.width
        self.original['height'] = self.height
        self.original['height'] = self.depth


class Static(Sprite):
    def __init__(self, game, **kwargs):
        super(Static, self).__init__(game, **kwargs)
        if not self in self.level.statics:
            self.level.statics.append(self)
        self.velocity = Vector()

    def preupdate(self):
        super(Static, self).preupdate()

    def update(self):
        self.x += self.velocity.x / self.game.fps
        self.y += self.velocity.y / self.game.fps
        self.z += self.velocity.z / self.game.fps


class Entrance(Sprite):
    def __init__(self, game, **kwargs):
        if 'width' not in kwargs:
            direction = kwargs['direction']
            if direction == 1 or direction == 3:
                width = 50
                depth = 20
            else:
                width = 20
                depth = 50
            height = 150
        super(Entrance, self).__init__(game, width = width, height = height, depth = depth, **kwargs)
        self.index = kwargs['index']
        self.connection = kwargs['connection']
        self.direction = kwargs['direction']
        self.level.entrances.append(self)
        self.color = pygame.Color(0, 0, 0)

    def update(self):
        # if self.overlap(self.level.player):
        #     self.game.changeState(self.connection)
        pass

    def draw(self):
        plane = pygame.Surface((self.width, self.height + self.depth))
        plane.fill((255, 255, 255))
        plane.set_alpha(150)
        pygame.draw.rect(plane, (230, 230, 230), (0, 0, self.width, self.depth))
        pygame.draw.rect(plane, (200, 200, 200), (0, self.depth, self.width, self.height))
        pygame.draw.rect(plane, (230, 230, 230), (0, self.height, self.width, self.depth))
        pygame.draw.line(plane, (230, 20, 20), (0, self.depth), (self.width, self.height + self.depth), 3)
        pygame.draw.line(plane, (230, 20, 20), (self.width, self.depth), (0, self.height + self.depth), 3)

        if self.selected:
            c = (0, 100, 155)
            warningRectangle = pygame.Surface((self.width, self.height + self.depth))
            warningRectangle.fill(c)
            warningRectangle.set_alpha(50)
            plane.blit(warningRectangle, (self.x - self.camera.x, self.z - self.y - self.height - self.camera.y))
            self.screen.blit(plane, (self.x - self.camera.x, self.z - self.y - self.height - self.camera.y))
            pygame.draw.rect(self.screen, (100, 150, 255), (self.x - self.camera.x, self.z - self.y - self.height - self.camera.y, self.width, self.height + self.depth), 1)
        else:
            self.screen.blit(plane, (self.x - self.camera.x, self.z - self.y - self.height - self.camera.y))


class Dynamic(Sprite):
    def __init__(self, game, **kwargs):
        super(Dynamic, self).__init__(game, **kwargs)
        self.velocity = Vector()

    def collide(self):
        inf = float('inf')
        self.colliding = False
        self.onFloor = False
        for i in range(0, 2):
            for sprite in self.level.statics:
                if sprite == self:
                    continue

                velocity = Vector()
                invEntry = Vector()
                invExit = Vector()
                entry = Vector()
                exit = Vector()

                velocity.x = (self.velocity.x - sprite.velocity.x) / self.game.fps
                velocity.y = (self.velocity.y - sprite.velocity.y) / self.game.fps
                velocity.z = (self.velocity.z - sprite.velocity.z) / self.game.fps

                broadPhase = Cube(
                    min(self.x, self.x + velocity.x),
                    min(self.y, self.y + velocity.y),
                    min(self.z, self.z + velocity.z),
                    self.width + abs(velocity.x),
                    self.height + abs(velocity.y),
                    self.depth + abs(velocity.z)
                )

                if velocity.x == 0 and velocity.y == 0 and velocity.z == 0:
                    continue

                if (broadPhase.x + broadPhase.width <= sprite.x
                    or broadPhase.x >= sprite.x + sprite.width
                    or broadPhase.y + broadPhase.height <= sprite.y
                    or broadPhase.y >= sprite.y + sprite.height
                    or broadPhase.z + broadPhase.depth <= sprite.z
                    or broadPhase.z >= sprite.z + sprite.depth):
                    continue


                if velocity.x > 0:
                    invEntry.x = sprite.x - (self.x + self.width)
                    invExit.x = (sprite.x + sprite.width) - self.x

                else:
                    invEntry.x = (sprite.x + sprite.width) - self.x
                    invExit.x = sprite.x - (self.x + self.width)

                if velocity.y > 0:
                    invEntry.y = sprite.y - (self.y + self.height)
                    invExit.y = (sprite.y + sprite.height) - self.y
                else:
                    invEntry.y = (sprite.y + sprite.height) - self.y
                    invExit.y = sprite.y - (self.y + self.height)

                if velocity.z > 0:
                    invEntry.z = sprite.z - (self.z + self.depth)
                    invExit.z = (sprite.z + sprite.depth) - self.z
                else:
                    invEntry.z = (sprite.z + sprite.depth) - self.z
                    invExit.z = sprite.z - (self.z + self.depth)

                if velocity.x == 0:
                    entry.x = -inf
                    exit.x = inf
                else:
                    entry.x = invEntry.x / velocity.x
                    exit.x = invExit.x / velocity.x

                if velocity.y == 0:
                    entry.y = -inf
                    exit.y = inf
                else:
                    entry.y = invEntry.y / velocity.y
                    exit.y = invExit.y / velocity.y

                if velocity.z == 0:
                    entry.z = -inf
                    exit.z = inf
                else:
                    entry.z = invEntry.z / velocity.z
                    exit.z = invExit.z / velocity.z

                normal = Vector()

                entryTime = max(entry.x, entry.y, entry.z)
                exitTime = min(exit.x, exit.y, exit.z)

                if entryTime > exitTime or (entry.x < 0 and entry.y < 0 and entry.z < 0) or (entry.x > 1 or entry.y > 1 or entry.z > 1):
                    normal.x = 0
                    normal.y = 0
                    normal.z = 0
                    continue
                else:
                    if entryTime == entry.x:
                        normal.y = 0
                        normal.z = 0
                        if velocity.x < 0:
                            normal.x = 1
                        else:
                            normal.x = -1
                    elif entryTime == entry.y:
                        normal.x = 0
                        normal.z = 0
                        if velocity.y < 0:
                            normal.y = 1
                        else:
                            normal.y = -1
                    else:
                        normal.x = 0
                        normal.y = 0
                        if velocity.z < 0:
                            normal.z = 1
                        else:
                            normal.z = -1

                    if i == 0:
                        if normal.y == 1:
                            self.onFloor = True
                            self.velocity.x += sprite.velocity.x
                            self.velocity.y = -(self.y - (sprite.y + sprite.height + (sprite.velocity.y / self.game.fps))) * self.game.fps
                        elif normal.y == -1:
                            self.velocity.y = (sprite.y + (sprite.velocity.y / self.game.fps) - (self.y + self.height)) * self.game.fps
                    else:
                        if normal.x == 1:
                            self.velocity.x = -(self.x - (sprite.x + sprite.width + (sprite.velocity.x / self.game.fps))) * self.game.fps
                        elif normal.x == -1:
                            self.velocity.x = (sprite.x + (sprite.velocity.x / self.game.fps) - (self.x + self.width)) * self.game.fps
                        if normal.z == 1:
                            self.velocity.z = -(self.z - (sprite.z + sprite.depth + (sprite.velocity.z / self.game.fps))) * self.game.fps
                        elif normal.z == -1:
                            self.velocity.z = (sprite.z + (sprite.velocity.z / self.game.fps) - (self.z + self.depth)) * self.game.fps

    def update(self):
        self.x += int(self.velocity.x / self.game.fps)
        self.y += int(self.velocity.y / self.game.fps)
        self.z += int(self.velocity.z / self.game.fps)


class Player(Dynamic):
    def __init__(self, game, x, y, z):
        super(Player, self).__init__(game, x = x, y = y, z = z, width =  50, height =  100, depth = 50)
        self.mouse = self.game.mouse
        self.onFloor = []
        self.focusSpot = Vector2d(self.x + self.width / 2, self.z + self.depth / 2 - self.y - self.height / 2)

    def initialise(self):
        super(Player, self).initialise()
        # self.focusSpot.x = self.x + self.width / 2
        # self.focusSpot.y = self.z + self.depth / 2 - self.y - self.height / 2

    def getKeys(self):
        k = pygame.key.get_pressed()

        if k[pygame.K_d]:
            self.velocity.x = 250
        elif k[pygame.K_a]:
            self.velocity.x = -250
        else:
            self.velocity.x = 0

        if k[pygame.K_s]:
            self.velocity.z = 250
        elif k[pygame.K_w]:
            self.velocity.z = -250
        else:
            self.velocity.z = 0

        if k[pygame.K_SPACE] and self.onFloor:
            self.velocity.y = 600

    def updateFocusSpot(self):
        x1 = self.x + self.width / 2 + self.velocity.x * 0.3
        y1 = self.z - self.y + self.depth / 2 + self.velocity.z * 0.4 - self.y - self.height / 2 + 50
        theta = math.atan2(self.mouse.x + self.camera.x - x1, self.mouse.y + self.camera.y - y1)
        x2 = x1 + math.sin(theta) * 5 * math.sqrt(abs(self.mouse.x + self.camera.x - x1))
        y2 = y1 + math.cos(theta) * 5 * math.sqrt(abs(self.mouse.y + self.camera.y - y1))
        self.focusSpot.x += (x2 - self.focusSpot.x) / (self.game.fps * 0.2)
        self.focusSpot.y += (y2 - self.focusSpot.y) / (self.game.fps * 0.2)

    def checkIfAlive(self):
        if self.y < 0:
            self.level.reset()
            return

        for sprite in self.level.statics:
            if (self.x < sprite.x + sprite.width
                and self.x + self.width > sprite.x
                and self.y < sprite.y + sprite.height
                and self.y + self.height > sprite.y
                and self.z < sprite.z + sprite.depth
                and self.z + self.depth > sprite.z):
                self.level.reset()
                return

def getTime():
    return pygame.time.get_ticks()

def displayingOrder(a, b):
    if a.z >= b.z + b.depth or a.y >= b.y + b.height:
        return 1
    elif a.z + a.depth >= b.z + b.depth and a.z + a.depth > b.z + b.depth:
        return 1
    elif a.y + a.height == b.y + b.height and (a.z + a.depth == b.z + b.depth or a.z + a.depth == b.z + b.depth):
        return 0
    else:
        return -1

def scaleImage(image, scale):
    if isinstance(scale, (int, float)):
        rect = image.get_rect()
        i = pygame.transform.scale(image, (int(rect.width * scale), int(rect.height * scale)))
    else:
        i = pygame.transfrom.scale(image, scale)
    return i

def main():
    control = Control(1080, 720)
    control.run()


if __name__ == '__main__':
    main()
