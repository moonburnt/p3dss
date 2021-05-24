*Spritesheet handling library for Panda3D*

# p3dss

## Description:

**p3dss** is a spritesheet handling library, initially started as part of my WIP
game [a2s3](https://github.com/moonburnt/a2s3). Since its beginning, I've added
quite a few features and detached all parts that made it game-specific, so now
its possible to use it in literally any project. It also has been relicensed under
more permissive license, so now its possible to use it in proprietary projects too.

## Development Status:

Work in progress. While I generally try to make each update stable, there may be
changes requiring code adjustments. If you will consider to use this library -
refer to the particular version in your project's dependencies.

## Dependencies:

This project depends solely on panda3d and nothing else.

## Limitations:

1. I've only tested this with .png images, but theoretically every texture format
supported by panda3d itself, should work. For as long as its static image and not
something already animated (gif, etc).

2. Because this library's spritesheet handling mechanism is based on setting
offsets, rather than cutting image in memory, following limitations apply:
- Spritesheet **has to divide to provided sprite size without remainder**. If it
doesnt cut to perfect sprites, you will get strange results while using some of
these (e.g blurry parts, parts of other sprite visible on previous and such)
- Amount of sprite rows and columns **must be the power of 2**. Otherwise you will
get glitches described above

## Usage:

- Install library with setup.py
- Check [usage examples](https://github.com/moonburnt/p3dss/tree/master/example)

## License:

This software has been licensed under [MIT](LICENSE). For license of media used
in example snippets, see [sprite_info.txt](
https://github.com/moonburnt/p3dss/tree/master/example/sprite_info.txt)
