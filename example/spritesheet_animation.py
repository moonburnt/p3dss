#!/usr/bin/env python3

# Simple example of how to use p3dss in order to use whole spritesheet's data to
# create entity with multiple 2d animations/sprites attached to it

import p3dss
from direct.showbase.ShowBase import ShowBase
from os.path import join
import logging

log = logging.getLogger()

SPRITESHEET = join(join(".", "media"), "32x32-bat-sprite.png")
# For the time being, p3dss uses this kinda weird-ish dictionary format to declare,
# which sprite refers to which action. It may look complicated, but it all makes
# sense in long run, since it allows for per-action settings.
SPRITES = {
    # If we pass "sprites" as single int or (0, 0) - p3ds will automatically
    # consider it to be a single sprite
    "dead": {"sprites": 0},
    # While passing tuple, list or set will turn it into animation sequence
    "fly_forward": {"sprites": (1, 3)},
    # As for "per-action settings": there we enabled looping, so animation
    # will play till we another visuals-changing event will occur.
    # While default behavior is to play animation once and then stop
    "fly_right": {"sprites": (5, 7), "loop": True},
    "fly_backward": {"sprites": (9, 11)},
    "fly_left": {"sprites": (13, 15), "loop": True},
}
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
        self.bat = p3dss.SpritesheetObject(
            name="Bat",
            spritesheet=spritesheet,
            sprites=SPRITES,
            sprite_size=SPRITE_SIZE,
        )

        # SpritesheetObject has internal var called "node". Which is the local
        # instance of CardMaker node, attached to parent (we didnt pass it above,
        # thus parent has been set to default, which is render).
        # I thought about "proxifying" its functions outside instead, but found
        # it overcomplicated without good reason.
        # So, basically, each time we need to affect our CardMaker node attached
        # to nodepath, we cast required functions onto its "node" variable
        self.bat.node.set_pos(0, 0, 1)
        self.bat.node.set_billboard_point_eye()

        # Now, lets make our bat fly right from the start (by default, our object
        # appears with sprite 0. Which is, in our case, "dead").
        # The recommended way to do that is by casting "switch" function, which
        # will stop playback of current animation and then start the new one
        self.bat.switch("fly_right")
        # Passing invalid animations wont affect playback. If you have logging
        # module enabled - you will get warning message in your log about it
        self.bat.switch("do_a_barrel_roll")

        # Now lets make our bat change animations when specific buttons has been
        # pressed. Since "switch" action only change action if it hasnt been set
        # or different from current - if you will press some button multiple times
        # in a row - current action will be only changed on first press
        base.accept("w", self.change_animation, ["fly_forward"])
        base.accept("d", self.change_animation, ["fly_right"])
        base.accept("s", self.change_animation, ["fly_backward"])
        base.accept("a", self.change_animation, ["fly_left"])
        base.accept("space", self.change_animation, ["dead"])

    def change_animation(self, action):
        self.bat.switch(action)


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
