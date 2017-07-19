from setuptools import setup
from setuptools import find_packages

setup(name='maze_explorer',
      version='0.0.1',
      author='Mr-Yellow',
      author_email='mr-yellow@mr-yellow.com',
      description='A maze exploration game engine',
      packages=find_packages(),
      url='',
      license='MIT',
      install_requires=['cocos2d', 'pyglet']
)


#package_dir={'gym_mazeexplorer' : 'gym_mazeexplorer/envs'},
