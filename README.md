*Spritesheet handling library for Panda3D*

# p3dss

## Description:

**p3dss** is a spritesheet handling library, initially started as part of my WIP
game [a2s3](https://github.com/moonburnt/a2s3). Since its beginning, I've added
quite a few features and detached all parts that made it game-specifix, so now
its possible to use it in literally any project. It also has been relicensed under
more permissive license, so now its possible to use it in proprietary projects too.

## Dependencies:

This project depends solely on panda3d and nothing else.

## Limitations:

I've only tested this with .png images, but theoretically every texture format
supported by panda3d itself, should work. For as long as its static image and not
something already animated (gif, etc).

## Usage:

- Install library with setup.py
- Check [usage examples](https://github.com/moonburnt/p3dss/tree/master/example)

## License:

This software has been licensed under [MIT](LICENSE). For license of media used
in example snippets, see [sprite_info.txt](
https://github.com/moonburnt/p3dss/tree/master/example/sprite_info.txt)
