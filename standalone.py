from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
#

import random
import math

import pyglet
from pyglet.window import key
from pyglet.gl import *

import cocos
from cocos.director import director
#from cocos import draw
# TODO: Replace with straight up CircleShape
#import cocos.collision_model as cm
#import cocos.mapcolliders as mc
#import cocos.euclid as eu
#import cocos.actions as ac
#import cocos.tiles as ti
#from cocos.rect import Rect

import config
from message import MessageLayer
from world import WorldLayer

def reflection_y(a):
    assert isinstance(a, eu.Vector2)
    return eu.Vector2(a.x, -a.y)


# Gym integration
def act(action):
    # FIXME: buttons... context.

    # Reset other buttons
    if k in self.buttons:
        self.buttons[k] = 0

    self.buttons[action] = 1

    # Do something
    step()

    # FIXME: player... context.
    reward = self.player.stats['reward']
    self.player.stats['reward'] = 0
    return reward

def step():
    pyglet.clock.tick()

    for window in pyglet.app.windows:
        window.switch_to()
        window.dispatch_events()
        window.dispatch_event('on_draw')
        window.flip()

    # TODO: Return `reward, state` etc.
    # TODO: Doing this in another layer, `act` returns reward only
    # reward = self.reward
    # self.reward = 0
    # TODO: Trace `done`, setting terminal state elsewhere.

def main(argv):

    # make window
    director.init(**config.settings['window'])
    #pyglet.font.add_directory('.') # adjust as necessary if font included
    scene = cocos.scene.Scene()
    z = 0

    palette = config.settings['view']['palette']
    #Player.palette = palette
    r, g, b = palette['bg']
    scene.add(cocos.layer.ColorLayer(r, g, b, 255), z=z)
    z += 1
    message_layer = MessageLayer()
    scene.add(message_layer, z=z)
    z += 1
    world_layer = WorldLayer(fn_show_message=message_layer.show_message)
    scene.add(world_layer, z=z)
    z += 1

    if '-s' in argv or '--step' in argv:
        print('Waiting for step...')
        director._set_scene(scene)
        # TODO: Sleep and step externally.
    else:
        print('Running event loop...')
        director.run(scene)

if __name__ == "__main__":
   main(sys.argv[1:])
