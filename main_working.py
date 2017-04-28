from __future__ import division
import Tkinter as tk
from Tkinter import *
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
        self.root.minsize(width = 1150, height = 700)
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
        super(GameFrame, self).__init__(parent)
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

    def update(self):
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
                    if sprite in self.selected:
                        clickedSelected = True
                    if not sprite in toSelect:
                        toSelect.append(sprite)

            if len(toSelect) > 0:
                self.dragging = True
                if not self.shift and not clickedSelected:
                    self.deselect()

                toSelect.sort(displayingOrder)
                toSelect[-1].selected = True

                self.select(toSelect[-1])

            else:
                if not self.shift and not clickedSelected:
                    self.deselect()

                if self.lastPressed < getTime() < self.lastPressed + 150:
                    self.game.addBlock(self.x + self.camera.x, 0, self.y + self.camera.y, 50, 50, 50)
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
                    self.debug.text('x: %s' % sprite.x, x = self.x + 10, y = self.y)
                    self.debug.text('y: %s' % sprite.y, x = self.x + 10, y = self.y + 20)
                    self.debug.text('z: %s' % sprite.z, x = self.x + 10, y = self.y + 40)

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
        self.camera = Vector()

    def update(self):
        self.toWrite = []
        self.toDraw = []

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
            self.screen.blit(bg, (text['x'] - self.camera.x, text['y'] - self.camera.y))
            self.screen.blit(label, (text['x'] - self.camera.x, text['y'] - self.camera.y))

        for shape in self.toDraw:
            if shape['type'] == 'point':
                if hasattr(self, 'camera'):
                    pygame.draw.ellipse(self.screen, (0, 0, 0), (shape['x'] - self.camera.x, shape['y'] - self.camera.y, 4, 4))
                else:
                    pygame.draw.ellipse(self.screen, (0, 0, 0), (shape['x'], shape['y'], 4, 4))


class Game(object):
    def __init__(self, control, width, height):
        pygame.init()
        pygame.display.init()
        self.control = control
        self.path = control.path
        self.width = width
        self.height = height
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.debug = Debug(self)
        self.camera = Camera(self)
        self.mouse = Mouse(self)
        self.mode = 'preview'
        self.gravity = 2400
        self.levels = []
        self.progress = 0
        self.story = 0
        self.current = Level(self, 1)
        self.current.initialise(1)
        self.mouse.initialise()
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

    def preview(self):
        self.debug.update()
        self.mouse.update()
        self.current.preview()
        self.current.draw()
        self.mouse.draw()
        self.debug.all()

    def play(self):
        self.getKeys()
        self.debug.update()
        self.current.preupdate()
        self.current.update()
        self.current.draw()
        self.debug.all()

    def update(self):
        k = pygame.key.get_pressed()
        if k[K_ESCAPE]:
            exit()

        self.screen.fill((255, 255, 255))
        if self.mode == 'play':
            self.play()
        elif self.mode == 'preview':
            self.preview()

        pygame.display.update()
        self.clock.tick(self.fps)


class ObjectFactory(object):
    def __init__(self, level):
        self.level = level

    def dynamic(self, x, y, z, width, height, depth):
        self.level.dynamics_list.append({'x': x, 'y': y, 'z': z, 'width': width, 'height': height, 'depth': depth})

    def static(self, x, y, z, width, height, depth):
        self.level.statics_list.append({'x': x, 'y': y, 'z': z, 'width': width, 'height': height, 'depth': depth})


