from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
#

from maze_explorer import MazeExplorer

# Gym integration
#def act(action):
#    # FIXME: buttons... context.
#
#    # Reset other buttons
#    if k in self.buttons:
#        self.buttons[k] = 0
#
#    self.buttons[action] = 1
#
#    # Do something
#    step()
#
#    # FIXME: player... context.
#    reward = self.player.stats['reward']
#    self.player.stats['reward'] = 0
#    return reward
#
#def step():
#    pyglet.clock.tick()
#
#    for window in pyglet.app.windows:
#        window.switch_to()
#        window.dispatch_events()
#        window.dispatch_event('on_draw')
#        window.flip()
#
#    # TODO: Return `reward, state` etc.
#    # TODO: Doing this in another layer, `act` returns reward only
#    # reward = self.reward
#    # self.reward = 0
#    # TODO: Trace `done`, setting terminal state elsewhere.

def main(argv):

    engine = MazeExplorer()

    engine.start()


if __name__ == "__main__":
   main(sys.argv[1:])
