import logging
from panda3d.core import Texture

log = logging.getLogger(__name__)

#idk if this thing deserve its own module, but at least it doesnt consume much space
def cut_spritesheet(spritesheet, size):
    '''Receive str(path to spritesheet) and tuple of sprite size = (x, y). Based
    on sprite size and size of spritesheet, make list of offsets for each sprite
    on the sheet, which can later be used to select, some particular sprite to use.
    Then returns said list to function that requested it'''

    #for now, this has 2 limitations:
    # 1. Spritesheet HAS TO DIVIDE TO PROVIDED SPRITE SIZE WITHOUT REMAINDER. If
    #it doesnt cut to perfect sprites, you will get strange results during using
    #some of these sprites.
    # 2. Amount of sprite rows and columns MUST BE POWER OF 2. Otherwise - see
    #above. This is because of limitation of set_tex_offset() and set_tex_scale()
    #functions, both of which operate with floats between 0 and 1 to determine
    #texture's size and position.
    #I assume, its possible to fix both of these. But right now I have no idea how
    #As for first - maybe cut garbage data with PNMimage module, before processing?

    log.debug(f"Attempting to cut spritesheet into sprites of {size} size")
    size_x, size_y = size

    #Determining amount of sprites in each row
    spritesheet_x = spritesheet.get_orig_file_x_size()
    spritesheet_y = spritesheet.get_orig_file_y_size()

    sprite_columns = int(spritesheet_x / size_x)
    sprite_rows = int(spritesheet_y / size_y)
    log.debug(f"Our sheet has {sprite_columns}x{sprite_rows} sprites")

    #idk if these should be flipped - its 3 am
    #this may backfire on values bigger than one... but it should never happen
    horizontal_offset_step = 1/sprite_columns
    vertical_offset_step = 1/sprite_rows
    log.debug(f"Offset steps are {horizontal_offset_step, vertical_offset_step}")

    offsets = []

    #dont ask questions, "it just works".
    #Basically, the thing is: originally, I did the following:
    #for row in range(0, sprite_rows):
    #BUT, this made offsets list start from bottom layer to top, which worked but
    #broke the whole "from top left to bottom right" style of image processing.
    #So I went for this "kinda hacky" solution. It works on 2x2 sheet, idk about
    #anything bigger than that
    for row in range(sprite_rows-1, -1, -1):
        log.debug(f"Processing row {row}")
        for column in range(0, sprite_columns):
            log.debug(f"Processing column {column}")
            horizontal_offset = column * horizontal_offset_step
            vertical_offset = row * vertical_offset_step
            log.debug(f"Got offsets: {horizontal_offset, vertical_offset}")
            offsets.append((horizontal_offset, vertical_offset))

    log.debug(f"Spritesheet contain following offsets: {offsets}")

    #maybe rename it into something more convenient?
    sprites = {}
    sprites['offset_steps'] = (horizontal_offset_step, vertical_offset_step)
    sprites['offsets'] = offsets

    log.debug(f"Got following data: {sprites}, returning")

    return sprites
