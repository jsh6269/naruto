import pygame
from pygame.transform import rotozoom, flip


def form(x):
    width = 1425
    if x > width - 250:
        return width - 250
    elif x < -30:
        return -30
    else:
        return int(x)


def get_img(name, num=None, ang=0, mag=0.8, isflip=False):
    loc = './naruto'
    if num is None:
        if not isflip:
            return rotozoom(pygame.image.load('{}/{}.png'.format(loc, name)), ang, mag)
        else:
            return rotozoom(flip(pygame.image.load('{}/{}.png'.format(loc, name)), True, False), ang, mag)
    elif not isflip:
        return [rotozoom(pygame.image.load('{}/{} ({}).png'.format(loc, name, idx)), ang, mag)
                for idx in range(1, num+1)]
    else:
        return [rotozoom(flip(pygame.image.load('{}/{} ({}).png'.format(loc, name, idx)), True, False), ang, mag)
                for idx in range(1, num+1)]
