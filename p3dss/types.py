from collections import namedtuple
import logging

log = logging.getLogger(__name__)

# Coordinates = namedtuple("Coordinates", ["x", "y"])
SpritesheetData = namedtuple(
    "SpritesheetData", ["spritesheet", "offsets", "step_sizes"]
)
