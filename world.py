import math
from random import randint

import pyglet

import cocos
import cocos.euclid as eu
import cocos.mapcolliders as mc
import cocos.tiles as ti
from cocos import draw

import config
from player import Player
from generator import Generator
from score import ScoreLayer

import os
script_dir = os.path.dirname(__file__)

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
        world = config.settings['world']
        self.width = world['width']  # world virtual width
        self.height = world['height']  # world virtual height

        self.generator = Generator()

        self.bindings = world['bindings']
        buttons = {}
        for k in self.bindings:
            buttons[self.bindings[k]] = 0
        self.buttons = buttons

        # load resources:
        pics = {}
        #pics["player"] = pyglet.resource.image('player7.png')
        pics["player"] = pyglet.image.load(os.path.join(script_dir, 'player7.png'))

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
        #if self.player is Player:
        #    self.player.reset()

    def generate_random_level(self):
        """
        Configure and add cocos layers
        """

        # build !
        width = self.width
        height = self.height
        #min_separation = min_separation_rel * rPlayer
        #wall_scale_min = self.wall_scale_min
        #wall_scale_max = self.wall_scale_max
        pics = self.pics
        z = 0

        # add walls
        #self.map_layer = ti.load(os.path.join(script_dir, 'test.tmx'))['map0']
        self.map_layer = self.generator.map()
        self.map_layer.set_view(0, 0, self.map_layer.px_width, self.map_layer.px_height)
        # FIXME: Both `scale_x` and `scale_y`
        self.map_layer.scale = config.scale_x
        self.add(self.map_layer, z=z)
        z += 1

        # add floor
        self.visit_layer = ti.load(os.path.join(script_dir, 'ones.tmx'))['map0']
        for i in xrange(0, len(self.map_layer.cells)):
            for j in xrange(0, len(self.map_layer.cells[i])):
                col = self.map_layer.cells[i][j]
                # If wall exists, remove floor
                if col.tile and col.tile.id > 0:
                    self.visit_layer.cells[i][j].tile = None

        self.visit_layer.set_view(0, 0, self.visit_layer.px_width, self.visit_layer.px_height)
        # FIXME: Both `scale_x` and `scale_y`
        self.visit_layer.scale = config.scale_x
        self.add(self.visit_layer, z=-1)

        # add player
        # Start in random corner
        corner = randint(0,3)
        padding = eu.Vector2(self.map_layer.tw*1.5, self.map_layer.th*1.5)
        corners = [
            (padding.x, padding.y), # Bottom left
            (padding.x, self.map_layer.px_width-padding.y), # Bottom right
            (self.map_layer.px_height-padding.x, padding.y), # Top left
            (self.map_layer.px_height-padding.x, self.map_layer.px_width-padding.y) # Top right
        ]
        cx, cy = corners[corner]
        self.player = Player(cx, cy, 'player', pics['player'])
        self.add(self.player, z=z)
        z += 1

        self.score = ScoreLayer(self.player.stats)
        self.add(self.score, z=z)
        z += 1

        # Draw sensors
        # TODO: Decouple into view rendering
        a = math.radians(self.player.rotation)
        for sensor in self.player.sensors:
            rad = a + sensor.angle
            start = self.player.cshape.center
            end = start.copy()
            end.x += math.sin(rad) * sensor.proximity;
            end.y += math.cos(rad) * sensor.proximity;
            sensor.line = draw.Line(start, end, (50,50,100,200))
            self.map_layer.add(sensor.line)

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
        """
        Updates game engine each tick
        """
        # if not playing dont update model
        if self.win_status != 'undecided':
            return

        # update target
        self.player.update_rotation(dt, self.buttons)

        # Get planned update
        oldRect, newRect, newVel = self.player.get_move(dt, self.buttons)

        # Update planned velocity to avoid collisions
        # modifies `newRect` to be the nearest rect ... still outside any `map_layer` object.
        newVel.x, newVel.y = self.collide_map(self.map_layer, oldRect, newRect, newVel.x, newVel.y)

        # Stop at edges of map
        # FIXME: Use top, bottom, left, right etc instead of radius
        if newRect.top > self.height:
            newRect.y = self.height - (self.player.radius * 2)

        if newRect.bottom < 0:
            newRect.y = 0

        if newRect.left < 0:
            newRect.x = 0

        if newRect.right > self.width:
            newRect.x = self.width - (self.player.radius * 2)

        newPos = self.player.cshape.center
        newPos.x, newPos.y = newRect.center

        # Collision detected
        if self.bumped_x or self.bumped_y:
            #print("Bumped", newVel, self.bumped_x, self.bumped_y)
            self.player.game_over = True

        self.player.velocity = newVel
        self.player.update_center(newPos)

        self.update_visited(newPos)

        #print(self.player.stats)

        # Out of battery, set terminal state
        if self.player.stats['battery'] < 0:
        #    print('Battery empty')
            self.player.stats['battery'] = 0
            # TODO: Let agent keep playing in hopes of finding end-goal
            self.player.game_over = True

        if self.player.game_over:
            self.player.stats['reward'] += self.player.rewards['terminal']
            #print('Game Over', self.player.stats['reward'])

        # Check path for each sensor

        a = math.radians(self.player.rotation)
        for sensor in self.player.sensors:
            rad = a + sensor.angle
            dis = min(self.distance_to_tile(newPos, rad), sensor.max_range)

            # Keep state of sensed range
            sensor.proximity = dis

            # Redirect sensor lines
            # TODO: Decouple into view rendering
            a = math.radians(self.player.rotation)
            for sensor in self.player.sensors:
                rad = a + sensor.angle
                start = self.player.cshape.center
                end = start.copy()
                end.x += math.sin(rad) * sensor.proximity;
                end.y += math.cos(rad) * sensor.proximity;
                sensor.line.start = start
                sensor.line.end = end

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
        """
        Updates exploration map visited status
        """
        assert isinstance(pos, eu.Vector2)

        # Helper function
        def set_visited(layer, cell):
            if cell and not cell.properties.get('visited') and cell.tile and cell.tile.id > 0:
                cell.properties['visited'] = True

                # Adjust next reward for exploration
                self.player.stats['reward'] += self.player.rewards['explore']
                self.player.stats['score'] += self.player.rewards['explore']

                # TODO: Decouple into view rendering
                # Change colour of visited cells
                key = layer.get_key_at_pixel(cell.x, cell.y)
                #layer.set_cell_color(key[0], key[1], [155,155,155])
                layer.set_cell_opacity(key[0], key[1], 255*0.8)
        # End Helper

        # Get the current tile under player
        current = self.visit_layer.get_at_pixel(pos.x, pos.y)

        if current:
            set_visited(self.visit_layer, current)
            neighbours = self.visit_layer.get_neighbors(current)
            for cell in neighbours:
                neighbour = neighbours[cell]
                set_visited(self.visit_layer, neighbour)

    # Find line intersects next tile
    def distance_to_tile(self, point, direction, length = 50):
        """
        Find nearest wall on a given bearing.
        Used for agent wall sensors.
        """
        assert isinstance(point, eu.Vector2)
        assert isinstance(direction, int) or isinstance(direction, float)
        assert isinstance(length, int) or isinstance(length, float)

        # Recursive dead-reckoning to next tile
        # Given `point`, look for where intersects with next boundary (`y % 10`) in `direction`
        def search_grid(search, rad, distance = 0, depth = 10):
            assert isinstance(search, eu.Vector2)
            assert isinstance(rad, float)

            if depth == 0:
                return distance
            depth -= 1

            # Exit if outside window.
            if abs(search.x) > self.width or abs(search.y) > self.height:
                return distance

            m = math.tan(rad) # Slope
            sin = math.sin(rad)
            cos = math.cos(rad)
            #print(sin, cos)

            top    = (cos > 0)
            bottom = (cos < 0)
            left   = (sin < 0)
            right  = (sin > 0)

            start  = eu.Vector2(search.x, search.y)
            ends   = eu.Vector2()

            # Helper function
            # Find next grid on given axis
            def get_boundary(axis, increasing):
                assert (isinstance(axis, str) or isinstance(axis, unicode)) and (axis == 'x' or axis == 'y')

                if axis == 'x':
                    tile = self.map_layer.tw
                    position = search.x
                elif axis == 'y':
                    tile = self.map_layer.th
                    position = search.y

                # Set bound to next tile on axis
                bound = (position % tile)
                if increasing:
                    bound = tile - bound
                    bound = position + bound + 1
                else:
                    bound = position - bound - 1

                # Find intersect
                if axis == 'x':
                    intersect = ((bound - search.x) / m) + search.y
                    return eu.Vector2(bound, intersect)
                elif axis == 'y':
                    intersect = -m * (search.y - bound) + search.x
                    return eu.Vector2(intersect, bound)
            # End Helper

            if top or bottom:
                ends.y = get_boundary('y', top)

                # FIXME: Should these exit? What if other line collides sooner?
                # Exit if outside window.
                if abs(ends.y.y) > self.height:
                    return distance

            if left or right:
                ends.x = get_boundary('x', right)

                # Exit if outside window.
                if abs(ends.x.x) > self.width:
                    return distance

            # Get shortest collision between axis
            lengths = eu.Vector2(0, 0)
            if type(ends.x) == eu.Vector2:
                diff = start - ends.x
                lengths.x = math.sqrt(diff.dot(diff))
            if type(ends.y) == eu.Vector2:
                diff = start - ends.y
                lengths.y = math.sqrt(diff.dot(diff))

            end = None

            # Find shortest boundary intersect
            index_min = min(xrange(len(lengths)), key=lengths.__getitem__)

            if lengths[index_min] > 0:
                distance += lengths[index_min]
                end = ends[index_min]

            if end:
                #line = draw.Line(start, end, (50,50,100,130))
                #self.map_layer.add(line)
                cell = self.map_layer.get_at_pixel(end.x, end.y)
                if not cell or not cell.tile or not cell.tile.id > 0:
                    # Recurse
                    return search_grid(end, rad, distance, depth)

            return distance
        # End Helper

        # Start at `point`, check tile under each pixel
        return search_grid(point, direction)

    #def open_gate(self):
    #    self.gate.color = Player.palette['gate']

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