class Level(object):
    def __init__(self, game, index):
        self.game = game
        self.debug = game.debug
        self.screen = game.screen
        self.camera = game.camera
        self.index = index
        self.frame = 0
        self.sprites = []
        self.statics = []
        self.dynamics = []
        self.entrances = []

    def initialise(self, entranceIndex):
        levels_path = self.game.path + '/levels'
        level_path = levels_path + '/level_' + str(3) + '.json'
        level_json = open(level_path, 'r')
        self.data = json.load(level_json)
        level_json.close()

        animations_path = self.game.path + '/assets/animations.json'
        animations_json = open(animations_path, 'r')
        self.animations = json.load(animations_json)
        animations_json.close()

        self.debug.camera = self.camera
        self.sprites = []
        self.statics = []
        self.dynamics = []
        self.entrances = []

        for sprite in self.data['sprites']:
            globals()[sprite['class']](self.game, *sprite['arguments'])

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

    def reset(self):
        for sprite in self.sprites:
            sprite.initialise()

    def save(self):
        for sprite in self.sprites:
            sprite.selected = False
            sprite.save()
        levelData = {'index': self.index, 'sprites': []}
        for sprite in self.sprites:
            spriteData = {
                'class': sprite.__class__.__name__,
                'arguments': [value for key, value in sprite.original]
            }
            levelData['sprites'].append(spriteData)
        print 'saved'

    def preview(self):
        for sprite in self.sprites:
            sprite.preview()
        k = pygame.key.get_pressed()
        if k[K_o]:
            self.save()

    def preupdate(self):
        for sprite in self.sprites:
            sprite.preupdate()

    def update(self):
        self.player.getKeys()
        self.player.updateFocusSpot()
        self.camera.update()

        for dynamic in self.dynamics:
            dynamic.velocity.y -= self.game.gravity / self.game.fps

        self.sprites.sort(key = lambda sprite: sprite.y)

        for dynamic in self.dynamics:
            dynamic.collide()

        for sprite in self.statics + self.dynamics + self.entrances:
            sprite.update()

        if self.player.y < 0:
            self.player.initialise()

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
        # if self.followed:
        #     self.x = self.followed.x - self.width / 2
        #     self.y = self.followed.y - self.height / 2
        pass


# class Plane(object):
#     def __init__(self, game, x, y, z, width, height, image):
#         super(Plane, self).__init__()
#


class Cube(object):
    def __init__(self, x, y, z, width, height, depth):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth


class Animation(object):
    def __init__(self, data):
        self.name = data['name']
        self.sequence = data['sequence']
        self.looped = data['looped']
        self.length = sum([frame['time'] for frame in self.sequence])
        self.index = 0
        self.current = self.sequence[0]
        self.previous = self.sequence[-1]


class AnimationManager(object):
    def __init__(self, sprite):
        self.game = sprite.game
        self.debug = sprite.debug
        self.sprite = sprite
        self.all = [
            Animation({
                'name': 'walk',
                'sequence': [
                    {'time': 5, 'x': 25},
                    {'time': 20, 'x': 100},
                    {'time': 5, 'x': 125},
                    {'time': 25, 'x': 0},
                    {'time': 25, 'x': 0}
                ],
                'looped': True
            })
        ]
        self.playing = []
        self.index = 0

    def find(self, animationName):
        for animation in self.all:
            if animation.name == animationName:
                return animation

    def play(self, animationName):
        animation = self.find(animationName)
        if animation and animation not in self.playing:
            self.playing.append(animation)

    def stop(self, animationName):
        animation = self.find(animationName)
        if animation and animation in self.playing:
            self.playing.remove(animation)

    def update(self):
        for animation in self.playing:
            if animation.index >= animation.length:
                animation.index = 0
                if not animation.looped:
                    self.sprite.velocity.x = 0
                    self.sprite.velocity.y = 0
                    self.sprite.velocity.z = 0
                    self.playing.remove(animation)
                    break
            length = 0
            for frame in animation.sequence:
                length += frame['time']
                if length > animation.index:
                    animation.current = frame
                    animation.previous = animation.sequence[animation.sequence.index(frame) - 1]
                    break

            if 'x' in animation.current:
                self.sprite.velocity.x = (animation.current['x'] - (self.sprite.x - self.sprite.original['x'])) / (length - animation.index) * self.game.fps
            if 'y' in animation.current:
                self.sprite.velocity.y = (animation.current['y'] - (self.sprite.y - self.sprite.original['y'])) / (length - animation.index) * self.game.fps
            if 'z' in animation.current:
                self.sprite.velocity.z = (animation.current['z'] - (self.sprite.z - self.sprite.original['z'])) / (length - animation.index) * self.game.fps

            animation.index += 1


