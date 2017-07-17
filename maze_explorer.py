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
from cocos import draw
# TODO: Replace with straight up CircleShape
import cocos.collision_model as cm
import cocos.mapcolliders as mc
import cocos.euclid as eu
import cocos.actions as ac
import cocos.tiles as ti
from cocos.rect import Rect

tile_size = 10
tiles_x = 50
tiles_y = 50

fe = 1.0e-4
consts = {
    "window": {
        "width": 500,
        "height": 500,
        "vsync": True,
        "resizable": False
    },
    "world": {
        "width": tile_size * tiles_x,
        "height": tile_size * tiles_y,
        "rPlayer": tile_size / 2,
        #"wall_scale_min": 0.75,  # relative to player
        #"wall_scale_max": 2.25,  # relative to player
        "topSpeed": 100.0,
        "angular_velocity": 240.0,  # degrees / s
        "accel": 85.0,
        "deaccel": 5.0,
        "bindings": {
            key.LEFT: 'left',
            key.RIGHT: 'right',
            key.UP: 'up',
        },
        "battery": {
            "angular": 0.04,
            "linear": 0.05
        },
        "reward": {
            "explore": 1.0
        }
    },
    "view": {
        # as the font file is not provided it will decay to the default font;
        # the setting is retained anyway to not downgrade the code
        "font_name": 'Axaxax',
        "palette": {
            'bg': (0, 65, 133),
            'player': (237, 27, 36),
            'wall': (247, 148, 29),
            'gate': (140, 198, 62),
            'food': (140, 198, 62)
        }
    }
}

# world to view scales
scale_x = consts["window"]["width"] / consts["world"]["width"]
scale_y = consts["window"]["height"] / consts["world"]["height"]

def world_to_view(v):
    """world coords to view coords; v an eu.Vector2, returns (float, float)"""
    return v.x * scale_x, v.y * scale_y

class Player(cocos.sprite.Sprite):
    palette = {}  # injected later

    def __init__(self, cx, cy, radius, btype, img, vel=None):
        super(Player, self).__init__(img)
        # the 1.05 so that visual radius a bit greater than collision radius
        self.scale = (radius * 1.05) * scale_x / (self.image.width / 2.0)
        self.btype = btype
        self.color = self.palette[btype]
        self.cshape = cm.CircleShape(eu.Vector2(cx, cy), radius)
        self.update_center(self.cshape.center)
        if vel is None:
            vel = eu.Vector2(0.0, 0.0)
        self.vel = vel

    def update_center(self, cshape_center):
        """cshape_center must be eu.Vector2"""
        assert isinstance(cshape_center, eu.Vector2)

        self.position = world_to_view(cshape_center)
        self.cshape.center = cshape_center

    def calc_move(self, dt, vel):
        assert isinstance(vel, eu.Vector2)

        old = self.cshape.center
        remaining_dt = dt
        new = old.copy()

        while remaining_dt > 1.e-6:
            new = old + remaining_dt * vel
            consumed_dt = remaining_dt
            # what about screen boundaries ? if colision bounce
            #if new.x < r:
            #    consumed_dt = (r - ppos.x) / newVel.x
            #    new = ppos + consumed_dt * newVel
            #    newVel = -reflection_y(newVel)
            #if new.x > (self.width - r):
            #    consumed_dt = (self.width - r - ppos.x) / newVel.x
            #    new = ppos + consumed_dt * newVel
            #    newVel = -reflection_y(newVel)
            #if new.y < r:
            #    consumed_dt = (r - ppos.y) / newVel.y
            #    new = ppos + consumed_dt * newVel
            #    newVel = reflection_y(newVel)
            #if new.y > (self.height - r):
            #    consumed_dt = (self.height - r - ppos.y) / newVel.y
            #    new = ppos + consumed_dt * newVel
            #    newVel = reflection_y(newVel)
            remaining_dt -= consumed_dt

        # Upper left corner of Rect
        new.x -= self.cshape.r
        new.y -= self.cshape.r

        return new

    def get_rect(self):
        ppos = self.cshape.center
        r = self.cshape.r

        return Rect(ppos.x-r, ppos.y-r, r*2, r*2)

