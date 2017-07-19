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

    def __init__(self, visible = True):
        config.settings['window']['visible'] = visible

        self.director = director
        self.director.init(**config.settings['window'])
        #pyglet.font.add_directory('.') # adjust as necessary if font included
        self.z = 0

        self.actions_num = len(config.settings['world']['bindings'])

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
        self.world_layer = WorldLayer(fn_show_message=message_layer.show_message)
        self.scene.add(self.world_layer, z=self.z)
        self.z += 1

        self.director._set_scene(self.scene)

    def act(self, action):
        assert isinstance(action, int)
        #assert self.action_space.contains(action), "%r (%s) invalid"%(action, type(action))

        # Reset other buttons
        for k in self.world_layer.buttons:
            self.world_layer.buttons[k] = 0

        key = sorted(self.world_layer.buttons.keys())[action]

        # Set action for next step
        self.world_layer.buttons[key] = 1

        # Act in the environment
        self.step()

        # Return reward and reset for next step
        reward = self.world_layer.player.stats['reward']
        self.world_layer.player.stats['reward'] = 0

        # TODO: Return actual action taken, observation and reward
        info = {}
        observation = []
        return observation, reward, self.world_layer.player.game_over, info

    def step(self):
        self.director.window.switch_to()
        self.director.window.dispatch_events()
        self.director.window.dispatch_event('on_draw')
        self.director.window.flip()

        # Ticking before events caused glitches.
        pyglet.clock.tick()

        #for window in pyglet.app.windows:
        #    window.switch_to()
        #    window.dispatch_events()
        #    window.dispatch_event('on_draw')
        #    window.flip()

    def run(self):
        self.create_scene()
        return self.director.run(self.scene)
