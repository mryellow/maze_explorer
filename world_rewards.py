class WorldRewards(object):
    """
    WorldRewards

    Methods inherited by WorldLayer
    Has context for game settings, map state and player state

    Responsabilities:
        Add rewards to player in response to game events
    """

    def __init__(self):
        super(WorldRewards, self).__init__()

    # Reward functions implementing game modes
    def reward_battery(self):
        """
        Add a battery level reward
        """
        mode = self.mode['battery']
        if mode and mode and self.__test_cond(mode):
            self.logger.debug('Battery out')
            self.player.stats['reward'] += mode['reward']

            self.player.game_over = self.player.game_over or mode['terminal']

    def reward_item(self, item_type):
        """
        Add a food collision reward
        """
        assert isinstance(item_type, str)

        mode = self.mode['items']
        if mode and mode[item_type] and self.__test_cond(mode[item_type]):
            self.logger.debug("{item_type} consumed".format(item_type=item_type))
            self.player.stats['reward'] += mode[item_type]['reward']
            self.player.stats['score'] += mode[item_type]['reward']

            self.player.game_over = self.player.game_over or mode[item_type]['terminal']

    def reward_wall(self):
        """
        Add a wall collision reward
        """
        mode = self.mode['wall']
        if mode and mode and self.__test_cond(mode):
            self.logger.debug("Wall {x}/{y}'".format(x=self.bumped_x, y=self.bumped_y))
            self.player.stats['reward'] += mode['reward']

            self.player.game_over = self.player.game_over or mode['terminal']

    def reward_explore(self):
        """
        Add an exploration reward
        """
        mode = self.mode['explore']
        if mode and mode['reward'] and self.__test_cond(mode):
            self.player.stats['reward'] += mode['reward']
            self.player.stats['score'] += mode['reward']

            self.player.game_over = self.player.game_over or mode['terminal']

    def reward_goal(self):
        """
        Add an end goal reward
        """
        mode = self.mode['goal']
        if mode and mode['reward'] and self.__test_cond(mode):
            if mode['reward'] > 0:
                self.logger.info("Escaped!!")
            self.player.stats['reward'] += mode['reward']
            self.player.stats['score'] += mode['reward']

            self.player.game_over = self.player.game_over or mode['terminal']

    def __test_cond(self, mode):
        try:
            return mode['cond'](self.player)
        except KeyError:
            return True
