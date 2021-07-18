*Spritesheet handling library for Panda3D*

# p3dss

## Description:

**p3dss** is a spritesheet handling library, initially started as part of my WIP
game [a2s3](https://github.com/moonburnt/a2s3). While its main focus is to provide
a single object to handle all sprites and animations on spritesheet image, it
also has some side abilities, such as batch texture cutting.

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
- Some functionality may require your spritesheet to fit such amount of sprites
into its rows and columns, that **will be the power of 2**.
Depending on case, it may be possible to circuimvent it with Config.rpc magic
(see example code for further info).

## Usage:

- Install library with setup.py
- Check [usage examples](https://github.com/moonburnt/p3dss/tree/master/example)

## License:

This software has been licensed under [MIT](
https://github.com/moonburnt/p3dss/blob/master/LICENSE).
For license of media used in example snippets, see [media_info.txt](
https://github.com/moonburnt/p3dss/tree/master/example/media/media_info.txt)
