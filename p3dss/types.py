from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
import logging

log = logging.getLogger(__name__)

SpritesheetData = namedtuple(
    "SpritesheetData", ["spritesheet", "offsets", "step_sizes"]
)


@dataclass(frozen=True)
class SpritesheetItem:
    """Storage that holds info about named spritesheet items"""

    # Name of this sequence
    name: str
    # Sequence of sprite numbers, even if its just one
    sprites: tuple
    playback_speed: float = 0.1
    # Can be int too. If not set - sequence will play till the end.
    # Not implemented right now #TODO
    # playback_length: float = 0.0
    # Should we start this sequence again at the end or not
    loop: bool = False
    # This specifies if we should reset to default item once this one is over
    # You probably shouldnt use it with single-sprite without length, lol
    reset_on_complete: bool = False


class PlaybackState(Enum):
    """Playback states of SpritesheetNode"""

    stop = 0
    play = 1
    pause = 2
