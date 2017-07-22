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
    def reward_item(self, item_type):
        """
        Add a food collision reward
        """
        assert isinstance(item_type, str)

        if self.mode['items'] and self.mode['items'][item_type]:
            self.logger.debug(item_type + " consumed")
            self.player.stats['reward'] += self.mode['items'][item_type]['reward']
            self.player.stats['score'] += self.mode['items'][item_type]['reward']

            self.player.game_over = self.player.game_over or self.mode['items'][item_type]['terminal']

    def reward_wall(self):
        """
        Add a wall collision reward
        """
        if self.mode['wall'] and self.mode['wall']:
            self.logger.debug("Wall {x}/{y}'".format(x=self.bumped_x, y=self.bumped_y))
            self.player.stats['reward'] += self.mode['wall']['reward']

            self.player.game_over = self.player.game_over or self.mode['wall']['terminal']

    def reward_explore(self):
        """
        Add an exploration reward
        """
        if self.mode['explore'] and self.mode['explore']['reward']:
            # TODO: Condition in config?
            if self.player.stats['battery'] > 50:
                self.player.stats['reward'] += self.mode['explore']['reward']
                self.player.stats['score'] += self.mode['explore']['reward']

                self.player.game_over = self.player.game_over or self.mode['explore']['terminal']

    def reward_goal(self):
        """
        Add an end goal reward
        """
        if self.mode['goal'] and self.mode['goal']['reward']:
            # TODO: Condition in config?
            if self.player.stats['battery'] <= 50:
                if self.mode['goal']['reward'] > 0:
                    self.logger.info("Escaped!!")
                self.player.stats['reward'] += self.mode['goal']['reward']
                self.player.stats['score'] += self.mode['goal']['reward']

                self.player.game_over = self.player.game_over or self.mode['goal']['terminal']