class MessageLayer(cocos.layer.Layer):

    """Transitory messages over WorldLayer

    Responsability:
    full display cycle for transitory messages, with effects and
    optional callback after hiding the message.
    """

    def show_message(self, msg, callback=None):
        w, h = director.get_window_size()

        self.msg = cocos.text.Label(msg,
                                    font_size=52,
                                    font_name=consts['view']['font_name'],
                                    anchor_y='center',
                                    anchor_x='center',
                                    width=w,
                                    multiline=True,
                                    align="center")
        self.msg.position = (w / 2.0, h)

        self.add(self.msg)

        actions = (
            ac.Show() + ac.Accelerate(ac.MoveBy((0, -h / 2.0), duration=0.5)) +
            ac.Delay(1) +
            ac.Accelerate(ac.MoveBy((0, -h / 2.0), duration=0.5)) +
            ac.Hide()
        )

        if callback:
            actions += ac.CallFunc(callback)

        self.msg.do(actions)

def reflection_y(a):
    assert isinstance(a, eu.Vector2)
    return eu.Vector2(a.x, -a.y)

class WorldLayer(cocos.layer.Layer, mc.RectMapCollider):

    """
    Responsabilities:
        Generation: random generates a level
        Initial State: Set initial playststate
        Play: updates level state, by time and user input. Detection of
        end-of-level conditions.
        Level progression.
    """
    is_event_handler = True

    def __init__(self, fn_show_message=None):
        super(WorldLayer, self).__init__()
        self.fn_show_message = fn_show_message

        # basic geometry
        world = consts['world']
        self.width = world['width']  # world virtual width
        self.height = world['height']  # world virtual height
        self.rPlayer = world['rPlayer']  # player radius in virtual space
        #self.wall_scale_min = world['wall_scale_min']
        #self.wall_scale_max = world['wall_scale_max']
        self.topSpeed = world['topSpeed']
        self.angular_velocity = world['angular_velocity']
        self.accel = world['accel']
        self.deaccel = world['deaccel']

        self.battery_use = world['battery']
        self.reward_explore = world['reward']['explore']
        self.battery = 100
        self.reward = 0

        self.bindings = world['bindings']
        buttons = {}
        for k in self.bindings:
            buttons[self.bindings[k]] = 0
        self.buttons = buttons

        # load resources:
        pics = {}
        pics["player"] = pyglet.resource.image('player7.png')
        #pics["food"] = pyglet.resource.image('circle6.png')
        #pics["wall"] = pyglet.resource.image('circle6.png')
        self.pics = pics

        #cell_size = self.rPlayer * self.wall_scale_max * 2.0 * 1.25
        #cell_size = self.rPlayer * 0.1
        #self.collman = cm.CollisionManagerGrid(0.0, self.width,
        #                                       0.0, self.height,
        #                                       cell_size, cell_size)

        #self.toRemove = set()

        self.on_bump_handler = self.on_bump_slide

        self.schedule(self.update)
        self.ladder_begin()

    def ladder_begin(self):
        self.level_num = 0
        self.empty_level()
        #msg = 'Maze Explorer'
        #self.fn_show_message(msg, callback=self.level_launch)
        self.level_launch()

    def level_launch(self):
        self.generate_random_level()
        #msg = 'level %d' % self.level_num
        #self.fn_show_message(msg, callback=self.level_start)
        self.level_start()

    def level_start(self):
        self.win_status = 'undecided'

    def level_conquered(self):
        self.win_status = 'intermission'
        msg = 'level %d\nconquered !' % self.level_num
        # TODO: Set `done`.
        self.fn_show_message(msg, callback=self.level_next)

    def level_losed(self):
        self.win_status = 'losed'
        msg = 'ouchhh !!!'
        # TODO: Set `done`.
        self.fn_show_message(msg, callback=self.ladder_begin)

    def level_next(self):
        self.empty_level()
        self.level_num += 1
        self.level_launch()

    def empty_level(self):
        # del old actors, if any
        for node in self.get_children():
            self.remove(node)
        assert len(self.children) == 0
        self.player = None
        self.gate = None
        #self.food_cnt = 0
        #self.toRemove.clear()

        self.win_status = 'intermission'  # | 'undecided' | 'conquered' | 'losed'

        # player phys params
        self.topSpeed = 75.0  # 50.
        self.impulse_dir = eu.Vector2(0.0, 1.0)
        self.impulseForce = 0.0

    def generate_random_level(self):
        # hardcoded params:
        #food_num = 5
        #food_scale = 1.0  # relative to player
        #wall_num = 10
        #gate_scale = 1.5  # relative to player
        #min_separation_rel = 3.0  # as fraction of player diameter

        # build !
        width = self.width
        height = self.height
        rPlayer = self.rPlayer
        #min_separation = min_separation_rel * rPlayer
        #wall_scale_min = self.wall_scale_min
        #wall_scale_max = self.wall_scale_max
        pics = self.pics
        z = 0

        # add walls
        self.map_layer = ti.load('test.tmx')['map0']
        self.map_layer.set_view(0, 0, self.map_layer.px_width, self.map_layer.px_height)
        # FIXME: Separate `scale_x` and `scale_y`
        self.map_layer.scale = scale_x
        self.add(self.map_layer, z=z)
        z += 1

        # add floor
        self.visit_layer = ti.load('ones.tmx')['map0']
        for i in xrange(0, len(self.map_layer.cells)):
            for j in xrange(0, len(self.map_layer.cells[i])):
                col = self.map_layer.cells[i][j]
                # If wall exists, remove floor
                if col.tile and col.tile.id > 0:
                    self.visit_layer.cells[i][j].tile = None

        self.visit_layer.set_view(0, 0, self.visit_layer.px_width, self.visit_layer.px_height)
        # FIXME: Separate `scale_x` and `scale_y`
        self.visit_layer.scale = scale_x
        self.add(self.visit_layer, z=-1)

        # add player
        cx, cy = (0.5 * width, 0.5 * height)
        self.player = Player(cx, cy, rPlayer, 'player', pics['player'])
        self.add(self.player, z=z)
        z += 1

        #self.collman.add(self.map_layer)
        #self.collman.add(self.player)

        #minSeparation = min_separation * 2. * rPlayer

        # add gate
        #rGate = gate_scale * rPlayer
        #self.gate = Player(cx, cy, rGate, 'gate', pics['wall'])
        #self.gate.color = Player.palette['wall']
        #cntTrys = 0
        #while cntTrys < 100:
        #    cx = rGate + random.random() * (width - 2.0 * rGate)
        #    cy = rGate + random.random() * (height - 2.0 * rGate)
        #    self.gate.update_center(eu.Vector2(cx, cy))
        #    if not self.collman.they_collide(self.player, self.gate):
        #        break
        #    cntTrys += 1
        #self.add(self.gate, z=z)
        #z += 1
        #self.collman.add(self.gate)

        # add food
        #rFood = food_scale * rPlayer
        #self.cnt_food = 0
        #for i in range(food_num):
        #    food = Player(cx, cy, rFood, 'food', pics['food'])
        #    cntTrys = 0
        #    while cntTrys < 100:
        #        cx = rFood + random.random() * (width - 2.0 * rFood)
        #        cy = rFood + random.random() * (height - 2.0 * rFood)
        #        food.update_center(eu.Vector2(cx, cy))
        #        if self.collman.any_near(food, min_separation) is None:
        #            self.cnt_food += 1
        #            self.add(food, z=z)
        #            z += 1
        #            self.collman.add(food)
        #            break
        #        cntTrys += 1

        # add walls
        #for i in range(wall_num):
        #    s = random.random()
        #    r = rPlayer * (wall_scale_min * s + wall_scale_max * (1.0 - s))  # lerp
        #    wall = Player(cx, cy, r, 'wall', pics['wall'])
        #    cntTrys = 0
        #    while cntTrys < 100:
        #        cx = r + random.random() * (width - 2.0 * r)
        #        cy = r + random.random() * (height - 2.0 * r)
        #        wall.update_center(eu.Vector2(cx, cy))
        #        if self.collman.any_near(wall, min_separation) is None:
        #            self.add(wall, z=z)
        #            z += 1
        #            self.collman.add(wall)
        #            break
        #        cntTrys += 1

    def update(self, dt):
        # if not playing dont update model
        if self.win_status != 'undecided':
            return

        # update target
        buttons = self.buttons
        ma = buttons['right'] - buttons['left']
        if ma != 0:
            self.battery -= self.battery_use['angular']
            self.player.rotation += ma * dt * self.angular_velocity

        a = math.radians(self.player.rotation)
        self.impulse_dir = eu.Vector2(math.sin(a), math.cos(a))

        newVel = self.player.vel

        # Redirect existing vel to new direction.
        nv = newVel.magnitude()
        newVel = nv * self.impulse_dir

        mv = buttons['up']
        if mv != 0:
            self.battery -= self.battery_use['linear']
            newVel += dt * mv * self.accel * self.impulse_dir
            nv = newVel.magnitude()
            if nv > self.topSpeed:
                newVel *= self.topSpeed / nv
        else:
            newVel += dt * self.deaccel * -newVel

        # Position collision rects
        oldRect = self.player.get_rect()
        newRect = oldRect.copy()
        newRect.x, newRect.y = self.player.calc_move(dt, newVel)

        # Debugging, Can I rotate Rects for collision?
        #myOldRect = oldRect.copy()
        #myOldRect.width = 200
        #myOldRect.rotation = self.player.rotation + 90
        #myNewRect = myOldRect.copy()
        #myNewRect.x, myNewRect.y = self.player.calc_move(dt, newVel)
        #print('myNewRect', myNewRect, myNewRect.rotation)
        #myModVel = self.collide_map(self.map_layer, myOldRect, myNewRect, newVel.x, newVel.y)

        # Update position with new velocity
        newVel.x, newVel.y = self.collide_map(self.map_layer, oldRect, newRect, newVel.x, newVel.y)
        newPos = self.player.cshape.center
        newPos.x, newPos.y = newRect.center

        # Collision detected
        if self.bumped_x or self.bumped_y:
            # TODO: Episode over?
            print("bumped", newVel, self.bumped_x, self.bumped_y)

        self.player.vel = newVel
        self.player.update_center(newPos)

        self.update_visited(newPos)

        print('battery', self.battery)

        a = math.radians(self.player.rotation)
        disFor = self.distance_to_tile(newPos, a)
        #disLeft = self.distance_to_tile(newPos, (math.pi/4)+a)
        #disRight = self.distance_to_tile(newPos, -(math.pi/4)+a)
        print('dis', disFor)


        # update collman
        #self.collman.clear()
        #for z, node in self.children:
        #    self.collman.add(node)

        # interactions player - others
        #for other in self.collman.iter_colliding(self.player):
        #    print('collman', other)
        #    typeball = other.btype

        #    if typeball == 'food':
        #        self.toRemove.add(other)
        #        self.cnt_food -= 1
        #        if not self.cnt_food:
        #            self.open_gate()
        #
        #    elif (typeball == 'wall' or
        #          typeball == 'gate' and self.cnt_food > 0):
        #        self.level_losed()
        #
        #    elif typeball == 'gate':
        #        self.level_conquered()



        # at end of frame do removes; as collman is fully regenerated each frame
        # theres no need to update it here.
    #    for node in self.toRemove:
    #        self.remove(node)
    #    self.toRemove.clear()

    def update_visited(self, pos):
        assert isinstance(pos, eu.Vector2)

        def set_visited(layer, cell):
            if not cell.properties.get('visited') and cell.tile and cell.tile.id > 0:
                cell.properties['visited'] = True

                # Adjust next reward for exploration
                self.reward += self.reward_explore

                # Change colour of visited cells
                key = layer.get_key_at_pixel(cell.x, cell.y)
                #layer.set_cell_color(key[0], key[1], [155,155,155])
                layer.set_cell_opacity(key[0], key[1], 255*0.8)

        # Get the current tile under player
        current = self.visit_layer.get_at_pixel(pos.x, pos.y)
        set_visited(self.visit_layer, current)

        neighbours = self.visit_layer.get_neighbors(current)
        for cell in neighbours:
            neighbour = neighbours[cell]
            set_visited(self.visit_layer, neighbour)

        print('reward', self.reward)

    # Find line intersects next tile
    def distance_to_tile(self, point, direction, length = 50):
        assert isinstance(point, eu.Vector2)
        assert isinstance(direction, int) or isinstance(direction, float)
        assert isinstance(length, int) or isinstance(length, float)

        # Given `point`, look for where inersects with next boundary (`y % 10`) in `direction`
        def search_grid(search_x, search_y, rad, depth=5):
            if depth == 0:
                return
            depth -= 1

            m = math.tan(rad) # Slope
            sin = math.sin(rad)
            cos = math.cos(rad)

            boundary_x = self.map_layer.tw - (search_x % self.map_layer.tw)
            boundary_y = self.map_layer.th - (search_y % self.map_layer.th)

            # top
            if cos > 0 and False:
                boundary_y = search_y + boundary_y

            # bottom
            if cos < 0 and False:
                boundary_y = search_y - boundary_y

            # Intersect with horizontal line
            if cos > 0 or cos < 0:
                print('boundary_y', search_x, boundary_y)
                new_x = -m * (search_y - boundary_y) + search_x
                #print('new_x', new_x)
                start = search_x, search_y
                end = new_x, boundary_y

            # right
            if sin > 0:
                boundary_x = search_x + boundary_x

            # left
            if sin < 0:
                boundary_x = search_x - boundary_x

            if sin > 0 or sin < 0:
                print('boundary_x', search_x, boundary_x)
                new_y = ((boundary_x - search_x) / m) + search_y
                #print('new_y', new_y)
                start = search_x, search_y
                end = boundary_x, new_y

            if end:
                print('line', start, end)
                line = draw.Line(start, end, (155,155,155,155))
                self.map_layer.add(line)

                cell = self.map_layer.get_at_pixel(end[0], end[1])
                if cell and cell.tile and cell.tile.id > 0:
                    print('cell', cell.tile.id)
                #else:
                    # Recurse
                    #search_grid(end[0]+1, end[1]+1, rad, depth)

        # Start at `point`, check tile under each pixel
        search_grid(point.x, point.y, direction)

        #x = point.x
        #y = point.y
        #d = math.sqrt(math.pow(2, x - x1) + math.pow(2, y - y1))
        #print('d', d)

        return 0

    def open_gate(self):
        self.gate.color = Player.palette['gate']

    def on_key_press(self, k, m):
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 1
            return True
        return False

    def on_key_release(self, k, m):
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 0
            return True
        return False

def step():
    pyglet.clock.tick()

    for window in pyglet.app.windows:
        window.switch_to()
        window.dispatch_events()
        window.dispatch_event('on_draw')
        window.flip()

    # TODO: Return `reward, state` etc.
    # reward = self.reward
    # self.reward = 0
    # TODO: Trace `done`, setting terminal state elsewhere.

def main(argv):

    # make window
    director.init(**consts['window'])
    #pyglet.font.add_directory('.') # adjust as necessary if font included
    scene = cocos.scene.Scene()
    z = 0

    palette = consts['view']['palette']
    Player.palette = palette
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
