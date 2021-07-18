#!/usr/bin/env python3

# In this example we will learn how to use p3dss to cut spritesheet texture into
# multiple sprite textures. This may be useful, in case we need to use some
# panda's default thing that dont understand internal format of p3dss.
# In this particular case, spritesheet holds textures of buttons, which we need
# to retrieve and then invoke direct gui's button with them

from p3dss import processor
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import (DirectButton, DGG)
from os.path import join
import logging

log = logging.getLogger()

SPRITESHEET = join(join(".", "media"), "example_button.png")
SPRITE_SIZE = (64, 32)

class Game(ShowBase):
    def __init__(self):
        # Setting up base stuff
        super().__init__()
        self.disable_mouse()
        base.camera.set_pos(0, 300, 10)
        base.camera.look_at(0, 0, 0)

        # Just like in other example, loading spritesheet texture manually
        spritesheet = loader.load_texture(SPRITESHEET)

        # Feeding spritesheet to processor in order to retrieve our sprites.
        # Unlike spritesheet objects from other example, the only requirement
        # for spritesheet in this case is to fit provided sprites amount perfectly
        # (e.g you can cut 128x128 image onto 64x32 sprites, but not onto 30x30).
        # HOWEVER, in order to circuimvent the restriction with amount of items
        # in spritesheet's rows or columns not being power of 2, you need to
        # manually set "textures-power-2 none" in your Config.rpc.
        # If everything has went fine, you will get list of items named like
        # {spritesheet_name_without_extension}_{sprite_num}. In case its impossible
        # to fetch spritesheet name, mask "sprite" will be used instead of it
        sprites = processor.get_textures(
                                    spritesheet = spritesheet,
                                    sprite_sizes = SPRITE_SIZE,
                                    )

        # Creating simple button that disables itself on click.
        # DirectButton objects accept either one or up to 4 frameTexture items,
        # in following order of button state they will represent:
        # normal -> hover -> clicked -> disabled
        # If you wont pass some, first will be used instead
        self.button = DirectButton(
                            command = self.disable_button,
                            pos = (0, 1, 0),
                            relief = DGG.FLAT,
                            scale = 0.1,
                            frameTexture = sprites,
                            frameSize = (-2, 2, -1, 1),
                            parent = base.aspect2d,
                            )

    def disable_button(self):
        self.button["state"] = DGG.DISABLED

if __name__ == "__main__":
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
                       fmt='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
                       datefmt='%d.%m.%y %H:%M:%S'
                       ))
    log.addHandler(handler)

    play = Game()
    play.run()
