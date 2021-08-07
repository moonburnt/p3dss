#!/usr/bin/env python3

# In this example we will learn how to use p3dss to create single-sprite objects.
# Panda3d already has such functionality, but it may be a bit complicated to set
# everything up - thus p3dss provides simple wrapper function to generate object
# for you with sane defaults. The only required argument there is sprite texture

import p3dss
from direct.showbase.ShowBase import ShowBase
from panda3d.core import SamplerState
from os.path import join
import logging

log = logging.getLogger()

SPRITESHEET = join(join(".", "media"), "32x32-bat-sprite.png")
SPRITE_SIZE = (32, 32)


class Game(ShowBase):
    def __init__(self):
        # Setting up base stuff
        super().__init__()
        self.disable_mouse()
        base.camera.set_pos(0, 300, 10)
        base.camera.look_at(0, 0, 0)

        # Loading spritesheet texture into memory
        spritesheet = loader.load_texture(SPRITESHEET)

        # Just like in example with buttons, our original image is spritesheet.
        # Thus lets cut it off
        sprites = p3dss.processor.get_textures(
            spritesheet=spritesheet,
            sprite_sizes=SPRITE_SIZE,
            # Applying texture filter that will make our image look crisp-sharp, 
            # since its pixel art
            texture_filter=SamplerState.FT_nearest,
        )

        # Now, we want to create simple static object that has but third sprite
        # from whole sheet as its texture
        sprite_node = p3dss.make_sprite_node(
            sprite=sprites[3],
            parent=render,
            position=(0, 0, 1),
        )

        # Applying billboard to make it always face camera, and thats about it
        sprite_node.set_billboard_point_eye()


if __name__ == "__main__":
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt="[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
            datefmt="%d.%m.%y %H:%M:%S",
        )
    )
    log.addHandler(handler)

    play = Game()
    play.run()
