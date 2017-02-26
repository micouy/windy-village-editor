from __future__ import division
from __future__ import division
import Tkinter as tk
from Tkinter import *
import pygame
import random
import math
import os

def mapToRange(value, in_min, in_max, out_min, out_max):
    return ((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

class Rectangle(object):
    def __init__(self, x = 0, y = 0, width = 0, height = 0):
        self.x = x
        self.y = y
        self.width = abs(width)
        self.height = abs(height)

class Point2D(object):
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

class Control(object):
    def __init__(self, width, height):
        self.mode = 'preview'
        self.frames = FramesManager(self, width, height)

        self.game = Game(self, width, height)
        self.sprites = self.game.sprites

    def changeMode(self, mode):
        self.mode = mode
        self.game.changeMode(mode)

    def update(self):
        self.frames.update()
        if self.mode == 'preview':
            self.game.preview()
        elif self.mode == 'play':
            self.game.update()

    def addBlock(self, x, y, width, height):
        self.game.addBlock(x, y, width, height)

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
        self.control = parent.control
        self.root = parent.root
        self.parent = parent
        self.frame = Frame(self.parent.frame, width = width, height = height)
        self.frame.grid(column = 0, row = 0)
        os.environ['SDL_WINDOWID'] = str(self.frame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'

class ControlMenu(WidgetManager):
    def __init__(self, parent):
        super(ControlMenu, self).__init__(parent, 0, 0)
        self.frame.grid_columnconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(1, weight = 1)
        self.previewMode_button = Button(self.frame, text = 'Preview', command = lambda: self.control.changeMode('preview'))
        self.previewMode_button.grid(row = 0, column = 0, sticky = W + E)
        self.playMode_button = Button(self.frame, text = 'Play', command = lambda: self.control.changeMode('play'))
        self.playMode_button.grid(row = 0, column = 1, sticky = W + E)

class AddBlockMenu(WidgetManager):
    def __init__(self, parent):
        super(AddBlockMenu, self).__init__(parent, 1, 0)
        self.x_entry = LabelEntry(self.frame, 'x: ', 0, 0)
        self.y_entry = LabelEntry(self.frame, 'y: ', 1, 0)
        self.width_entry = LabelEntry(self.frame, 'width: ', 3, 0)
        self.height_entry = LabelEntry(self.frame, 'height: ', 4 * 3, 0)

        # self.z_entry = LabelEntry(self.frame, 'z: ', 2, 0)
        # self.depth_entry = LabelEntry(self.frame, 'depth: ', 5, 0)

        self.addBlock_button = Button(self.frame, text = 'Add block', command = lambda: self.addBlock())
        self.addBlock_button.grid(row = 5, columnspan = 2, pady = 2)

        self.response_label = Label(self.frame, text = '')
        self.response_label.grid(row = 6, columnspan = 2, sticky = W, pady = 2)

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

class Game(object):
    def __init__(self, control, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((1000, 600))
        self.screen.fill(pygame.Color(255,255, 255))
        self.clock = pygame.time.Clock()
        pygame.display.init()
        self.sprites = [
            Sprite(self, 0, 0, 100, 100),
            Sprite(self, 300, 100, 100, 100),
            Sprite(self, 200, 0, 100, 100),
            Sprite(self, 100, 300, 100, 100)
        ]
        self.mouse = Mouse(self)
        self.mode = 'preview'

    def changeMode(self, mode):
        if mode == 'preview':
            self.mouse.initialise()
            self.mode = mode
            for sprite in self.sprites:
                sprite.initialise()
        elif mode == 'play':
            self.mode = mode
            for sprite in self.sprites:
                sprite.selected = False
                sprite.save()

    def preview(self):
        self.mouse.update()

        for sprite in self.sprites:
            sprite.preview()

        self.screen.fill((255, 255, 255))

        for sprite in self.sprites:
            sprite.draw()

        self.mouse.draw()

        pygame.display.update()
        self.clock.tick(60)

    def update(self):
        for sprite in self.sprites:
            sprite.update()

        self.screen.fill((255, 255, 255))

        for sprite in self.sprites:
            sprite.draw()

        pygame.display.update()
        self.clock.tick(30)

    def addBlock(self, x, y, width, height):
        self.sprites.append(Sprite(self, x, y, width, height))

class Mouse(object):
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.sprites = game.sprites
        self.x, self.y = pygame.mouse.get_pos()
        self.delta = Point2D()
        self.pressed = Point2D(None, None)
        self.selection = Rectangle()
        self.selected = []
        self.isDragging = False
        self.hasMoved = False
        self.isShift = False
        self.isUp = True
        self.isDown = False
        self.isReleased = False
        self.isPressed = False
        self.info = {'isDown': False, 'isUp': True}

    def initialise(self):
        self.x, self.y = pygame.mouse.get_pos()
        self.delta = Point2D()
        self.pressed = Point2D(None, None)
        self.selection = Rectangle()
        self.selected = []
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
                self.isPressed= True

        if self.isDown:
            if self.info['isUp']:
                self.isDown = False
                self.isUp = True
                self.isReleased = True

        if self.isReleased:
            self.pressed.x = self.pressed.y = None

        if self.isReleased:
            self.isDragging = False

        if self.isDown:
            if self.x != self.pressed.x or self.y != self.pressed.y:
                self.hasMoved = True

        if self.isPressed:
            self.pressed.x, self.pressed.y = self.x, self.y
            self.hasMoved = False
            for sprite in self.sprites:
                if (sprite.x < self.x
                and sprite.x + sprite.width > self.x
                and sprite.y < self.y
                and sprite.y + sprite.height > self.y):
                    if not sprite in self.selected:
                        if not self.isShift:
                            for selected in self.selected:
                                selected.selected = False
                                self.selected = []
                        self.selected.append(sprite)
                        sprite.selected = True
                    self.isDragging = True
                    break
            else:
                if not self.isShift:
                    for sprite in self.selected:
                        sprite.selected = False
                        self.selected = []

        if not self.isDragging:
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

        if self.selection.width > 0 and self.selection.height > 0:
            for sprite in self.sprites:
                if (self.selection.x - sprite.width / 4 * 3 <= sprite.x
                and self.selection.x + self.selection.width + sprite.width / 4 * 3 >= sprite.x + sprite.width
                and self.selection.y - sprite.width / 4 * 3 <= sprite.y
                and self.selection.y + self.selection.height + sprite.width / 4 * 3 >= sprite.y + sprite.height):
                    if not sprite in self.selected:
                        self.selected.append(sprite)
                        sprite.selected = True
                elif sprite in self.selected and not self.isShift:
                    self.selected.remove(sprite)
                    sprite.selected = False

        if self.isDragging:
            for sprite in self.selected:
                sprite.x += self.delta.x
                sprite.y += self.delta.y

    def get(self):
        return {'up': self.up, 'down': self.down, 'released': self.released, 'pressed': self.pressed}

    def draw(self):
        if self.selection.width and self.selection.height:
            selectionRectangle = pygame.Surface((self.selection.width, self.selection.height))
            selectionRectangle.fill((0, 100, 155))
            selectionRectangle.set_alpha(50)
            self.screen.blit(selectionRectangle, (self.selection.x, self.selection.y))
            pygame.draw.rect(self.screen, (100, 150, 255), (self.selection.x, self.selection.y, self.selection.width, self.selection.height), 1)

class Sprite(object):
    def __init__(self, game, x, y, width, height):
        self.original = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        self.game = game
        self.screen = game.screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_x = 9
        self.velocity_y = 5
        self.selected = False

    def initialise(self):
        self.x = self.original['x']
        self.y = self.original['y']
        self.width = self.original['width']
        self.height = self.original['height']

    def update(self):
        if self.x + self.width + self.velocity_x > self.game.width or self.x + self.velocity_x < 0:
            self.velocity_x *= -1
        if self.y + self.height + self.velocity_y > self.game.height or self.y + self.velocity_y < 0:
            self.velocity_y *= -1
        self.x += self.velocity_x
        self.y += self.velocity_y

    def preview(self):
        pass

    def save(self):
        self.original['x'] = self.x
        self.original['y'] = self.y
        self.original['width'] = self.width
        self.original['height'] = self.height

    def draw(self):
        if self.selected:
            pygame.draw.rect(self.screen, (50, 100, 150), (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height))

def main():
    control = Control(1000, 600)

    while True:
        control.update()

if __name__ == '__main__':
    main()
