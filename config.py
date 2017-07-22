import math
import logging

import pyglet
from pyglet.window import key

import os
script_dir = os.path.dirname(__file__)

tiles = {
    "tw": 10,
    "th": 10,
    "width": 50,
    "height": 50
}

#fe = 1.0e-4
settings = {
    "log_level": logging.INFO,
    "window": {
        "width": 500,
        "height": 500,
        "vsync": True,
        "resizable": False
    },
    "player": {
        "radius": tiles['tw'] / 4,
        # TODO: Put all velocity settings in dict
        "top_speed": 50.0 / 4,
        "angular_velocity": 240.0 / 4,  # degrees / s
        "accel": 85.0,
        "deaccel": 5.0,
        # TODO: Refactor to action `costs`, will apply to whichever `stat`
        "battery_use": {
            "angular": 0.01,
            "linear": 0.01
        },
        "sensors": {
            "num": 9,
            "fov": 15*math.pi/180,
            "max_range": 200 / 4
        }
    },
    "world": {
        "width": tiles['tw'] * tiles['width'],
        "height": tiles['th'] * tiles['height'],
        "bindings": {
            #0: 'noop',
            key.LEFT: 'left',
            key.RIGHT: 'right',
            key.UP: 'up',
        }
    },
    "view": {
        # as the font file is not provided it will decay to the default font;
        # the setting is retained anyway to not downgrade the code
        "font_name": 'Axaxax',
        "palette": {
            'bg': (0, 65, 133),
            'wall': (50, 50, 100), # Wall sensor colour
            'player': (237, 27, 36),
            #'wall': (247, 148, 29),
            'gate': (140, 198, 62),
            'food': (140, 198, 62),
            'poison': (198, 62, 62)
        }
    }
}

modes = [
    # Mode 0
    {
        "explore": {
            "reward": 1.0,
            "terminal": False
        },
        "goal": {
            "reward": 200.0,
            "terminal": True
        },
        "wall": {
            "reward": -100.0,
            "terminal": True
        },
        "items": {}
    },
    # Mode 1
    {
        "explore": {
            "reward": 0.0,
            "terminal": False
        },
        "goal": {
            "reward": 0.0,
            "terminal": False
        },
        "wall": {
            "reward": -100.0,
            "terminal": True
        },
        "items": {
            "food": {
                "num": 50,
                "scale": 2.0,
                "reward": 2.0,
                "terminal": False
            },
            "poison": {
                "num": 50,
                "scale": 2.0,
                "reward": -4.0,
                "terminal": False
            },
        }
    }
]

# Ensure all modes have items for convenience
for mode in modes:
    if mode['items'] is None:
        mode['items'] = {}

# world to view scales
scale_x = settings["window"]["width"] / settings["world"]["width"]
scale_y = settings["window"]["height"] / settings["world"]["height"]

# load resources:
pics = {
    "player": pyglet.image.load(os.path.join(script_dir, 'assets', 'player7.png')),
    "food": pyglet.image.load(os.path.join(script_dir, 'assets', 'circle6.png')),
    "poison": pyglet.image.load(os.path.join(script_dir, 'assets', 'circle6.png'))
}
