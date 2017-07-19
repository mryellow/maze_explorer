import gym
import gym_mazeexplorer

env = gym.make('MazeExplorer-v0')
env.reset()

for _ in range(100):
    env.render()
    action = env.action_space.sample()
    observation, reward, done, info = env.step(action)
