class WorldRewards():
    """
    WorldRewards

    Methods inherited by WorldLayer
    Has context for game settings, map state and player state

    Responsabilities:
        Add rewards to player in response to game events
    """

    def __init__(self):
        super(Rewards, self).__init__()

    # Reward functions implementing game modes
    def reward_collision(self):
        """
        Add a wall collision reward
        """
        self.logger.debug("Bump {x}/{y}'".format(x=self.bumped_x, y=self.bumped_y))
        if self.mode == 0:
            self.player.stats['reward'] += self.player.rewards['collision']
            # Wall collisions end the episode in mode 0
            self.player.game_over = True

    def reward_explore(self):
        """
        Add an exploration reward
        """
        if self.mode == 0:
            if self.player.stats['battery'] > 50:
                self.player.stats['reward'] += self.player.rewards['explore']
                self.player.stats['score'] += self.player.rewards['explore']

    def reward_goal(self):
        """
        Add an end goal reward
        """
        if self.mode == 0:
            if self.player.stats['battery'] <= 50:
                self.logger.info("Escaped!!")
                self.player.stats['reward'] += self.player.rewards['goal']
                self.player.game_over = True

    def reward_terminal(self):
        """
        Add a terminal reward
        """
        assert self.player.game_over

        if self.mode == 0:
            self.player.stats['reward'] += self.player.rewards['terminal']
