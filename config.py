import math

import pyglet
from pyglet.window import key

tile_size = 10
tiles_x = 50
tiles_y = 50

#fe = 1.0e-4
settings = {
    "window": {
        "width": 500,
        "height": 500,
        "vsync": True,
        "resizable": False
    },
    "player": {
        "radius": tile_size / 4,
        "top_speed": 50.0 / 4,
        "angular_velocity": 240.0,  # degrees / s
        "accel": 85.0,
        "deaccel": 5.0,
        "battery_use": {
            "angular": 0.01,
            "linear": 0.01
        },
        "rewards": {
            "collision": -10.0,
            "explore": 1.0,
            "terminal": 0.0,
            "goal": 100.0
        },
        "sensors": {
            "num": 9,
            "fov": 15*math.pi/180,
            "max_range": 200 / 4
        }
    },
    "world": {
        "width": tile_size * tiles_x,
        "height": tile_size * tiles_y,
        "tiles_x": tiles_x,
        "tiles_y": tiles_x,
        #"wall_scale_min": 0.75,  # relative to player
        #"wall_scale_max": 2.25,  # relative to player
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
            'player': (237, 27, 36),
            'wall': (247, 148, 29),
            'gate': (140, 198, 62),
            'food': (140, 198, 62)
        }
    }
}

# world to view scales
scale_x = settings["window"]["width"] / settings["world"]["width"]
scale_y = settings["window"]["height"] / settings["world"]["height"]
