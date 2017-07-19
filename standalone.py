from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
#

from random import randint

from maze_explorer import MazeExplorer

def main(argv):

    engine = MazeExplorer()
    if '-r' in argv or '--random' in argv:
        print('Random test agent...')

        engine.create_scene()

        while not engine.director.window.has_exit:
            action = randint(0, engine.actions_num)
            reward = engine.act(action)
            print(action, reward)
    elif '-s' in argv or '--step' in argv:
        print('Step by step...')
        engine.create_scene()
        #while not engine.director.window.has_exit:
            #engine.step()
    else:
        engine.start()

if __name__ == "__main__":
   main(sys.argv[1:])
