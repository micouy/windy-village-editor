from __future__ import division
import Tkinter as tk
from Tkinter import *
import json
import pygame
import random
import math
import os

##### EDITOR COMPONENTS #####


class FramesManager(object):
    def __init__(self, control, width, height):
        self.control = control
        self.root = tk.Tk()

        self.root.minsize(width=1150, height=700)
        self.frame = Frame(self.root)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
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
        self.frame.grid(row=row, column=column)


class RightDoc(WidgetManager):
    def __init__(self, parent):
        self.parent = parent
        self.control = parent.control
        self.root = parent.root
        self.frame = Frame(self.parent.frame)
        self.frame.grid(row=0, column=1, ipadx=10, ipady=10, sticky=N)
        self.controlMenu = ControlMenu(self)
        self.addBlockDoc = AddBlockMenu(self)


class GameFrame(WidgetManager):
    def __init__(self, parent, width, height):
        self.control = parent.control
        self.root = parent.root
        self.parent = parent
        self.frame = Frame(self.parent.frame, width=width, height=height)
        self.frame.grid(column=0, row=0)
        os.environ['SDL_WINDOWID'] = str(self.frame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'


class ControlMenu(WidgetManager):
    def __init__(self, parent):
        super(ControlMenu, self).__init__(parent, 0, 0)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.previewMode_button = Button(
            self.frame, text='Preview', command=lambda: self.control.changeMode('preview'))
        self.previewMode_button.grid(row=0, column=0, sticky=W + E)
        self.playMode_button = Button(
            self.frame, text='Play', command=lambda: self.control.changeMode('play'))
        self.playMode_button.grid(row=0, column=1, sticky=W + E)


class AddBlockMenu(WidgetManager):
    def __init__(self, parent):
        super(AddBlockMenu, self).__init__(parent, 1, 0)
        self.x_entry = LabelEntry(self.frame, 'x: ', 0, 0)
        self.y_entry = LabelEntry(self.frame, 'y: ', 1, 0)
        self.width_entry = LabelEntry(self.frame, 'width: ', 3, 0)
        self.height_entry = LabelEntry(self.frame, 'height: ', 4 * 3, 0)

        # self.z_entry = LabelEntry(self.frame, 'z: ', 2, 0)
        # self.depth_entry = LabelEntry(self.frame, 'depth: ', 5, 0)

        self.addBlock_button = Button(
            self.frame, text='Add block', command=lambda: self.addBlock())
        self.addBlock_button.grid(row=5, columnspan=2, pady=2)

        self.response_label = Label(self.frame, text='')
        self.response_label.grid(row=6, columnspan=2, sticky=W, pady=2)

    def addBlock(self):
        x = self.x_entry.get()
        y = self.y_entry.get()
        width = self.width_entry.get()
        height = self.height_entry.get()

        if x.isdigit() and y.isdigit() and width.isdigit() and int(width) > 0 and height.isdigit() and int(height) > 0:
            self.control.addBlock(int(x), int(y), int(width), int(height))
            self.x_entry.delete()
            self.y_entry.delete()
            self.width_entry.delete()
            self.height_entry.delete()
            self.response_label.config(text='Block added')
        else:
            self.response_label.config(text='Enter correct values')


class LabelEntry(object):
    def __init__(self, parent, text, row, column, width=10):
        self.label = Label(parent, text=text)
        self.label.grid(row=row, column=column, sticky=W, pady=2)
        self.entry = Entry(parent, width=width)
        self.entry.grid(row=row, column=column + 1, pady=2)

    def get(self):
        return self.entry.get()

    def delete(self):
        self.entry.delete(0, 'end')

##### EDITOR #####


class Control(object):
    def __init__(self, width, height):
        self.mode = 'preview'
        self.path = os.path.dirname(os.path.realpath('__file__'))
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

    def addBlock(self, x, y, width, height):
        self.game.addBlock(x, y, width, height)

##### GAME #####


class Mouse(object):
    def __init__(self, game):
        self.lastPressed = 0
        self.game = game
        self.render = game.render
        self.current = game.current
        self.screen = game.screen
        self.camera = game.camera
        self.clock = game.clock
        self.sprites = self.current.sprites
        self.x, self.y = pygame.mouse.get_pos()
        self.delta = Vector2d()
        self.pressed = Vector2d(None, None)
        self.selection = Rectangle()
        self.selected = []
        self.toSelect = []
        self.isDragging = False
        self.hasMoved = False
        self.isShift = False
        self.isUp = True
        self.isDown = False
        self.isReleased = False
        self.isPressed = False
        self.info = {'isDown': False, 'isUp': True}

    def initialise(self):
        self.sprites = self.current.sprites
        self.x, self.y = pygame.mouse.get_pos()
        self.delta = Vector2d()
        self.pressed = Vector2d(None, None)
        self.selection = Rectangle()
        self.selected = []
        self.toSelect = []
        self.isDragging = False
        self.hasMoved = False
        self.isShift = False
        self.isUp = True
        self.isDown = False
        self.isReleased = False
        self.isPressed = False
        self.info = {'isDown': False, 'isUp': True}

    def update(self):
        self.isShift = False
        self.isPressed = False
        self.isReleased = False

        self.delta.x, self.delta.y = pygame.mouse.get_pos()
        self.delta.x -= self.x
        self.delta.y -= self.y
        self.x, self.y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.info['isDown'] = True
                self.info['isUp'] = False
            elif event.type == pygame.MOUSEBUTTONUP:
                self.info['isDown'] = False
                self.info['isUp'] = True

        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            self.isShift = True

        if self.isUp:
            if self.info['isDown']:
                self.isUp = False
                self.isDown = True
                self.isPressed = True

        if self.isDown:
            if self.info['isUp']:
                self.isDown = False
                self.isUp = True
                self.isReleased = True

        if self.isReleased:
            self.pressed.x = self.pressed.y = None

        if self.isUp:
            self.isDragging = False

        if self.isDown:
            if self.x != self.pressed.x or self.y != self.pressed.y:
                self.hasMoved = True

        if self.isPressed:
            self.pressed.x, self.pressed.y = self.x, self.y
            self.hasMoved = False
            self.isDragging = False
            self.toSelect = []

            for sprite in self.sprites:
                if (sprite.x - self.camera.x < self.x
                    and sprite.x + sprite.width - self.camera.x > self.x
                    and sprite.z - sprite.y - sprite.height - self.camera.y < self.y
                    and sprite.z - sprite.y + sprite.depth - self.camera.y > self.y):
                    if not sprite in self.toSelect:
                        self.toSelect.append(sprite)

            if len(self.toSelect) > 0:
                self.isDragging = True
                if not self.isShift:
                    for sprite in self.selected:
                        sprite.selected = False
                    self.selected = []

                self.toSelect.sort(displayingOrder)
                self.toSelect[-1].selected = True

                if not self.toSelect[-1] in self.selected:
                    self.selected.append(self.toSelect[-1])

            else:
                if not self.isShift:
                    for sprite in self.selected:
                        sprite.selected = False
                    self.selected = []

                self.render.text(self.lastPressed)
                self.render.text(getTime())
                if self.lastPressed < getTime() < self.lastPressed + 300:
                    self.game.addBlock(self.x + self.camera.x, 0, self.y + self.camera.y, 50, 50, 50)
            self.lastPressed = getTime()

        if not self.isDragging and self.isDown:
            if self.pressed.x and self.pressed.y:
                self.selection.x = min(self.x, self.pressed.x)
                self.selection.y = min(self.y, self.pressed.y)
                self.selection.width = abs(self.x - self.pressed.x)
                self.selection.height = abs(self.y - self.pressed.y)

        if self.isReleased:
            self.selection.x = None
            self.selection.y = None
            self.selection.width = None
            self.selection.height = None

        if self.selection.width > 0 and self.selection.height > 0 and self.selection.x and self.selection.y:
            for sprite in self.sprites:
                if (self.selection.x <= sprite.x - self.camera.x
                    and self.selection.x + self.selection.width >= sprite.x + sprite.width - self.camera.x
                    and self.selection.y <= sprite.z - sprite.y - self.camera.y
                    and self.selection.y + self.selection.height >= sprite.z + sprite.depth - sprite.y - sprite.height - self.camera.y):
                    if not sprite in self.selected:
                        self.selected.append(sprite)
                        sprite.selected = True
                elif sprite in self.selected and not self.isShift:
                    self.selected.remove(sprite)
                    sprite.selected = False

        if self.isDragging:
            for sprite in self.selected:
                sprite.x += self.delta.x
                sprite.z += self.delta.y

        if len(self.selected) == 1:
            sprite = self.selected[0]
            self.render.text('x: %s' % sprite.x)
            self.render.text('y: %s' % sprite.y)
            self.render.text('z: %s' % sprite.z)

    def get(self):
        return {'up': self.up, 'down': self.down, 'released': self.released, 'pressed': self.pressed}

    def draw(self):
        if self.selection.width and self.selection.height:
            selectionRectangle = pygame.Surface(
                (self.selection.width, self.selection.height))
            selectionRectangle.fill((0, 100, 155))
            selectionRectangle.set_alpha(50)
            self.screen.blit(selectionRectangle, (self.selection.x, self.selection.y))
            pygame.draw.rect(self.screen, (100, 150, 255), (self.selection.x, self.selection.y, self.selection.width, self.selection.height), 1)


class Rectangle(object):
    def __init__(self, x = 0, y = 0, width = 0, height = 0):
        self.x = x
        self.y = y
        self.width = abs(width)
        self.height = abs(height)


class Vector2d(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Vector(object):
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def add(self, a):
        self.x += a.x
        self.y += a.y
        self.z += a.z

    def mult(self, a):
        if a.isidgit():
            self.x *= a
            self.y *= a
            self.z *= a
        else:
            self.x *= a.x
            self.y *= a.y
            self.z *= a.z


class Velocity(Vector):
    def __init__(self):
        super(Velocity, self).__init__(0, 0, 0)


class Renderer(object):
    def __init__(self, game):
        self.font = pygame.font.SysFont('monospace', 20)
        self.game = game
        self.screen = game.screen
        self.toWrite = []
        self.toDraw = []

    def update(self):
        self.toWrite = []
        self.toDraw = []

    def text(self, text, x=None, y=None):
        self.toWrite.append({'text': text, 'x': x, 'y': y})

    def point(self, x, y):
        self.toDraw.append({'type': 'point', 'x': x, 'y': y})

    def all(self):
        if len(self.toWrite) > 0:
            bg = pygame.Surface((200, len(self.toWrite) * 15 + 20))
            bg.set_alpha(100)
            bg.fill((0, 0, 0))
            self.screen.blit(bg, (100, 100))
            label = self.font.render("Debug: ", 1, (0, 0, 0))
            self.screen.blit(label, (100, 100))
            for index, text in enumerate(self.toWrite):
                label = self.font.render(str(text['text']), 1, (0, 0, 0))
                if text['x'] and text['y']:
                    self.screen.blit(label, (text['x'], text['y']))
                else:
                    self.screen.blit(label, (100, 120 + index * 15))

        for shape in self.toDraw:
            if shape['type'] == 'point':
                if hasattr(self, 'camera'):
                    pygame.draw.ellipse(self.screen, (0, 0, 0), (shape['x'] - self.camera.x, shape['y'] - self.camera.y, 4, 4))
                else:
                    pygame.draw.ellipse(self.screen, (0, 0, 0), (shape['x'], shape['y'], 4, 4))


class Game(object):
    def __init__(self, control, WIDTH, HEIGHT):
        pygame.init()
        pygame.display.init()
        self.control = control
        self.path = control.path
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.render = Renderer(self)
        self.camera = Camera(self)
        self.mode = 'preview'
        self.gravity = 2400
        self.levels = []
        self.progress = 0
        self.story = 0
        self.current = Level(self, 1)
        self.current.initialise(1)
        self.mouse = Mouse(self)

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
        self.render.camera = None
        index, entrance = connection
        self.current = Level(self, index)
        self.current.initialise(entrance)

    def preview(self):
        self.render.update()
        self.mouse.update()
        self.current.preview()
        self.current.draw()
        self.mouse.draw()
        self.render.all()

    def play(self):
        self.getKeys()
        self.render.update()
        self.current.update()
        self.current.draw()
        self.render.all()

    def update(self):
        self.screen.fill((255, 255, 255))
        if self.mode == 'play':
            self.play()
        elif self.mode == 'preview':
            self.preview()

        pygame.display.update()
        self.clock.tick(self.FPS)


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
        self.render = game.render
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
        level_path = levels_path + '/level_' + str(self.index) + '.json'
        level_json = open(level_path, 'r')
        self.data = json.load(level_json)
        level_json.close()

        animations_path = self.game.path + '/assets/animations.json'
        animations_json = open(animations_path, 'r')
        self.animations = json.load(animations_json)
        animations_json.close()

        self.render.camera = self.camera
        self.sprites = []
        self.statics = []
        self.dynamics = []
        self.entrances = []

        for static in self.data['statics']:
            x = static['x']
            y = static['y']
            z = static['z']
            width = static['width']
            height = static['height']
            depth = static['depth']
            if 'image' in static:
                image = str(static['image'])
                folder = None
            elif 'folder' in static:
                image = None
                folder = str(static['folder'])
            else:
                image = None
                folder = None
            s = Static(self.game, x, y, z, width, height, depth, folder, image)
            self.statics.append(s)

        for dynamic in self.data['dynamics']:
            x = dynamic['x']
            y = dynamic['y']
            z = dynamic['z']
            width = dynamic['width']
            height = dynamic['height']
            depth = dynamic['depth']
            if 'image' in static:
                image = str(static['image'])
                folder = None
            elif 'folder' in static:
                image = None
                folder = str(static['folder'])
            else:
                image = None
                folder = None
            d = Dynamic(self.game, x, y, z, width, height, depth, folder, image)
            self.dynamics.append(d)

        player = {}

        for entrance in self.data['entrances']:
            index = entrance['index']
            connection = entrance['connection']
            direction = entrance['direction']
            x = entrance['x']
            y = entrance['y']
            z = entrance['z']

            if 'width' in entrance:
                width = entrance['width']
            else:
                if direction == 1 or direction == 3:
                    width = 50
                else:
                    width = 20
            if 'height' in entrance:
                height = entrance['height']
            else:
                height = 150
            if 'depth' in entrance:
                depth = entrance['depth']
            else:
                if direction == 1 or direction == 3:
                    depth = 20
                else:
                    depth = 50

            if index == entranceIndex:
                player['y'] = y

                if direction == 1:
                    player['x'] = x
                    player['z'] = z - 60
                elif direction == 2:
                    player['x'] = x + width + 10
                    player['z'] = z
                elif direction == 3:
                    player['x'] = x
                    player['z'] = z + depth + 10
                elif direction == 4:
                    player['x'] = x - 60
                    player['z'] = z

            e = Entrance(self.game, index, connection, direction, x, y, z, width, height, depth)
            self.entrances.append(e)

        self.player = Player(self.game, player['x'], player['y'], player['z'])
        self.dynamics.append(self.player)
        self.camera.follow(self.player.focusSpot)

    def reset(self):
        for sprite in self.sprites:
            sprite.initialise()

    def save(self):
        for sprite in self.sprites:
            sprite.selected = False
            sprite.save()

    def preview(self):
        pass

    def update(self):
        self.player.getKeys()
        self.player.updateFocusSpot()
        self.camera.update()
        for dynamic in self.dynamics:
            dynamic.velocity.y -= self.game.gravity / self.game.FPS

        self.sprites.sort(key=lambda entity: entity.y)

        for dynamic in self.dynamics:
            dynamic.collide()

        for entity in self.statics + self.dynamics + self.entrances:
            entity.update()

        if self.player.y < 0:
            self.reset()

    def draw(self):
        self.sprites.sort(displayingOrder)
        for entity in self.sprites:
            entity.draw()


class UI(object):
    def __init__(self, game):
        self.game = game
        self.render = game.render


class Camera(object):
    def __init__(self, game):
        self.game = game
        self.render = game.render
        self.width = game.WIDTH
        self.height = game.HEIGHT
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
            # self.x += math.floor((self.followed.x - self.x - self.width / 2) / (self.game.FPS * 0.1))
            # self.y += math.floor((self.followed.y - self.y - self.height / 2) / (self.game.FPS  * 0.1))
            self.x = self.followed.x - self.width / 2
            self.y = self.followed.y - self.height / 2


class Sprite(object):
    def __init__(self, game, x, y, z, width, height, depth, folder=None, image=None):
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
        self.render = game.render
        self.screen = game.screen
        self.level = game.current
        self.camera = self.level.camera
        self.level.sprites.append(self)
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth
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

    def addAnimations(self, entity):
        for animationSet in self.level.animations:
            if animationSet['entity'] == entity:
                self.animations = animationSet['animations']

    def play(self, name):
        if name != self.animation['name']:
            for animation in self.animations:
                if name == animation['name']:
                    self.animation = animation
                    self.animation['frame'] = 0

    def stopAnimation(self):
        self.animation = {'name': 'default', 'sequence': [0], 'frame': 0, 'looped': True}

    def initialise(self):
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

        if hasattr(self, 'animation'):
            if self.animation['frame'] < len(self.animation['sequence']) - 6 / self.game.FPS:
                self.animation['frame'] += 6 / self.game.FPS
            else:
                if self.animation['looped']:
                    self.animation['frame'] = 0
                elif 'link' in self.animation:
                    self.play(self.animation['link'])
                else:
                    self.stopAnimation()

            sequencesFrameNumber = int(math.floor(self.animation['frame']))
            sequence = self.animation['sequence']

            self.frame = self.frameset[sequence[sequencesFrameNumber]]

        if hasattr(self, 'frame'):
            self.screen.blit(self.frame, (self.x - self.camera.x, self.z - self.y - self.height - self.camera.y, self.width, self.height + self.depth))

        if self.selected:
            selectionRectangle = pygame.Surface((self.width, self.height + self.depth))
            selectionRectangle.fill((255, 0, 0))
            selectionRectangle.set_alpha(100)
            self.screen.blit(selectionRectangle, (self.x - self.camera.x, self.z - self.y - self.height - self.camera.y))


class Static(Sprite):
    def __init__(self, game, x, y, z, width, height, depth, folder=None, image=None):
        super(Static, self).__init__(game, x, y, z, width, height, depth, folder, image)
        self.velocity = Velocity()

    def addAnimations(self, entity):
        animations = self.level.data['animations']
        for d in animations:
            if d['entity'] == entity:
                self.animations = d['animations']

    def update(self):
        self.x += int(self.velocity.x / self.game.FPS)
        self.y += int(self.velocity.y / self.game.FPS)
        self.z += int(self.velocity.z / self.game.FPS)


class Entrance(Sprite):
    def __init__(self, game, index, connection, direction, x, y, z, width, height, depth):
        super(Entrance, self).__init__(game, x, y, z, width, height, depth, None)
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
        if self.overlap(self.level.player):
            self.game.changeState(self.connection)

    def draw(self):
        pygame.draw.rect(self.screen, (70, 70, 70), (self.x - self.camera.x, self.z - self.y - self.height - self.camera.y, self.width, self.depth))
        pygame.draw.rect(self.screen, (30, 30, 30), (self.x - self.camera.x, self.z - self.y - self.height + self.depth - self.camera.y, self.width, self.height))

    def overlap(self, entity):
        if entity.x + entity.width <= self.x:
            return False
        if entity.x >= self.x + self.width:
            return False
        if entity.y + entity.height <= self.y:
            return False
        if entity.y >= self.y + self.height:
            return False
        if entity.z + entity.depth <= self.z:
            return False
        if entity.z >= self.z + self.depth:
            return False

        return True


class Dynamic(Sprite):
    def __init__(self, game, x, y, z, width, height, depth, folder=None, image=None):
        super(Dynamic, self).__init__(game, x, y, z, width, height, depth, folder, image)
        self.velocity = Velocity()

    def collide(self):
        if self.onFloor:
            self.onFloor = []

        for i in range(2):
            for entity in self.level.statics + self.level.dynamics:
                if entity == self:
                    continue

                velocity = Velocity()

                velocity.x = int((self.velocity.x - entity.velocity.x) / self.game.FPS)
                velocity.y = int((self.velocity.y - entity.velocity.y) / self.game.FPS)
                velocity.z = int((self.velocity.z - entity.velocity.z) / self.game.FPS)

                if velocity.x == 0 and velocity.y == 0 and velocity.z == 0:
                    continue

                if velocity.x > 0 and self.x > entity.x + entity.width:
                    continue
                if velocity.x < 0 and self.x + self.width < entity.x:
                    continue
                if velocity.y > 0 and self.y > entity.y + entity.height:
                    continue
                if velocity.y < 0 and self.y + self.height < entity.y:
                    continue
                if velocity.z > 0 and self.z > entity.z + entity.depth:
                    continue
                if velocity.z < 0 and self.z + self.depth < entity.z:
                    continue

                if velocity.x > 0:
                    if self.x + self.width + velocity.x < entity.x:
                        continue
                elif velocity.x < 0:
                    if self.x + velocity.x > entity.x + entity.width:
                        continue
                else:
                    if entity.x >= self.x + self.width or entity.x + entity.width <= self.x:
                        continue

                if velocity.y > 0:
                    if self.y + self.height + velocity.y < entity.y:
                        continue
                elif velocity.y < 0:
                    if self.y + velocity.y > entity.y + entity.height:
                        continue
                else:
                    if entity.y >= self.y + self.height or entity.y + entity.height <= self.y:
                        continue

                if velocity.z > 0:
                    if self.z + self.depth + velocity.z < entity.z:
                        continue
                elif velocity.z < 0:
                    if self.z + velocity.z > entity.z + entity.depth:
                        continue
                else:
                    if entity.z >= self.z + self.depth or entity.z + entity.depth <= self.z:
                        continue

                if velocity.x > 0:
                    entry_x = abs((entity.x - (self.x + self.width)) / velocity.x)
                elif velocity.x < 0:
                    entry_x = abs((self.x - (entity.x + entity.width)) / velocity.x)
                else:
                    entry_x = float('inf')

                if velocity.y > 0:
                    entry_y = abs((entity.y - (self.y + self.height)) / velocity.y)
                elif velocity.y < 0:
                    entry_y = abs((self.y - (entity.y + entity.height)) / velocity.y)
                else:
                    entry_y = float('inf')

                if velocity.z > 0:
                    entry_z = abs((entity.z - (self.z + self.depth)) / velocity.z)
                elif velocity.z < 0:
                    entry_z = abs((self.z - (entity.z + entity.depth)) / velocity.z)
                else:
                    entry_z = float('inf')

                if i == 0:
                    if abs(entry_y) < 1:
                        if abs(entry_y) < 1:
                            self.velocity.y *= entry_y

                        if self.onFloor == [] or self.onFloor:
                            self.onFloor.append(entity)
                            self.velocity.x += entity.velocity.x
                            self.velocity.z += entity.velocity.z
                else:
                    if abs(entry_x) < 1:
                        if velocity.x > 0:
                            self.velocity.x = (abs(entity.x - (self.x + self.width)) - abs(entity.velocity.x / self.game.FPS)) * self.game.FPS
                        elif velocity.x < 0:
                            self.velocity.x = (abs(self.x - (entity.x + entity.width)) + (entity.velocity.x / self.game.FPS)) * self.game.FPS
                        else:
                            self.velocity.x *= entry_x
                    if abs(entry_z) < 1:
                        if velocity.z > 0:
                            self.velocity.z = (abs(entity.z - (self.z + self.depth)) + (entity.velocity.z / self.game.FPS)) * self.game.FPS
                        elif velocity.z < 0:
                            self.velocity.z = (abs(self.z - (entity.z + entity.depth)) + (entity.velocity.z / self.game.FPS)) * self.game.FPS
                        else:
                            self.velocity.z *= entry_z

        return True

    def update(self):
        self.x += int(self.velocity.x / self.game.FPS)
        self.y += int(self.velocity.y / self.game.FPS)
        self.z += int(self.velocity.z / self.game.FPS)


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
            self.play('walk')
        elif k[pygame.K_a]:
            self.play('walk')
            self.velocity.x = -250
        else:
            self.stopAnimation()
            self.velocity.x = 0

        if k[pygame.K_s]:
            self.velocity.z = 250
        elif k[pygame.K_w]:
            self.velocity.z = -250
        else:
            self.velocity.z = 0

        if k[pygame.K_SPACE] and self.onFloor != []:
            self.velocity.y = 600

    def updateFocusSpot(self):
        x = self.x + self.width / 2 + self.velocity.x * 0.7
        y = self.z - self.y + self.depth / 2 + self.velocity.z * 0.7 - self.y - self.height / 2 + 150
        self.focusSpot.x += math.floor((x - self.focusSpot.x) / (self.game.FPS * 0.5))
        self.focusSpot.y += math.floor((y - self.focusSpot.y) / (self.game.FPS * 0.5))

def getTime():
    return pygame.time.get_ticks()

def displayingOrder(a, b):
    if a.y + a.height > b.y and a.z + a.depth > b.z:
        return 1
    else:
        return -1

def scaleImage(image, scale):
    if isinstance(scale, int) or isinstance(scale, float):
        rect = image.get_rect()
        i = pygame.transform.scale(image, (int(rect.width * scale), int(rect.height * scale)))
    else:
        i = pygame.transfrom.scale(image, scale)

    return i


def main():
    control = Control(1400, 800)
    control.run()


if __name__ == "__main__":
    main()
