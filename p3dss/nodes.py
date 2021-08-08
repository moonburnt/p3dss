import logging
from panda3d.core import CardMaker, TextureStage, Texture, NodePath, Vec3, PythonTask
from . import processor, types

log = logging.getLogger(__name__)


def make_sprite_node(
    sprite: Texture,
    size: tuple = None,
    name: str = None,
    is_two_sided: bool = True,
    is_transparent: bool = True,
    parent: NodePath = None,
    position: Vec3 = None,
    scale: float = 0.0,
) -> NodePath:
    """Make flat single-sprite node out of provided data"""
    # Using WM_clamp instead of WM_mirror, to avoid issue with black 1-pixel
    # bars appearing on top of spritesheet randomly.
    # Idk if this needs to have possibility to override it #TODO
    sprite.set_wrap_u(Texture.WM_clamp)
    sprite.set_wrap_v(Texture.WM_clamp)

    # Creating CardMaker frame
    card = CardMaker(name or sprite.get_name() or "sprite")
    # This will fail if texture has been generated with no set_orig_file_size()
    size = size or (sprite.get_orig_file_x_size(), sprite.get_orig_file_y_size())

    # Been told that its not in pixels, thus accepting either 1, 2 or 4 values
    # Kinda jank, I know
    if len(size) > 3:
        card.set_frame(-size[0], size[1], -size[2], size[3])
    elif len(size) > 1:
        card.set_frame(-size[0], size[0], -size[1], size[1])
    else:
        card.set_frame(-size[0], size[0], -size[0], size[0])

    parent = parent or NodePath()
    node = parent.attach_new_node(card.generate())
    node.set_texture(sprite)

    # Making it possible to utilize texture's alpha channel settings
    # This is a float from 0 to 1, but I dont think there is a point to only
    # show half of actual object's transparency.
    # Do it manually afterwards if thats what you need
    if is_transparent:
        node.set_transparency(1)
    # Enabling ability to render texture on both front and back of card
    if is_two_sided:
        node.set_two_sided(True)
    # Setting object's position. This is done relatively to parent, thus if you
    # didnt pass any, it may be a bit janky
    if position:
        node.set_pos(*position)

    if scale and scale > 0:
        node.set_scale(scale)

    return node


