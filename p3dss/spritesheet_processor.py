from . import types, exceptions
from panda3d.core import Texture
from panda3d.core import LPoint2f as Point
import logging

log = logging.getLogger(__name__)

def _is_power_of_two(num):
    return (num and not(num & (num -1)))

def get_offsets(spritesheet:Texture, sprite_sizes:tuple):
    """Fetch all available offsets from provided spritesheet.
    """

    # For now, this has 2 limitations, both of which are addressed as exceptions:
    # 1. Spritesheet HAS TO DIVIDE TO PROVIDED SPRITE SIZE WITHOUT REMAINDER. If
    # it doesnt cut to perfect sprites, you will get strange results during using
    # some of these sprites.
    # 2. Amount of sprite rows and columns MUST BE POWER OF 2. Otherwise - see
    # above. This is because of limitation of set_tex_offset() and set_tex_scale()
    # functions, both of which operate with floats between 0 and 1 to determine
    # texture's size and position.
    # I assume, its possible to fix both of these. But right now I have no idea how

    # As for first - I can probably add bool to enable optional cut with PNMimage
    # of all the garbage that dont fit #TODO

    spritesheet_name = spritesheet.get_name()

    log.debug(f"Attempting to cut {spritesheet_name} into {sprite_sizes} sprites")
    size_x, size_y = sprite_sizes

    # Determining amount of sprites in each row
    spritesheet_x = spritesheet.get_orig_file_x_size()
    spritesheet_y = spritesheet.get_orig_file_y_size()

    # Checking if our spritesheet match first limitation, mentioned above
    if (spritesheet_x % size_x) or (spritesheet_x % size_y):
        raise exceptions.InvalidSpriteSize(spritesheet_name, sprite_sizes)

    sprite_columns = int(spritesheet_x / size_x)
    sprite_rows = int(spritesheet_y / size_y)

    # Checking if we pass second limitation from above
    if not _is_power_of_two(sprite_columns) or not _is_power_of_two(sprite_rows):
        raise exceptions.InvalidSpriteSize(spritesheet_name, sprite_sizes)

    log.debug(f"Our sheet has {sprite_columns}x{sprite_rows} sprites")

    #idk if these should be flipped - its 3 am
    #this may backfire on values bigger than one... but it should never happen
    horizontal_offset_step = 1/sprite_columns
    vertical_offset_step = 1/sprite_rows
    offset_steps = Point(horizontal_offset_step, vertical_offset_step)
    log.debug(f"Offset steps are {offset_steps}")

    spritesheet_offsets = []

    # We process rows backwards to make it match "from top left to bottom right"
    # style of image processing, used by most tools (and thus probs expected)
    for row in range(sprite_rows-1, -1, -1):
        log.debug(f"Processing row {row}")
        for column in range(0, sprite_columns):
            log.debug(f"Processing column {column}")
            horizontal_offset = column * horizontal_offset_step
            vertical_offset = row * vertical_offset_step
            offsets = Point(horizontal_offset, vertical_offset)
            log.debug(f"Got offsets: {offsets}")
            spritesheet_offsets.append(offsets)
    log.debug(f"Spritesheet contain following offsets: {spritesheet_offsets}")

    data = types.SpritesheetData(spritesheet, spritesheet_offsets, offset_steps)
    log.debug(f"Got following data: {data}, returning")

    return data
