import cocos
import cocos.collision_model as cm

import config

class WorldItems(object):
    """
    WorldItems

    Methods inherited by WorldLayer
    Has context for game settings, map state and player state

    Responsabilities:
        Add rewards to player in response to game events
    """

    def __init__(self):
        super(WorldItems, self).__init__()

        player = config.settings['player']
        world = config.settings['world']

        self.to_remove = set()

        # TODO: Only create if needed by game `mode`
        cell_size = player['radius'] * 0.25
        self.collman = cm.CollisionManagerGrid(0.0, world['width'],
                                               0.0, world['height'],
                                               cell_size, cell_size)

    def init_collisions(self):
        if self.mode == 0: return

        # FIXME: Check if already contains
        self.collman.add(self.player)

        #if self.mode == 1:
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

    def update_collisions(self):
        if self.mode == 0: return

        # update collman
        # FIXME: Why update each frame?
        self.collman.clear()
        for z, node in self.children:
            if hasattr(node, 'cshape') and type(node.cshape) == cm.CircleShape:
                self.collman.add(node)

        if self.mode == 1:
            # interactions player - others
            for other in self.collman.iter_colliding(self.player):
                self.logger.debug('collision', other)
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
        #for node in self.to_remove:
        #    self.remove(node)

        #print('c', type(self.to_remove))
        self.to_remove.clear()
