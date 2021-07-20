import logging

log = logging.getLogger(__name__)


class InvalidSpriteSize(Exception):
    """Exception thrown if spritesheet's size doesnt cut into provided sprite's
    sizes perfectly
    """

    def __init__(self, spritesheet, sprite_sizes):
        message = f"{spritesheet} wont cut into {sprite_sizes} chunks perfectly"
        super().__init__(message)
