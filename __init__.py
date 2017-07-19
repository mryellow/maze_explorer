from gym.envs.registration import registry, register, make, spec
from maze_environment import MazeEnv
# Algorithmic
# ----------------------------------------

register(
    id='MazeExplorer-v0',
    entry_point='maze_environment:MazeEnv',
    max_episode_steps=200,
    reward_threshold=25.0,
)