class SpritesheetNode:
    """Flat node with multiple sprites from single spritesheet attached to it"""

    def __init__(
        self,
        spritesheet: Texture,
        sprite_sizes: tuple,
        node_sizes: tuple = None,
        name: str = None,
        is_two_sided: bool = False,
        # Maybe I should rename this to "has_transparency" or "has_alpha_channel"?
        # #TODO
        is_transparent: bool = True,
        parent: NodePath = None,
        scale: float = 0.0,
        default_sprite: int = 0,
        position: Vec3 = None,
    ):

        parent = parent or NodePath()
        # name of animated object
        self.name = name or spritesheet.get_name() or "SpritesheetNode"
        self.sprite_sizes = sprite_sizes
        self.node_sizes = node_sizes or self.sprite_sizes

        sprite_data = processor.get_offsets(spritesheet, self.sprite_sizes)

        self.offsets = sprite_data.offsets

        self.node = make_sprite_node(
            sprite=spritesheet,
            # This is kept for backwards compatibility. I should probably make
            # generated objects have unified size measurement values across whole
            # library #TODO
            # size=(self.sizes[0] / 2, self.sizes[1] / 2),
            size=self.node_sizes,
            name=self.name,
            is_two_sided=is_two_sided,
            is_transparent=is_transparent,
            parent=parent,
            position=position,
            scale=scale,
        )

        # Sprite shown right now. This will crash if its value is greater than
        # amount of sprites in sheet
        self.current_sprite = default_sprite

        # okay, this does the magic
        # basically, to show the very first sprite of 2 in row, we set tex scale
        # to half (coz half is our normal char's size). If we will need to use it
        # with sprites other than first - then we also should adjust offset accordingly
        self.node.set_tex_scale(TextureStage.getDefault(), *sprite_data.step_sizes)

        # now,lets say, we need to use second sprite from sheet. Just do:
        # self.node.set_tex_offset(TextureStage.getDefault(), *offsets[1])
        self.node.set_tex_offset(
            TextureStage.getDefault(), *self.offsets[self.current_sprite]
        )

        self.items = {}
        # Name of item to reset playback to. If not set, playback of non-looped
        # items with reset_on_complete will stop at their last frame
        self.default_item = None
        # setting this to None may cause crashes on few rare cases, but going
        # for "idle_right" wont work for projectiles... So I technically add it
        # there for anims updater, but its meant to be overwritten at 100% cases
        self.current_item = None
        # Items to be played after current. Not implemented right now. #TODO
        # self.queue = []

        # This specifies if something plays right now or not
        self.playing = types.PlaybackState.stop

        # This used to specify amount of time left till shown item will be changed
        self.frame_time_left = 0
        # Number of item in current sequence that plays right now
        self.current_sequence_item = 0

        def play_current(event: PythonTask) -> PythonTask:
            """Taskmanager routine that plays currently shown item"""
            # Destroys the routine if node has been deleted
            if not self.node:
                return

            # If no playback is going on right now - either resetting to default
            # or just doing nothing till next frame
            if self.playing == types.PlaybackState.stop:
                return event.cont

            if self.playing == types.PlaybackState.pause:
                # This will crash if there is no current item, shouldnt happen
                if (
                    self.items[self.current_item].reset_on_complete
                    and self.default_item
                    and self.default_item != self.current_item
                ):
                    self.play(self.default_item)
                return event.cont

            # Getting delta time since last frame
            dt = globalClock.get_dt()
            self.frame_time_left -= dt
            if self.frame_time_left > 0:
                return event.cont

            # If amount of time passed has been more than required - resetting
            # timer and switching to next image in sequence
            # Idk if this is resource-efficient, will see #TODO
            self.frame_time_left = self.items[self.current_item].playback_speed

            self.current_sprite = self.items[self.current_item].sprites[
                self.current_sequence_item
            ]
            self.node.set_tex_offset(
                TextureStage.getDefault(), *self.offsets[self.current_sprite]
            )

            # idk how to do this better
            if (
                len(self.items[self.current_item].sprites)
                > self.current_sequence_item + 1
            ):
                self.current_sequence_item += 1
            else:
                self.current_sequence_item = 0
                # if looping is disabled - keeping last frame
                if not self.items[self.current_item].loop:
                    self.playing = types.PlaybackState.pause
                    return event.cont

            return event.cont

        base.task_mgr.add(play_current, f"Animation task of {self.name}")

    def add_item(
        self, item: types.SpritesheetItem, name: str = None, set_default: bool = False
    ):
        """Add provided item into self.items"""
        name = name or item.name
        self.items[name] = item
        if set_default:
            self.default_item = name

    def set_default(self, item_name: str):
        """Set item with provided name to default"""
        if not item_name in self.items:
            log.warning(f"{self.name} has no item named {item_name}!")
            return

        self.default_item = item_name

    def play(self, item_name: str, ignore_if_current: bool = True):
        """Make node switch to showcase of selected spritesheet's item"""
        # safety check to ensure that we wont crash everything with exception by
        # trying to play animation that doesnt exist
        if not item_name in self.items:
            log.warning(f"{self.name} has no item named {item_name}!")
            return

        if ignore_if_current and self.current_item == item_name:
            log.debug(f"{self.name} already plays {item_name}, wont switch")
            return

        self.stop()

        self.current_item = item_name
        self.frame_time_left = self.items[item_name].playback_speed
        self.playing = types.PlaybackState.play
        log.debug(f"{self.name} started playing {self.current_item}")

    def stop(self):
        """Stop current playback and reset self.current_item"""
        if self.current_item:
            self.playing = types.PlaybackState.stop
            log.debug(f"{self.name} has stopped playback of {self.current_item}")
            self.current_item = None
            self.current_sequence_item = 0