class Sprite(object):
    def __init__(self, game, x, y, z, width, height, depth, folder = None, image = None):
        self.original = {
            'x': x,
            'y': y,
            'z': z,
            'width': width,
            'height': height,
            'depth': depth
        }
        self.selected = False
        self.game = game
        self.debug = game.debug
        self.screen = game.screen
        self.level = game.current
        self.mouse = game.mouse
        self.camera = self.level.camera
        if not self in self.level.sprites:
            self.level.sprites.append(self)
        self.parent = None
        self.children = []
        self.x, self.y, self.z = x, y, z
        self.virtual = Vector(x, y, z)
        self.width, self.height, self.depth = width, height, depth
        self.overlapping = False
        self.color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        if image:
            i = pygame.image.load(self.game.path + '/assets/images/' + image)
            self.frame = i

        if folder:
            self.frameset = []
            for f in os.listdir(self.game.path + '/assets/' + folder):
                i = pygame.image.load(self.game.path + '/assets/' + folder + '/' + f)
                self.frameset.append(i)
            self.animations = []
            self.animation = {'name': 'default', 'sequence': [0], 'frame': 0, 'looped': True}
            self.animations.append(self.animation)
            self.frame = self.frameset[self.animation['sequence'][self.animation['frame']]]

    def addChild(self, child):
        self.children.append(child)
        child.parent = self

    def addAnimations(self, sprite):
        for animationSet in self.level.animations:
            if animationSet['sprite'] == sprite:
                self.animations = animationSet['animations']

    def play(self, animationName):
        for animation in self.animations:
            if animation['name'] == animationName:
                self.animation = animation

    def getSelfDisplayingIndex(self):
        return self.level.sprites.index(self)

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
            # if not (sprite.x + sprite.width > self.x
            #     or sprite.x < self.x + self.width
            #     or sprite.y + sprite.height > self.y
            #     or sprite.y < self.y + self.height
            #     or sprite.z + sprite.depth > self.z
            #     or sprite.z < self.z + self.depth):
            #     self.overlapping = True

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
        pass
        # if self.parent:
        #     self.x = self.virtual.x + self.parent.x
        #     self.y = self.virtual.y + self.parent.y
        #     self.z = self.virtual.z + self.parent.z

    def update(self, name):
        if name != self.animation['name']:
            for animation in self.animations:
                if name == animation['name']:
                    self.animation = animation
                    self.animation['frame'] = 0

    def stopAnimation(self):
        self.animation = {'name': 'default', 'sequence': [0], 'frame': 0, 'looped': True}

    def initialise(self):
        self.overlapping = False
        self.x = self.original['x']
        self.y = self.original['y']
        self.z = self.original['z']

    def save(self):
        self.original['x'] = self.x
        self.original['y'] = self.y
        self.original['z'] = self.z
        self.original['width'] = self.width
        self.original['height'] = self.height
        self.original['height'] = self.depth

    def draw(self):
        pygame.draw.rect(self.screen, (self.color.r, self.color.g, self.color.b), (self.x - self.camera.x, self.z - self.y - self.height - self.camera.y, self.width, self.depth))
        pygame.draw.rect(self.screen, (self.color.r * 0.8, self.color.g * 0.8, self.color.b * 0.8), (self.x - self.camera.x, self.z - self.y - self.height + self.depth - self.camera.y, self.width, self.height))

        # if hasattr(self, 'animation'):
        #     if self.animation['frame'] < len(self.animation['sequence']) - 6 / self.game.fps:
        #         self.animation['frame'] += 6 / self.game.fps
        #     else:
        #         if self.animation['looped']:
        #             self.animation['frame'] = 0
        #         elif 'link' in self.animation:
        #             self.play(self.animation['link'])
        #         else:
        #             self.stopAnimation()
        #
        #     sequencesFrameNumber = int(math.floor(self.animation['frame']))
        #     sequence = self.animation['sequence']
        #
        #     self.frame = self.frameset[sequence[sequencesFrameNumber]]
        #
        # if hasattr(self, 'frame'):
        #     self.screen.blit(self.frame, (self.x - self.camera.x, self.z - self.y - self.height - self.camera.y, self.width, self.height + self.depth))

        # if self.selected or self.overlapping:
            # if self.overlapping:
            #     c = (225, 130, 20)
        if self.selected:
            c = (0, 100, 155)
            warningRectangle = pygame.Surface((self.width, self.height + self.depth))
            warningRectangle.fill(c)
            warningRectangle.set_alpha(50)
            self.screen.blit(warningRectangle, (self.x - self.camera.x, self.z - self.y - self.height - self.camera.y))
            pygame.draw.rect(self.screen, (100, 150, 255), (self.x - self.camera.x, self.z - self.y - self.height - self.camera.y, self.width, self.height + self.depth), 1)


