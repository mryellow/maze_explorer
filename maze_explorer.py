from __future__ import division, print_function, unicode_literals

import pyglet
#from pyglet.gl import *

import cocos
from cocos.director import director

import config
from message import MessageLayer
from world import WorldLayer

class MazeExplorer():
    """
    Wrapper for game engine
    """

    def __init__(self):
        self.director = director
        self.director.init(**config.settings['window'])
        #pyglet.font.add_directory('.') # adjust as necessary if font included
        self.z = 0

    def create_scene(self):
        self.scene = cocos.scene.Scene()
        self.z = 0

        palette = config.settings['view']['palette']
        #Player.palette = palette
        r, g, b = palette['bg']
        self.scene.add(cocos.layer.ColorLayer(r, g, b, 255), z=self.z)
        self.z += 1
        message_layer = MessageLayer()
        self.scene.add(message_layer, z=self.z)
        self.z += 1
        world_layer = WorldLayer(fn_show_message=message_layer.show_message)
        self.scene.add(world_layer, z=self.z)
        self.z += 1

    def start(self):
        self.create_scene()
        return self.director.run(self.scene)
