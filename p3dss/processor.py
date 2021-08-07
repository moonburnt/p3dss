from . import types, exceptions
from panda3d.core import Texture, SamplerState, LPoint2
from panda3d.core import PNMImage as Image
import logging

log = logging.getLogger(__name__)


def _is_power_of_two(num) -> bool:
    return num and not (num & (num - 1))


def _has_remainder(spritesheet: Texture, sprite_sizes: tuple) -> bool:
    return (spritesheet.get_orig_file_x_size() % sprite_sizes[0]) or (
        spritesheet.get_orig_file_y_size() % sprite_sizes[1]
    )


def _get_columns_and_rows(spritesheet: Texture, sprite_sizes: tuple) -> tuple:
    columns = int(spritesheet.get_orig_file_x_size() / sprite_sizes[0])
    rows = int(spritesheet.get_orig_file_y_size() / sprite_sizes[1])
    return (columns, rows)


def get_offsets(spritesheet: Texture, sprite_sizes: tuple) -> types.SpritesheetData:
    """Fetch all available offsets from provided spritesheet."""

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

    log.debug(f"Fetching {sprite_sizes} offsets from {spritesheet.get_name()}")

    # Checking if our spritesheet match first limitation, mentioned above
    if _has_remainder(spritesheet, sprite_sizes):
        raise exceptions.InvalidSpriteSize(spritesheet.get_name(), sprite_sizes)

    # Determining amount of sprites in each row
    sprite_columns, sprite_rows = _get_columns_and_rows(spritesheet, sprite_sizes)

    # Checking if we pass second limitation from above
    if not _is_power_of_two(sprite_columns) or not _is_power_of_two(sprite_rows):
        raise exceptions.InvalidSpriteSize(spritesheet.get_name(), sprite_sizes)

    log.debug(f"Our sheet has {sprite_columns}x{sprite_rows} sprites")

    # idk if these should be flipped - its 3 am
    # this may backfire on values bigger than one... but it should never happen
    horizontal_offset_step = 1 / sprite_columns
    vertical_offset_step = 1 / sprite_rows
    offset_steps = LPoint2(horizontal_offset_step, vertical_offset_step)
    log.debug(f"Offset steps are {offset_steps}")

    spritesheet_offsets = []

    # We process rows backwards to make it match "from top left to bottom right"
    # style of image processing, used by most tools (and thus probs expected)
    for row in range(sprite_rows - 1, -1, -1):
        log.debug(f"Processing row {row}")
        for column in range(0, sprite_columns):
            log.debug(f"Processing column {column}")
            horizontal_offset = column * horizontal_offset_step
            vertical_offset = row * vertical_offset_step
            offsets = LPoint2(horizontal_offset, vertical_offset)
            log.debug(f"Got offsets: {offsets}")
            spritesheet_offsets.append(offsets)
    log.debug(f"Spritesheet contain following offsets: {spritesheet_offsets}")

    data = types.SpritesheetData(spritesheet, spritesheet_offsets, offset_steps)
    log.debug(f"Got following data: {data}, returning")

    return data


def get_images(spritesheet: Texture, sprite_sizes: tuple) -> list:
    """Cut provided spritesheet texture into separate PNMImage objects"""
    if _has_remainder(spritesheet, sprite_sizes):
        raise exceptions.InvalidSpriteSize(spritesheet.get_name(), sprite_sizes)

    sprite_x, sprite_y = sprite_sizes
    columns, rows = _get_columns_and_rows(spritesheet, sprite_sizes)

    # This is safety check to ensure there wont be any weird effects during cutting,
    # caused by texture autorescale. In order to circuimvent this, you need to
    # set "textures-power-2 none" in your Config.rpc.
    # There seem to be setters and getters to deal with it on per-texture basis,
    # but thus far I couldnt figure out how to make them work properly #TODO
    if spritesheet.getTexturesPower2():
        if not _is_power_of_two(columns) or not _is_power_of_two(rows):
            raise exceptions.InvalidSpriteSize(spritesheet.get_name(), sprite_sizes)

    # Extract texture's image from memory
    sheet_image = Image()
    spritesheet.store(sheet_image)

    images = []
    for row in range(0, rows):
        log.debug(f"Processing row{row}")
        for column in range(0, columns):
            log.debug(f"Processing column {column}")
            # THIS WAS BUGGED - I HAD TO FLIP IT
            x = column * sprite_x
            y = row * sprite_y
            # passing amount of channels is important to allow transparency
            pic = Image(sprite_x, sprite_y, sheet_image.get_num_channels())
            pic.blendSubImage(sheet_image, 0, 0, x, y, sprite_x, sprite_y, 1.0)
            images.append(pic)

    log.debug(f"Got following images: {images}")
    return images


def to_textures(
    images: list,
    name_mask: str = None,
    image_sizes: LPoint2 = None,
    texture_filter: SamplerState = None,
) -> list:
    """Convert provided list of PNMImage objects into Texture objects"""
    # doing it like that to enable ez override in get_textures()
    name_mask = name_mask or "sprite"
    textures = []

    # without name mask, this may seem like it returns empty sequence, but its not
    for num, item in enumerate(images):
        # this is how we turn image into texture
        texture = Texture(f"{name_mask}_{num}")
        texture.load(item)
        if texture_filter is not None:
            texture.set_magfilter(texture_filter)
            texture.set_minfilter(texture_filter)
        if image_sizes:
            texture.set_orig_file_size(*image_sizes, 1)
        textures.append(texture)

    log.debug(f"Got following textures: {textures}")
    return textures


def get_textures(
    spritesheet: Texture, sprite_sizes: tuple, texture_filter: SamplerState = None
) -> list:
    """Cut provided spritesheet texture into multiple textures"""
    images = get_images(
        spritesheet=spritesheet,
        sprite_sizes=sprite_sizes,
    )
    # Allowing for inheriting filter from parent in case its been set
    # This is based on magfilter, coz I cant make it inherit from one or another
    # since they all have defaults set to enumerator with non-zero value
    if texture_filter is None:
        texture_filter = spritesheet.get_magfilter()

    return to_textures(images, spritesheet.get_name(), sprite_sizes, texture_filter)
