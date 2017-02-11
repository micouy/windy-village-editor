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

class Control(object):
    def __init__(self, width, height):
        self.mode = 'edit' # edit / preview
        self.frames = FrameManager(self, width, height)
        self.game = Game(self, width, height)
        self.sprites = self.game.sprites

    def update(self):
        self.frames.update()
        self.game.update()

    def addBlock(self, x, y, width, height):
        s = Sprite(self.game, x, y, width, height)

class FrameManager(object):
    def __init__(self, control, width, height):
        self.control = control
        self.width = width + 200
        self.height = height + 50
        self.root = tk.Tk()
        self.mainFrame = Frame(self.root, width = width, height = height)
        self.mainFrame.grid(columnspan = width, rowspan = 500)
        self.mainFrame.pack(side = LEFT)
        os.environ['SDL_WINDOWID'] = str(self.mainFrame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'

        self.addBlockDoc = AddBlockDoc(self)

    def update(self):
        self.root.update()

class AddBlockDoc(object):
    def __init__(self, parent):
        self.root = parent.root
        self.control = parent.control
        self.parent = parent
        self.frame = Frame(self.root, width = 75, height = self.parent.height)
        self.frame.pack(side = LEFT)
        self.x_entry = LabelEntry(self.frame, 'x: ', 0, 0)
        self.y_entry = LabelEntry(self.frame, 'y: ', 1, 0)
        # self.z_entry = LabelEntry(self.frame, 'z: ', 2, 0)
        self.width_entry = LabelEntry(self.frame, 'width: ', 3, 0)
        self.height_entry = LabelEntry(self.frame, 'height: ', 4, 0)
        # self.depth_entry = LabelEntry(self.frame, 'depth: ', 5, 0)

        self.addBlock_button = Button(self.frame, text = 'Add block', command = lambda: self.addBlock())
        self.addBlock_button.grid(row = 5)

        self.response_label = Label(self.frame, text = '')
        self.response_label.grid(row = 6, columnspan = 2, sticky = W)

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
        self.label.grid(row = row, column = column, sticky = W)
        self.entry = Entry(parent, width = width)
        self.entry.grid(row = row, column = column + 1)

    def get(self):
        return self.entry.get()

    def delete(self):
        self.entry.delete(0, 'end')

class Game(object):
    def __init__(self, control, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width,height))
        self.screen.fill(pygame.Color(255,255,255))
        self.clock = pygame.time.Clock()
        pygame.display.init()
        self.sprites = []
        self.mouse = {'ispressed': False, 'pressed': (), 'current': ()}

    def update(self):
        self.mouse['current'] = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse['pressed'] = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse['pressed'] = None

        for sprite in self.sprites:
            sprite.update()

        self.screen.fill((255, 255, 255))

        for sprite in self.sprites:
            sprite.draw()

        if self.mouse['pressed']:
            px, py = self.mouse['pressed']
            cx, cy = self.mouse['current']
            pygame.draw.rect(self.screen, (0, 50, 255), (min(cx, px), min(cy, py), abs(cx - px), abs(cy - py)))

        pygame.display.update()
        self.clock.tick(30)

class Mouse(object):
    def __init__(self):
        self.x, self.y = pygame.mouse.get_pos()
        self.pressed = False
        self.pressed_x, self.pressed_y = ()

    def upadate(self):
        for event in pygame.event.get():
        self.x, self.y = pygame.mouse.get_pos()
        self.pressed = False
        self.pressed_x, self.pressed_y = ()

class Sprite(object):
    def __init__(self, game, x, y, width, height):
        self.game = game
        self.screen = game.screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_x = 9
        self.velocity_y = 5
        self.game.sprites.append(self)

    def update(self):
        if self.x + self.width + self.velocity_x > self.game.width or self.x + self.velocity_x < 0:
            self.velocity_x *= -1
        if self.y + self.height + self.velocity_y > self.game.height or self.y + self.velocity_y < 0:
            self.velocity_y *= -1
        self.x += self.velocity_x
        self.y += self.velocity_y

    def draw(self):
        pygame.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height))

def main():
    control = Control(1000, 600)

    while True:
        control.update()

if __name__ == '__main__':
    main()
