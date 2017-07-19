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

        #print(template)

        # Start within borders
        self.recursive_division(template.cells, 3, 50-2, 50-2, 1, 1)

        #return ti.load(os.path.join(script_dir, 'logs', filename))['map0']
        return template

    def recursive_division(self, cells, min_size, width, height, x=0, y=0):
        #print(width, height, x, y)
        #if width - x <= min_size * 2 or height - y <= min_size * 2:
        #    return
        if width <= min_size or height <= min_size:
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

        if cut_size-min_size < min_size:
            return
        if gap_size-min_size < min_size:
            return

        # Random division and doorway
        print('cut/gap', min_size, cut_size-min_size, gap_size-min_size)
        cut = randint(min_size, cut_size-min_size)
        gap = randint(min_size, gap_size-min_size)

        if not (cut > 0 and gap > 0):
            print('small', cut, gap)
            return

        print(x,y,cut)

        for i in xrange(0, gap_size):
            # TODO: make 1 depend on `door_size`
            #if abs(gap - i) > 1:
            if abs(gap - i) > 0:
                # Copy wall tile from (0,0)
                if axis == HORIZONTAL:
                    print([x+i, y+cut])
                    cells[x+i][y+cut].tile = cells[0][0].tile
                else:
                    print([x+cut, y+i])
                    cells[x+cut][y+i].tile = cells[0][0].tile

        print(x, y, [cut, gap], [cut_size, gap_size], 'H' if (axis == HORIZONTAL) else 'V')


        nx, ny = x, y
        w, h = [cut, height] if (axis == HORIZONTAL) else [width, cut]
        self.recursive_division(cells, min_size, w, h, nx, ny)
        #print('a', nx, ny, w, h)

        nx, ny = [x-cut, y] if (axis == HORIZONTAL) else [x, y-cut]
        w, h = [cut_size-cut, height] if (axis == HORIZONTAL) else [width, cut_size-cut]
        self.recursive_division(cells, min_size, w, h, nx, ny)

        # FIXME: Wall in a doorway..

        #print(cut, cut_size, cut_size-cut)
        #nx, ny = [x+cut, y] if (axis == HORIZONTAL) else [x, y+cut]
        #w, h = [cut_size-cut, height] if (axis == HORIZONTAL) else [width, cut_size-cut]
        #self.recursive_division(cells, min_size, w, h, nx, ny)
        #print('b', nx, ny, w, h)
