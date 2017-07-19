import time
from random import randint

import cocos
import cocos.tiles as ti

import os
script_dir = os.path.dirname(__file__)

HORIZONTAL = 0
VERTICAL = 1

class Generator():
    def map(self):
        template = ti.load(os.path.join(script_dir, 'template.tmx'))['map0']
        template.set_view(0, 0, template.px_width, template.px_height)

        epoch = int(time.time())
        filename = 'map_' + str(epoch) + '.tmx'

        print(template)

        # Start within borders
        self.recursive_division(template.cells, 3, 50-2, 50-2, 1, 1)

        #return ti.load(os.path.join(script_dir, 'logs', filename))['map0']
        return template

    def recursive_division(self, cells, min_size, width, height, x=0, y=0):
        #print(width, height, x, y)
        if width - x <= min_size * 2 or height - y <= min_size * 2:
            return

        # Choose axis to divide
        if width < height:
            axis = VERTICAL
        elif height < width:
            axis = HORIZONTAL
        else:
            axis = randint(0,1)

        cut_size = height
        gap_size = width
        if axis == HORIZONTAL:
            cut_size = width
            gap_size = height

        # Random division and doorway
        cut = randint(min_size, cut_size-min_size)
        gap = randint(min_size, gap_size-min_size)

        if not (cut > 0 and gap > 0):
            print('small', cut, gap)
            return

        for i in xrange(0, gap_size):
            # FIXME: make 1 depend on `min_size`
            if abs(gap - i) > 1:
                # Copy wall tile from (0,0)
                if axis == HORIZONTAL:
                    cells[x+i][y+cut].tile = cells[0][0].tile
                else:
                    cells[x+cut][y+i].tile = cells[0][0].tile

        print(x, y, cut, cut_size, gap, gap_size, 'H' if (axis == HORIZONTAL) else 'V')

        nx, ny = x, y
        w, h = [cut, height] if (axis == HORIZONTAL) else [width, cut]
        self.recursive_division(cells, min_size, w, h, nx, ny)

        #nx, ny = [x+cut, y] if (axis == HORIZONTAL) else [x, y+cut]
        #w, h = [width-cut, height] if (axis == HORIZONTAL) else [width, height-cut]
        #self.recursive_division(cells, min_size, w, h, nx, ny)