class Static(Sprite):
    def __init__(self, game, x, y, z, width, height, depth, folder = None, image = None):
        super(Static, self).__init__(game, x, y, z, width, height, depth, folder, image)
        if not self in self.level.statics:
            self.level.statics.append(self)
        self.velocity = Vector()
        self.animation = AnimationManager(self)
        self.animation.play('walk')
    #
    # def addAnimations(self, sprite):
    #     animations = self.level.data['animations']
    #     for d in animations:
    #         if d['sprite'] == sprite:
    #             self.animations = d['animations']

    def preupdate(self):
        # super(Static, self).preupdate()
        self.animation.update()

    def update(self):
        self.x += int(self.velocity.x / self.game.fps)
        self.y += int(self.velocity.y / self.game.fps)
        self.z += int(self.velocity.z / self.game.fps)


class Entrance(Sprite):
    def __init__(self, game, index, connection, direction, x, y, z, width = None, height = None, depth = None):
        if not width:
            if direction == 1 or direction == 3:
                width = 50
                depth = 20
            else:
                width = 20
                depth = 50
            height = 150
        super(Entrance, self).__init__(game, x, y, z, width, height, depth, None)
        self.level.entrances.append(self)
        self.index = index
        self.connection = connection
        self.direction = direction
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth

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


    def overlap(self, sprite):
        pass
        # if sprite.x + sprite.width <= self.x:
        #     return False
        # if sprite.x >= self.x + self.width:
        #     return False
        # if sprite.y + sprite.height <= self.y:
        #     return False
        # if sprite.y >= self.y + self.height:
        #     return False
        # if sprite.z + sprite.depth <= self.z:
        #     return False
        # if sprite.z >= self.z + self.depth:
        #     return False
        #
        # return True


class Dynamic(Sprite):
    def __init__(self, game, x, y, z, width, height, depth, folder = None, image = None):
        super(Dynamic, self).__init__(game, x, y, z, width, height, depth, folder, image)
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
        super(Player, self).__init__(game, x, y, z, 50, 100, 50, 'player')
        self.onFloor = []
        self.focusSpot = Vector2d(self.x + self.width / 2, self.z + self.depth / 2 - self.y - self.height / 2)
        self.addAnimations('player')

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
        x = self.x + self.width / 2 + self.velocity.x * 0.7
        y = self.z - self.y + self.depth / 2 + self.velocity.z * 0.7 - self.y - self.height / 2 + 150
        self.focusSpot.x += math.floor((x - self.focusSpot.x) / (self.game.fps * 0.5))
        self.focusSpot.y += math.floor((y - self.focusSpot.y) / (self.game.fps * 0.5))

    def update(self):
        super(Player, self).update()

def getTime():
    return pygame.time.get_ticks()

def displayingOrder(a, b):
    if a.z >= b.z + b.depth or a.y >= b.y + b.height:
        return 1
    elif a.y + a.height == b.y + b.height and (a.z + a.depth == b.z + b.depth or a.z + a.depth == b.z + b.depth):
        return 0
    elif a.z + a.depth >= b.z + b.depth and a.z + a.depth > b.z + b.depth:
        return 1
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
    control = Control(1400, 800)
    control.run()


if __name__ == '__main__':
    main()
