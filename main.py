from __future__ import division
import Tkinter as tk
from Tkinter import *
from game_lib import *
import pygame
import random
import math
import os

root = tk.Tk()
embed = tk.Frame(root, width = 500, height = 500) #creates embed frame for pygame window
embed.grid(columnspan = (600), rowspan = 500) # Adds grid
embed.pack(side = LEFT) #packs window to the left
buttonwin = tk.Frame(root, width = 75, height = 500)
buttonwin.pack(side = LEFT)
os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
os.environ['SDL_VIDEODRIVER'] = 'windib'
screen = pygame.display.set_mode((500,500))
screen.fill(pygame.Color(255,255,255))
pygame.display.init()
pygame.display.update()

def draw():
    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (0,0,0), (random.randint(0, 100) + 200, random.randint(0, 100) + 200), 125)
    pygame.display.update()
    root.update()

button1 = Button(buttonwin,text = 'Draw',  command=draw)
button1.pack(side=LEFT)

while True:
    pygame.display.update()
    root.update()
