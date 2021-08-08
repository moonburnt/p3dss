#!/usr/bin/env python3

# Simple example of how to use p3dss in order to use whole spritesheet's data to
# create entity with multiple 2d animations/sprites attached to it

import p3dss
from direct.showbase.ShowBase import ShowBase
from os.path import join
import logging

log = logging.getLogger()

SPRITESHEET = join(join(".", "media"), "32x32-bat-sprite.png")

# List of named items on spritesheet. You can use something else to store them,
# just dont forget to convert afterwards
ITEMS = [
    # Numbers in "sprites" reffer to sprite's counter on whole spritesheet.
    # By default, SpritesheetNode will threat spritesheets as images containing
    # sprites of the same size spread across the whole. Thats where the counter
    # comes from, starting from top left corner of the spritesheet and going all
    # the way to its bottom right
    p3dss.SpritesheetItem(
        name="dead",
        # SpritesheetItem always expects sequence, thus single-sprite items still
        # should be packed into tuple
        sprites=(0,),
    ),
    p3dss.SpritesheetItem(
        name="fly_forward",
        sprites=(1, 2, 3),
    ),
    # Above are the minimal examples of SpritesheetItem descriptions. However,
    # there are some optional values to tinker with. For example, you can specify
    # if sequence should loop itself at the end (else it will stop at last frame)
    p3dss.SpritesheetItem(name="fly_right", sprites=(5, 6, 7), loop=True),
    # Or you can specify custom animation playback speed
    p3dss.SpritesheetItem(
        name="fly_backward",
        sprites=(9, 10, 11),
        playback_speed=0.5,
    ),
    p3dss.SpritesheetItem(
        name="fly_left",
        sprites=(13, 14, 15),
        loop=True,
        playback_speed=0.2,
    ),
]
SPRITE_SIZE = (32, 32)


class Game(ShowBase):
    def __init__(self):
        # Setting up base stuff
        super().__init__()
        self.disable_mouse()
        base.camera.set_pos(0, 300, 10)
        base.camera.look_at(0, 0, 0)

        # Setting up our spritesheet object.
        # Texture needs to be loaded separately, because I have no idea how exactly
        # you want to handle these - load on model's init, or right on game's
        # launch and then keep in memory
        spritesheet = loader.load_texture(SPRITESHEET)

        # Initializing our object. Values should be self-explanatory
        self.bat = p3dss.SpritesheetNode(
            name="Bat",
            spritesheet=spritesheet,
            sprite_sizes=SPRITE_SIZE,
            parent=render,
            position=(0, 0, 1),
        )

        # Adding named items to our object
        for item in ITEMS:
            self.bat.add_item(item)

        # SpritesheetNode has internal var called "node". Which is the NodePath
        # with our object's node attached to its parent. So, basically, each time
        # we need to do some Nodepath-specific magic thats out of the scope of
        # this library, we cast required functions onto this "node" variable
        self.bat.node.set_billboard_point_eye()

        # Now, lets make our bat fly right from the start (by default, the first
        # visible sprite will be the one from very top left of spritesheet.
        # We do that by casting "play" function, which will stop playback of
        # current item (in case there is one) and then start playing the new one
        self.bat.play("fly_right")
        # Passing invalid item names wont affect playback. If you have logging
        # module enabled - you will get warning message in your log about it
        self.bat.play("do_a_barrel_roll")

        # Now lets make our bat change items when specific buttons has been pressed.
        # play() has optional "ignore_if_current" argument that specifies if we
        # should ignore the item that already plays in case we requested it again,
        # or reset its playback and start over. By default its set to "True", so
        # dont be afraid of spamming the same button over and over - if requested
        # item is currently active, nothing will happen
        base.accept("w", self.bat.play, ["fly_forward"])
        base.accept("d", self.bat.play, ["fly_right"])
        base.accept("s", self.bat.play, ["fly_backward"])
        base.accept("a", self.bat.play, ["fly_left"])
        base.accept("space", self.bat.play, ["dead"])


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
